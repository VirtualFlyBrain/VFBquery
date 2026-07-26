"""Smoke tests for vfbquery-client.

Offline tests (adapter shaping) run anywhere. The live tests hit v3-cached and
are skipped unless VFB_LIVE_TESTS=1 is set, so CI stays hermetic by default.
"""
import os
import pandas as pd
import pytest

from vfbquery_client import VfbClient


def test_to_df_rows_and_list_columns():
    payload = {"rows": [
        {"id": "VFB_1", "label": "n1", "tags": "Neuron|Adult", "source": "hemibrain"},
        {"id": "VFB_2", "label": "n2", "tags": "Neuron", "source": "flywire"},
    ]}
    df = VfbClient._to_df(payload)
    assert list(df["id"]) == ["VFB_1", "VFB_2"]
    assert df.loc[0, "tags"] == ["Neuron", "Adult"]      # pipe-joined -> list


def test_to_df_handles_bare_list_and_dict():
    assert len(VfbClient._to_df([{"a": 1}, {"a": 2}])) == 2
    assert len(VfbClient._to_df({"a": 1})) == 1
    assert VfbClient._to_df(None).empty


def test_get_vfb_link():
    url = VfbClient.get_vfb_link(["VFB_jrchjtdb", "VFB_fw035286"], template="VFB_00101567")
    assert url.startswith("https://virtualflybrain.org/?id=VFB_jrchjtdb,VFB_fw035286")
    assert "t=VFB_00101567" in url


def test_search_params_sent_to_endpoint(monkeypatch):
    """Search must send names /search understands and no Solr config of its own."""
    seen = {}

    def fake_get(self, path, **params):
        seen["path"] = path
        seen["params"] = params
        return {"rows": [{"short_form": "FBbt_00067363", "label": "DA1 lPN"}]}

    monkeypatch.setattr(VfbClient, "_get", fake_get, raising=True)
    df = VfbClient().search("DA1 lPN", limit=3, filter_types=["Class", "Neuron"],
                            demote_types=["Individual"])
    assert seen["path"] == "search"
    assert seen["params"]["query"] == "DA1 lPN"
    assert seen["params"]["limit"] == 3
    # Candidate depth defaults to the website's 500, not to `limit` — asking Solr
    # for fewer candidates would drop good answers before ranking sees them.
    assert seen["params"]["rows"] == 500
    assert seen["params"]["filter_types"] == "Class,Neuron"
    assert seen["params"]["demote_types"] == "Individual"
    assert "exclude_types" not in seen["params"]   # empty filters are omitted
    assert list(df["short_form"]) == ["FBbt_00067363"]


def test_resolve_to_id_ranks_before_taking_top(monkeypatch):
    """_resolve_to_id must rank a full candidate set, then take row 0."""
    seen = {}

    def fake_get(self, path, **params):
        seen.update(params)
        return {"rows": [{"short_form": "FBbt_00067363", "label": "DA1 lPN"}]}

    monkeypatch.setattr(VfbClient, "_get", fake_get, raising=True)
    assert VfbClient()._resolve_to_id("DA1 lPN") == "FBbt_00067363"
    assert seen["limit"] == 1 and seen["rows"] == 500


def test_resolve_to_id_passes_ids_through(monkeypatch):
    def explode(self, path, **params):    # must not be called for an id
        raise AssertionError("searched for something that is already an id")

    monkeypatch.setattr(VfbClient, "_get", explode, raising=True)
    assert VfbClient()._resolve_to_id("VFB_jrchjtdb") == "VFB_jrchjtdb"
    assert VfbClient()._resolve_to_id("FBbt_00067363") == "FBbt_00067363"


@pytest.mark.skipif(os.environ.get("VFB_LIVE_TESTS") != "1",
                    reason="set VFB_LIVE_TESTS=1 to run live v3-cached tests")
def test_live_get_instances_da1lpn():
    vfb = VfbClient()
    df = vfb.get_instances("FBbt_00067363")   # DA1 lPN by id (no search dependency)
    assert isinstance(df, pd.DataFrame) and len(df) > 50
    assert "data_source" in df.columns        # renamed from 'source'


@pytest.mark.skipif(os.environ.get("VFB_LIVE_TESTS") != "1",
                    reason="set VFB_LIVE_TESTS=1 to run live v3-cached tests")
def test_live_search_ranks_class_first_for_da1_lpn():
    """The website's ranking puts the class above the individuals for 'DA1 lPN'.

    A plain Solr query does not — that ordering is the whole point of /search,
    so it is the thing worth asserting against the live service.
    """
    vfb = VfbClient()
    df = vfb.search("DA1 lPN", limit=5)
    assert len(df) == 5
    assert df.loc[0, "short_form"] == "FBbt_00067363"
    # Bare hemibrain bodyIds resolve too (they only match via shortform/xref).
    assert vfb._resolve_to_id("1734350908") == "VFB_jrchjtdb"
