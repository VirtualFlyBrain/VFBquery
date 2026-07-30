"""The three things `/search` promised but did not deliver.

The live test campaign left these alone as "faithful to the website rather than
broken". They are still faults from a caller's side, and each one is silent —
which is what makes them worth guarding:

1. **A misspelled type name answered 200 with zero rows.** Indistinguishable
   from a term that genuinely has nothing behind it, so the caller debugs their
   biology instead of their spelling. The fix needs a vocabulary, which means it
   needs a *live* vocabulary, which means it must fail open: a facet query that
   times out must not start refusing valid filters.

2. **`boost_types` and `demote_types` changed nothing observable.** They do
   reach Solr and do change its score order, but the website comparator then
   re-sorts on label text and never reads the score. And `demote_types` was
   worse than invisible: `^0.001` is a tiny *positive* boost, so the "demote"
   chip nudged the chosen type very slightly up.

3. **One term occupied several rows**, so `limit=10` on a term with six synonyms
   returned four terms. Right for a search box, wrong for a programmatic caller.

Solr is replaced at the seams, so these run offline.
"""
import asyncio

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from conftest import run
from vfbquery import ha_api
from vfbquery import search_config as sc


# A miniature of the real vocabulary, keeping the properties that matter: all
# lowercase (that is how the index stores the *indexed* terms), a family sharing
# a prefix, and a name whose stored spelling is capitalised.
VOCAB = {
    "entity": 741026,
    "anatomy": 660572,
    "nervous_system": 625912,
    "neuron": 540158,
    "class": 122360,
    "individual": 618665,
    "pub": 4211,
    "lineage_clone_LHl1": 12,
    "lineage_clone_LHl2": 9,
    "has_neuron_connectivity": 488110,
}


# --------------------------------------------------------------------------- #
# 1. The vocabulary itself
# --------------------------------------------------------------------------- #

def test_the_facet_query_asks_for_the_whole_list_not_solrs_first_hundred():
    """`facet.limit` defaults to 100, which would hide most of a 233-name list.

    A truncated vocabulary is worse than none: it would start rejecting the
    *valid* names that fell off the end, which is the one failure mode this
    feature must never have.
    """
    params = sc.build_facet_vocabulary_params()
    assert params["facet.limit"] == "-1"
    assert params["facet.mincount"] == "1"
    assert params["facet.field"] == sc.FACET_FIELD
    assert params["rows"] == "0"          # counts only; no documents wanted
    # Same fq as a real search, so the answer is what *this* search can filter
    # by rather than every value the field has ever held.
    assert params["fq"] == [sc.FQ_BASE, sc.FQ_NOT_DEPRECATED]


def test_both_solr_facet_encodings_parse():
    """Solr's default is a flat `[name, count, name, count]` list, not a map.

    `json.nl` can change it to a map, and a deployment that flips it should not
    silently produce an empty vocabulary — which, failing open, would disable
    validation everywhere with nothing in the response to say so.
    """
    flat = {"facet_counts": {"facet_fields": {
        sc.FACET_FIELD: ["neuron", 540158, "class", 122360, "gone", 0]}}}
    mapped = {"facet_counts": {"facet_fields": {
        sc.FACET_FIELD: {"neuron": 540158, "class": 122360, "gone": 0}}}}

    for payload in (flat, mapped):
        assert sc.parse_facet_vocabulary(payload) == {"neuron": 540158,
                                                      "class": 122360}

    # A response with no facet block at all is empty, not an exception.
    assert sc.parse_facet_vocabulary({}) == {}
    assert sc.parse_facet_vocabulary({"facet_counts": {"facet_fields": {}}}) == {}


def test_a_name_resolves_across_case_and_separators():
    """There is no single spelling a caller could be expected to guess.

    The indexed terms are lowercased by the analyser while the *stored* row
    values keep their capitalisation (`Nervous_system`), so both spellings are in
    circulation and neither is wrong. `_` versus `-` is not a distinction anyone
    means either.
    """
    resolved, unknown = sc.resolve_facet_names(
        ["Neuron", "nervous-system", "NERVOUS_SYSTEM", "Class", "pub"], VOCAB)
    assert unknown == {}
    # nervous_system requested twice in two spellings, returned once.
    assert resolved == ["neuron", "nervous_system", "class", "pub"]


