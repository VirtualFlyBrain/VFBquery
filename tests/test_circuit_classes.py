"""Class assignment and class-edge weights for class-level circuit paths (#114).

Offline: these exercise the pure functions in `vfbquery.vfb_circuit_classes`
on small hand-made datasets. Each case is a situation measured in the real
connectomes (see the module docstring and connectome-curation#1/#2).
"""
import pytest

from vfbquery import vfb_circuit_classes as vc
from vfbquery.circuit_axis_classes import AXIS_CLASSES

# A tiny hierarchy: KC > KCab > KCab-p; MBON; a lineage class and a
# transmitter class that cut across cell types.
ANC = {
    "KC": set(),
    "KCab": {"KC"},
    "KCab-p": {"KCab", "KC"},
    "MBON": set(),
    "MBON01": {"MBON"},
    "LIN": set(),
    "CHOL": set(),
    "T1": set(), "T2": set(), "T3": set(),
}
AXIS = {"LIN": "a lineage", "CHOL": "a transmitter"}


def assign(types, axis=AXIS):
    return vc.assign_classes(types, ANC, axis)


def test_single_leaf_type_is_assigned():
    a, st, leaves = assign({"n1": ["KCab-p"], "n2": ["MBON01"]})
    assert a == {"n1": "KCab-p", "n2": "MBON01"}
    assert leaves == {"KCab-p", "MBON01"}


def test_parent_class_with_subtyped_siblings_is_left_out():
    # FlyWire: KCab neurons beside KCab-p neurons. The KCab neurons get no
    # class, rather than a KCab node that holds only the remainder.
    a, st, leaves = assign({"n1": ["KCab-p"], "n2": ["KCab"]})
    assert a == {"n1": "KCab-p"}
    assert st["n2"] == (vc.NO_LEAF, ["KCab"])
    assert "KCab" not in leaves


def test_parent_class_is_a_leaf_when_nothing_below_it_is_used():
    a, _, _ = assign({"n1": ["KCab"], "n2": ["KCab"]})
    assert a == {"n1": "KCab", "n2": "KCab"}


def test_ancestor_typed_on_the_same_neuron_is_ignored():
    a, _, _ = assign({"n1": ["KC", "KCab-p"]})
    assert a == {"n1": "KCab-p"}


def test_axis_classes_do_not_compete_with_the_cell_type():
    # FlyWire/male CNS: "adult MBp1 lineage neuron + KCg-m" was the commonest
    # two-leaf pattern before axis classes were dropped.
    types = {"n1": ["LIN", "KCab-p"], "n2": ["CHOL", "MBON01"]}
    a, _, _ = assign(types)
    assert a == {"n1": "KCab-p", "n2": "MBON01"}
    a, st, _ = assign(types, axis={})
    assert st["n1"][0] == vc.MULTI_LEAF


def test_only_the_axis_class_itself_is_dropped_not_its_descendants():
    # Most cell types sit under a transmitter class in FBbt.
    anc = dict(ANC, KCab={"KC", "CHOL"}, **{"KCab-p": {"KCab", "KC", "CHOL"}})
    a, _, _ = vc.assign_classes({"n1": ["KCab-p"]}, anc, AXIS)
    assert a == {"n1": "KCab-p"}


def test_two_leaf_types_are_reported_not_tie_broken():
    # Male CNS: motor neurons typed to all three segment versions.
    a, st, _ = assign({"n1": ["T1", "T2", "T3"]})
    assert a == {}
    assert st["n1"] == (vc.MULTI_LEAF, ["T1", "T2", "T3"])


def test_status_of_axis_only_and_untyped_neurons():
    _, st, _ = assign({"n1": ["CHOL"], "n2": []})
    assert st["n1"] == (vc.ONLY_AXIS, ["CHOL"])
    assert st["n2"] == (vc.UNTYPED, [])


# ---------------------------------------------------------------------------
# Class edges
# ---------------------------------------------------------------------------

def test_class_inprop_sums_over_a_and_averages_over_all_of_b():
    assignment = {"a1": "A", "a2": "A", "b1": "B", "b2": "B"}
    up = {"b1": 100, "b2": 50}
    down = {"a1": 10, "a2": 40}
    # b2 gets nothing from A but still counts in the average.
    edges = [("a1", "b1", 6), ("a2", "b1", 4)]
    e = vc.aggregate_class_edges(edges, assignment, up, down)[("A", "B")]
    assert e["synapses"] == 10 and e["pairs"] == 2
    assert e["inprop_in"] == pytest.approx((6 / 100 + 4 / 100) / 2)
    assert e["inprop_out"] == pytest.approx((6 / 10 + 4 / 40) / 2)


def test_one_neuron_per_class_reduces_to_neuron_inprop():
    e = vc.aggregate_class_edges([("a", "b", 7)], {"a": "A", "b": "B"},
                                 {"b": 70}, {"a": 14})[("A", "B")]
    assert e["inprop_in"] == pytest.approx(0.1)
    assert e["inprop_out"] == pytest.approx(0.5)


def test_edges_to_unassigned_neurons_are_dropped():
    e = vc.aggregate_class_edges([("a", "x", 5), ("a", "b", 5)],
                                 {"a": "A", "b": "B"}, {"b": 10, "x": 10}, {"a": 10})
    assert list(e) == [("A", "B")]


