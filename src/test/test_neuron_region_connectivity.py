"""Tests for NeuronRegionConnectivityQuery.

Tests the query that finds brain regions where a given neuron has synaptic terminals.
This implements the neuron_region_connectivity_query from the VFB XMI specification.
"""

import pytest
import pandas as pd

from vfbquery.vfb_queries import (
    get_neuron_region_connectivity,
    NeuronRegionConnectivityQuery_to_schema,
    get_term_info,
)

# VFB_jrchk00s = LPC1 (FlyEM-HB:1775513344) — known to have region connectivity data.
TEST_NEURON = "VFB_jrchk00s"


class TestNeuronRegionConnectivityDict:
    """Tests using return_dataframe=False (dict output)."""

    @pytest.mark.integration
    def test_returns_results(self):
        result = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=False
        )
        assert isinstance(result, dict)
        assert result["count"] > 0
        assert len(result["rows"]) > 0

    @pytest.mark.integration
    def test_row_has_expected_keys(self):
        result = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=False, limit=1
        )
        assert result["rows"], "Expected at least one row"
        row = result["rows"][0]
        expected_keys = {"id", "region", "presynaptic_terminals", "postsynaptic_terminals", "tags"}
        assert expected_keys.issubset(row.keys())

    @pytest.mark.integration
    def test_headers_present(self):
        result = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=False, limit=1
        )
        assert "headers" in result
        assert "region" in result["headers"]
        assert "presynaptic_terminals" in result["headers"]
        assert "postsynaptic_terminals" in result["headers"]

    @pytest.mark.integration
    def test_limit_respected(self):
        result = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=False, limit=3
        )
        assert len(result["rows"]) <= 3
        assert result["count"] >= len(result["rows"])


class TestNeuronRegionConnectivityDataFrame:
    """Tests using return_dataframe=True (DataFrame output)."""

    @pytest.mark.integration
    def test_returns_dataframe(self):
        df = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=True
        )
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
        df = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=True, limit=1
        )
        expected_cols = {"id", "region", "presynaptic_terminals", "postsynaptic_terminals", "tags"}
        assert expected_cols.issubset(set(df.columns))

    @pytest.mark.integration
    def test_limit_respected(self):
        df = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=True, limit=3
        )
        assert len(df) <= 3


class TestNeuronRegionConnectivitySchema:
    def test_schema_generation(self):
        term_info = get_term_info(TEST_NEURON)
        neuron_name = term_info.get('Name', TEST_NEURON) if term_info else TEST_NEURON

        schema = NeuronRegionConnectivityQuery_to_schema(neuron_name, TEST_NEURON)
        assert schema.query == "NeuronRegionConnectivityQuery"
        assert schema.function == "get_neuron_region_connectivity"
        assert schema.preview == 5
        assert "region" in schema.preview_columns
        assert "presynaptic_terminals" in schema.preview_columns
        assert "postsynaptic_terminals" in schema.preview_columns
