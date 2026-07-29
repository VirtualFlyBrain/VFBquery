"""Endpoint tests for /combine — the half that ``tests/test_combine.py`` cannot reach.

``tests/test_combine.py`` covers ``vfbquery.combine``: the grammar, the
precedence, the set algebra, the explanations and the lossless column merge, all
of it offline and none of it aware that an HTTP service exists. What it cannot
cover is ``handle_combine``: how a query string becomes operands, which
parameters are the endpoint's own and which are operand names, what is rejected
before any query runs, and — the expensive one — that an operand hits *exactly*
the cache key a direct ``/run_query`` would hit. That last one is not cosmetic:
at a workshop where forty people run the same documented example, a key that
differs by one character is forty Neo4j queries instead of one, and nothing else
in the suite would notice.

Most tests replace the two seams the handler reaches the network through
(``_run_query_payload`` and ``_search_payload``), so they run offline and
deterministically while leaving the whole of the handler real. The last section
goes one level deeper and patches ``_run_query`` itself, which is what actually
exercises the cache key, the coalescer and the queue-depth guard.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from conftest import run
from vfbquery import ha_api


# A tiny world, shaped like the real thing: a `headers` map whose identity
# column is declared `selection_id`, and rows carrying columns the other
# operands do not have, so the merge has something to lose if it goes wrong.
def _table(ids, id_column="id", extra=None):
    headers = {id_column: {"title": "Add to search", "type": "selection_id",
                           "order": 0},
               "label": {"title": "Name", "type": "markdown", "order": 1}}
    for column in (extra or {}):
        headers[column] = {"title": column.title(), "type": "text", "order": 9}
    rows = []
    for i in ids:
        row = {id_column: i, "label": f"name of {i}"}
        row.update({k: v for k, v in (extra or {}).items()})
        rows.append(row)
    return {"headers": headers, "rows": rows, "count": len(rows)}


WORLD = {
    # Two overlapping "queries", one nested, one disjoint.
    ("NeuronsPartHere", "FBbt_calyx"): _table(["VFB_1", "VFB_2", "VFB_3"],
                                              extra={"via": "calyx"}),
    ("NeuronsPartHere", "FBbt_lh"): _table(["VFB_2", "VFB_3", "VFB_4"],
                                           extra={"nt": "ACh"}),
    ("NeuronsPartHere", "FBbt_al"): _table(["VFB_3"]),
    ("NeuronsPartHere", "FBbt_empty"): _table([]),
}


def _make_app(monkeypatch, world=None, on_query=None):
    """A real app around fake operand seams.

    ``asked`` records what the handler asked for, in order, which is how
    "operands run concurrently" and "an unused operand is not run" are observed
    rather than inferred from the body.
    """
    world = WORLD if world is None else world
    asked = []

    async def fake_run_query(request, short_form, query_type):
        asked.append((query_type, short_form))
        if on_query is not None:
            await on_query(query_type, short_form)
        try:
            return world[(query_type, short_form)]
        except KeyError:
            raise RuntimeError(f"no such term {short_form}")

    async def fake_search(request, text):
        asked.append(("search", text))
        return dict(_table(["VFB_2", "VFB_9"], id_column="short_form"),
                    query=text)

    monkeypatch.setattr(ha_api, "_run_query_payload", fake_run_query,
                        raising=True)
    monkeypatch.setattr(ha_api, "_search_payload", fake_search, raising=True)

    app = web.Application()
    app.router.add_get("/combine", ha_api.handle_combine)
    return app, asked


async def _client(app):
    client = TestClient(TestServer(app))
    await client.start_server()
    return client


def _get(app, params):
    """One GET /combine, returning (status, body)."""
    async def go():
        client = await _client(app)
        try:
            response = await client.get("/combine", params=params)
            return response.status, await response.json()
        finally:
            await client.close()
    return run(go())


# ---------------------------------------------------------------------------
# The happy path, and what the answer has to carry with it
# ---------------------------------------------------------------------------

def test_an_intersection_returns_the_overlap_and_shows_its_working(monkeypatch):
    """The result, the grouping actually used, and a per-step trace.

    The step counts are the part a biologist checks: `91 of 567 and 314` is
    plausible, `91 of 567 and 91` means the second query is a subset and the AND
    told you nothing you did not already know.
    """
    app, asked = _make_app(monkeypatch)
    status, body = _get(app, {"expr": "calyx AND lh",
                              "calyx": "NeuronsPartHere:FBbt_calyx",
                              "lh": "NeuronsPartHere:FBbt_lh"})
    assert status == 200
    assert {r["id"] for r in body["rows"]} == {"VFB_2", "VFB_3"}
    assert body["count"] == 2
    assert body["as_read"] == "(calyx AND lh)"
    assert len(body["steps"]) == 1
    step = body["steps"][0]
    assert step["input_counts"] == [3, 3] and step["result_count"] == 2
    # Both were run, and only those two.
    assert sorted(asked) == [("NeuronsPartHere", "FBbt_calyx"),
                             ("NeuronsPartHere", "FBbt_lh")]
    # The per-operand accounting a user needs to tell "the overlap is small"
    # from "one of my queries barely returned anything".
    assert body["operands"]["calyx"]["distinct_terms"] == 3
    assert body["operands"]["calyx"]["query"] == "NeuronsPartHere:FBbt_calyx"


def test_no_column_from_any_operand_is_lost(monkeypatch):
    """Both sides' extra columns survive into the merged table.

    This is the explicit requirement — "results columns need to be able to be
    combined in a way so no data from the final results is lost". A merge that
    simply took the left-hand table's schema would pass every other test here.
    """
    app, _ = _make_app(monkeypatch)
    _, body = _get(app, {"expr": "calyx AND lh",
                         "calyx": "NeuronsPartHere:FBbt_calyx",
                         "lh": "NeuronsPartHere:FBbt_lh"})
    assert "via" in body["headers"] and "nt" in body["headers"]
    row = next(r for r in body["rows"] if r["id"] == "VFB_2")
    assert row["via"] == "calyx" and row["nt"] == "ACh"
    # And the provenance of each row: which operands it came from.
    assert set(row["found_in"]) == {"calyx", "lh"}
    assert row["found_in_count"] == 2


def test_bracketing_changes_the_answer_and_the_response_says_so(monkeypatch):
    """`a AND b NOT c` and `a AND [b NOT c]` are different questions.

    Under the default precedence AND and NOT bind equally and associate left, so
    the first is `((a AND b) NOT c)`. The brackets are the user's way to say
    otherwise, and `as_read` is how they check they were understood.
    """
    app, _ = _make_app(monkeypatch)
    params = {"calyx": "NeuronsPartHere:FBbt_calyx",
              "lh": "NeuronsPartHere:FBbt_lh",
              "al": "NeuronsPartHere:FBbt_al"}

    _, flat = _get(app, dict(params, expr="calyx AND lh NOT al"))
    app, _ = _make_app(monkeypatch)
    _, bracketed = _get(app, dict(params, expr="calyx AND [lh NOT al]"))

    assert flat["as_read"] == "((calyx AND lh) NOT al)"
    assert bracketed["as_read"] == "(calyx AND (lh NOT al))"
    # Same answer here — {2,3} minus {3} either way — but arrived at
    # differently, and the traces show it.
    assert {r["id"] for r in flat["rows"]} == {"VFB_2"}
    assert {r["id"] for r in bracketed["rows"]} == {"VFB_2"}
    assert [s["operation"] for s in flat["steps"]] == ["AND", "NOT"]
    assert [s["operation"] for s in bracketed["steps"]] == ["NOT", "AND"]


def test_plain_english_names_the_queries_rather_than_the_letters(monkeypatch):
    """The reading has to be checkable by someone who does not read algebra.

    "(a AND b)" tells a user nothing they did not type. Naming the actual
    queries is what turns the echo into a check.
    """
    app, _ = _make_app(monkeypatch)
    _, body = _get(app, {"expr": "calyx AND lh",
                         "calyx": "NeuronsPartHere:FBbt_calyx",
                         "lh": "NeuronsPartHere:FBbt_lh"})
    english = body["plain_english"]
    assert "FBbt_calyx" in english and "FBbt_lh" in english
    assert "calyx AND lh" not in english


# ---------------------------------------------------------------------------
# Operand kinds
# ---------------------------------------------------------------------------

def test_a_literal_id_list_combines_without_running_anything(monkeypatch):
    """`ids:` is how an outside set — a paper's supplementary table, a previous
    /combine result — enters the algebra."""
    app, asked = _make_app(monkeypatch)
    _, body = _get(app, {"expr": "calyx NOT mine",
                         "calyx": "NeuronsPartHere:FBbt_calyx",
                         "mine": "ids:VFB_1,VFB_9"})
    assert {r["id"] for r in body["rows"]} == {"VFB_2", "VFB_3"}
    # The id list cost nothing: only the real query was run.
    assert asked == [("NeuronsPartHere", "FBbt_calyx")]


def test_a_search_operand_combines_on_its_own_id_column(monkeypatch):
    """/search calls the column `short_form`, /run_query calls it `id`.

    They still have to meet. The comparison axis is whichever column each table
    *declares* as `selection_id`, not a column name agreed in advance — which is
    the whole reason the identity is read from the headers.
    """
    app, _ = _make_app(monkeypatch)
    _, body = _get(app, {"expr": "calyx AND found",
                         "calyx": "NeuronsPartHere:FBbt_calyx",
                         "found": "search:kenyon cell"})
    assert {r["id"] for r in body["rows"]} == {"VFB_2"}
    assert body["operands"]["calyx"]["id_column"] == "id"
    assert body["operands"]["found"]["id_column"] == "short_form"


# ---------------------------------------------------------------------------
# Explaining before paying
# ---------------------------------------------------------------------------

def test_explain_only_describes_the_expression_without_running_a_query(monkeypatch):
    """A client can offer "what will this do?" as a button.

    The value is entirely in the *not running*: an expression with four operands
    against a busy server is exactly the thing a user wants to check the reading
    of first.
    """
    app, asked = _make_app(monkeypatch)
    status, body = _get(app, {"expr": "calyx AND lh NOT al",
                              "explain_only": "true",
                              "calyx": "NeuronsPartHere:FBbt_calyx",
                              "lh": "NeuronsPartHere:FBbt_lh",
                              "al": "NeuronsPartHere:FBbt_al"})
    assert status == 200
    assert asked == []
    assert body["as_read"] == "((calyx AND lh) NOT al)"
    assert "FBbt_calyx" in body["plain_english"]
    assert "rows" not in body and "count" not in body


def test_an_operand_the_expression_never_names_is_reported_not_run(monkeypatch):
    """Defining `d` and forgetting to use it is a typo with a silent cost.

    Left unsaid, the user reads a three-operand answer as a four-operand one.
    It also must not be *run*: a query nobody asked for is wasted server time
    and, worse, would widen the implicit universe and quietly change what NOT
    means.
    """
    app, asked = _make_app(monkeypatch)
    _, body = _get(app, {"expr": "calyx AND lh",
                         "calyx": "NeuronsPartHere:FBbt_calyx",
                         "lh": "NeuronsPartHere:FBbt_lh",
                         "al": "NeuronsPartHere:FBbt_al"})
    assert body["unused_operands"] == ["al"]
    assert ("NeuronsPartHere", "FBbt_al") not in asked
    assert any("never used" in w for w in body["warnings"])


# ---------------------------------------------------------------------------
# Refusals — every one of these is cheaper than a wrong answer
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("params,fragment", [
    # No expression at all.
    ({"a": "NeuronsPartHere:FBbt_calyx"}, "expr"),
    # An expression naming something that was never defined. The message lists
    # what *was* defined, because the usual cause is a typo in one or the other.
    ({"expr": "calyx AND lhh", "calyx": "NeuronsPartHere:FBbt_calyx",
      "lh": "NeuronsPartHere:FBbt_lh"}, "lhh"),
    # A spec that is not a query at all.
    ({"expr": "a", "a": "FBbt_calyx"}, "not a query"),
    # A query type that does not exist. The message lists the ones that do.
    ({"expr": "a", "a": "NeuronsPartHear:FBbt_calyx"}, "unknown query type"),
    # A query type with no term after it.
    ({"expr": "a", "a": "NeuronsPartHere:"}, "no term"),
    # Bracket that never closes.
    ({"expr": "[a AND b", "a": "ids:VFB_1", "b": "ids:VFB_2"}, "bracket"),
    # Two operands with no operator between them.
    ({"expr": "a b", "a": "ids:VFB_1", "b": "ids:VFB_2"}, "operator"),
    # A limit that is not a number.
    ({"expr": "a", "a": "ids:VFB_1", "limit": "lots"}, "integer"),
])
def test_bad_requests_are_refused_with_a_message_that_names_the_problem(
        monkeypatch, params, fragment):
    app, asked = _make_app(monkeypatch)
    status, body = _get(app, params)
    assert status == 400
    assert fragment.lower() in body["error"].lower()
    # Nothing was run: a request that cannot be answered must not cost a query.
    assert asked == []


def test_an_expression_with_no_operands_at_all_says_what_is_missing(monkeypatch):
    app, _ = _make_app(monkeypatch)
    status, body = _get(app, {"expr": "a AND b"})
    assert status == 400
    assert "operand" in body["error"].lower()


def test_too_many_operands_is_refused_with_a_way_forward(monkeypatch):
    """The cost limit, not a parser limit — and the message says how to get
    round it, because "no" without "instead, do this" is a dead end."""
    app, asked = _make_app(monkeypatch)
    params = {"expr": " OR ".join(f"n{i}" for i in range(20))}
    params.update({f"n{i}": f"ids:VFB_{i}" for i in range(20)})
    status, body = _get(app, params)
    assert status == 400
    assert "too many operands" in body["error"].lower()
    assert "ids:" in body["error"]
    assert asked == []


def test_an_over_long_expression_is_refused_before_tokenising(monkeypatch):
    app, _ = _make_app(monkeypatch)
    # Just over the limit rather than absurdly over it: a megabyte of brackets
    # never reaches the handler at all, because aiohttp rejects the request line
    # first, and a test that only proves *that* proves nothing about this code.
    expr = "a OR " * 500 + "a"
    assert len(expr) > ha_api.MAX_COMBINE_EXPR_LEN
    status, body = _get(app, {"expr": expr, "a": "ids:VFB_1"})
    assert status == 400
    assert str(ha_api.MAX_COMBINE_EXPR_LEN) in body["error"]


def test_the_endpoints_own_parameters_are_not_mistaken_for_operands(monkeypatch):
    """`limit`, `universe`, `explain_only` and friends are reserved.

    Operands are named freely so that expressions read like biology
    (`calyx AND lh`, not `op1 AND op2`); the price is that the handler has to
    know which keys are its own. Getting this wrong turns `&limit=10` into "the
    operand `limit` is not a query" — a 400 on a perfectly good request.
    """
    app, _ = _make_app(monkeypatch)
    status, body = _get(app, {"expr": "calyx OR lh", "limit": "1",
                              "calyx": "NeuronsPartHere:FBbt_calyx",
                              "lh": "NeuronsPartHere:FBbt_lh"})
    assert status == 200
    assert len(body["rows"]) == 1
    # The full size is still reported, so a capped answer is visibly capped
    # rather than looking like a one-row result.
    assert body["count"] == 4 and body["capped"] is True


# ---------------------------------------------------------------------------
# Warnings — the ways a combination is silently wrong
# ---------------------------------------------------------------------------

def test_an_empty_operand_is_a_warning_not_a_failure(monkeypatch):
    """Zero rows is an answer. It is also the most misread answer there is:
    `a AND (empty)` is empty for a reason that has nothing to do with biology."""
    app, _ = _make_app(monkeypatch)
    status, body = _get(app, {"expr": "calyx AND nothing",
                              "calyx": "NeuronsPartHere:FBbt_calyx",
                              "nothing": "NeuronsPartHere:FBbt_empty"})
    assert status == 200
    assert body["rows"] == []
    assert any("returned nothing" in w for w in body["warnings"])


def test_a_truncated_operand_warns_by_default_and_fails_on_request(monkeypatch):
    """A capped table makes AND lose members and NOT keep them, invisibly.

    Two behaviours because there are two users: someone exploring wants the
    partial answer with a health warning, and someone about to put a number in a
    paper wants the request to fail instead. `require_complete=true` is the
    second one asking for it.
    """
    world = dict(WORLD)
    world[("DatasetImages", "big")] = dict(_table(["VFB_1", "VFB_2"]),
                                           count=60002)
    app, _ = _make_app(monkeypatch, world=world)
    status, body = _get(app, {"expr": "calyx AND big",
                              "calyx": "NeuronsPartHere:FBbt_calyx",
                              "big": "DatasetImages:big"})
    assert status == 200
    assert any("cut short" in w for w in body["warnings"])
    assert body["operands"]["big"]["truncated"] is True

    app, _ = _make_app(monkeypatch, world=world)
    status, body = _get(app, {"expr": "calyx AND big",
                              "calyx": "NeuronsPartHere:FBbt_calyx",
                              "big": "DatasetImages:big",
                              "require_complete": "true"})
    assert status == 409
    assert body["operand"] == "big"


def test_two_namespaces_that_can_never_meet_are_diagnosed(monkeypatch):
    """`FBbt_` classes and `VFB_` individuals do not intersect, ever.

    An empty answer here is not biology, it is a category error, and the user
    who made it has no way to tell the two apart from a row count of zero.
    """
    world = dict(WORLD)
    world[("SubclassesOf", "FBbt_x")] = _table(["FBbt_11", "FBbt_12"])
    app, _ = _make_app(monkeypatch, world=world)
    _, body = _get(app, {"expr": "calyx AND classes",
                         "calyx": "NeuronsPartHere:FBbt_calyx",
                         "classes": "SubclassesOf:FBbt_x"})
    assert body["rows"] == []
    # Named in the terms a biologist uses, not by ID prefix: "individual" and
    # "anatomy class" is the distinction being made, and someone who does not
    # already know that `FBbt_` means class is exactly who the warning is for.
    diagnosis = next(w for w in body["warnings"] if "different kinds" in w)
    assert "individual" in diagnosis and "anatomy class" in diagnosis
    # And it is attached to the step that went empty, not only to the summary.
    assert "why_empty" in body["steps"][0]


def test_a_complement_against_the_implicit_universe_is_flagged(monkeypatch):
    """NOR over an implicit universe is always empty, and that is not obvious.

    The implicit universe is "everything any operand returned", so `a NOR b` —
    "in neither" — has nothing left to be in. Rather than answer 0 rows and let
    the user conclude something biological, say why, and say that `universe=`
    is the fix.
    """
    app, _ = _make_app(monkeypatch)
    _, body = _get(app, {"expr": "calyx NOR lh",
                         "calyx": "NeuronsPartHere:FBbt_calyx",
                         "lh": "NeuronsPartHere:FBbt_lh"})
    assert body["rows"] == []
    assert any("universe" in w.lower() for w in body["warnings"])


def test_an_explicit_universe_makes_the_complement_meaningful(monkeypatch):
    """With a stated universe, "in neither" has an answer.

    `universe=` is also the one place the endpoint's set-of-everything is a
    biological choice rather than an artefact: "of the neurons in this dataset,
    which are in neither region" is a real question.
    """
    app, _ = _make_app(monkeypatch)
    _, body = _get(app, {"expr": "calyx NOR lh",
                         "calyx": "NeuronsPartHere:FBbt_calyx",
                         "lh": "NeuronsPartHere:FBbt_lh",
                         "universe": "ids:VFB_1,VFB_2,VFB_3,VFB_4,VFB_5"})
    assert {r["id"] for r in body["rows"]} == {"VFB_5"}
    assert body["universe"]["source"] == "explicit"
    assert body["universe"]["size"] == 5


def test_an_operand_query_that_fails_is_a_500_that_names_the_stage(monkeypatch):
    """The traceback stays in the log; the response says which stage died."""
    app, _ = _make_app(monkeypatch)
    status, body = _get(app, {"expr": "a AND b",
                              "a": "NeuronsPartHere:FBbt_calyx",
                              "b": "NeuronsPartHere:FBbt_nonexistent"})
    assert status == 500
    assert "queries" in body["error"].lower()
    assert "RuntimeError" in body["detail"]


# ---------------------------------------------------------------------------
# The seam the other tests patch out: cache keys, coalescing, backpressure
# ---------------------------------------------------------------------------

def _real_dispatch_app(monkeypatch, calls, delay=0):
    """An app running the *real* `_run_query_payload`, with only the blocking
    query function replaced.

    A ThreadPoolExecutor stands in for the ProcessPoolExecutor: `run_in_executor`
    treats them identically and a thread pool can see a monkeypatched module
    where a subprocess cannot.
    """
    def fake_run_query(short_form, func_name, force_refresh=False,
                       offset=0, limit=0):
        calls.append((short_form, func_name, offset, limit))
        return _table([f"{short_form}_1", f"{short_form}_2"])

    monkeypatch.setattr(ha_api, "_run_query", fake_run_query, raising=True)

    app = web.Application()
    app.router.add_get("/combine", ha_api.handle_combine)
    app.router.add_get("/run_query", ha_api.handle_run_query)

    async def on_startup(app):
        app["result_cache"] = ha_api.ResultCache(ttl_seconds=300)
        app["coalescer"] = ha_api.RequestCoalescer()
        app["pool"] = ThreadPoolExecutor(max_workers=4)
        app["semaphore"] = asyncio.Semaphore(4)
        app["tracker"] = ha_api.QueueTracker()
        app["max_queue_depth"] = None

    async def on_cleanup(app):
        app["pool"].shutdown(wait=False)

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


def test_an_operand_shares_one_cache_entry_with_a_direct_run_query(monkeypatch):
    """The reason `_run_query_payload` rebuilds the key by hand rather than
    inventing its own.

    Forty workshop attendees running the documented example, some through
    /combine and some through /run_query, must cost one Neo4j query. A key that
    differs by a single character costs forty and nothing else in the suite
    would notice — the answers would all still be correct.
    """
    calls = []
    app = _real_dispatch_app(monkeypatch, calls)

    async def go():
        client = await _client(app)
        try:
            first = await client.get(
                "/combine", params={"expr": "a",
                                    "a": "NeuronsPartHere:FBbt_00007401"})
            assert first.status == 200
            assert len(calls) == 1
            # Same term, same query type, now by the direct route.
            second = await client.get(
                "/run_query", params={"id": "FBbt_00007401",
                                      "query_type": "NeuronsPartHere"})
            assert second.status == 200
            assert len(calls) == 1, (
                "the operand and the direct call built different cache keys")
        finally:
            await client.close()

    run(go())


def test_a_paged_query_asks_for_the_whole_answer(monkeypatch):
    """Combine needs every row, not the first page.

    A window is fine for a table someone is scrolling; for set algebra it is a
    truncated operand wearing a different name, and the AND would quietly lose
    whatever fell off the end.
    """
    calls = []
    app = _real_dispatch_app(monkeypatch, calls)

    async def go():
        client = await _client(app)
        try:
            await client.get("/combine",
                             params={"expr": "a",
                                     "a": "NeuronsPartHere:FBbt_00007401"})
            assert calls[0][2] == 0 and calls[0][3] == 0
        finally:
            await client.close()

    run(go())


def test_the_same_operand_twice_in_one_expression_runs_once(monkeypatch):
    """`a AND (b OR a)` names `a` twice; the coalescer must not.

    This is also the general case of two concurrent requests for the same
    operand, which is what a room of people clicking the same example is.
    """
    calls = []
    app = _real_dispatch_app(monkeypatch, calls)

    async def go():
        client = await _client(app)
        try:
            response = await client.get(
                "/combine", params={"expr": "a AND [b OR a]",
                                    "a": "NeuronsPartHere:FBbt_00007401",
                                    "b": "NeuronsPartHere:FBbt_00007053"})
            assert response.status == 200
            # Two distinct terms, two queries — not three.
            assert len(calls) == 2
        finally:
            await client.close()

    run(go())


def test_a_full_queue_sheds_the_whole_combination_as_one_503(monkeypatch):
    """Backpressure has to survive the fan-out.

    Operands run in an `asyncio.gather`, so a shed operand raises rather than
    returning a Response. If that raise were not caught the request would 500 —
    telling a client that is being asked to slow down that the server is broken,
    and losing the Retry-After that makes the queue drain.
    """
    calls = []
    app = _real_dispatch_app(monkeypatch, calls)

    async def go():
        client = await _client(app)
        try:
            # A queue that is full before the request arrives.
            app["max_queue_depth"] = 1
            await app["tracker"].enter_queue()
            response = await client.get(
                "/combine", params={"expr": "a OR b",
                                    "a": "NeuronsPartHere:FBbt_00007401",
                                    "b": "NeuronsPartHere:FBbt_00007053"})
            assert response.status == 503
            assert response.headers.get("Retry-After")
            assert calls == []
        finally:
            await client.close()

    run(go())
