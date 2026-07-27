"""Regression tests for the three ways this service used to fail slowly.

Each of these is a bug that leaves the process running and answering health
checks while it stops being able to do its job — the failure mode that does not
page anyone. They are grouped here because they share that shape, not because
they share code:

* ``_abandon``    — a cancelled request used to leave its coalescer key
                    registered and its future unsettled, so every later request
                    for the same query parked forever. Permanent: nothing
                    unregisters the key short of a restart.
* ``QueueTracker`` — cancelling while queued used to decrement the wrong
                    counter, leaking ``waiting`` until the queue guard 503'd an
                    idle server.
* ``ResultCache``  — unbounded, on a key space (``/search`` text x ``rows``)
                    that any client can enumerate.

No pytest-asyncio: each test drives one coroutine on a fresh loop via ``run``.
"""
import asyncio

import pytest
# Imported, not `importorskip`ed: aiohttp is what ha_api is written in, so a
# skip here would report "nothing to check" for a service that cannot start.
# Missing dependencies are a broken environment, and the gate script says so
# with its own exit code rather than by quietly not running anything.
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

from conftest import run
from vfbquery import ha_api


# ---------------------------------------------------------------------------
# _abandon — the coalescer contract under cancellation
# ---------------------------------------------------------------------------

def test_abandon_settles_the_future_and_frees_the_key():
    async def go():
        coalescer = ha_api.RequestCoalescer()
        fut, owner = await coalescer.get_or_create("k")
        assert owner and coalescer.in_flight_count == 1

        ha_api._abandon(coalescer, fut, "k")

        assert fut.done() and isinstance(fut.exception(), ha_api.Overloaded)
        assert coalescer.in_flight_count == 0
        # The key is free, so the retry the 503 asks for starts a fresh future
        # rather than joining a dead one.
        fut2, owner2 = await coalescer.get_or_create("k")
        assert owner2 and fut2 is not fut

    run(go())


def test_abandon_is_a_noop_once_the_future_is_settled():
    """It lives in `finally`, so it runs on the success path too.

    If it were not a no-op there it would replace a good result with a 503 on
    every single request — so this is the test that stops the backstop from
    being worse than the bug.
    """
    async def go():
        coalescer = ha_api.RequestCoalescer()
        fut, _ = await coalescer.get_or_create("k")
        fut.set_result({"rows": [{"id": "VFB_1"}]})
        await coalescer.remove("k")

        ha_api._abandon(coalescer, fut, "k")

        assert fut.result() == {"rows": [{"id": "VFB_1"}]}

    run(go())


def _search_app(hold):
    """Just enough app for handle_search; the Solr step is patched out."""
    app = web.Application()
    app["result_cache"] = ha_api.ResultCache(ttl_seconds=300)
    app["coalescer"] = ha_api.RequestCoalescer()
    app["search_semaphore"] = asyncio.Semaphore(1)
    app["search_queue_wait"] = 5.0
    app["search_stats"] = {"in_flight": 0, "queued": 0, "served": 0,
                           "shed": 0, "failed": 0}
    app["http"] = None
    return app


