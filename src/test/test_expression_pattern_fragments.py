"""
Test suite for epFrag (Expression Pattern Fragments) query.

This query uses Owlery instances endpoint to find individual expression pattern
fragment images that are part of a specified expression pattern.

FIXED: Query now works correctly with proper IRI resolution for VFBexp_* IDs.

The three execution tests below were skipped for a period because the Owlery
/instances endpoint exceeded the 300 s per-test budget for epFrag on every
expression pattern tried. That was a server-side limitation, not a code defect,
and it has since been resolved: the reference query now answers in ~4 s.

    http://owl.virtualflybrain.org/kbs/vfb/instances?object=<http://purl.obolibrary.org/obo/BFO_0000050> some <http://virtualflybrain.org/reports/VFBexp_FBtp0022557>

returns 5823 instances well inside the budget, so the skips are removed and
these tests run for real again. If Owlery regresses, the honest response is to
fix Owlery — re-adding a skip here would hide the regression behind a green
check, which is exactly what TESTING.md forbids.
"""

import unittest
import sys
import os
import pandas as pd

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import (
    get_expression_pattern_fragments,
    get_term_info,
    epFrag_to_schema
)


class TestExpressionPatternFragments(unittest.TestCase):
    """Test cases for epFrag query functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # epFrag finds individual fragments (Expression_pattern_fragment) that are
        # part_of a Class Expression_pattern, via the Owlery /instances endpoint.
        self.test_expression_pattern = "VFBexp_FBtp0022557"  # P{VGlut-GAL4.D} expression pattern

    def test_schema_generation(self):
        """Test that the schema function generates correct Query object."""
        schema = epFrag_to_schema("test expression pattern", {"short_form": self.test_expression_pattern})

        self.assertEqual(schema.query, "epFrag")
        self.assertEqual(schema.function, "get_expression_pattern_fragments")
        self.assertIn("test expression pattern", schema.label)
        self.assertEqual(schema.preview, 5)
        self.assertIn("id", schema.preview_columns)
        self.assertIn("thumbnail", schema.preview_columns)

    def test_expression_pattern_fragments_execution(self):
        """Test that expression pattern fragments query executes and returns results."""
        result = get_expression_pattern_fragments(self.test_expression_pattern)

        self.assertIsNotNone(result)
        # Result can be dict or DataFrame
        if isinstance(result, dict):
            self.assertIn('count', result)
            self.assertGreater(result['count'], 0,
                             f"Expected at least 1 result for {self.test_expression_pattern}")
            print(f"\n✓ Query returned {result['count']} expression pattern fragments")
        else:
            # DataFrame
            self.assertIsInstance(result, pd.DataFrame)
            self.assertGreater(len(result), 0,
                             f"Expected at least 1 result for {self.test_expression_pattern}")
            print(f"\n✓ Query returned {len(result)} expression pattern fragments")

    def test_return_dataframe_parameter(self):
        """Test that return_dataframe parameter works correctly."""
        df_result = get_expression_pattern_fragments(self.test_expression_pattern, return_dataframe=True, limit=5)
        dict_result = get_expression_pattern_fragments(self.test_expression_pattern, return_dataframe=False, limit=5)

        self.assertIsInstance(df_result, pd.DataFrame)
        self.assertFalse(df_result.empty, "expression pattern should have fragments")
        self.assertIsInstance(dict_result, dict)
        self.assertTrue(dict_result.get('rows'), "expression pattern should have fragments")

    def test_limit_parameter(self):
        """Test that limit parameter restricts results."""
        limited_result = get_expression_pattern_fragments(self.test_expression_pattern, return_dataframe=True, limit=3)

        self.assertIsInstance(limited_result, pd.DataFrame)
        self.assertFalse(limited_result.empty, "expression pattern should have fragments")
        self.assertLessEqual(len(limited_result), 3)

    def test_term_info_integration(self):
        """epFrag must be offered in term_info for an expression pattern (fast:
        no query execution, preview=False). Covers the epFrag wiring without the
        slow Owlery /instances call."""
        term_info = get_term_info(self.test_expression_pattern, preview=False)

        self.assertIsNotNone(term_info)
        self.assertIn('Expression_pattern', term_info.get('SuperTypes', []),
                      f"{self.test_expression_pattern} should be an Expression_pattern")
        query_names = [q.get('query') for q in term_info.get('Queries', []) if isinstance(q, dict)]
        self.assertIn('epFrag', query_names,
                      "epFrag should be available for expression pattern terms")
        print(f"\n✓ epFrag query found in term_info for {self.test_expression_pattern}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
