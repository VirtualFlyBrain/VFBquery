"""Endpoint tests for /search and /xref — the parts a helper test cannot reach.

``tests/test_xref.py`` covers the row-shaping helpers in isolation, and that is
where their edge cases belong. What it cannot cover is ``handle_xref`` itself:
the reverse direction's confirmation step, the candidate de-duplication and cap
that surround it, and the cache keys both handlers build. Those were unguarded —
deleting the exact-accession confirmation, the thing the endpoint was written to
do, left the whole suite green, as did dropping ``db`` and the facets from the
two cache keys.

Solr is replaced at the two seams the handlers reach it through
(``_solr_search_ranked`` and ``_fetch_term_info_docs``), so these run offline and
deterministically. Everything between those seams is the real handler: the same
coalescer, cache, semaphore and response envelope the service runs.
"""
import asyncio

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from conftest import run
from vfbquery import ha_api

# One candidate that really carries the accession, and one that merely ranks
# well for it. Free-text search on a bare numeric bodyId puts near-misses at the
# top — that is how the MCP resolved one to the wrong neuron, and it is the
# whole reason for the confirmation step.
WANTED = "1734350908"

TERM_INFOS = {
    "VFB_right": {
        "term": {"core": {"label": "DA1_lPN_R (FlyEM-HB:1734350908)"}},
        "xrefs": [
            {"accession": WANTED, "is_data_source": True,
             "link_base": "https://neuprint.janelia.org/?q=",
             "site": {"symbol": "hb", "short_form": "neuprint_hb",
                      "label": "Neuprint hemibrain"}},
            {"accession": WANTED, "is_data_source": False,
             "site": {"symbol": "", "short_form": "neuronbridge",
                      "label": "neuronbridge"}},
        ],
    },
    "VFB_nearmiss": {
        "term": {"core": {"label": "DA1_lPN_L (FlyEM-HB:1734350907)"}},
        "xrefs": [
            {"accession": "1734350907",
             "site": {"symbol": "hb", "short_form": "neuprint_hb",
                      "label": "Neuprint hemibrain"}},
        ],
    },
}


def _make_app(ranked_ids, term_infos=None, monkeypatch=None):
    """A real app around fake Solr seams.

    ``ranked_ids`` is what ``/search`` "found", in rank order and with whatever
    duplication the caller wants to test; ``fetched`` records the id lists the
    handler actually asked for, which is how the de-duplication and the
    candidate cap are observed rather than inferred from the row count.
    """
    fetched = []
    searched = []

    async def fake_search(app, query, rows, limit=None, **facets):
        searched.append({"query": query, "rows": rows, "limit": limit, **facets})
        docs = [{"short_form": sf, "label": sf} for sf in ranked_ids]
        return docs[:limit] if limit else docs, len(docs), {"numFound": len(docs)}, len(docs)

    async def fake_terminfo(session, ids):
        ids = list(ids)
        fetched.append(ids)
        infos = TERM_INFOS if term_infos is None else term_infos
        return {i: infos[i] for i in ids if i in infos}

    monkeypatch.setattr(ha_api, "_solr_search_ranked", fake_search, raising=True)
    monkeypatch.setattr(ha_api, "_fetch_term_info_docs", fake_terminfo, raising=True)

    app = web.Application()
    app.router.add_get("/search", ha_api.handle_search)
    app.router.add_get("/xref", ha_api.handle_xref)

    async def on_startup(app):
        app["result_cache"] = ha_api.ResultCache(ttl_seconds=300)
        app["coalescer"] = ha_api.RequestCoalescer()
        app["search_semaphore"] = asyncio.Semaphore(4)
        app["search_queue_wait"] = 10
        app["search_stats"] = {"in_flight": 0, "queued": 0, "served": 0,
                               "shed": 0, "failed": 0}
        app["http"] = None          # the seams that would use it are patched

    app.on_startup.append(on_startup)
    return app, fetched, searched


