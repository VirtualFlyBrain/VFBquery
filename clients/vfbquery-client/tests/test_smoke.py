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


@pytest.mark.skipif(os.environ.get("VFB_LIVE_TESTS") != "1",
                    reason="set VFB_LIVE_TESTS=1 to run live v3-cached tests")
def test_live_get_instances_da1lpn():
    vfb = VfbClient()
    df = vfb.get_instances("FBbt_00067363")   # DA1 lPN by id (no search dependency)
    assert isinstance(df, pd.DataFrame) and len(df) > 50
    assert "data_source" in df.columns        # renamed from 'source'