def test_a_prefix_is_not_a_match_on_purpose():
    """`neuro` must not silently mean `neuron`.

    `/xref` does widen to a prefix, and that is right there: a database name is
    a label the caller half-remembers. A *type* filter is the opposite — the
    caller is narrowing, and a filter that matched an arbitrary prefix would
    quietly widen the very thing they asked to restrict. So `neuro` is an error
    with a suggestion, not a silent expansion to `neuron` plus four others.
    """
    resolved, unknown = sc.resolve_facet_names(["neuro"], VOCAB)
    assert resolved == []
    assert "neuron" in unknown["neuro"]
    assert "has_neuron_connectivity" in unknown["neuro"]


def test_suggestions_lead_with_containment_then_fall_back_to_fuzzy():
    """With 200-odd names, a short wrong name is usually a fragment of the right
    one, while a long wrong name is usually a typo. Both get help."""
    # Fragment: the whole lineage family.
    assert sc.suggest_facet_names("lineage", VOCAB) == ["lineage_clone_LHl1",
                                                        "lineage_clone_LHl2"]
    # Typo: containment finds nothing, difflib does.
    assert "neuron" in sc.suggest_facet_names("nueron", VOCAB)
    # Nothing remotely close gets no guesses rather than a random one.
    assert sc.suggest_facet_names("zzzzzzzz", VOCAB) == []
    assert sc.suggest_facet_names("", VOCAB) == []


def test_an_unknown_name_names_itself_and_offers_suggestions():
    """The message has to identify *which* parameter and *which* value.

    Four type parameters are in play and a caller may have passed several names
    to each; "unknown type" on its own leaves them to bisect.
    """
    with pytest.raises(ha_api.BadParam) as exc:
        ha_api._resolve_facet_list(["neuron", "nueron"], VOCAB, "filter_types")
    message = str(exc.value)
    assert "filter_types" in message and "nueron" in message
    assert "did you mean" in message and "neuron" in message
    assert "/facets" in message          # tells them where the list is
    # BadParam is a ValueError, so an un-updated caller still catches it.
    assert isinstance(exc.value, ValueError)


def test_validation_fails_open_when_the_vocabulary_is_unavailable():
    """A Solr blip must not turn every faceted search into a 400.

    An empty vocabulary means "do not validate", never "nothing matches". This
    is the whole reason the resolver takes the vocabulary as an argument rather
    than fetching it: the degraded path is testable.
    """
    assert ha_api._resolve_facet_list(["whatever"], {}, "filter_types") == \
        ["whatever"]
    # And an empty request list is passed through untouched either way.
    assert ha_api._resolve_facet_list([], VOCAB, "filter_types") == []
    assert ha_api._resolve_facet_list(None, VOCAB, "filter_types") is None


# --------------------------------------------------------------------------- #
# 2. Demotion, as Solr will actually accept it
# --------------------------------------------------------------------------- #

def test_demotion_boosts_the_complement_because_negative_boosts_are_a_500():
    """`facets_annotation:X^-100` answers HTTP 500 — verified against the live
    index, not assumed. The complement form parses and is the exact mirror: it
    adds the same +100 to every document that is *not* X.
    """
    params = sc.build_params("neuron", demote_types=["Individual"])
    bq = params["bq"]
    assert "(*:* -facets_annotation:Individual)^100" in bq
    # The two things that must not reappear for a demoted type: a negative boost
    # (a 500) and the website's ^0.001 (a tiny positive boost, so not a demotion
    # at all).
    assert "^-" not in bq
    assert "facets_annotation:Individual" + sc.FILTER_NEGATIVE not in bq

    # `^0.001` does still appear once, on `Deprecated`, and that is the website's
    # base bq copied verbatim rather than an oversight here: it is equally
    # ineffective, but `FQ_NOT_DEPRECATED` already removes those documents
    # outright, so the dead clause has nothing left to fail to demote.
    assert "facets_annotation:Deprecated^0.001" in sc.BQ_BASE
    assert "Deprecated" in " ".join(sc.build_params("neuron")["fq"])

    # Boost is the plain form, and the two are symmetric in weight.
    boosted = sc.build_params("neuron", boost_types=["Class"])["bq"]
    assert "facets_annotation:Class^100" in boosted
    assert sc.FILTER_POSITIVE == "^100"


