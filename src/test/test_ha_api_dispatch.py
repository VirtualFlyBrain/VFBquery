"""Unit tests for the 1.22.36 dispatch, budget and parameter-warning changes.

Deliberately free of Neo4j and Solr: every one of these is about the plumbing
between an HTTP request and a worker, and that plumbing is exactly what a live
query hides. The compute-budget behaviour in particular can only be tested with
a worker whose duration is known in advance.
"""
import asyncio
import functools

import pytest

from vfbquery import ha_api


def sync(fn):
    """Run an async test body on a fresh loop.

    Deliberately not pytest-asyncio: the coroutine tests below are the only
    async ones in the suite, and they are not worth a new test dependency that
    CI would have to install on every run.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))
    return wrapper


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

class _Req:
    """The two attributes of a request the parameter helpers actually read."""

    def __init__(self, **query):
        self.query = dict(query)


def test_flag_warning_silent_on_recognised_values():
    for value in ("true", "1", "yes", "on", "false", "0", "no", "off", "", "TRUE"):
        assert ha_api._flag_warning(_Req(f=value), "f") is None, value
    assert ha_api._flag_warning(_Req(), "f") is None


def test_flag_warning_names_the_typo():
    warn = ha_api._flag_warning(_Req(include_graph="y"), "include_graph")
    assert warn is not None
    assert "include_graph" in warn and "'y'" in warn
    assert "read as false" in warn


def test_unknown_param_warning_suggests_the_near_miss():
    warns = ha_api._unknown_param_warnings(
        _Req(filter_type="Neuron"), ha_api._SEARCH_PARAMS)
    assert len(warns) == 1
    assert "'filter_type'" in warns[0] and "'filter_types'" in warns[0]


def test_unknown_param_warning_without_a_near_miss():
    warns = ha_api._unknown_param_warnings(
        _Req(utm_source="twitter"), ha_api._SEARCH_PARAMS)
    assert warns == ["Ignored unrecognised parameter 'utm_source'"]


def test_known_params_produce_no_warnings():
    assert ha_api._unknown_param_warnings(
        _Req(query="Tm1", rows="500", unique="true"),
        ha_api._SEARCH_PARAMS) == []


def test_empty_known_set_disables_the_check():
    """A handler that has not declared its parameters must not accuse callers."""
    assert ha_api._unknown_param_warnings(_Req(anything="1"), None) == []


def test_with_warnings_does_not_mutate_the_cached_result():
    cached = {"rows": [1, 2]}
    out = ha_api._with_warnings(cached, ["careful"])
    assert out["warnings"] == ["careful"]
    assert "warnings" not in cached, "cached dict was mutated in place"


def test_with_warnings_appends_to_existing():
    out = ha_api._with_warnings({"warnings": ["a"]}, ["b"])
    assert out["warnings"] == ["a", "b"]


def test_with_warnings_is_a_noop_without_warnings():
    cached = {"rows": []}
    assert ha_api._with_warnings(cached, []) is cached


# ---------------------------------------------------------------------------
# exclude_dbs resolution
# ---------------------------------------------------------------------------

SITES = [
    {"label": "FlyWire", "symbol": "fw", "short_form": "flywire783"},
    {"label": "male CNS", "symbol": "mc", "short_form": "male_cns_v0_9"},
    {"label": "hemibrain", "symbol": "hb",
     "short_form": "neuprint_JRC_Hemibrain_1point2point1"},
    {"label": "Adult Brain (CATMAID)", "symbol": "fafb",
     "short_form": "catmaid_fafb"},
]


def test_exclude_dbs_short_form_resolves_to_the_symbol():
    resolved, rewritten = ha_api._resolve_exclude_dbs(["flywire783"], SITES)
    assert resolved == ["fw"]
    assert rewritten == ["flywire783"]


def test_exclude_dbs_symbol_is_already_canonical():
    resolved, rewritten = ha_api._resolve_exclude_dbs(["fw"], SITES)
    assert resolved == ["fw"]
    assert rewritten == []


def test_exclude_dbs_default_resolves_to_itself():
    """The cache-key property: shipping this must not orphan cached defaults."""
    from vfbquery.vfb_connectivity import DEFAULT_EXCLUDE_DBS
    resolved, rewritten = ha_api._resolve_exclude_dbs(
        list(DEFAULT_EXCLUDE_DBS), SITES)
    assert resolved == list(DEFAULT_EXCLUDE_DBS)
    assert rewritten == []


def test_exclude_dbs_preserves_caller_order():
    resolved, _ = ha_api._resolve_exclude_dbs(["fafb", "hb"], SITES)
    assert resolved == ["fafb", "hb"], "order must not be normalised"


def test_exclude_dbs_accepts_a_nickname():
    """`flywire` is not a spelling of anything, and is what people type."""
    resolved, rewritten = ha_api._resolve_exclude_dbs(["flywire"], SITES)
    assert resolved == ["fw"]
    assert rewritten == ["flywire"]


def test_exclude_dbs_unknown_name_raises_with_a_suggestion():
    with pytest.raises(ha_api.BadParam) as exc:
        ha_api._resolve_exclude_dbs(["flywire999"], SITES)
    message = str(exc.value)
    assert "flywire999" in message
    assert "flywire783" in message, "no did-you-mean suggestion"
    assert "/list_connectome_datasets" in message


def test_exclude_dbs_nonsense_raises_without_a_suggestion():
    with pytest.raises(ha_api.BadParam) as exc:
        ha_api._resolve_exclude_dbs(["zzzzzz"], SITES)
    assert "zzzzzz" in str(exc.value)


def test_exclude_dbs_fails_open_without_a_vocabulary():
    """An unavailable dataset list must not turn every request into a 400."""
    resolved, rewritten = ha_api._resolve_exclude_dbs(["anything"], [])
    assert resolved == ["anything"]
    assert rewritten == []


# ---------------------------------------------------------------------------
# _shielded
# ---------------------------------------------------------------------------

@sync
async def test_shielded_timeout_does_not_cancel_the_work():
    done = []

    async def work():
        await asyncio.sleep(0.2)
        done.append("finished")
        return "result"

    task = asyncio.ensure_future(work())
    with pytest.raises(asyncio.TimeoutError):
        await ha_api._shielded(task, 0.05)
    assert not task.cancelled(), "the budget cancelled the computation"

    assert await task == "result"
    assert done == ["finished"]


@sync
async def test_shielded_returns_within_budget():
    async def work():
        return 42
    assert await ha_api._shielded(asyncio.ensure_future(work()), 5) == 42


@sync
async def test_shielded_zero_budget_waits_indefinitely():
    async def work():
        await asyncio.sleep(0.05)
        return "slow"
    assert await ha_api._shielded(asyncio.ensure_future(work()), 0) == "slow"


# ---------------------------------------------------------------------------
# _spawn_compute
# ---------------------------------------------------------------------------

class _Cache:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def put(self, key, value):
        self.store[key] = value

    def invalidate(self, key):
        self.store.pop(key, None)


class _Coalescer:
    def __init__(self):
        self.keys = {}

    async def get_or_create(self, key):
        if key in self.keys:
            return self.keys[key], False
        fut = asyncio.get_event_loop().create_future()
        self.keys[key] = fut
        return fut, True

    async def remove(self, key):
        self.keys.pop(key, None)


class _Tracker:
    def __init__(self):
        self.events = []

    async def enter_queue(self):
        self.events.append("queue")

    async def leave_queue_start_work(self):
        self.events.append("start")

    async def finish_work(self, started=False):
        self.events.append(("finish", started))

    @property
    def snapshot(self):
        return {"active": 0, "waiting": 0, "total_served": 0}


class _InlinePool:
    """Stands in for the thread pool: runs the worker on the loop's executor."""


