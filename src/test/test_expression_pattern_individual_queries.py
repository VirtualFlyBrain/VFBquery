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


def _stock_anchors(term_info):
    """Every short_form a FindStocks query in the menu is anchored on."""
    return sorted(
        q.get("takes", {}).get("default", {}).get("short_form")
        for q in (term_info or {}).get("Queries", []) or []
        if isinstance(q, dict) and q.get("query") == "FindStocks"
    )


class TestExpressionPatternStockQueries(unittest.TestCase):
    """FindStocks is propagated to expression patterns via the driver feature(s)
    reached through the graph (`expresses` / `has_hemidriver`), not by parsing
    the VFBexp_ short_form. The query anchors on the FlyBase feature (FBtp/...),
    since find_stocks cannot route the VFBexp_/VFB_ id itself."""

    EP_CLASS = "VFBexp_FBtp0060056"          # P{GMR40G10-GAL4} expression pattern
    EP_INDIVIDUAL = "VFB_00020530"           # R40G10 image, has its own `expresses` edge
    SPLIT_CLASS = "VFBexp_FBtp0129935FBtp0129968"  # intersectional, two `has_hemidriver`
    SPLIT_INDIVIDUAL = "VFB_00070031"        # split image, no own driver edge

    def _anchors_or_skip(self, short_form):
        ti = get_term_info(short_form, preview=False)
        if not ti:
            self.skipTest("term_info unavailable (no live VFB backend)")
        return _stock_anchors(ti)

    def test_class_stock_query_on_driver_feature(self):
        self.assertEqual(self._anchors_or_skip(self.EP_CLASS), ["FBtp0060056"])

    def test_instance_stock_query_matches_its_driver(self):
        # Regular EP image carries its own `expresses` edge — same feature as the class.
        self.assertEqual(self._anchors_or_skip(self.EP_INDIVIDUAL), ["FBtp0060056"])

    def test_split_class_offers_a_stock_query_per_hemidriver(self):
        self.assertEqual(self._anchors_or_skip(self.SPLIT_CLASS),
                         ["FBtp0129935", "FBtp0129968"])

    def test_split_instance_inherits_hemidriver_stock_queries(self):
        # No own driver edge: features come from the pattern class it instantiates.
        self.assertEqual(self._anchors_or_skip(self.SPLIT_INDIVIDUAL),
                         ["FBtp0129935", "FBtp0129968"])


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
        # ...anchored identically to the class. Most inherited queries run on the
        # class itself; FindStocks is the exception — on both the class and the
        # instance it anchors on the embedded FlyBase feature (find_stocks cannot
        # route the VFBexp_ id), so parity means "same anchor as the class".
        for qid in class_menu:
            self.assertEqual(ind_menu[qid], class_menu[qid],
                             f"{qid} on the instance should anchor as it does on the class")
            if qid != "FindStocks":
                self.assertEqual(class_menu[qid], self.EP_CLASS,
                                 f"{qid} should run on the class {self.EP_CLASS}")

    def test_expected_ep_queries_present(self):
        if not self.ind:
            self.skipTest("term_info unavailable (no live VFB backend)")
        ind_menu = _menu(self.ind)
        # SubclassesOf is intentionally NOT expected: it is gated on has_subClass,
        # and this expression-pattern class is a leaf (no subclasses), so the query
        # would only ever return empty.
        for qid in ("AnatomyExpressedIn", "epFrag", "ListAllAvailableImages"):
            self.assertIn(qid, ind_menu, f"expected {qid} inherited onto the EP instance")
            self.assertEqual(ind_menu[qid], self.EP_CLASS)

    def test_guaranteed_empty_queries_excluded(self):
        """PartsOf / NeuronsPartHere are gated out for expression patterns: they
        match the Anatomy facet but have no class-level parts or overlapping
        neuron classes, so they would only ever return empty (epFrag covers an
        expression pattern's actual parts)."""
        if not self.ind or not self.cls:
            self.skipTest("term_info unavailable (no live VFB backend)")
        for qid in ("PartsOf", "NeuronsPartHere"):
            self.assertNotIn(qid, _menu(self.cls), f"{qid} should be gated out on the EP class")
            self.assertNotIn(qid, _menu(self.ind), f"{qid} should be gated out on the EP instance")

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
