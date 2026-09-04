"""A class-connectivity backend failure must never read as ``count: 0``.

Backend-free: every Neo4j/Solr/Owlery touch point inside
``_aggregate_class_connectivity`` is monkeypatched, so these run in CI without
credentials and exercise exactly the paths that used to ``return []``.

Why: on 2026-09-04 gamma Kenyon cell (FBbt_00100247) showed "There is no data
to display" for DownstreamClassConnectivity. The origin had returned
``{'count': 0}`` during a moment it could not fetch per-instance connectivity,
the Solr result cache stored it (``count >= 0`` is "valid"), and the
v3-cached nginx edge pinned that 200 for a month. Three caches, one lie.
"""
import types

import pytest

from vfbquery import ha_api
from vfbquery import solr_result_cache as src
from vfbquery import vfb_queries as vq


CLASS = "FBbt_00100247"
INSTANCES = {"VFB_1", "VFB_2", "VFB_3"}


class _NC:
    """Stand-in for ``vc.nc`` whose ``commit_list`` returns whatever we say."""

    def __init__(self, reply):
        self._reply = reply

    def commit_list(self, statements):
        reply = self._reply
        if isinstance(reply, Exception):
            raise reply
        return reply


def _membership_reply(instances=INSTANCES):
    """A Neo4j transaction result listing *instances* under CLASS."""
    return [{
        "columns": ["cid", "label", "iids"],
        "data": [{"row": [CLASS, "gamma Kenyon cell", sorted(instances)]}],
    }]


def _wire(monkeypatch, *, membership=None, edges=None, missing=(),
          partner_entries=None, ancestors=None, partner_membership=None):
    """Patch every backend seam of ``_aggregate_class_connectivity``.

    Defaults describe a healthy query with one downstream partner class.
    """
    if membership is None:
        membership = _membership_reply()
    if edges is None:
        edges = {i: [{"id": "VFB_p", "outputs": 5}] for i in INSTANCES}
    if partner_entries is None:
        partner_entries = [{"object": {"short_form": "FBbt_p"}}]
    if ancestors is None:
        ancestors = ({"FBbt_p"}, {"FBbt_p": "partner"})
    if partner_membership is None:
        partner_membership = {"VFB_p": {"FBbt_p"}}

    fake_vc = types.SimpleNamespace(
        nc=_NC(membership),
        vfb=types.SimpleNamespace(oc=types.SimpleNamespace(
            get_subclasses=lambda **kw: [])),
    )
    monkeypatch.setattr(vq, "vc", fake_vc)
    monkeypatch.setattr(vq, "_bulk_fetch_per_instance_connectivity",
                        lambda ids: (dict(edges), list(missing)))
    monkeypatch.setattr(vq, "_fetch_connectivity_entries",
                        lambda *a, **k: list(partner_entries))
    monkeypatch.setattr(vq, "_get_partner_class_ancestors",
                        lambda *a, **k: ancestors)
    monkeypatch.setattr(vq, "_build_partner_instance_class_membership",
                        lambda ids: dict(partner_membership))


# ---------------------------------------------------------------------------
# _aggregate_class_connectivity
# ---------------------------------------------------------------------------

def test_healthy_query_returns_rows(monkeypatch):
    _wire(monkeypatch)
    status = {}
    rows = vq._aggregate_class_connectivity(CLASS, "downstream", status=status)
    assert [r["id"] for r in rows] == ["FBbt_p"]
    assert rows[0]["connected_n"] == 3 and rows[0]["total_n"] == 3
    assert status == {"missing": 0, "total": 3}


def test_class_with_no_instances_is_a_true_zero(monkeypatch):
    _wire(monkeypatch, membership=[{"columns": ["cid", "label", "iids"],
                                    "data": []}])
    assert vq._aggregate_class_connectivity(CLASS, "downstream") == []


def test_instances_with_no_positive_edges_is_a_true_zero(monkeypatch):
    _wire(monkeypatch, edges={i: [] for i in INSTANCES},
          partner_entries=[], ancestors=(set(), {}))
    assert vq._aggregate_class_connectivity(CLASS, "downstream") == []


def test_membership_query_exception_raises(monkeypatch):
    _wire(monkeypatch, membership=RuntimeError("neo4j down"))
    with pytest.raises(vq.ConnectivityBackendError):
        vq._aggregate_class_connectivity(CLASS, "downstream")


