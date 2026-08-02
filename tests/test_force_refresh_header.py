"""Regression tests: the refresh header the edge already speaks was ignored here.

The nginx layer in front of this service (``v3-cached``) has long defined
``X-Force-Refresh: true`` — from a whitelisted IP — as "bypass the edge cache
and overwrite the canonical slot with a fresh upstream response". This service
read no request headers at all, so that header refreshed the edge *from an
unrefreshed upstream*: the operator got a 200, the edge dutifully stored it, and
the stale answer was re-canonicalised for another six months.

The obvious workaround makes it worse rather than better. Appending
``&force_refresh=true`` does refresh this service, but it changes
``$request_uri`` and therefore the nginx cache key, so the fresh answer lands in
a *different* slot. The canonical URL — the one users actually call — can never
be healed that way, no matter how many times the refresh is run.

Honouring the header here closes the seam: one request, from the whitelist,
refreshes both layers at the URL that matters. These tests drive the real
handler through a real aiohttp server and assert on the observable consequence
— whether the in-process L1 entry was dropped and the worker re-ran — rather
than on any internal flag.

The app is assembled by hand rather than through ``create_app`` because that
starts a ``ProcessPoolExecutor`` whose initializer imports the entire query
stack. ``pool = None`` makes ``run_in_executor`` use the default thread pool,
which is all a stubbed worker needs.
"""
import asyncio

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from conftest import run
from vfbquery import ha_api


def _make_app():
    app = web.Application()
    app.router.add_get("/get_term_info", ha_api.handle_get_term_info)

    async def on_startup(app):
        app["result_cache"] = ha_api.ResultCache(ttl_seconds=300)
        app["coalescer"] = ha_api.RequestCoalescer()
        app["tracker"] = ha_api.QueueTracker()
        app["semaphore"] = asyncio.Semaphore(2)
        app["pool"] = None          # default executor; the worker is a stub

    app.on_startup.append(on_startup)
    return app


def _stub_worker(monkeypatch):
    """Replace the worker with one that counts runs and echoes force_refresh."""
    runs = []

    def fake_run_term_info(short_form, force_refresh=False):
        runs.append({"id": short_form, "force_refresh": force_refresh})
        return {"Name": short_form, "run": len(runs),
                "saw_force_refresh": force_refresh}

    monkeypatch.setattr(ha_api, "_run_term_info", fake_run_term_info,
                        raising=True)
    return runs


def _drive(headers_second=None, params_second=None):
    """Two identical requests; the second optionally carrying a refresh signal.

    The first populates the L1 cache. What the second does with it is the whole
    question.
    """
    async def go():
        client = TestClient(TestServer(_make_app()))
        await client.start_server()
        try:
            first = await client.get("/get_term_info", params={"id": "VFB_0001"})
            first_body = await first.json()
            second = await client.get(
                "/get_term_info",
                params=dict({"id": "VFB_0001"}, **(params_second or {})),
                headers=headers_second or {})
            second_body = await second.json()
            return first_body, second_body
        finally:
            await client.close()
    return run(go())


# ---------------------------------------------------------------------------
# The cache is real, so "it re-ran" means something
# ---------------------------------------------------------------------------

def test_a_repeat_request_is_served_from_the_l1_cache(monkeypatch):
    """The control. Without it, every assertion below proves nothing.

    If a plain repeat also re-ran the worker, "the header re-ran the worker"
    would be indistinguishable from "this endpoint never caches".
    """
    runs = _stub_worker(monkeypatch)
    first, second = _drive()
    assert len(runs) == 1
    assert first["run"] == second["run"] == 1


def test_the_query_parameter_still_refreshes(monkeypatch):
    """``force_refresh=true`` keeps working exactly as it did.

    The header is additive; nothing about the existing spelling changes.
    """
    runs = _stub_worker(monkeypatch)
    _, second = _drive(params_second={"force_refresh": "true"})
    assert len(runs) == 2
    assert runs[1]["force_refresh"] is True
    assert second["run"] == 2


