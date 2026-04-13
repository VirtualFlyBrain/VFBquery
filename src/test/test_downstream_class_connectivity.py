"""Tests for DownstreamClassConnectivity query.

Tests the query that finds downstream partner neuron classes for a given
neuron class, using the pre-indexed downstream_connectivity_query Solr field.
"""

import pytest
import pandas as pd

from vfbquery.vfb_queries import (
    get_downstream_class_connectivity,
    DownstreamClassConnectivity_to_schema,
)

# FBbt_00001482 = lineage NB3-2 primary interneuron — known to have
# downstream_connectivity_query data in the vfb_json Solr core.
TEST_CLASS = "FBbt_00001482"
# A class that is unlikely to have downstream connectivity data.
EMPTY_CLASS = "FBbt_00000001"


class TestDownstreamClassConnectivityDict:
    """Tests using return_dataframe=False (dict output)."""

    @pytest.mark.integration
    def test_returns_results(self):
        result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True
        )
        assert isinstance(result, dict)
        assert result["count"] > 0
        assert len(result["rows"]) > 0

    @pytest.mark.integration
    def test_row_has_expected_keys(self):
        result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )
        assert result["rows"], "Expected at least one row"
        row = result["rows"][0]
        expected_keys = {
            "id", "downstream_class", "total_n", "connected_n",
            "percent_connected", "pairwise_connections", "total_weight", "avg_weight",
        }
        assert expected_keys.issubset(row.keys())

    @pytest.mark.integration
    def test_headers_present(self):
        result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )
        assert "headers" in result
        assert "downstream_class" in result["headers"]

    @pytest.mark.integration
    def test_limit_respected(self):
        result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=3, force_refresh=True
        )
        assert len(result["rows"]) <= 3
        # count should reflect total, not the limited set
        assert result["count"] >= len(result["rows"])

    @pytest.mark.integration
    def test_empty_class_returns_zero(self):
        result = get_downstream_class_connectivity(
            EMPTY_CLASS, return_dataframe=False, force_refresh=True
        )
        assert result["count"] == 0
        assert result["rows"] == []


class TestDownstreamClassConnectivityDataFrame:
    """Tests using return_dataframe=True (DataFrame output)."""

    @pytest.mark.integration
    def test_returns_dataframe(self):
        df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, force_refresh=True
        )
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
        df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, limit=1, force_refresh=True
        )
        expected_cols = {
            "id", "downstream_class", "total_n", "connected_n",
            "percent_connected", "pairwise_connections", "total_weight", "avg_weight",
        }
        assert expected_cols.issubset(set(df.columns))

    @pytest.mark.integration
    def test_limit_respected(self):
        df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, limit=5, force_refresh=True
        )
        assert len(df) <= 5

    @pytest.mark.integration
    def test_empty_class_returns_empty_dataframe(self):
        df = get_downstream_class_connectivity(
            EMPTY_CLASS, return_dataframe=True, force_refresh=True
        )
        assert isinstance(df, pd.DataFrame)
        assert df.empty


class TestDownstreamClassConnectivitySchema:
    def test_schema_generation(self):
        schema = DownstreamClassConnectivity_to_schema(
            "test neuron class", {"short_form": TEST_CLASS}
        )
        assert schema.query == "DownstreamClassConnectivity"
        assert schema.function == "get_downstream_class_connectivity"
        assert schema.preview == 5
        assert "downstream_class" in schema.preview_columns
        assert "percent_connected" in schema.preview_columns
