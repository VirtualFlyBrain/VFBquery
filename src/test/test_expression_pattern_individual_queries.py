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
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import get_term_info, term_info_parse_object


class _FixtureResults:
    """Minimal SOLR-result stand-in wrapping a committed term_info fixture."""
    def __init__(self, docs):
        self.docs = docs
        self.hits = len(docs)


def _fixture_term_info(name):
    """Parse a committed complete term_info fixture through the render code, so the
    FindStocks generation can be tested without live SOLR content. See TESTING.md
    'Fixture vs live (data_health)'."""
    path = os.path.join(os.path.dirname(__file__),
                        "fixtures", "term_info", name + ".json")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    sf = doc["term"]["core"]["short_form"]
    return term_info_parse_object(_FixtureResults([{"term_info": [json.dumps(doc)]}]), sf)


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
        """Render code (PR-blocking): FindStocks anchors on the EP class's own
        `expresses` feature, from a complete fixture. See TESTING.md
        'Fixture vs live (data_health)'."""
        self.assertEqual(
            _stock_anchors(_fixture_term_info("ep_class_VFBexp_FBtp0060056")),
            ["FBtp0060056"])

    @pytest.mark.data_health
    def test_class_stock_query_on_driver_feature_live(self):
        """Data-health (scheduled only): the same against live SOLR."""
        self.assertEqual(self._anchors_or_skip(self.EP_CLASS), ["FBtp0060056"])

    def test_instance_stock_query_matches_its_driver(self):
        # Regular EP image carries its own `expresses` edge — same feature as the class.
        """Render code (PR-blocking): the EP image's own `expresses` edge yields
        the same FindStocks feature as its class. See TESTING.md."""
        self.assertEqual(
            _stock_anchors(_fixture_term_info("ep_individual_VFB_00020530")),
            ["FBtp0060056"])

    @pytest.mark.data_health
    def test_instance_stock_query_matches_its_driver_live(self):
        """Data-health (scheduled only): the same against live SOLR."""
        self.assertEqual(self._anchors_or_skip(self.EP_INDIVIDUAL), ["FBtp0060056"])

    SPLIT_COMBO = "FBco0001890"              # FlyBase combination of the two

    def _split_fixture_anchors(self, combos):
        """Parse the split fixture with the FlyBase combination lookup stubbed,
        keeping the render test hermetic (no Chado)."""
        import vfbquery.flybase_stocks as fbs
        real = fbs.combinations_for_constructs
        fbs.combinations_for_constructs = combos
        try:
            return _stock_anchors(
                _fixture_term_info("split_VFBexp_FBtp0129935FBtp0129968"))
        finally:
            fbs.combinations_for_constructs = real

    def test_split_class_offers_one_stock_query_on_its_combination(self):
        """Render code (PR-blocking): a split's two ``has_hemidriver`` constructs
        collapse onto the FlyBase combination they build, so the menu offers a
        single FindStocks (exact combination first, hemidriver fallback) rather
        than one per half. See TESTING.md 'Fixture vs live (data_health)'."""
        seen = []

        def combos(construct_ids):
            seen.append(sorted(construct_ids))
            return [self.SPLIT_COMBO]

        self.assertEqual(self._split_fixture_anchors(combos), [self.SPLIT_COMBO])
        self.assertEqual(seen, [["FBtp0129935", "FBtp0129968"]])

    def test_split_combination_stock_label_names_the_combination(self):
        """Render code (PR-blocking): the label keeps its usual wording and names
        the FBco in brackets, where it used to name each FBtp."""
        import vfbquery.flybase_stocks as fbs
        real = fbs.combinations_for_constructs
        fbs.combinations_for_constructs = lambda ids: [self.SPLIT_COMBO]
        try:
            ti = _fixture_term_info("split_VFBexp_FBtp0129935FBtp0129968")
        finally:
            fbs.combinations_for_constructs = real
        labels = [q["label"] for q in ti["Queries"] if q.get("query") == "FindStocks"]
        self.assertEqual(labels, [f"Find fly stocks for {ti['Name']} ({self.SPLIT_COMBO})"])

    def test_split_without_curated_combination_keeps_a_query_per_hemidriver(self):
        """Render code (PR-blocking): no FlyBase combination -> per-hemidriver queries."""
        self.assertEqual(self._split_fixture_anchors(lambda ids: []),
                         ["FBtp0129935", "FBtp0129968"])

    def test_split_combination_lookup_failure_keeps_a_query_per_hemidriver(self):
        """Render code (PR-blocking): a Chado failure must not drop the stock queries."""
        def combos(ids):
            raise RuntimeError("chado down")
        self.assertEqual(self._split_fixture_anchors(combos),
                         ["FBtp0129935", "FBtp0129968"])

    @pytest.mark.data_health
    def test_split_class_offers_one_stock_query_on_its_combination_live(self):
        """Data-health (scheduled only): the same against the live SOLR document, so an incomplete
        production split document (no ``Expression_pattern`` type / no
        ``has_hemidriver``) is caught. Deselected on PRs via ``-m 'not data_health'``."""
        self.assertEqual(self._anchors_or_skip(self.SPLIT_CLASS), [self.SPLIT_COMBO])

    @pytest.mark.data_health
    def test_split_instance_inherits_combination_stock_query(self):
        # No own driver edge: the features come from the pattern class it
        # instantiates, which `_stock_features_via_parent_pattern` fetches with a
        # LIVE `_load_term_info(parent)` call. A fixture for the individual alone
        # cannot make this hermetic (the parent lookup still hits SOLR), so this
        # stays a live (data_health) test rather than a PR-blocking fixture one.
        self.assertEqual(self._anchors_or_skip(self.SPLIT_INDIVIDUAL), [self.SPLIT_COMBO])