def test_no_output_proportion_when_a_member_lacks_an_output_total():
    # CATMAID datasets have no total_downstream; a mean over the members that
    # happen to have one would be a different quantity.
    assignment = {"a1": "A", "a2": "A", "b": "B"}
    e = vc.aggregate_class_edges([("a1", "b", 5)], assignment, {"b": 10}, {"a1": 10})
    assert e[("A", "B")]["inprop_out"] is None


# ---------------------------------------------------------------------------
# The axis list
# ---------------------------------------------------------------------------

def test_axis_list_labels_match_the_review_pattern():
    # Every listed class should look like an axis class; a mismatch means a
    # cell type was listed by mistake (or the pattern needs widening).
    odd = [l for l in AXIS_CLASSES.values() if not vc.AXIS_LABEL_PATTERN.search(l)]
    assert odd == []


@pytest.mark.parametrize("label", [
    "adult fruitless aSP10 neuron",
    "dopaminergic PAM neuron 1",
    "adult serotonergic T1 neuron",
    "adult fan-shaped body layer 5 neuron of DM6 lineage",
    "femoral pretarsal depressor muscle secondary motor neuron",
    "adult doublesex pC1a (female) neuron",
])
def test_cell_types_are_not_flagged_as_axis_candidates(label):
    assert not vc.AXIS_LABEL_PATTERN.search(label)


# ---------------------------------------------------------------------------
# Output files and manifest
# ---------------------------------------------------------------------------

def _write_tiny(folder):
    types = {"a1": ["KCab-p"], "a2": ["KCab-p"], "b1": ["MBON01"],
             "x": ["KCab"], "y": ["T1", "T2"]}
    up = {"b1": 20, "a2": 10}
    down = {"a1": 10, "a2": 5}
    labels = {"KCab-p": "KCab-p label", "MBON01": "MBON01 label", "KCab": "KCab label",
              "T1": "T1 label", "T2": "T2 label"}
    edges = [("a1", "b1", 4), ("a2", "b1", 6), ("x", "b1", 2), ("a1", "elsewhere", 9)]
    meta = {"connectome": "tiny", "run": "run-1", "built": "2026-11-18T00:00:00Z"}
    return vc.write_site(str(folder / "tiny"), meta, types, up, down, labels,
                         {"MBON01": "MBON01"}, ANC, iter(edges), log=lambda *_: None)


def test_site_files_follow_the_agreed_layout(tmp_path):
    _, entry = _write_tiny(tmp_path)
    assert sorted(p.name for p in (tmp_path / "tiny").iterdir()) == sorted(
        list(vc.TABLES) + ["summary.md"])
    assert set(entry["files"]) == {f"tiny/{n}" for n in vc.TABLES}

    meta, header, rows = vc.read_table(str(tmp_path / "tiny" / "neuron_edges.tsv.gz"))
    assert "run: run-1" in meta and "connectome: tiny" in meta
    assert header == ["source", "target", "synapses", "inprop_in", "inprop_out"]
    # The edge to a neuron outside the dataset is dropped; unassigned x is kept.
    assert rows == [["a1", "b1", "4", "0.2", "0.4"], ["a2", "b1", "6", "0.3", "1.2"],
                    ["x", "b1", "2", "0.1", ""]]
    assert entry["neuron_edges"] == 3

    _, _, rows = vc.read_table(str(tmp_path / "tiny" / "class_edges.tsv.gz"))
    assert rows == [["KCab-p", "MBON01", "10", "2", "0.5", "0.8"]]
    _, _, rows = vc.read_table(str(tmp_path / "tiny" / "neuron_classes.tsv.gz"))
    assert rows == [["a1", "KCab-p"], ["a2", "KCab-p"], ["b1", "MBON01"]]
    _, _, rows = vc.read_table(str(tmp_path / "tiny" / "classes.tsv.gz"))
    assert rows == [["KCab-p", "KCab-p label", "", "2"], ["MBON01", "MBON01 label", "MBON01", "1"]]
    _, _, rows = vc.read_table(str(tmp_path / "tiny" / "report.tsv"))
    assert rows == [["x", vc.NO_LEAF, "KCab", "KCab label"],
                    ["y", vc.MULTI_LEAF, "T1|T2", "T1 label|T2 label"]]


def test_same_content_gives_the_same_checksums(tmp_path):
    _, e1 = _write_tiny(tmp_path / "one")
    _, e2 = _write_tiny(tmp_path / "two")
    assert e1["files"] == e2["files"]


def test_manifest_lists_files_with_rows_and_checksums(tmp_path):
    import hashlib
    import json
    _, entry = _write_tiny(tmp_path)
    vc.write_manifest(str(tmp_path), "run-1", {"built": "x"}, {"tiny": entry})
    m = json.loads((tmp_path / vc.MANIFEST).read_text())
    assert m["run"] == "run-1" and m["format"] == vc.FORMAT_VERSION
    assert not (tmp_path / (vc.MANIFEST + ".tmp")).exists()
    for path, f in m["datasets"]["tiny"]["files"].items():
        data = (tmp_path / path).read_bytes()
        assert hashlib.sha256(data).hexdigest() == f["sha256"]
    assert m["datasets"]["tiny"]["files"]["tiny/class_edges.tsv.gz"]["rows"] == 1