def _make_app():
    return {
        "result_cache": _Cache(),
        "pool": None,          # None => loop default executor
        "semaphore": asyncio.Semaphore(4),
    }


@sync
async def test_spawn_compute_caches_and_resolves():
    app = _make_app()
    coalescer, tracker = _Coalescer(), _Tracker()
    fut, _ = await coalescer.get_or_create("k")

    task = ha_api._spawn_compute(app, coalescer, tracker, fut, "k",
                                 lambda a, b: {"rows": [a, b]}, (1, 2))
    result = await task
    assert result == {"rows": [1, 2]}
    assert app["result_cache"].get("k") == {"rows": [1, 2]}
    assert fut.done() and fut.result() == {"rows": [1, 2]}
    assert ("finish", True) in tracker.events


@sync
async def test_spawn_compute_survives_a_handler_that_gives_up():
    """The regression this whole change exists for.

    The handler stops waiting after its budget; the computation must still land
    in the cache so the caller's retry is cheap instead of starting over.
    """
    app = _make_app()
    coalescer, tracker = _Coalescer(), _Tracker()
    fut, _ = await coalescer.get_or_create("slow")

    def slow_worker():
        import time
        time.sleep(0.3)
        return {"rows": ["expensive"]}

    task = ha_api._spawn_compute(app, coalescer, tracker, fut, "slow",
                                 slow_worker, ())
    with pytest.raises(asyncio.TimeoutError):
        await ha_api._shielded(task, 0.05)

    assert app["result_cache"].get("slow") is None, "not finished yet"
    await asyncio.wait_for(asyncio.shield(task), 5)
    assert app["result_cache"].get("slow") == {"rows": ["expensive"]}


@sync
async def test_spawn_compute_store_hook_shapes_what_is_cached():
    app = _make_app()
    coalescer, tracker = _Coalescer(), _Tracker()
    fut, _ = await coalescer.get_or_create("k")

    task = ha_api._spawn_compute(app, coalescer, tracker, fut, "k",
                                 lambda: {"rows": [1, 2, 3]}, (),
                                 store=lambda r: {"rows": r["rows"][:1]})
    assert await task == {"rows": [1]}
    assert app["result_cache"].get("k") == {"rows": [1]}


@sync
async def test_spawn_compute_propagates_failure_to_waiters():
    app = _make_app()
    coalescer, tracker = _Coalescer(), _Tracker()
    fut, _ = await coalescer.get_or_create("boom")

    def failing():
        raise RuntimeError("neo4j said no")

    task = ha_api._spawn_compute(app, coalescer, tracker, fut, "boom",
                                 failing, ())
    with pytest.raises(RuntimeError):
        await task
    assert fut.done() and isinstance(fut.exception(), RuntimeError)
    assert app["result_cache"].get("boom") is None
    assert "boom" not in coalescer.keys


@sync
async def test_computing_response_is_503_with_retry_after():
    resp = ha_api._computing_response("key", 180)
    assert resp.status == 503
    assert resp.headers["Retry-After"] == "30"
    assert b"still being computed" in resp.body
