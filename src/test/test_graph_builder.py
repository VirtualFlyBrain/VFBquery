"""Tests for graph_builder module — graph construction from connectivity data."""
import pytest

from vfbquery.graph_builder import (
    assign_group,
    build_graph,
    graph_from_query_connectivity,
    graph_from_neuron_neuron,
    graph_from_neuron_region,
    graph_from_downstream_class,
    graph_from_upstream_class,
    _strip_markdown_link,
    _extract_id_from_markdown,
    _node_display_label,
    MAX_NODES,
    MAX_EDGES,
    GRAPH_VERSION,
)


# ---------------------------------------------------------------------------
# assign_group tests
# ---------------------------------------------------------------------------

class TestAssignGroup:
    def test_neurotransmitter_from_tags(self):
        assert assign_group(["cholinergic neuron", "visual system"]) == "cholinergic"

    def test_gabaergic_from_tags(self):
        assert assign_group(["GABAergic neuron"]) == "GABAergic"

    def test_glutamatergic_from_label(self):
        assert assign_group(None, "adult glutamatergic neuron Tm5") == "glutamatergic"

    def test_system_from_tags(self):
        assert assign_group(["visual projection neuron"]) == "visual"

    def test_region_from_label(self):
        assert assign_group(None, "adult medulla neuron Tm1") == "medulla"

    def test_region_mushroom_body(self):
        assert assign_group(None, "mushroom body output neuron MBON-01") == "mushroom body"

    def test_pipe_separated_tags(self):
        assert assign_group("cholinergic|visual system") == "cholinergic"

    def test_unknown_returns_other(self):
        assert assign_group(["something unknown"]) == "other"

    def test_none_tags_none_label(self):
        assert assign_group(None, "") == "other"

    def test_priority_nt_over_system(self):
        """Neurotransmitter should win over system."""
        assert assign_group(["cholinergic", "visual"]) == "cholinergic"


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

class TestMarkdownHelpers:
    def test_strip_markdown_link(self):
        assert _strip_markdown_link("[Tm1](FBbt_001)") == "Tm1"

    def test_strip_plain_text(self):
        assert _strip_markdown_link("plain text") == "plain text"

    def test_strip_empty(self):
        assert _strip_markdown_link("") == ""

    def test_extract_id_from_markdown(self):
        assert _extract_id_from_markdown("[Tm1](FBbt_001)") == "FBbt_001"

    def test_extract_id_plain(self):
        assert _extract_id_from_markdown("FBbt_001") == "FBbt_001"

    def test_node_display_label_prefers_symbol(self):
        assert _node_display_label({"symbol": "Tm1", "label": "adult medulla neuron Tm1"}) == "Tm1"

    def test_node_display_label_falls_back_to_label(self):
        assert _node_display_label({"symbol": "", "label": "some neuron"}) == "some neuron"


# ---------------------------------------------------------------------------
# build_graph tests
# ---------------------------------------------------------------------------