def test_cancelled_owner_does_not_strand_the_key(monkeypatch):
    """The bug this backstop exists for, end to end.

    ``asyncio.CancelledError`` is a ``BaseException``, so the handler's
    ``except Exception`` never saw it: the owner vanished holding a registered
    key and an unsettled future, and the *next* request for that query awaited
    it forever. It is latent today only because aiohttp defaults
    ``handler_cancellation=False`` — one config change from a permanent outage,
    which is not a margin worth relying on.
    """
    async def slow_search(app, query, rows, limit=None, **facets):
        await asyncio.sleep(30)
        raise AssertionError("should have been cancelled")

    monkeypatch.setattr(ha_api, "_solr_search_ranked", slow_search, raising=True)

    async def go():
        app = _search_app(hold=30)
        req = make_mocked_request("GET", "/search?query=abc", app=app)
        task = asyncio.ensure_future(ha_api.handle_search(req))
        await asyncio.sleep(0.2)                 # let it register the key
        assert app["coalescer"].in_flight_count == 1

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        # Both halves matter: a freed key with an unsettled future still hangs
        # anyone who attached before the cancellation.
        assert app["coalescer"].in_flight_count == 0, "coalescer key stranded"

        # And the query is usable again rather than poisoned for the life of
        # the process. Patch in something fast so this does not just re-hang.
        async def fast_search(app, query, rows, limit=None, **facets):
            return [{"short_form": "FBbt_1"}], 1, {"numFound": 1}, 1

        monkeypatch.setattr(ha_api, "_solr_search_ranked", fast_search,
                            raising=True)
        resp = await asyncio.wait_for(
            ha_api.handle_search(
                make_mocked_request("GET", "/search?query=abc", app=app)),
            timeout=5)
        assert resp.status == 200

    run(go())


def test_waiters_of_a_cancelled_owner_get_an_answer(monkeypatch):
    """A coalesced waiter must be told, not left holding the future.

    This is the half that survives even if the key is freed: whoever attached
    before the owner was cancelled is awaiting an object only the owner could
    ever settle.
    """
    async def slow_search(app, query, rows, limit=None, **facets):
        await asyncio.sleep(30)

    monkeypatch.setattr(ha_api, "_solr_search_ranked", slow_search, raising=True)

    async def go():
        app = _search_app(hold=30)
        owner = asyncio.ensure_future(ha_api.handle_search(
            make_mocked_request("GET", "/search?query=abc", app=app)))
        await asyncio.sleep(0.2)
        waiter = asyncio.ensure_future(ha_api.handle_search(
            make_mocked_request("GET", "/search?query=abc", app=app)))
        await asyncio.sleep(0.2)
        assert app["coalescer"].coalesced_total == 1, "the waiter did not coalesce"

        owner.cancel()
        with pytest.raises(asyncio.CancelledError):
            await owner

        resp = await asyncio.wait_for(waiter, timeout=5)
        assert resp.status == 503                # told to retry, not stranded

    run(go())


# ---------------------------------------------------------------------------
# QueueTracker — which counter a cancelled request was holding
# ---------------------------------------------------------------------------

def test_finish_work_started_false_releases_the_waiting_slot():
    async def go():
        t = ha_api.QueueTracker()
        await t.enter_queue()
        assert t.snapshot["waiting"] == 1

        # Cancelled before it ever got a worker slot: what it holds is a
        # *waiting* slot. Decrementing `active` here is the leak.
        await t.finish_work(started=False)

        assert t.snapshot == {"active": 0, "waiting": 0, "total_served": 0}

    run(go())


def test_finish_work_default_still_releases_an_active_slot():
    async def go():
        t = ha_api.QueueTracker()
        await t.enter_queue()
        await t.leave_queue_start_work()
        assert t.snapshot["active"] == 1 and t.snapshot["waiting"] == 0
        await t.finish_work()
        assert t.snapshot == {"active": 0, "waiting": 0, "total_served": 1}

    run(go())


def test_repeated_queued_cancellations_do_not_drift():
    """The leak was cumulative, which is why it presented as a slow death.

    One mis-decrement is invisible; `max_queue_depth` of them and the guard
    503s every request on a completely idle server.
    """
    async def go():
        t = ha_api.QueueTracker()
        for _ in range(250):                 # > the default max_queue_depth
            await t.enter_queue()
            await t.finish_work(started=False)
        assert t.snapshot["waiting"] == 0
        assert t.snapshot["active"] == 0

    run(go())


# ---------------------------------------------------------------------------
# ResultCache — bounded by entries and by rows
# ---------------------------------------------------------------------------

def _result(n_rows):
    return {"rows": [{"i": i} for i in range(n_rows)]}


