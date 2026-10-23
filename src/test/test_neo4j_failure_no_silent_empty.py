"""A failed Neo4j main query must never read as "no rows".

Backend-free: ``vc`` is monkeypatched, so these run in CI without credentials.

Why: from 2026-10-12 the TransgeneExpressionHere main query for mushroom body
timed out on pdb. ``commit_list`` reports that by returning ``False``, which
became an empty table, so the function returned ``{'count': 2339, 'rows': []}``
— and the Solr result cache's ``count >= 0`` rule would have stored it.
"""
import types

import pytest

from vfbquery import cached_functions as cf
from vfbquery import solr_result_cache as src
from vfbquery import vfb_queries as vq


def _count_reply(n):
    return [{"columns": ["total_count"], "data": [{"row": [n]}]}]


class _NC:
    """Stand-in for ``vc.nc`` replaying one reply per ``commit_list`` call."""

    def __init__(self, *replies):
        self._replies = list(replies)

    def commit_list(self, statements):
        return self._replies.pop(0)


def _wire(monkeypatch, *replies):
    monkeypatch.setattr(vq, "vc", types.SimpleNamespace(
        nc=_NC(*replies),
        vfb=types.SimpleNamespace(oc=types.SimpleNamespace(
            get_subclasses=lambda **kw: [])),
    ))


def test_transgene_expression_raises_when_main_query_fails(monkeypatch):
    _wire(monkeypatch, _count_reply(2339), False)
    with pytest.raises(vq.Neo4jQueryError, match="TransgeneExpressionHere main query"):
        cf._original_get_transgene_expression_here(
            "FBbt_00003748", return_dataframe=False, limit=10)


def test_transgene_expression_raises_when_count_query_fails(monkeypatch):
    _wire(monkeypatch, False)
    with pytest.raises(vq.Neo4jQueryError, match="TransgeneExpressionHere count query"):
        cf._original_get_transgene_expression_here(
            "FBbt_00003748", return_dataframe=False, limit=10)


def test_expression_overlaps_raises_when_main_query_fails(monkeypatch):
    _wire(monkeypatch, _count_reply(79), False)
    with pytest.raises(vq.Neo4jQueryError, match="ExpressionOverlapsHere main query"):
        cf._original_get_expression_overlaps_here(
            "VFBexp_FBtp0001321", return_dataframe=False, limit=5)


def test_genuinely_empty_result_is_still_returned(monkeypatch):
    empty = [{"columns": [], "data": []}]
    _wire(monkeypatch, _count_reply(0), empty)
    result = cf._original_get_transgene_expression_here(
        "FBbt_00000000", return_dataframe=False, limit=10)
    assert result["count"] == 0
    assert result["rows"] == []


@pytest.mark.parametrize("result, missing", [
    ({"headers": {}, "rows": [], "count": 2339}, True),
    ({"headers": {}, "rows": [], "count": 0}, False),
    ({"headers": {}, "rows": [{"id": "x"}], "count": 2339}, False),
    ({"headers": {}, "rows": [], "count": -1}, False),
    ({"Id": "FBbt_00003748", "Name": "mushroom body"}, False),
    ([], False),
])
def test_result_rows_missing(result, missing):
    assert src.result_rows_missing(result) is missing


def test_result_rows_missing_accepts_numpy_count():
    np = pytest.importorskip("numpy")
    assert src.result_rows_missing({"rows": [], "count": np.int64(5)}) is True


# ---------------------------------------------------------------------------
# read path: entries stored before the write-path guard existed
# ---------------------------------------------------------------------------

class _Solr:
    """Answers cache lookups from a dict and records delete posts."""

    def __init__(self, docs):
        self.docs = docs
        self.posts = []

    def get(self, url, params=None, timeout=None):
        doc_id = (params or {}).get("q", "").split("id:", 1)[-1]
        payload = self.docs.get(doc_id)
        docs = [{"cache_data": payload}] if payload is not None else []
        return types.SimpleNamespace(status_code=200,
                                     json=lambda: {"response": {"docs": docs}})

    def post(self, url, data=None, headers=None, params=None, timeout=None):
        self.posts.append(data)
        return types.SimpleNamespace(status_code=200, text="", json=lambda: {})


def _cache_with(monkeypatch, result):
    import json
    for var in ("VFBQUERY_CACHE_NAMESPACE", "VFBQUERY_CACHE_NAMESPACE_FALLBACK",
                "VFBQUERY_CACHE_READONLY", "VFBQUERY_CACHE_ENABLED"):
        monkeypatch.delenv(var, raising=False)
    cache = src.SolrResultCache()
    monkeypatch.setattr(cache, "_solr_available", lambda: True)
    payload = src._encode_cache_field(json.dumps(
        cache._create_cache_metadata(result, limit=-1)))
    solr = _Solr({"vfb_query_transgene_expression_here_T": payload})
    monkeypatch.setattr(src.requests, "get", solr.get)
    monkeypatch.setattr(src.requests, "post", solr.post)
    return cache, solr


def test_cached_result_with_missing_rows_is_a_miss_and_purged(monkeypatch):
    # Stored 2026-10-15 for mushroom body by the pre-fix code, served to every
    # PR check until it expired.
    cache, solr = _cache_with(monkeypatch, {"headers": {}, "rows": [], "count": 2339})
    assert cache.get_cached_result("transgene_expression_here", "T", limit=-1) is None
    assert any("vfb_query_transgene_expression_here_T" in p for p in solr.posts)


def test_cached_result_with_missing_rows_is_not_purged_when_read_only(monkeypatch):
    cache, solr = _cache_with(monkeypatch, {"headers": {}, "rows": [], "count": 2339})
    monkeypatch.setenv("VFBQUERY_CACHE_READONLY", "true")
    assert cache.get_cached_result("transgene_expression_here", "T", limit=-1) is None
    assert solr.posts == []


def test_cached_result_with_rows_is_served(monkeypatch):
    good = {"headers": {}, "rows": [{"id": "VFBexp_1"}], "count": 2339}
    cache, solr = _cache_with(monkeypatch, good)
    assert cache.get_cached_result("transgene_expression_here", "T", limit=-1) == good
    assert solr.posts == []
