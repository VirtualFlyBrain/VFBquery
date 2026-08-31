"""Tests for vfb_connectivity module — connectome datasets and neuron connectivity.

Fixture choice matters here. Every test in this file is an integration test that
runs against the shared production Neo4j, and CI runs them with the SOLR result
cache disabled, so each call is paid in full. Two rules keep that affordable:

* Prefer small classes. ``giant fiber neuron`` (8 individuals) and
  ``giant fiber coupled neuron 2`` (30) are used wherever the assertion does
  not depend on the class being large.
* Where a large class is the point — ``Kenyon cell`` has no individuals of its
  own and ~16,000 under its subclasses, which is exactly what the subclass
  expansion tests exist to check — ask for it with ``group_by_class=True``.
  That bounds the reply at one row per class pair instead of one per individual
  pair, so the traversal under test is unchanged while the table that comes
  back over the wire stays in the tens of rows.

The expensive results are also module-scoped fixtures rather than repeated
calls, so the three tests that need the same query cost one query between them.
"""
import pytest

from vfbquery.vfb_connectivity import list_connectome_datasets, query_connectivity

#: A small, stable pair: 8 and 30 connectivity individuals respectively, one
#: class each, no subclasses. Cheap enough to query several times — the two
#: sides give 42 connections under the default excludes in well under two
#: seconds.
#:
#: The downstream side is deliberately not ``peripherally synapsing
#: interneuron``, which reads like the obvious partner for the giant fiber and
#: was used here until it was actually measured. Every one of its 17
#: connections to ``giant fiber neuron`` lives in ``hb`` or ``fafb``, so
#: ``DEFAULT_EXCLUDE_DBS`` removes all of them and the pair answers 0 —
#: silently, since an empty table is a valid answer. A fixture for this file
#: has to be checked against the *default* excludes, not merely shown to exist.
KNOWN_UPSTREAM = "giant fiber neuron"
KNOWN_DOWNSTREAM = "giant fiber coupled neuron 2"

#: The subclass-expansion pair. DA1 lPN has 68 individuals; Kenyon cell has none
#: of its own and ~16,000 across 38 subclasses. Only ever queried grouped.
EXPANSION_UPSTREAM = "DA1 lPN"
EXPANSION_UPSTREAM_ID = "FBbt_00067363"
EXPANSION_DOWNSTREAM = "Kenyon cell"
EXPANSION_DOWNSTREAM_ID = "FBbt_00003686"


@pytest.fixture(scope="module")
def expansion_result():
    """DA1 lPN -> Kenyon cell, grouped, run once for the whole module."""
    return query_connectivity(
        upstream_type=EXPANSION_UPSTREAM,
        downstream_type=EXPANSION_DOWNSTREAM,
        group_by_class=True,
    )


@pytest.fixture(scope="module")
def datasets():
    return list_connectome_datasets()


# ---------------------------------------------------------------------------
# list_connectome_datasets tests
# ---------------------------------------------------------------------------


class TestListConnectomeDatasets:
    @pytest.mark.integration
    def test_returns_datasets(self, datasets):
        assert len(datasets) > 0

    @pytest.mark.integration
    def test_datasets_have_label_and_symbol(self, datasets):
        for d in datasets:
            assert "label" in d
            assert "symbol" in d

    @pytest.mark.integration
    def test_hemibrain_present(self, datasets):
        symbols = [d["symbol"] for d in datasets]
        assert "hb" in symbols

    @pytest.mark.integration
    def test_every_dataset_has_symbol(self, datasets):
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
        # Grouped on all three sides: a one-sided query returns every partner of
        # the named type, which is the one shape in this file that can run to
        # thousands of rows. Grouping bounds it at class pairs, and the
        # containment being asserted holds either way.
        both = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            group_by_class=True,
        )
        up_only = query_connectivity(
            upstream_type=KNOWN_UPSTREAM, group_by_class=True,
        )
        down_only = query_connectivity(
            downstream_type=KNOWN_DOWNSTREAM, group_by_class=True,
        )

        assert both["count"] > 0
        assert both["count"] <= up_only["count"]
        assert both["count"] <= down_only["count"]


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


