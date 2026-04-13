"""Tests for NeuronNeuronConnectivityQuery.

Tests the query that finds neurons connected to a given neuron.
This implements the neuron_neuron_connectivity_query from the VFB XMI specification.
"""

import pytest
import pandas as pd

from vfbquery.vfb_queries import (
    get_neuron_neuron_connectivity,
    NeuronNeuronConnectivityQuery_to_schema,
)

# VFB_jrchk00s = LPC1 (FlyEM-HB:1775513344) — known to have connectivity data.
TEST_NEURON = "VFB_jrchk00s"


class TestNeuronNeuronConnectivityDict:
    """Tests using return_dataframe=False (dict output)."""

    @pytest.mark.integration
    def test_returns_results(self):
        result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False
        )
        assert isinstance(result, dict)
        assert result["count"] > 0
        assert len(result["rows"]) > 0

    @pytest.mark.integration
    def test_row_has_expected_keys(self):
        result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False, limit=1
        )
        assert result["rows"], "Expected at least one row"
        row = result["rows"][0]
        expected_keys = {"id", "label", "outputs", "inputs", "tags"}
        assert expected_keys.issubset(row.keys())

    @pytest.mark.integration
    def test_headers_present(self):
        result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False, limit=1
        )
        assert "headers" in result
        assert "label" in result["headers"]
        assert "outputs" in result["headers"]
        assert "inputs" in result["headers"]

    @pytest.mark.integration
    def test_limit_respected(self):
        result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False, limit=3
        )
        assert len(result["rows"]) <= 3
        assert result["count"] >= len(result["rows"])

    @pytest.mark.integration
    def test_direction_upstream(self):
        all_result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False
        )
        up_result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False, direction='upstream'
        )
        assert up_result["count"] > 0
        assert up_result["count"] <= all_result["count"]

    @pytest.mark.integration
    def test_direction_downstream(self):
        all_result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False
        )
        down_result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False, direction='downstream'
        )
        assert down_result["count"] > 0
        assert down_result["count"] <= all_result["count"]


class TestNeuronNeuronConnectivityDataFrame:
    """Tests using return_dataframe=True (DataFrame output)."""

    @pytest.mark.integration
    def test_returns_dataframe(self):
        df = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=True
        )
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
        df = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=True, limit=1
        )
        expected_cols = {"id", "label", "outputs", "inputs", "tags"}
        assert expected_cols.issubset(set(df.columns))

    @pytest.mark.integration
    def test_limit_respected(self):
        df = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=True, limit=5
        )
        assert len(df) <= 5


class TestNeuronNeuronConnectivitySchema:
    def test_schema_generation(self):
        schema = NeuronNeuronConnectivityQuery_to_schema(
            "LPC1", {"short_form": TEST_NEURON}
        )
        assert schema.query == "NeuronNeuronConnectivityQuery"
        assert schema.function == "get_neuron_neuron_connectivity"
        assert schema.label == "Neurons connected to LPC1"
        assert schema.preview == 5
        assert schema.preview_columns == ["id", "label", "outputs", "inputs", "tags"]
