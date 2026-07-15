"""
Test suite for class->instance query inheritance in term_info.

The legacy term-info builder (uk.ac.vfb.geppetto VFBProcessTermInfoCachedJson,
gate ~line 1757) brought a class's full query menu down onto Individuals of a
fixed set of anatomical / expression-pattern types, running each query on the
parent class (QueryChecker.check(query, classVariable)). The VFBquery port had
replaced that type-based gate with a Technique == "computer graphic" heuristic,
which only caught painted domains and dropped confocal instances such as
expression-pattern images (R40G10, VFB_00020530) and splits (VFB_00069525).

The reinstated behaviour: an Individual of one of the inherited types shows
exactly the queries its parent class shows, anchored on the class. These tests
assert that parity: instance inherited-menu ⊇ class menu, and every inherited
query runs on the class rather than the individual.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import get_term_info


def _menu(term_info):
    """query_id -> anchored short_form for each query in a term_info menu."""
    out = {}
    for q in (term_info or {}).get("Queries", []) or []:
        if isinstance(q, dict):
            out[q.get("query")] = q.get("takes", {}).get("default", {}).get("short_form")
    return out


class TestExpressionPatternIndividualQueries(unittest.TestCase):
    """R40G10 expression-pattern image inherits its class's menu."""

    EP_INDIVIDUAL = "VFB_00020530"   # R40G10 in the adult brain (confocal)
    EP_CLASS = "VFBexp_FBtp0060056"  # P{GMR40G10-GAL4} expression pattern

    @classmethod
    def setUpClass(cls):
        cls.ind = get_term_info(cls.EP_INDIVIDUAL, preview=False)
        cls.cls = get_term_info(cls.EP_CLASS, preview=False)

    def test_is_expression_pattern_individual(self):
        if not self.ind:
            self.skipTest("term_info unavailable (no live VFB backend)")
        self.assertTrue(self.ind.get("IsIndividual"))
        self.assertIn("Expression_pattern", self.ind.get("SuperTypes", []))

    def test_instance_menu_includes_everything_the_class_offers(self):
        if not self.ind or not self.cls:
            self.skipTest("term_info unavailable (no live VFB backend)")
        class_menu = _menu(self.cls)
        ind_menu = _menu(self.ind)
        # Queries the class offers must all appear on the instance...
        missing = set(class_menu) - set(ind_menu)
        self.assertFalse(missing, f"instance is missing class queries: {sorted(missing)}")
        # ...and each such inherited query must run on the class, not the instance.
        for qid in class_menu:
            self.assertEqual(ind_menu[qid], self.EP_CLASS,
                             f"{qid} on the instance should anchor on {self.EP_CLASS}")

    def test_expected_ep_queries_present(self):
        if not self.ind:
            self.skipTest("term_info unavailable (no live VFB backend)")
        ind_menu = _menu(self.ind)
        # SubclassesOf is intentionally NOT expected: it is gated on has_subClass,
        # and this expression-pattern class is a leaf (no subclasses), so the query
        # would only ever return empty.
        for qid in ("AnatomyExpressedIn", "epFrag", "ListAllAvailableImages",
                    "NeuronsPartHere", "PartsOf"):
            self.assertIn(qid, ind_menu, f"expected {qid} inherited onto the EP instance")
            self.assertEqual(ind_menu[qid], self.EP_CLASS)

    def test_no_query_is_anchored_on_the_individual(self):
        """Inherited class queries run on the class; none should target the VFB_ instance."""
        for qid, anchor in _menu(self.ind).items():
            self.assertNotEqual(anchor, self.EP_INDIVIDUAL,
                                f"{qid} should not run on the individual")


class TestSplitIndividualQueries(unittest.TestCase):
    """A confocal split-GAL4 image was also missed by the technique gate."""

    SPLIT_INDIVIDUAL = "VFB_00069525"  # JRC_SS00810 in the Adult Brain

    def test_split_individual_inherits_ep_queries(self):
        ind = get_term_info(self.SPLIT_INDIVIDUAL, preview=False)
        if not ind:
            self.skipTest("term_info unavailable (no live VFB backend)")
        self.assertTrue(ind.get("IsIndividual"))
        self.assertIn("Split", ind.get("SuperTypes", []))
        ind_menu = _menu(ind)
        # AnatomyExpressedIn is the defining expression-pattern query; it must be
        # present and anchored on a class (VFBexp*), not the VFB_ individual.
        self.assertIn("AnatomyExpressedIn", ind_menu)
        self.assertNotEqual(ind_menu["AnatomyExpressedIn"], self.SPLIT_INDIVIDUAL)
        self.assertTrue(str(ind_menu["AnatomyExpressedIn"]).startswith("VFBexp"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