class TestQueryConnectivityRollup:
    """Grouped queries roll up over the subclass hierarchy, so a row appears for
    every level with data up to each named query term — the two-ended analogue
    of the single-ended DownstreamClassConnectivity / UpstreamClassConnectivity
    rollup. The distinguishing case is EPG <-> ExR1: across datasets EPG is
    typed both to its parent class and per-glomerulus, and ExR1 both to its
    parent and to DM3/DM4 lineage, so only a rollup produces the parent-to-parent
    row. exclude_dbs=[] keeps every dataset in scope."""

    #: EPG parent and ExR1 parent. EPG has per-glomerulus subclasses; ExR1 has
    #: DM3/DM4 lineage subclasses. Both parents have directly-typed instances in
    #: some datasets, which is what makes the parent-to-parent row real.
    ROLLUP_UP = "FBbt_00047030"    # EPG
    ROLLUP_DOWN = "FBbt_00003655"  # ExR1

    @pytest.fixture(scope="class")
    def rollup_result(self):
        return query_connectivity(
            upstream_type=self.ROLLUP_UP,
            downstream_type=self.ROLLUP_DOWN,
            group_by_class=True,
            exclude_dbs=[],
        )

    @pytest.mark.integration
    def test_top_level_query_term_row_present(self, rollup_result):
        # The row the non-rolled-up grouping never emitted: both sides at the
        # named query term, aggregating every level beneath them.
        conns = rollup_result["connections"]
        assert conns
        assert any(
            c["upstream_class_id"] == self.ROLLUP_UP
            and c["downstream_class_id"] == self.ROLLUP_DOWN
            for c in conns
        ), "expected a rolled-up EPG->ExR1 parent-to-parent row"

    @pytest.mark.integration
    def test_finer_levels_also_present(self, rollup_result):
        # Rollup adds levels, it does not replace them: subclass-level rows still
        # appear alongside the parent-to-parent row.
        conns = rollup_result["connections"]
        assert any(
            c["upstream_class_id"] != self.ROLLUP_UP
            or c["downstream_class_id"] != self.ROLLUP_DOWN
            for c in conns
        )

    @pytest.mark.integration
    def test_parent_row_dominates_its_children(self, rollup_result):
        # The parent-to-parent row is a set-union over every child pair, so its
        # weight is at least that of any single child pair sharing an endpoint.
        conns = rollup_result["connections"]
        top = next(
            c for c in conns
            if c["upstream_class_id"] == self.ROLLUP_UP
            and c["downstream_class_id"] == self.ROLLUP_DOWN
        )
        children = [
            c for c in conns
            if c["upstream_class_id"] == self.ROLLUP_UP
            and c["downstream_class_id"] != self.ROLLUP_DOWN
        ]
        for child in children:
            assert top["total_weight"] >= child["total_weight"]


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
    def test_exclude_all_returns_no_results(self, datasets):
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
    def test_parent_class_with_no_direct_instances_returns_results(self, expansion_result):
        # Kenyon cell has zero directly-typed individuals; all ~16,000 sit under
        # its subclasses. Matching the named class alone returns nothing.
        assert expansion_result["count"] > 0
        assert expansion_result["resolved"]["downstream"]["classes_searched"] > 1
        assert expansion_result["resolved"]["downstream"]["instances"] > 1000

    @pytest.mark.integration
    def test_resolved_reports_how_a_label_was_read(self, expansion_result):
        up = expansion_result["resolved"]["upstream"]
        assert up["query"] == EXPANSION_UPSTREAM
        assert up["id"] == EXPANSION_UPSTREAM_ID
        # A non-exact resolution has to be stated, not silently applied.
        assert any(EXPANSION_UPSTREAM in w for w in expansion_result["warnings"])

    @pytest.mark.integration
    def test_anchor_side_does_not_change_the_answer(self):
        # The query is driven from whichever side has fewer individuals; that is
        # a performance choice and must not be an answer choice. Run on the
        # small pair: forcing the anchor onto Kenyon cell's ~16,000 individuals
        # tested nothing extra and cost the most of anything in this file.
        from vfbquery.vfb_connectivity import (
            _get_nc, _subclass_closure, _build_connectivity_cypher,
            _resolve_neuron_type_label, DEFAULT_EXCLUDE_DBS,
        )
        from vfbquery.neo4j_client import dict_cursor

        nc = _get_nc()
        up_id = _resolve_neuron_type_label(nc, KNOWN_UPSTREAM)
        down_id = _resolve_neuron_type_label(nc, KNOWN_DOWNSTREAM)
        _, up_ids, _ = _subclass_closure(nc, up_id)
        _, down_ids, _ = _subclass_closure(nc, down_id)
        counts = []
        for anchor in ("upstream", "downstream"):
            cypher = _build_connectivity_cypher(
                up_ids, down_ids, 5, False, DEFAULT_EXCLUDE_DBS, anchor=anchor,
            )
            counts.append(len(dict_cursor(nc.commit_list([cypher]))))
        assert counts[0] == counts[1] > 0

    @pytest.mark.integration
    def test_ambiguous_label_lists_candidates(self):
        # Matches several labels by containment and none exactly, so it must not
        # be guessed at.
        result = query_connectivity(upstream_type="lobe projection neuron D")
        assert result["count"] == 0
        assert any("ambiguous" in w for w in result["warnings"])


class TestQueryConnectivityExcludeDbsDefault:
    @pytest.mark.integration
    def test_default_excludes_are_a_strict_subset_of_everything(self, expansion_result):
        # Grouped, and reusing the module fixture for the default half, so this
        # costs one extra query rather than two full ungrouped ones over every
        # dataset — which is what made it the most expensive test here.
        from vfbquery.vfb_connectivity import DEFAULT_EXCLUDE_DBS

        everything = query_connectivity(
            upstream_type=EXPANSION_UPSTREAM,
            downstream_type=EXPANSION_DOWNSTREAM,
            exclude_dbs=[],
            group_by_class=True,
        )
        assert DEFAULT_EXCLUDE_DBS == ["hb", "fafb"]
        assert 0 < expansion_result["count"] < everything["count"]

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