def test_a_demote_stays_a_soft_weight_not_a_hard_filter():
    """Demoting a type must not remove it. `exclude_types` is how you remove it,
    and conflating the two would make `demote_types` a destructive parameter
    with a gentle-sounding name."""
    params = sc.build_params("neuron", demote_types=["Individual"])
    fq = params["fq"]
    assert not any("Individual" in clause for clause in fq)


# --------------------------------------------------------------------------- #
# 3. Making the boost visible: the partition
# --------------------------------------------------------------------------- #

def _rows(*specs):
    """`("FBbt_1", "Class")` -> a row shaped like one `refine_results` emits."""
    return [{"short_form": sf, "label": sf,
             sc.FACET_FIELD: list(facets)} for sf, *facets in specs]


def test_the_partition_is_stable_so_the_website_order_survives_inside_it():
    """The point is to make the boost visible *without* replacing the ranking.

    A sort by "is boosted" that was not stable would scramble the comparator's
    work inside each group, which is a much bigger change than the caller asked
    for — they asked to see their type first, not to lose the ranking.
    """
    rows = _rows(("a", "Individual"), ("b", "Class"), ("c", "Individual"),
                 ("d", "Class"), ("e", "Pub"))
    out = sc.partition_by_facets(rows, boost_types=["class"])
    assert [r["short_form"] for r in out] == ["b", "d", "a", "c", "e"]

    out = sc.partition_by_facets(rows, demote_types=["individual"])
    assert [r["short_form"] for r in out] == ["b", "d", "e", "a", "c"]

    # Both at once: boosted first, untouched middle, demoted last.
    out = sc.partition_by_facets(rows, boost_types=["pub"],
                                 demote_types=["class"])
    assert [r["short_form"] for r in out] == ["e", "a", "c", "b", "d"]


def test_a_row_matching_both_is_boosted():
    """"Show me these" is a stronger statement than "push those down", and it is
    the only reading under which `boost_types=X&demote_types=X` means anything.
    """
    rows = _rows(("a", "Class"), ("b", "Individual"))
    out = sc.partition_by_facets(rows, boost_types=["class"],
                                 demote_types=["class"])
    assert [r["short_form"] for r in out] == ["a", "b"]


def test_the_partition_compares_folded_because_the_two_ends_disagree():
    """The row carries `Nervous_system`; the index term the filter matched is
    `nervous_system`. A case-sensitive comparison here would make the endpoint
    accept a name and then quietly fail to act on it — the worst of both."""
    rows = _rows(("a", "Nervous_system"), ("b", "Class"))
    out = sc.partition_by_facets(rows, boost_types=["nervous-system"])
    assert [r["short_form"] for r in out] == ["a", "b"]

    # A single string rather than a list is what some rows actually carry.
    rows = [{"short_form": "a", sc.FACET_FIELD: "Class"},
            {"short_form": "b", sc.FACET_FIELD: []}]
    assert sc.row_facets(rows[0]) == {"class"}
    assert sc.row_facets(rows[1]) == set()


def test_the_partition_is_a_no_op_when_nobody_asked():
    """Default search order is untouched — including for every existing caller,
    which is why this can ride a patch release."""
    rows = _rows(("a", "Class"), ("b", "Individual"))
    assert sc.partition_by_facets(rows) == rows
    assert sc.partition_by_facets(rows, [], []) == rows
    assert sc.partition_by_facets(rows) is not rows      # copied, not aliased


def test_the_partition_runs_after_the_comparator_not_before():
    """Order of operations is the whole fix, so it is asserted structurally.

    Partitioning first and sorting after would discard the partition entirely —
    the comparator re-sorts on label text — and the symptom would be exactly the
    bug this change exists to fix, with the code apparently doing the right
    thing.
    """
    import inspect
    src = inspect.getsource(ha_api._rank_search_docs)
    assert src.index("sort_results") < src.index("partition_by_facets")

    src = inspect.getsource(sc.search)
    assert src.index("sort_results") < src.index("partition_by_facets")


# --------------------------------------------------------------------------- #
# 4. One row per term
# --------------------------------------------------------------------------- #

def test_dedupe_keeps_the_best_ranked_row_for_each_term():
    """Rows arrive ranked, so the first occurrence is by definition the best
    placed one — the synonym row that actually matched, not an arbitrary one."""
    rows = [{"short_form": "FBbt_1", "label": "medulla"},
            {"short_form": "FBbt_2", "label": "lobula"},
            {"short_form": "FBbt_1", "label": "me (medulla)"}]
    out = sc.dedupe_by_short_form(rows)
    assert [r["label"] for r in out] == ["medulla", "lobula"]