class TestBuildGraph:
    def test_basic_structure(self):
        nodes = [
            {"id": "a", "label": "A", "full_label": "Node A", "group": "other"},
            {"id": "b", "label": "B", "full_label": "Node B", "group": "other"},
        ]
        edges = [{"source": "a", "target": "b", "weight": 10}]
        g = build_graph(nodes, edges, title="Test")

        assert g["type"] == "basic_graph"
        assert g["version"] == GRAPH_VERSION
        assert g["title"] == "Test"
        assert g["directed"] is True
        assert len(g["nodes"]) == 2
        assert len(g["edges"]) == 1
        assert "clipped" not in g

    def test_deduplication(self):
        nodes = [
            {"id": "a", "label": "A", "full_label": "A", "group": "x"},
            {"id": "a", "label": "A", "full_label": "A", "group": "x"},
            {"id": "b", "label": "B", "full_label": "B", "group": "x"},
        ]
        edges = []
        g = build_graph(nodes, edges)
        assert len(g["nodes"]) == 2

    def test_clipping_notification_edges(self):
        nodes = [
            {"id": f"n{i}", "label": f"N{i}", "full_label": f"N{i}", "group": "x"}
            for i in range(5)
        ]
        edges = [
            {"source": "n0", "target": f"n{i % 5}", "weight": i}
            for i in range(MAX_EDGES + 50)
        ]
        g = build_graph(nodes, edges)
        assert "clipped" in g
        assert g["clipped"]["edges_total"] == MAX_EDGES + 50
        assert g["clipped"]["edges_included"] == MAX_EDGES

    def test_clipping_notification_nodes(self):
        nodes = [
            {"id": f"n{i}", "label": f"N{i}", "full_label": f"N{i}", "group": "x"}
            for i in range(MAX_NODES + 20)
        ]
        # Create edges only between first MAX_NODES nodes so some nodes have degree
        edges = [
            {"source": f"n{i}", "target": f"n{i+1}", "weight": 1}
            for i in range(min(MAX_NODES, len(nodes) - 1))
        ]
        g = build_graph(nodes, edges)
        assert "clipped" in g
        assert g["clipped"]["nodes_total"] == MAX_NODES + 20
        assert g["clipped"]["nodes_included"] == MAX_NODES

    def test_no_clipping_when_under_limits(self):
        nodes = [
            {"id": "a", "label": "A", "full_label": "A", "group": "x"},
        ]
        edges = []
        g = build_graph(nodes, edges)
        assert "clipped" not in g

    def test_auto_colour_assignment(self):
        nodes = [
            {"id": "a", "label": "A", "full_label": "A", "group": "cholinergic"},
            {"id": "b", "label": "B", "full_label": "B", "group": "GABAergic"},
        ]
        edges = []
        g = build_graph(nodes, edges)
        colours = {n["id"]: n["color"] for n in g["nodes"]}
        assert colours["a"] != colours["b"]

    def test_directed_false(self):
        g = build_graph([], [], directed=False)
        assert g["directed"] is False


# ---------------------------------------------------------------------------
# Converter tests with mock data (no network)
# ---------------------------------------------------------------------------

def _mock_batch_lookup(monkeypatch):
    """Patch batch_lookup_ids to avoid Neo4j calls."""
    def fake_batch(ids):
        return {
            i: {"label": f"Label for {i}", "symbol": f"sym_{i}", "tags": []}
            for i in ids
        }
    import vfbquery.graph_builder as gb
    monkeypatch.setattr(gb, "batch_lookup_ids", fake_batch)


