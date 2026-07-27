"""Regression tests: shedding must not strand the requests that coalesced.

The coalescer's contract is that whoever creates a future settles it. Every
normal path in ``ha_api`` does. The *shed* paths did not: they dropped the key
and returned 503, leaving every request that had already attached to that key
awaiting a future nobody would ever complete — those handlers never returned at
all, and the client saw a hang rather than the 503 the server had decided on.

The window is neither theoretical nor small: the owner sits in
``asyncio.wait_for(sem.acquire(), timeout=search_queue_wait)`` — ten seconds by
default — with the key already registered, and shedding only happens under
concurrent load, which is precisely when duplicate queries arrive. The bug fired
exactly when the mechanism meant to protect the service was doing its job.

These drive the real handlers through a real aiohttp server with the search
budget shrunk to one slot, so the shed path is reached by genuine contention.
The app is assembled here rather than via ``create_app`` on purpose: that starts
a ``ProcessPoolExecutor`` whose initializer loads the whole query stack, which
these tests neither need nor should wait for.
"""
import asyncio

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from conftest import run
from vfbquery import ha_api


def _make_app(queue_wait):
    """Minimal app with just what /search and /xref touch, one search slot."""
    app = web.Application()
    app.router.add_get("/search", ha_api.handle_search)
    app.router.add_get("/xref", ha_api.handle_xref)

    async def on_startup(app):
        app["result_cache"] = ha_api.ResultCache(ttl_seconds=300)
        app["coalescer"] = ha_api.RequestCoalescer()
        app["search_semaphore"] = asyncio.Semaphore(1)
        app["search_queue_wait"] = queue_wait
        app["search_stats"] = {"in_flight": 0, "queued": 0, "served": 0,
                               "shed": 0, "failed": 0}
        app["http"] = None          # never reached; the Solr step is patched

    app.on_startup.append(on_startup)
    return app


async def _start(monkeypatch, hold=2.0, queue_wait=0.3):
    async def slow_search(app, query, rows, limit=None, **facets):
        await asyncio.sleep(hold)
        return [], 0, {"numFound": 0}, 0

    async def slow_terminfo(session, ids):
        await asyncio.sleep(hold)
        return {}

    monkeypatch.setattr(ha_api, "_solr_search_ranked", slow_search, raising=True)
    monkeypatch.setattr(ha_api, "_fetch_term_info_docs", slow_terminfo,
                        raising=True)
    client = TestClient(TestServer(_make_app(queue_wait)))
    await client.start_server()
    return client


async def _pile_up(client, path, params, n=4):
    """One request takes the only slot; ``n-1`` identical ones coalesce behind it.

    They share a cache key, so all but the first attach to the first's future —
    which is the state the bug stranded.
    """
    return await asyncio.wait_for(
        asyncio.gather(*[client.get(path, params=params) for _ in range(n)],
                       return_exceptions=True),
        timeout=25)


def test_search_waiters_get_the_503_not_a_hang(monkeypatch):
    async def go():
        client = await _start(monkeypatch, hold=2.0, queue_wait=0.3)
        try:
            hog = asyncio.ensure_future(
                client.get("/search", params={"query": "hog"}))
            await asyncio.sleep(0.1)
            rs = await _pile_up(client, "/search", {"query": "same"})
            # Reaching this line at all is the first half: before the fix the
            # three coalesced requests never returned and the gather above hit
            # its 25s timeout instead.
            assert [r.status for r in rs] == [503] * 4
            # The second half, and the one that discriminates. `_abandon` in the
            # `finally` is a *backstop* — revert `_shed` and it still settles the
            # future, so the waiters still get a 503 and a status-only assertion
            # would stay green. What it cannot fake is the shed's own answer:
            # `_abandon` carries "Request aborted, please retry" / Retry-After 1.
            # Asserting the header and the body is therefore what tells "the
            # owner shed and said so" apart from "something rescued the hang".
            for r in rs:
                assert r.headers.get("Retry-After") == "5"
                body = await r.json()
                assert body["error"] == "Search overloaded, please retry later"
            hog.cancel()
        finally:
            await client.close()

    run(go())