def test_rows_without_a_short_form_are_all_kept():
    """There is nothing to tell them apart by, so collapsing them to one would
    silently discard data — and the no-data-loss rule applies here too."""
    rows = [{"label": "x"}, {"label": "y"}, {"short_form": "", "label": "z"}]
    assert sc.dedupe_by_short_form(rows) == rows
    assert sc.count_distinct_terms(rows) == 3


def test_distinct_terms_counts_terms_while_count_counts_rows():
    rows = [{"short_form": "FBbt_1"}, {"short_form": "FBbt_1"},
            {"short_form": "FBbt_2"}]
    assert len(rows) == 3
    assert sc.count_distinct_terms(rows) == 2


# --------------------------------------------------------------------------- #
# 5. The endpoints
# --------------------------------------------------------------------------- #

def _make_app(monkeypatch, docs, vocabulary=VOCAB):
    """A real app with the Solr seams replaced.

    The facet vocabulary is pre-seeded rather than fetched, so `app["http"]`
    being absent cannot silently turn a validation test into a fail-open test
    that passes for the wrong reason.
    """
    calls = []

    async def fake_solr(query, rows, timeout=30, session=None, **kwargs):
        calls.append({"query": query, "rows": rows, **kwargs})
        return list(docs)

    async def fake_fetch(app, query, rows, timeout=30, **kwargs):
        return await fake_solr(query, rows, **kwargs)

    monkeypatch.setattr(ha_api, "_fetch_search_docs", fake_fetch, raising=False)

    app = web.Application()
    app.router.add_get("/search", ha_api.handle_search)
    app.router.add_get("/facets", ha_api.handle_facets)

    async def on_startup(app):
        app["result_cache"] = ha_api.ResultCache(ttl_seconds=300)
        app["coalescer"] = ha_api.RequestCoalescer()
        app["search_semaphore"] = asyncio.Semaphore(4)
        app["search_queue_wait"] = 10
        app["search_stats"] = {"in_flight": 0, "queued": 0, "served": 0,
                               "shed": 0, "failed": 0}
        app["http"] = None
        if vocabulary is not None:
            app["facet_vocab"] = {"values": dict(vocabulary),
                                  "fetched": 1e18, "ttl": 1e18}

    app.on_startup.append(on_startup)
    return app, calls


def _seeded_search_app(monkeypatch, ranked, vocabulary=VOCAB):
    """As above, but patching the ranked seam — the shape most tests want."""
    searched = []

    async def fake_search(app, query, rows, limit=None, unique=False, **facets):
        searched.append({"query": query, "rows": rows, "limit": limit,
                         "unique": unique, **facets})
        rows_out = [dict(r) for r in ranked]
        distinct = sc.count_distinct_terms(rows_out)
        if unique:
            rows_out = sc.dedupe_by_short_form(rows_out)
        total = len(rows_out)
        if limit is not None:
            rows_out = rows_out[:limit]
        return rows_out, total, {"numFound": len(ranked)}, len(ranked), distinct

    monkeypatch.setattr(ha_api, "_solr_search_ranked", fake_search, raising=True)
    app, _ = _make_app(monkeypatch, [], vocabulary=vocabulary)
    return app, searched


async def _get(app, path, params):
    client = TestClient(TestServer(app))
    await client.start_server()
    try:
        resp = await client.get(path, params=params)
        return resp.status, await resp.json()
    finally:
        await client.close()


def test_a_misspelled_type_is_a_400_with_suggestions_not_an_empty_result(
        monkeypatch):
    """The defect, from the caller's side.

    200-with-zero-rows is the answer a valid filter also gives, so the caller
    has no way to tell a typo from a term with nothing behind it.
    """
    app, searched = _seeded_search_app(monkeypatch, [])
    status, body = run(_get(app, "/search",
                            {"query": "neuron", "filter_types": "NotAType"}))
    assert status == 400
    assert "filter_types" in body["error"] and "NotAType" in body["error"]
    # Rejected before Solr was asked: a 400 that still ran the query would pass
    # a status-only test while still costing the service the work.
    assert searched == []


