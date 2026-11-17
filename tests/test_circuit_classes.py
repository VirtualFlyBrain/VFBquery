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