def test_xref_waiters_get_the_503_not_a_hang(monkeypatch):
    """Same contract on /xref — it shares the semaphore, so it sheds too.

    Asserted to the same depth as the /search sibling, and for the same reason:
    status alone does not distinguish the shed's 503 from the `_abandon`
    backstop's, so a status-only version of this test passed with `_shed`
    reverted.
    """
    async def go():
        client = await _start(monkeypatch, hold=2.0, queue_wait=0.3)
        try:
            hog = asyncio.ensure_future(
                client.get("/xref", params={"id": "VFB_hog"}))
            await asyncio.sleep(0.1)
            rs = await _pile_up(client, "/xref", {"id": "VFB_same"})
            assert [r.status for r in rs] == [503] * 4
            for r in rs:
                assert r.headers.get("Retry-After") == "5"
                body = await r.json()
                assert body["error"] == "Search overloaded, please retry later"
            hog.cancel()
        finally:
            await client.close()

    run(go())


def test_shed_frees_the_key_for_the_next_caller(monkeypatch):
    """A shed must not poison the cache key: the retry the 503 asks for has to
    be able to succeed once the pressure is off.

    This is the end-to-end half of the `remove` ordering in `_shed`, and it does
    bite: delete that `await coalescer.remove(...)` and the key stays registered
    holding a failed future, so the retry coalesces onto it and gets the *same*
    503 forever — a 503 that tells the caller to retry into a state that can
    never clear. The `finally: _abandon(...)` backstop does not save this one,
    because it returns early on an already-settled future.
    """
    async def go():
        client = await _start(monkeypatch, hold=0.5, queue_wait=0.05)
        try:
            hog = asyncio.ensure_future(
                client.get("/search", params={"query": "hog"}))
            await asyncio.sleep(0.05)
            shed = await client.get("/search", params={"query": "later"})
            assert shed.status == 503
            await hog                       # let the slot come back
            again = await client.get("/search", params={"query": "later"})
            assert again.status == 200
        finally:
            await client.close()

    run(go())


def test_a_shed_answers_with_the_overload_and_frees_its_key():
    """The two halves of `_shed` that are not about logging.

    Split from the GC test below because that one may not touch the future at
    all — see its docstring.
    """
    async def go():
        coalescer = ha_api.RequestCoalescer()
        fut, owner = await coalescer.get_or_create("k")
        assert owner
        resp = await ha_api._shed(coalescer, fut, "k", "nope", retry_after="7")
        assert resp.status == 503
        assert resp.headers["Retry-After"] == "7"
        exc = fut.exception()
        assert isinstance(exc, ha_api.Overloaded)
        # The waiters answer *from* this exception, so its payload is the wire
        # format, not an internal detail.
        assert (exc.message, exc.retry_after) == ("nope", "7")
        # Key released, so a retry starts a fresh future rather than joining a
        # failed one.
        fut2, owner2 = await coalescer.get_or_create("k")
        assert owner2 and fut2 is not fut

    run(go())


def test_shed_leaves_no_unretrieved_exception():
    """A shed with no waiters must not log 'exception was never retrieved'.

    ``_shed`` sets an exception on a future that, in the common case, nobody is
    awaiting. Retrieving it immediately is what keeps asyncio quiet at GC time;
    without that, every shed writes a spurious error into the service log and
    real errors get lost among them.

    The obvious way to write this does not work: an earlier version asserted
    ``isinstance(fut.exception(), Overloaded)``, and *that call* is itself the
    fix — it marks the exception retrieved, so deleting ``fut.exception()`` from
    ``_shed`` left the test green. The test has to reach the future's
    destructor without ever having looked inside it, which is why the identity
    of the exception is asserted in the test above and not here.

    So: install a handler, drop the only reference, collect. asyncio reports an
    unretrieved exception from ``Future.__del__``, which calls
    ``loop.call_exception_handler`` synchronously — no polling, no sleep.
    """
    async def go():
        import gc

        handled = []
        asyncio.get_event_loop().set_exception_handler(
            lambda loop, context: handled.append(context))

        coalescer = ha_api.RequestCoalescer()
        fut, _owner = await coalescer.get_or_create("k")
        await ha_api._shed(coalescer, fut, "k", "nope")

        del fut                 # the coalescer dropped its reference in _shed
        gc.collect()
        assert handled == [], (
            "shedding logged an asyncio error: "
            f"{[c.get('message') for c in handled]}")

    run(go())


def test_facet_validation_rejects_solr_syntax():
    """filter_types & friends land in `fq`/`bq` unescaped, so they are validated
    against a charset. A facet name containing Solr syntax is a 400, not a
    rewritten filter."""
    assert ha_api._parse_type_list("Class,Individual") == ["Class", "Individual"]
    assert ha_api._parse_type_list("") is None
    assert ha_api._parse_type_list(None) is None
    for bad in ("Class) OR (*:*", "a:b", 'x"y', "a b", "*", "x" * 65):
        with pytest.raises(ValueError):
            ha_api._parse_type_list(bad)