@pytest.mark.parametrize("param", ["filter_types", "exclude_types",
                                   "boost_types", "demote_types"])
def test_all_four_type_parameters_are_validated(monkeypatch, param):
    """All four take names from the same vocabulary, so a typo in any of them
    has the same silent failure — including the two whose only effect is on
    ordering, where a typo produces a *plausible* answer."""
    app, _ = _seeded_search_app(monkeypatch, [])
    status, body = run(_get(app, "/search", {"query": "neuron",
                                             param: "nueron"}))
    assert status == 400 and param in body["error"]


def test_a_valid_name_is_canonicalised_before_it_reaches_solr(monkeypatch):
    """Resolution is not just a gate — it rewrites the caller's spelling to the
    index's, which is what makes `nervous-system` work rather than merely be
    accepted."""
    app, searched = _seeded_search_app(monkeypatch, [])
    status, _ = run(_get(app, "/search", {"query": "neuron",
                                          "filter_types": "NERVOUS-SYSTEM",
                                          "boost_types": "Class"}))
    assert status == 200
    assert searched[0]["filter_types"] == ["nervous_system"]
    assert searched[0]["boost_types"] == ["class"]


def test_a_search_with_no_type_parameters_never_touches_the_vocabulary(
        monkeypatch):
    """The common case must not pay for the feature, and must not become newly
    dependent on a second Solr call succeeding."""
    app, _ = _seeded_search_app(monkeypatch, [], vocabulary=None)
    called = []

    async def boom(app):
        called.append(1)
        return {}

    monkeypatch.setattr(ha_api, "_facet_vocabulary", boom, raising=True)
    status, _ = run(_get(app, "/search", {"query": "neuron"}))
    assert status == 200 and called == []


def test_unique_collapses_rows_and_applies_before_the_limit(monkeypatch):
    """`limit=2` must mean two terms, not two rows.

    Applying the limit first and de-duplicating after would return one term for
    `limit=2` on a term with two synonym rows — a silent short page, which is
    the failure a caller is least likely to notice.
    """
    ranked = [{"short_form": "FBbt_1", "label": "medulla"},
              {"short_form": "FBbt_1", "label": "me (medulla)"},
              {"short_form": "FBbt_2", "label": "lobula"},
              {"short_form": "FBbt_3", "label": "lamina"}]
    app, _ = _seeded_search_app(monkeypatch, ranked)

    status, body = run(_get(app, "/search", {"query": "medulla", "limit": "2",
                                             "unique": "true"}))
    assert status == 200
    assert [r["short_form"] for r in body["rows"]] == ["FBbt_1", "FBbt_2"]
    assert body["unique"] is True

    # Without it, the same limit returns two rows of one term — unchanged
    # behaviour, which is the point of it being opt-in.
    app, _ = _seeded_search_app(monkeypatch, ranked)
    status, body = run(_get(app, "/search", {"query": "medulla", "limit": "2"}))
    assert [r["short_form"] for r in body["rows"]] == ["FBbt_1", "FBbt_1"]
    assert body["unique"] is False


def test_distinct_terms_is_reported_whether_or_not_unique_was_asked_for(
        monkeypatch):
    """The gap between rows and terms should be visible without a second
    request — that is what makes the duplication comprehensible rather than
    looking like a bug in the caller's paging."""
    ranked = [{"short_form": "FBbt_1"}, {"short_form": "FBbt_1"},
              {"short_form": "FBbt_2"}]
    app, _ = _seeded_search_app(monkeypatch, ranked)
    status, body = run(_get(app, "/search", {"query": "x"}))
    assert status == 200
    assert body["count"] == 3 and body["distinct_terms"] == 2


def test_unique_is_part_of_the_cache_key(monkeypatch):
    """It changes the rows, so sharing a key serves one caller's collapsed list
    to the next — well-formed and plausible, with nothing to say so."""
    ranked = [{"short_form": "FBbt_1"}, {"short_form": "FBbt_1"}]
    app, searched = _seeded_search_app(monkeypatch, ranked)

    async def go():
        client = TestClient(TestServer(app))
        await client.start_server()
        try:
            await client.get("/search", params={"query": "same"})
            await client.get("/search", params={"query": "same",
                                                "unique": "true"})
            assert len(searched) == 2, "unique missing from the cache key"
            # The identical repeat *is* cached, so this tests the key rather
            # than the absence of caching.
            await client.get("/search", params={"query": "same",
                                                "unique": "true"})
            assert len(searched) == 2
        finally:
            await client.close()
    run(go())


