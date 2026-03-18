"""Tests for vfb_connectivity module — connectome datasets and neuron connectivity."""
import pytest

from vfbquery.vfb_connectivity import list_connectome_datasets, query_connectivity

KNOWN_UPSTREAM = "giant fiber neuron"
KNOWN_DOWNSTREAM = "peripherally synapsing interneuron"


# ---------------------------------------------------------------------------
# list_connectome_datasets tests
# ---------------------------------------------------------------------------


class TestListConnectomeDatasets:
    @pytest.mark.integration
    def test_returns_datasets(self):
        datasets = list_connectome_datasets()
        assert len(datasets) > 0

    @pytest.mark.integration
    def test_datasets_have_label_and_symbol(self):
        datasets = list_connectome_datasets()
        for d in datasets:
            assert "label" in d
            assert "symbol" in d

    @pytest.mark.integration
    def test_hemibrain_present(self):
        datasets = list_connectome_datasets()
        symbols = [d["symbol"] for d in datasets]
        assert "hb" in symbols

    @pytest.mark.integration
    def test_every_dataset_has_symbol(self):
        datasets = list_connectome_datasets()
        for d in datasets:
            assert d["symbol"], f"Dataset {d['label']} has empty symbol"


# ---------------------------------------------------------------------------
# query_connectivity tests
# ---------------------------------------------------------------------------


class TestQueryConnectivityKnown:
    @pytest.mark.integration
    def test_known_connection_both_types(self):
        result = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
        )
        assert result["count"] > 0
        assert len(result["connections"]) == result["count"]

    @pytest.mark.integration
    def test_both_types_subset_of_either_alone(self):
        result_both = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
        )
        result_up = query_connectivity(upstream_type=KNOWN_UPSTREAM)
        result_down = query_connectivity(downstream_type=KNOWN_DOWNSTREAM)

        assert result_both["count"] > 0
        assert result_both["count"] <= result_up["count"]
        assert result_both["count"] <= result_down["count"]


class TestQueryConnectivityGroupByClass:
    @pytest.mark.integration
    def test_group_by_class(self):
        result = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            group_by_class=True,
        )
        assert result["count"] > 0
        conn = result["connections"][0]
        assert "upstream_class" in conn
        assert "downstream_class" in conn


class TestQueryConnectivityWeightFiltering:
    @pytest.mark.integration
    def test_higher_weight_fewer_results(self):
        result_low = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            weight=1,
        )
        result_high = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            weight=50,
        )
        assert result_low["count"] >= result_high["count"]


class TestQueryConnectivityExcludeDbs:
    @pytest.mark.integration
    def test_exclude_all_returns_no_results(self):
        datasets = list_connectome_datasets()
        all_symbols = [d["symbol"] for d in datasets]
        result = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            exclude_dbs=all_symbols,
        )
        assert result["count"] == 0


class TestQueryConnectivityEdgeCases:
    @pytest.mark.integration
    def test_nonexistent_type_returns_warning(self):
        result = query_connectivity(
            upstream_type="xyzzy_nonexistent_neuron_type_99999",
            downstream_type=KNOWN_DOWNSTREAM,
        )
        assert result["count"] == 0
        assert len(result["warnings"]) > 0

    def test_no_types_raises_error(self):
        with pytest.raises(ValueError, match="At least one"):
            query_connectivity()