def test_membership_query_false_reply_raises(monkeypatch):
    # commit_list signals a transaction error by returning False, which
    # dict_cursor used to swallow into [] — the silent path.
    _wire(monkeypatch, membership=False)
    with pytest.raises(vq.ConnectivityBackendError):
        vq._aggregate_class_connectivity(CLASS, "downstream")


def test_no_per_instance_connectivity_at_all_raises(monkeypatch):
    _wire(monkeypatch, edges={}, missing=sorted(INSTANCES))
    with pytest.raises(vq.ConnectivityBackendError):
        vq._aggregate_class_connectivity(CLASS, "downstream")


def test_partner_classes_unresolved_despite_edges_raises(monkeypatch):
    _wire(monkeypatch, partner_entries=[], ancestors=(set(), {}))
    with pytest.raises(vq.ConnectivityBackendError):
        vq._aggregate_class_connectivity(CLASS, "downstream")


def test_partner_membership_failure_raises(monkeypatch):
    _wire(monkeypatch, partner_membership={})
    with pytest.raises(vq.ConnectivityBackendError):
        vq._aggregate_class_connectivity(CLASS, "downstream")


def test_partial_coverage_is_reported_in_status(monkeypatch):
    edges = {"VFB_1": [{"id": "VFB_p", "outputs": 5}]}
    _wire(monkeypatch, edges=edges, missing=["VFB_2", "VFB_3"])
    status = {}
    rows = vq._aggregate_class_connectivity(CLASS, "downstream", status=status)
    assert rows and status == {"missing": 2, "total": 3}


# ---------------------------------------------------------------------------
# the public functions: partial flag, and the Solr cache refusing it
# ---------------------------------------------------------------------------

def test_partial_result_is_flagged_and_complete_result_is_not(monkeypatch):
    _wire(monkeypatch)
    full = vq.get_downstream_class_connectivity.__wrapped__(
        CLASS, return_dataframe=False)
    assert full["count"] == 1 and vq.PARTIAL_RESULT_KEY not in full

    _wire(monkeypatch, edges={"VFB_1": [{"id": "VFB_p", "outputs": 5}]},
          missing=["VFB_2", "VFB_3"])
    partial = vq.get_downstream_class_connectivity.__wrapped__(
        CLASS, return_dataframe=False)
    assert partial["count"] == 1
    assert partial[vq.PARTIAL_RESULT_KEY]["missing_instances"] == 2
    assert partial[vq.PARTIAL_RESULT_KEY]["total_instances"] == 3
    assert src.result_is_partial(partial) and not src.result_is_partial(full)


def test_upstream_shares_the_same_paths(monkeypatch):
    _wire(monkeypatch, membership=False)
    with pytest.raises(vq.ConnectivityBackendError):
        vq.get_upstream_class_connectivity.__wrapped__(
            CLASS, return_dataframe=False)


# ---------------------------------------------------------------------------
# ha_api: what the edge is told
# ---------------------------------------------------------------------------

def test_empty_result_is_not_cached_at_the_edge():
    headers = ha_api._edge_cache_headers({"headers": {}, "rows": [], "count": 0})
    assert headers["X-Accel-Expires"] == "0"
    assert headers["Cache-Control"] == "no-store"


def test_partial_result_gets_a_short_edge_ttl():
    result = {"headers": {}, "rows": [{"id": "x"}], "count": 1,
              ha_api.PARTIAL_RESULT_KEY: {"missing_instances": 2}}
    headers = ha_api._edge_cache_headers(result)
    assert headers["X-Accel-Expires"] == str(ha_api.PARTIAL_RESULT_EDGE_TTL)
    assert headers["Cache-Control"] == "max-age=%d" % ha_api.PARTIAL_RESULT_EDGE_TTL


def test_complete_result_gets_the_edge_default():
    assert ha_api._edge_cache_headers(
        {"headers": {}, "rows": [{"id": "x"}], "count": 1}) == {}


def test_page_past_the_end_is_not_empty():
    # count is the authority: a later page of a 40-row result has no rows
    # in this slice but is not a "no data" answer.
    assert not ha_api._result_is_empty({"rows": [], "count": 40})
    assert ha_api._result_is_empty({"rows": []})
    assert not ha_api._result_is_empty({"error": "boom"})