def test_the_facets_endpoint_lists_names_with_counts_and_filters(monkeypatch):
    """233 undocumented names cannot be guessed, so the 400 has to point
    somewhere real."""
    app, _ = _seeded_search_app(monkeypatch, [])

    async def go():
        client = TestClient(TestServer(app))
        await client.start_server()
        try:
            body = await (await client.get("/facets")).json()
            assert body["count"] == body["total"] == len(VOCAB)
            # Commonest first, so a caller skimming the head sees the useful ones.
            assert body["facets"][0] == {"name": "entity", "docs": 741026}

            body = await (await client.get(
                "/facets", params={"contains": "lineage"})).json()
            assert [f["name"] for f in body["facets"]] == ["lineage_clone_LHl1",
                                                           "lineage_clone_LHl2"]
            # `total` still describes the whole vocabulary, so a filtered
            # response cannot be mistaken for the full list.
            assert body["count"] == 2 and body["total"] == len(VOCAB)

            # `contains` folds too, so a caller can paste back what they typed.
            body = await (await client.get(
                "/facets", params={"contains": "NERVOUS SYSTEM"})).json()
            assert [f["name"] for f in body["facets"]] == ["nervous_system"]
        finally:
            await client.close()
    run(go())


def test_the_facets_endpoint_says_so_when_it_cannot_answer(monkeypatch):
    """An empty list would read as "this index has no types", which is a
    statement about the data rather than about the outage."""
    app, _ = _seeded_search_app(monkeypatch, [], vocabulary=None)

    async def unavailable(app):
        return {}

    monkeypatch.setattr(ha_api, "_facet_vocabulary", unavailable, raising=True)
    status, body = run(_get(app, "/facets", {}))
    assert status == 503
    # And it says search is unaffected, so nobody escalates a degraded
    # discovery endpoint into an outage.
    assert "Search still works" in body["error"]


def test_a_failed_vocabulary_fetch_is_remembered_only_briefly():
    """Caching a failure for the success TTL would disable validation for an
    hour over one blip; re-asking a healthy Solr once a minute costs nothing."""
    assert ha_api.FACET_VOCAB_FAIL_TTL < ha_api.FACET_VOCAB_TTL
    assert ha_api.FACET_VOCAB_FAIL_TTL <= 60


def test_the_vocabulary_fetch_fails_open_rather_than_propagating():
    """Any exception at all — no session, timeout, bad JSON, Solr 500 — has to
    come back as an empty dict, because the caller uses it to decide whether to
    validate and an exception here would 500 a search that could have run."""
    app = {}
    values = run(ha_api._facet_vocabulary(app))
    assert values == {}                      # app["http"] is absent
    # Negative-cached, so the next search does not re-ask immediately.
    assert app["facet_vocab"]["ttl"] == ha_api.FACET_VOCAB_FAIL_TTL


# --------------------------------------------------------------------------- #
# 6. The flag parser
# --------------------------------------------------------------------------- #

class _FakeRequest:
    def __init__(self, **query):
        self.query = query


def test_query_flag_accepts_the_spellings_already_in_use():
    """`force_refresh` already accepted these four across the module; a second
    boolean parameter answering to a different set would be a trap."""
    for yes in ("true", "TRUE", "1", "yes", "on", " true "):
        assert ha_api._query_flag(_FakeRequest(unique=yes), "unique") is True
    for no in ("false", "0", "no", "off", "maybe"):
        assert ha_api._query_flag(_FakeRequest(unique=no), "unique") is False


def test_a_flag_has_no_wrong_answer_worth_a_400():
    """Absent and blank both fall back to the default, deliberately.

    Unlike `weight=abc`, where substituting the default answers a question
    nobody put, a flag's default *is* an answer to "do you want this?" — and
    `?unique=` is an unset variable in someone's URL builder.
    """
    assert ha_api._query_flag(_FakeRequest(), "unique") is False
    assert ha_api._query_flag(_FakeRequest(unique=""), "unique") is False
    assert ha_api._query_flag(_FakeRequest(unique=" "), "unique") is False
    assert ha_api._query_flag(_FakeRequest(), "unique", default=True) is True