def test_the_header_alone_refreshes(monkeypatch):
    """The fix. Same URL, no query parameter — so the edge key is unchanged.

    That last part is the point: this is a refresh that can heal the canonical
    cache slot, which ``&force_refresh=true`` structurally cannot.
    """
    runs = _stub_worker(monkeypatch)
    _, second = _drive(headers_second={"X-Force-Refresh": "true"})
    assert len(runs) == 2
    assert second["run"] == 2


def test_the_header_is_propagated_down_to_the_solr_cache(monkeypatch):
    """Dropping the L1 entry is only half a refresh.

    If the header invalidated the in-process cache but did not reach
    ``get_term_info``, the recompute would be served straight back out of the
    three-month Solr entry — the same stale answer, more slowly. The flag has to
    travel the whole way down.
    """
    runs = _stub_worker(monkeypatch)
    _, second = _drive(headers_second={"X-Force-Refresh": "true"})
    assert runs[1]["force_refresh"] is True
    assert second["saw_force_refresh"] is True


@pytest.mark.parametrize("value", ["true", "TRUE", "1", "yes", "on", " true "])
def test_the_accepted_spellings_match_the_edge(monkeypatch, value):
    """nginx accepts ``true|1|yes|on``; accepting a narrower set would be a trap.

    An operator whose ``X-Force-Refresh: 1`` bypassed the edge but not this
    service would see a fresh-looking 200 carrying stale content — the exact
    failure this change removes, reintroduced by a spelling mismatch.
    """
    runs = _stub_worker(monkeypatch)
    _drive(headers_second={"X-Force-Refresh": value})
    assert len(runs) == 2


@pytest.mark.parametrize("value", ["false", "0", "no", "off"])
def test_an_explicit_no_is_still_a_no(monkeypatch, value):
    runs = _stub_worker(monkeypatch)
    _, second = _drive(headers_second={"X-Force-Refresh": value})
    assert len(runs) == 1
    assert second["run"] == 1


# ---------------------------------------------------------------------------
# A misspelled header must not silently do nothing
# ---------------------------------------------------------------------------

def test_an_unrecognised_value_is_read_as_false_and_says_so(monkeypatch):
    """Silence here is the expensive failure mode.

    A bulk warm run sends this header hundreds of thousands of times. If
    ``X-Force-Refresh: please`` were read as false with no comment, the whole
    run would appear to succeed — 200s throughout — and refresh nothing, and
    nobody would find out until the previews were still blank weeks later.
    """
    _stub_worker(monkeypatch)

    async def go():
        client = TestClient(TestServer(_make_app()))
        await client.start_server()
        try:
            response = await client.get(
                "/get_term_info", params={"id": "VFB_0001"},
                headers={"X-Force-Refresh": "please"})
            return await response.json()
        finally:
            await client.close()

    body = run(go())
    warnings = body.get("warnings", [])
    assert any("X-Force-Refresh" in w for w in warnings), warnings
    # The warning has to be actionable, so it names the values that do work.
    assert any("true" in w for w in warnings), warnings


def test_a_good_header_produces_no_warning(monkeypatch):
    """Warnings that fire on correct usage get filtered out, then missed."""
    _stub_worker(monkeypatch)

    async def go():
        client = TestClient(TestServer(_make_app()))
        await client.start_server()
        try:
            response = await client.get(
                "/get_term_info", params={"id": "VFB_0001"},
                headers={"X-Force-Refresh": "true"})
            return await response.json()
        finally:
            await client.close()

    body = run(go())
    assert not [w for w in body.get("warnings", []) if "X-Force-Refresh" in w]


def test_the_header_is_not_mistaken_for_an_unknown_query_parameter(monkeypatch):
    """``_unknown_param_warnings`` polices the query string, not the headers."""
    _stub_worker(monkeypatch)

    async def go():
        client = TestClient(TestServer(_make_app()))
        await client.start_server()
        try:
            response = await client.get(
                "/get_term_info", params={"id": "VFB_0001"},
                headers={"X-Force-Refresh": "true"})
            return await response.json()
        finally:
            await client.close()

    assert "warnings" not in run(go())
