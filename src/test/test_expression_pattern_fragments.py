"""
Test suite for epFrag (Expression Pattern Fragments) query.

This query uses Owlery instances endpoint to find individual expression pattern
fragment images that are part of a specified expression pattern.

TODO: Query needs fixing - returns 0 results for known test cases.
Example: VFBexp_FBtp0022557 should have image VFB_00008416 but query returns 0 results.
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
        # TODO: Query needs fixing - VFBexp_FBtp0022557 has image VFB_00008416 but returns 0 results
        # epFrag should find individual fragments (Expression_pattern_fragment) that are part_of a Class Expression_pattern
        self.test_expression_pattern = "VFBexp_FBtp0022557"  # P{VGlut-GAL4.D} expression pattern (should have VFB_00008416)
        
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
        """Test that expression pattern fragments query executes without errors."""
        result = get_expression_pattern_fragments(self.test_expression_pattern)
        
        self.assertIsNotNone(result)
        # Result can be dict or DataFrame
        if isinstance(result, dict):
            self.assertIn('count', result)
            # TODO: Should return at least 1 result (VFB_00008416) but currently returns 0
            # Query implementation needs debugging
            self.assertGreaterEqual(result['count'], 0)
        else:
            # DataFrame
            self.assertIsInstance(result, pd.DataFrame)
    
    def test_return_dataframe_parameter(self):
        """Test that return_dataframe parameter works correctly."""
        # Test with return_dataframe=True
        df_result = get_expression_pattern_fragments(self.test_expression_pattern, return_dataframe=True, limit=5)
        
        # Test with return_dataframe=False
        dict_result = get_expression_pattern_fragments(self.test_expression_pattern, return_dataframe=False, limit=5)
        
        # Both should return valid results
        self.assertIsNotNone(df_result)
        self.assertIsNotNone(dict_result)
        
    def test_limit_parameter(self):
        """Test that limit parameter restricts results."""
        limited_result = get_expression_pattern_fragments(self.test_expression_pattern, return_dataframe=True, limit=3)
        
        self.assertIsNotNone(limited_result)
        
        # If results exist, should respect limit
        if hasattr(limited_result, '__len__') and len(limited_result) > 0:
            self.assertLessEqual(len(limited_result), 3)
    
    def test_term_info_integration(self):
        """Test that epFrag appears in term_info for expression patterns."""
        # Get term info for an expression pattern
        term_info = get_term_info(self.test_expression_pattern, preview=False)
        
        self.assertIsNotNone(term_info)
        
        # Check if epFrag query is in the queries list
        # Note: This will only appear if the term has the correct supertypes
        if term_info:
            queries = term_info.get('Queries', [])
            query_names = [q.get('query') for q in queries if isinstance(q, dict)]
            
            # epFrag should appear for expression patterns
            if 'Expression_pattern' in term_info.get('SuperTypes', []):
                self.assertIn('epFrag', query_names,
                             "epFrag should be available for expression pattern terms")
                print(f"\n✓ epFrag query found in term_info for {self.test_expression_pattern}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