class TestGraphFromQueryConnectivity:
    def test_class_level(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        connections = [
            {
                "upstream_class": "Kenyon cell",
                "upstream_class_id": "FBbt_001",
                "downstream_class": "MBON-01",
                "downstream_class_id": "FBbt_002",
                "total_upstream_count": 100,
                "connected_upstream_count": 50,
                "percent_connected": 50,
                "pairwise_connections": 200,
                "total_weight": 5000,
                "average_weight": 25,
            },
        ]
        g = graph_from_query_connectivity(connections, group_by_class=True,
                                          upstream_type="Kenyon cell",
                                          downstream_type="MBON-01")
        assert g is not None
        assert g["type"] == "basic_graph"
        assert len(g["nodes"]) == 2
        assert len(g["edges"]) == 1
        assert g["edges"][0]["weight"] == 5000
        assert g["directed"] is True

    def test_per_neuron(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        connections = [
            {
                "upstream_class": "Kenyon cell",
                "upstream_class_id": "FBbt_001",
                "upstream_neuron_id": "VFB_n001",
                "upstream_neuron_name": "KC-alpha 1",
                "weight": 42,
                "downstream_neuron_id": "VFB_n002",
                "downstream_neuron_name": "MBON-01 R",
                "downstream_class": "MBON-01",
                "downstream_class_id": "FBbt_002",
            },
        ]
        g = graph_from_query_connectivity(connections, group_by_class=False)
        assert g is not None
        assert len(g["nodes"]) == 2
        assert g["edges"][0]["weight"] == 42

    def test_empty_connections(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        assert graph_from_query_connectivity([], group_by_class=True) is None


class TestGraphFromNeuronNeuron:
    def test_basic(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        rows = [
            {"id": "VFB_p1", "label": "Partner 1", "outputs": 10, "inputs": 5, "tags": "visual"},
            {"id": "VFB_p2", "label": "Partner 2", "outputs": 0, "inputs": 20, "tags": "olfactory"},
        ]
        g = graph_from_neuron_neuron(rows, "VFB_primary", "My Neuron")
        assert g is not None
        assert len(g["nodes"]) == 3  # primary + 2 partners
        # Partner 1: 1 output + 1 input edge; Partner 2: 1 input edge
        assert len(g["edges"]) == 3
        assert g["directed"] is True

    def test_empty(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        assert graph_from_neuron_neuron([], "VFB_x") is None


class TestGraphFromNeuronRegion:
    def test_basic(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        rows = [
            {"id": "FBbt_r1", "region": "Medulla", "presynaptic_terminals": 100,
             "postsynaptic_terminals": 50, "tags": "optic lobe"},
            {"id": "FBbt_r2", "region": "Lobula", "presynaptic_terminals": 30,
             "postsynaptic_terminals": 10, "tags": "optic lobe"},
        ]
        g = graph_from_neuron_region(rows, "VFB_n1", "Neuron X")
        assert g is not None
        assert g["directed"] is False
        assert len(g["nodes"]) == 3  # primary + 2 regions
        assert len(g["edges"]) == 2
        assert g["edges"][0]["weight"] == 150  # 100 + 50

    def test_empty(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        assert graph_from_neuron_region([], "VFB_x") is None


class TestGraphFromDownstreamClass:
    def test_basic(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        rows = [
            {"id": "FBbt_d1", "downstream_class": "[MBON-01](FBbt_d1)",
             "total_n": 100, "connected_n": 50, "percent_connected": 50,
             "pairwise_connections": 200, "total_weight": 5000, "avg_weight": 25},
            {"id": "FBbt_d2", "downstream_class": "[Tm1](FBbt_d2)",
             "total_n": 80, "connected_n": 40, "percent_connected": 50,
             "pairwise_connections": 100, "total_weight": 2000, "avg_weight": 20},
        ]
        g = graph_from_downstream_class(rows, "FBbt_primary", "KC")
        assert g is not None
        assert g["directed"] is True
        assert len(g["nodes"]) == 3  # primary + 2 downstream
        assert len(g["edges"]) == 2
        # Edges should be primary -> downstream
        assert all(e["source"] == "FBbt_primary" for e in g["edges"])

    def test_empty(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        assert graph_from_downstream_class([], "FBbt_x") is None


class TestGraphFromUpstreamClass:
    def test_basic(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        rows = [
            {"id": "FBbt_u1", "upstream_class": "[PN1](FBbt_u1)",
             "total_n": 60, "connected_n": 30, "percent_connected": 50,
             "pairwise_connections": 150, "total_weight": 3000, "avg_weight": 20},
        ]
        g = graph_from_upstream_class(rows, "FBbt_primary", "KC")
        assert g is not None
        assert g["directed"] is True
        assert len(g["nodes"]) == 2
        # Edges should be upstream -> primary
        assert g["edges"][0]["source"] == "FBbt_u1"
        assert g["edges"][0]["target"] == "FBbt_primary"

    def test_empty(self, monkeypatch):
        _mock_batch_lookup(monkeypatch)
        assert graph_from_upstream_class([], "FBbt_x") is None


# ---------------------------------------------------------------------------
# Integration tests (require network access to Neo4j)
# ---------------------------------------------------------------------------

class TestGraphIntegration:
    @pytest.mark.integration
    def test_query_connectivity_with_graph(self):
        """query_connectivity result can be converted to a graph."""
        from vfbquery.vfb_connectivity import query_connectivity
        result = query_connectivity(
            upstream_type="giant fiber neuron",
            group_by_class=True,
        )
        assert result["count"] > 0
        g = graph_from_query_connectivity(
            result["connections"], group_by_class=True,
            upstream_type="giant fiber neuron",
        )
        assert g is not None
        assert g["type"] == "basic_graph"
        assert len(g["nodes"]) > 0
        assert len(g["edges"]) > 0
        # Check node structure
        for n in g["nodes"]:
            assert "id" in n
            assert "label" in n
            assert "full_label" in n
            assert "group" in n
            assert "color" in n