def test_cache_evicts_least_recently_used_not_least_recently_inserted():
    c = ha_api.ResultCache(ttl_seconds=300, max_entries=3, max_rows=10**6)
    for k in ("a", "b", "c"):
        c.put(k, _result(1))
    c.get("a")                     # 'a' is now the most recent, 'b' the oldest
    c.put("d", _result(1))

    assert c.get("b") is None      # evicted
    assert c.get("a") is not None  # kept, because it was *used*
    assert c.size == 3 and c.evicted == 1


def test_cache_bounds_rows_not_just_entries():
    """Entry count alone does not bound memory.

    An unlimited /search for a common word ranks ~1500 rows (~0.5MB), so a
    thousand-entry cache of those is half a gigabyte while looking well within
    its limit.
    """
    c = ha_api.ResultCache(ttl_seconds=300, max_entries=1000, max_rows=100)
    c.put("big", _result(60))
    c.put("also_big", _result(60))
    assert c.get("big") is None            # pushed out by the row ceiling
    assert c.rows == 60 and c.evicted == 1


def test_an_oversized_entry_is_evicted_last_but_still_evicted():
    """The row ceiling is a bound, so nothing is exempt from it.

    A result bigger than the whole ceiling is dropped rather than kept — it
    becomes a permanent miss, which is a cost, not a wrong answer, and the
    alternative is a memory bound that silently isn't one. It is evicted
    *last*, though: the colder entries go first.
    """
    c = ha_api.ResultCache(ttl_seconds=300, max_entries=10, max_rows=50)
    c.put("cold", _result(10))
    c.put("huge", _result(500))
    assert c.get("cold") is None and c.get("huge") is None
    assert c.size == 0 and c.rows == 0


def test_the_default_ceiling_leaves_room_for_the_largest_cacheable_result():
    """Asserted as the ratio the comment claims, not merely as `>`.

    `_evict_to_fit` drops an entry heavier than the whole ceiling, so the two
    constants have to stay far enough apart that no single handler result can
    approach it. Reading the deploy's env would make a legitimate override
    (`VFBQUERY_RESULT_ROW_CAP=100000`) fail a *unit* test, so this checks the
    defaults the module ships with.
    """
    assert ha_api.DEFAULT_CACHE_MAX_ROWS == 4 * ha_api.DEFAULT_RESULT_ROW_CAP


def test_replacing_a_key_does_not_double_count_its_rows():
    c = ha_api.ResultCache(ttl_seconds=300, max_entries=10, max_rows=10**6)
    c.put("k", _result(10))
    c.put("k", _result(3))
    assert c.size == 1 and c.rows == 3


def test_cache_counts_a_rowless_result_as_one():
    """Term-info payloads have no `rows`; they must still count toward entries."""
    c = ha_api.ResultCache(ttl_seconds=300, max_entries=2, max_rows=10**6)
    c.put("a", {"term": {"core": {}}})
    c.put("b", {"term": {"core": {}}})
    c.put("c", {"term": {"core": {}}})
    assert c.size == 2 and c.rows == 2 and c.evicted == 1


def test_invalidate_releases_the_row_budget_too():
    c = ha_api.ResultCache(ttl_seconds=300, max_entries=10, max_rows=10**6)
    c.put("k", _result(10))
    c.invalidate("k")
    assert c.get("k") is None and c.size == 0 and c.rows == 0
    c.invalidate("never_there")            # no-op, not a KeyError

def test_expiry_releases_the_row_budget_too():
    """A TTL drop that forgot the row count would ratchet `rows` upward until
    the cache believed it was full of entries it no longer held."""
    c = ha_api.ResultCache(ttl_seconds=0, max_entries=10, max_rows=10**6)
    c.put("k", _result(10))
    assert c.get("k") is None              # expired on read
    assert c.rows == 0

    c2 = ha_api.ResultCache(ttl_seconds=0, max_entries=10, max_rows=10**6)
    c2.put("k", _result(10))
    assert c2.evict_expired() == 1         # ...and on the sweep
    assert c2.rows == 0 and c2.size == 0