class TestExpressionPatternIndividualQueries(unittest.TestCase):
    """R40G10 expression-pattern image inherits its class's menu."""

    EP_INDIVIDUAL = "VFB_00020530"   # R40G10 in the adult brain (confocal)
    EP_CLASS = "VFBexp_FBtp0060056"  # P{GMR40G10-GAL4} expression pattern
    IND_FIXTURE = "ep_individual_VFB_00020530"
    CLS_FIXTURE = "ep_class_VFBexp_FBtp0060056"

    @classmethod
    def setUpClass(cls):
        # Fixture-backed (PR-blocking, deterministic): every assertion below reads
        # only the parsed term_info menu, so these run against committed fixtures
        # rather than live SOLR. The live docs are re-checked on the schedule by
        # test_menus_live (data_health). See TESTING.md 'Fixture vs live'.
        cls.ind = _fixture_term_info(cls.IND_FIXTURE)
        cls.cls = _fixture_term_info(cls.CLS_FIXTURE)

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

    @pytest.mark.data_health
    def test_menus_live(self):
        """Data-health (scheduled only): the live EP class/instance documents still
        produce the inherited menu the fixtures encode — catches drift in the
        built vfb_json. Deselected on PRs via ``-m 'not data_health'``."""
        ind = get_term_info(self.EP_INDIVIDUAL, preview=False)
        cls = get_term_info(self.EP_CLASS, preview=False)
        self.assertTrue(ind and cls, "live EP term_info unavailable")
        class_menu, ind_menu = _menu(cls), _menu(ind)
        self.assertFalse(set(class_menu) - set(ind_menu),
                         "instance is missing class queries (live)")
        for qid in ("AnatomyExpressedIn", "epFrag", "ListAllAvailableImages"):
            self.assertIn(qid, ind_menu, f"expected {qid} on the live EP instance")


class TestSplitIndividualQueries(unittest.TestCase):
    """A confocal split-GAL4 image was also missed by the technique gate."""

    SPLIT_INDIVIDUAL = "VFB_00069525"  # JRC_SS00810 in the Adult Brain

    SPLIT_FIXTURE = "split_individual_VFB_00069525"

    def test_split_individual_inherits_ep_queries(self):
        """Render code (PR-blocking): the split image's inherited menu, from a
        complete fixture. See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_split_individual_inherits_ep_queries(
            _fixture_term_info(self.SPLIT_FIXTURE))

    @pytest.mark.data_health
    def test_split_individual_inherits_ep_queries_live(self):
        """Data-health (scheduled only): the same against live SOLR."""
        ind = get_term_info(self.SPLIT_INDIVIDUAL, preview=False)
        if not ind:
            self.skipTest("term_info unavailable (no live VFB backend)")
        self._check_split_individual_inherits_ep_queries(ind)

    def _check_split_individual_inherits_ep_queries(self, ind):
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