async def _client(app):
    client = TestClient(TestServer(app))
    await client.start_server()
    return client


# ---------------------------------------------------------------------------
# /xref — the reverse direction is the endpoint's reason for existing
# ---------------------------------------------------------------------------

def test_the_reverse_direction_returns_only_a_confirmed_match(monkeypatch):
    """A candidate is returned only if it really carries that accession.

    The near-miss ranks *first* here, deliberately: without the confirmation the
    handler answers with a confident, well-ranked, wrong neuron — which is worse
    than answering with nothing, because nothing is visibly an absence.
    """
    app, fetched, _ = _make_app(["VFB_nearmiss", "VFB_right"],
                                monkeypatch=monkeypatch)

    async def go():
        client = await _client(app)
        try:
            body = await (await client.get("/xref",
                                           params={"accession": WANTED})).json()
            assert body["direction"] == "accession_to_id"
            assert {r["id"] for r in body["rows"]} == {"VFB_right"}
            # Both of the right term's xrefs carry it, so both come back...
            assert body["count"] == 2
            # ...and the near-miss's own accession is not among them, which is
            # what fails if the `== want` filter is dropped.
            assert all(r["accession"] == WANTED for r in body["rows"])
            # It was checked, not skipped: the cost is real and is reported.
            assert body["candidates_checked"] == 2
            assert fetched == [["VFB_nearmiss", "VFB_right"]]
        finally:
            await client.close()

    run(go())


def test_an_accession_nobody_carries_is_an_empty_frame_not_a_guess(monkeypatch):
    """The documented answer for an accession that is in no indexed text."""
    app, _, _ = _make_app(["VFB_nearmiss"], monkeypatch=monkeypatch)

    async def go():
        client = await _client(app)
        try:
            body = await (await client.get(
                "/xref", params={"accession": "no-such-accession"})).json()
            assert body["rows"] == [] and body["count"] == 0
            # Still reported as work done — "checked one and it was not it" and
            # "found nothing to check" are different answers.
            assert body["candidates_checked"] == 1
        finally:
            await client.close()

    run(go())


def test_candidates_are_deduplicated_and_capped(monkeypatch):
    """`refine_results` explodes one term into a row per matching synonym.

    Fetching per row would open, parse and confirm the same document several
    times over, and would make XREF_MAX_CANDIDATES bound an unpredictable number
    of actual *terms* — the one thing it is supposed to bound.
    """
    duplicated = ["VFB_right", "VFB_right", "VFB_right"]
    many = ["VFB_%03d" % i for i in range(ha_api.XREF_MAX_CANDIDATES + 10)]
    app, fetched, _ = _make_app(duplicated + many, monkeypatch=monkeypatch)

    async def go():
        client = await _client(app)
        try:
            body = await (await client.get("/xref",
                                           params={"accession": WANTED})).json()
            asked = fetched[0]
            assert len(asked) == len(set(asked))            # no repeats
            assert len(asked) == ha_api.XREF_MAX_CANDIDATES  # and capped
            assert asked[0] == "VFB_right"                   # rank order kept
            assert body["candidates_checked"] == ha_api.XREF_MAX_CANDIDATES
            # De-duplication is upstream of the rows, so the real term's two
            # xrefs appear once each rather than three times each.
            assert body["count"] == 2
        finally:
            await client.close()

    run(go())


def test_the_forward_direction_is_one_document_not_a_search(monkeypatch):
    app, fetched, searched = _make_app([], monkeypatch=monkeypatch)

    async def go():
        client = await _client(app)
        try:
            body = await (await client.get("/xref",
                                           params={"id": "VFB_right"})).json()
            assert body["direction"] == "id_to_accession"
            assert body["candidates_checked"] == 1
            assert [r["accession"] for r in body["rows"]] == [WANTED, WANTED]
            assert fetched == [["VFB_right"]]
            assert searched == []       # no ranking pass in this direction
        finally:
            await client.close()

    run(go())