def test_cache_ceilings_are_configurable_from_the_environment(monkeypatch):
    """They are deploy knobs, so the reader has to actually read them."""
    monkeypatch.setenv("VFBQUERY_CACHE_MAX_ROWS", "42")
    assert ha_api._int_env("VFBQUERY_CACHE_MAX_ROWS", 100000) == 42


@pytest.mark.parametrize("raw", ["", "   ", "lots", "1_0_0!"])
def test_a_ceiling_that_is_not_a_number_falls_back_rather_than_crashing(
        monkeypatch, raw):
    """Every way of not setting it has to reach the same default.

    Empty is the one that bites: that is what an absent value looks like coming
    out of a k8s env block, and `int("")` raises like any other bad input. A
    tuning parameter must never be the reason a pod refuses to start.
    """
    monkeypatch.setenv("VFBQUERY_CACHE_MAX_ROWS", raw)
    assert ha_api._int_env("VFBQUERY_CACHE_MAX_ROWS", 100000) == 100000


def test_an_unset_ceiling_reaches_the_default():
    """The env is not guaranteed clean, so delete rather than assume."""
    import os
    os.environ.pop("VFBQUERY_CACHE_MAX_ROWS", None)
    assert ha_api._int_env("VFBQUERY_CACHE_MAX_ROWS", 100000) == 100000


# ---------------------------------------------------------------------------
# ...and the bound has to see the payload it is bounding
# ---------------------------------------------------------------------------

def _connectivity(n):
    """The real /query_connectivity envelope: no `rows` key anywhere."""
    return {"connections": [{"weight": 5} for _ in range(n)],
            "warnings": [], "count": n}


def test_a_connectivity_result_is_weighed_by_its_connections():
    """The row ceiling counted `rows` only, so this whole shape weighed 1.

    Not hypothetical: Tm1 -> T3 neuron at the default weight is ~12 000
    connections. A cache holding a thousand of those reported 1 000 rows
    against a ceiling of 100 000 while actually holding twelve million — the
    exact failure an entry count alone was supposed to be too weak to catch.
    """
    c = ha_api.ResultCache(ttl_seconds=300, max_entries=1000, max_rows=10**6)
    c.put("conn", _connectivity(11916))
    assert c.rows == 11916

    # ...so the ceiling now fires on them, which is the whole point.
    c = ha_api.ResultCache(ttl_seconds=300, max_entries=1000, max_rows=20000)
    c.put("a", _connectivity(11916))
    c.put("b", _connectivity(11916))
    assert c.get("a") is None and c.rows == 11916 and c.evicted == 1


def test_the_weight_is_the_longest_list_not_a_named_key():
    """So an endpoint inventing a third key cannot repeat the mistake."""
    assert ha_api.ResultCache._weight({"whatever": [0] * 7, "count": 7}) == 7
    # A short list next to a long one must not win.
    assert ha_api.ResultCache._weight(
        {"warnings": ["a"], "connections": [0] * 9}) == 9
    # Rowless payloads (term info) still cost their entry slot.
    assert ha_api.ResultCache._weight({"term": {"core": {}}}) == 1
    assert ha_api.ResultCache._weight("not a container") == 1


def test_the_row_cap_truncates_connections_too():
    """Same reasoning as `rows`: the cap exists to bound the serialised body.

    /query_connectivity is capable of the largest payloads the service has, so
    exempting it left the one endpoint that most needs the cap without it.
    """
    capped = ha_api._cap_result_rows(_connectivity(50), cap=10)
    assert len(capped["connections"]) == 10
    assert capped["capped"] is True and capped["limit"] == 10
    assert capped["count"] == 50               # the true total is preserved

    # Under the cap it is returned untouched — no stray `capped` flag.
    small = _connectivity(3)
    assert ha_api._cap_result_rows(small, cap=10) is small
