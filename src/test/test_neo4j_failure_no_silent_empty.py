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