def test_db_is_part_of_the_xref_cache_key(monkeypatch):
    """Otherwise the first caller's filter is served to everyone after them.

    Both requests are for the same term, so they differ *only* by `db` — which
    is exactly the collision an id-only key produces, and it is silent: the
    second caller gets a plausible, well-formed, filtered-by-someone-else answer.
    """
    app, _, _ = _make_app([], monkeypatch=monkeypatch)

    async def go():
        client = await _client(app)
        try:
            unfiltered = await (await client.get(
                "/xref", params={"id": "VFB_right"})).json()
            filtered = await (await client.get(
                "/xref", params={"id": "VFB_right", "db": "hb"})).json()
            assert unfiltered["count"] == 2
            assert filtered["count"] == 1
            assert filtered["rows"][0]["db"] == "hb"
        finally:
            await client.close()

    run(go())


@pytest.mark.parametrize("params, why", [
    ({}, "neither"),
    ({"id": "VFB_x", "accession": "1"}, "both"),
])
def test_xref_wants_exactly_one_direction(monkeypatch, params, why):
    """Guessing which one was meant is how an ambiguous request becomes a wrong
    answer instead of a corrected one."""
    app, _, _ = _make_app([], monkeypatch=monkeypatch)

    async def go():
        client = await _client(app)
        try:
            resp = await client.get("/xref", params=params)
            assert resp.status == 400, why
            assert "exactly one of" in (await resp.json())["error"]
        finally:
            await client.close()

    run(go())


def test_an_over_long_id_is_rejected_before_it_reaches_solr(monkeypatch):
    app, fetched, _ = _make_app([], monkeypatch=monkeypatch)

    async def go():
        client = await _client(app)
        try:
            resp = await client.get("/xref",
                                    params={"id": "V" * (ha_api.MAX_ID_LEN + 1)})
            assert resp.status == 400
            assert fetched == []
        finally:
            await client.close()

    run(go())


# ---------------------------------------------------------------------------
# /search — the facet parameters
# ---------------------------------------------------------------------------

def test_facets_are_part_of_the_search_cache_key(monkeypatch):
    """`filter_types` changes the results, so it has to change the key.

    Sharing one key across facet sets serves the first caller's filter to
    everyone who follows — and because the rows are well-formed and plausibly
    ranked, nothing about the response says so.
    """
    app, _, searched = _make_app(["VFB_a", "VFB_b"], monkeypatch=monkeypatch)

    async def go():
        client = await _client(app)
        try:
            await client.get("/search", params={"query": "same"})
            await client.get("/search", params={"query": "same",
                                                "filter_types": "Class"})
            await client.get("/search", params={"query": "same",
                                                "exclude_types": "Class"})
            # Three distinct requests, so three trips to Solr; a shared key
            # would show up here as one.
            assert len(searched) == 3
            assert searched[1]["filter_types"] == ["Class"]
            assert searched[2]["exclude_types"] == ["Class"]
            # ...and the identical repeat *is* cached, so this is testing the
            # key rather than the absence of caching.
            await client.get("/search", params={"query": "same"})
            assert len(searched) == 3
        finally:
            await client.close()

    run(go())


def test_a_facet_containing_solr_syntax_is_a_400(monkeypatch):
    """Facet names are interpolated into `fq`/`bq` unescaped.

    `_parse_type_list` has its own unit test; this is the other half — that the
    handler turns that ValueError into a 400 rather than a 500 traceback, and
    that nothing reaches Solr.
    """
    app, _, searched = _make_app(["VFB_a"], monkeypatch=monkeypatch)

    async def go():
        client = await _client(app)
        try:
            resp = await client.get("/search", params={
                "query": "neuron", "filter_types": "Class) OR (*:*"})
            assert resp.status == 400
            # The offending value is echoed, so the caller can see which of four
            # facet parameters it came from without guessing.
            assert (await resp.json())["error"] == \
                "invalid facet name: 'Class) OR (*:*'"
            assert searched == []
        finally:
            await client.close()

    run(go())
