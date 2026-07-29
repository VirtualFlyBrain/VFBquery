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


class TestQueryConnectivitySubclassExpansion:
    """A named type has to mean its subclasses, or the obvious queries answer
    with an empty table that reads as 'not connected'."""

    @pytest.mark.integration
    def test_parent_class_with_no_direct_instances_returns_results(self):
        # Kenyon cell has zero directly-typed individuals; all ~16,000 sit under
        # its subclasses. Matching the named class alone returns nothing.
        result = query_connectivity(
            upstream_type="DA1 lPN", downstream_type="Kenyon cell",
        )
        assert result["count"] > 0
        assert result["resolved"]["downstream"]["classes_searched"] > 1
        assert result["resolved"]["downstream"]["instances"] > 1000

    @pytest.mark.integration
    def test_resolved_reports_how_a_label_was_read(self):
        result = query_connectivity(
            upstream_type="DA1 lPN", downstream_type="Kenyon cell",
        )
        up = result["resolved"]["upstream"]
        assert up["query"] == "DA1 lPN"
        assert up["id"] == "FBbt_00067363"
        # A non-exact resolution has to be stated, not silently applied.
        assert any("DA1 lPN" in w for w in result["warnings"])

    @pytest.mark.integration
    def test_anchor_side_does_not_change_the_answer(self):
        # The query is driven from whichever side has fewer individuals; that is
        # a performance choice and must not be an answer choice.
        from vfbquery.vfb_connectivity import (
            _get_nc, _subclass_closure, _build_connectivity_cypher,
            DEFAULT_EXCLUDE_DBS,
        )
        from vfbquery.neo4j_client import dict_cursor

        nc = _get_nc()
        _, up_ids, _ = _subclass_closure(nc, "FBbt_00067363")   # DA1 lPN
        _, down_ids, _ = _subclass_closure(nc, "FBbt_00003686")  # Kenyon cell
        counts = []
        for anchor in ("upstream", "downstream"):
            cypher = _build_connectivity_cypher(
                up_ids, down_ids, 5, False, DEFAULT_EXCLUDE_DBS, anchor=anchor,
            )
            counts.append(len(dict_cursor(nc.commit_list([cypher]))))
        assert counts[0] == counts[1] > 0

    @pytest.mark.integration
    def test_ambiguous_label_lists_candidates(self):
        # "neuron " (with the trailing space) is contained in a great many
        # labels and matches none exactly, so it must not be guessed at.
        result = query_connectivity(upstream_type="lobe projection neuron D")
        assert result["count"] == 0
        assert any("ambiguous" in w for w in result["warnings"])


class TestQueryConnectivityExcludeDbsDefault:
    @pytest.mark.integration
    def test_default_excludes_are_a_strict_subset_of_everything(self):
        from vfbquery.vfb_connectivity import DEFAULT_EXCLUDE_DBS

        default = query_connectivity(
            upstream_type="DA1 lPN", downstream_type="Kenyon cell",
        )
        everything = query_connectivity(
            upstream_type="DA1 lPN", downstream_type="Kenyon cell",
            exclude_dbs=[],
        )
        assert DEFAULT_EXCLUDE_DBS == ["hb", "fafb"]
        assert 0 < default["count"] < everything["count"]

    @pytest.mark.integration
    def test_default_matches_passing_it_explicitly(self):
        from vfbquery.vfb_connectivity import DEFAULT_EXCLUDE_DBS

        implicit = query_connectivity(
            upstream_type=KNOWN_UPSTREAM, downstream_type=KNOWN_DOWNSTREAM,
        )
        explicit = query_connectivity(
            upstream_type=KNOWN_UPSTREAM, downstream_type=KNOWN_DOWNSTREAM,
            exclude_dbs=list(DEFAULT_EXCLUDE_DBS),
        )
        assert implicit["count"] == explicit["count"]


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
