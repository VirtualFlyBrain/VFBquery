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


class TestDownstreamClassConnectivityHierarchyRollup:
    """Regression tests for the partner-side hierarchy rollup behaviour:
    connections to a child class also count toward each ancestor class within
    the Neuron subtree, without double-counting under FBbt multi-inheritance.
    """

    @pytest.fixture(scope='class')
    def result(self):
        return get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

    @pytest.mark.integration
    def test_parent_class_appears_with_sensible_counts(self, result):
        """A row keyed on a parent class should have connected_n at least as
        large as any of its descendant rows (set-union semantics) and at most
        the sum of descendant connected_n (no double-counting beyond what
        multi-inheritance forces).
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor

        rows = result["rows"]
        ids = [r["id"] for r in rows]
        assert ids, "Expected at least one row to test against"

        # Find any (parent, child) pair among the row ids.
        q = (
            "MATCH (p:Class)<-[:SUBCLASSOF*1..]-(c:Class) "
            "WHERE p.short_form IN %s AND c.short_form IN %s "
            "RETURN p.short_form AS parent, c.short_form AS child LIMIT 1"
            % (ids, ids)
        )
        pairs = get_dict_cursor()(vc.nc.commit_list([q]))
        if not pairs:
            pytest.skip("No parent/child pair among result rows for this class")

        parent_id = pairs[0]["parent"]
        child_id = pairs[0]["child"]
        parent_row = next(r for r in rows if r["id"] == parent_id)
        # Sum connected_n across all descendant rows (not just the one returned).
        desc_q = (
            "MATCH (p:Class {short_form: '%s'})<-[:SUBCLASSOF*1..]-(c:Class) "
            "WHERE c.short_form IN %s "
            "RETURN collect(DISTINCT c.short_form) AS descs"
            % (parent_id, ids)
        )
        desc_rows = get_dict_cursor()(vc.nc.commit_list([desc_q]))
        descendant_ids = desc_rows[0]["descs"] if desc_rows else [child_id]
        descendant_rows = [r for r in rows if r["id"] in descendant_ids]
        max_child = max(r["connected_n"] for r in descendant_rows)
        sum_child = sum(r["connected_n"] for r in descendant_rows)
        assert parent_row["connected_n"] >= max_child, (
            f"Parent {parent_id} connected_n={parent_row['connected_n']} should "
            f"be >= max descendant connected_n={max_child}"
        )
        assert parent_row["connected_n"] <= sum_child, (
            f"Parent {parent_id} connected_n={parent_row['connected_n']} should "
            f"be <= sum of descendant connected_n={sum_child}"
        )

    @pytest.mark.integration
    def test_total_n_is_constant_across_rows(self, result):
        """`total_n` is the queried-side instance count and must be the same
        for every output row (regression for the previous summed-across-
        subclasses value).
        """
        rows = result["rows"]
        assert rows, "Expected at least one row"
        total_ns = {r["total_n"] for r in rows}
        assert len(total_ns) == 1, (
            f"Expected total_n to be constant across rows, got: {total_ns}"
        )
        assert next(iter(total_ns)) > 0

    @pytest.mark.integration
    def test_no_rows_above_neuron_root(self, result):
        """The partner-side ancestor walk should stop at the Neuron class
        (FBbt_00005106). No row id should be a class outside the Neuron
        subtree.
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor, NEURON_ROOT_SHORT_FORM

        ids = [r["id"] for r in result["rows"]]
        assert ids, "Expected at least one row"
        q = (
            "MATCH (root:Class {short_form: '%s'})<-[:SUBCLASSOF*0..]-(c:Class) "
            "WHERE c.short_form IN %s "
            "RETURN collect(DISTINCT c.short_form) AS in_neuron"
            % (NEURON_ROOT_SHORT_FORM, ids)
        )
        result_rows = get_dict_cursor()(vc.nc.commit_list([q]))
        in_neuron = set(result_rows[0]["in_neuron"]) if result_rows else set()
        offenders = [i for i in ids if i not in in_neuron]
        assert not offenders, (
            f"Found {len(offenders)} row(s) outside the Neuron subtree: "
            f"{offenders[:5]}"
        )


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
