"""
Unit tests for publication and transgene queries.

This tests:
1. get_terms_for_pub - Terms referencing a publication
2. get_transgene_expression_here - Complex transgene expression query

Test terms:
- DOI_10_7554_eLife_04577 - Example publication
- FBbt_00003748 - mushroom body (for transgene expression)
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vfbquery.vfb_queries import (
    get_terms_for_pub,
    get_transgene_expression_here,
    TermsForPub_to_schema,
    TransgeneExpressionHere_to_schema
)


class PublicationTransgeneQueriesTest(unittest.TestCase):
    """Test cases for publication and transgene queries"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pub_term = 'DOI_10_7554_eLife_04577'  # Example publication
        self.anatomy_term = 'FBbt_00003748'  # mushroom body
        
    def test_get_terms_for_pub(self):
        """Test get_terms_for_pub query"""
        result = get_terms_for_pub(self.pub_term, return_dataframe=True, limit=10)
        self.assertIsNotNone(result, "Result should not be None")
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} terms for publication {self.pub_term}")
            self.assertIn('id', result.columns)
            self.assertIn('label', result.columns)
            
    def test_get_terms_for_pub_formatted(self):
        """Test get_terms_for_pub with formatted output"""
        result = get_terms_for_pub(self.pub_term, return_dataframe=False, limit=5)
        self.assertIsNotNone(result)
        
        if isinstance(result, dict):
            self.assertIn('headers', result)
            self.assertIn('rows', result)
            
    def test_get_transgene_expression_here(self):
        """Test get_transgene_expression_here query"""
        result = get_transgene_expression_here(self.anatomy_term, return_dataframe=True, limit=10)
        self.assertIsNotNone(result, "Result should not be None")
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} transgene expressions in {self.anatomy_term}")
            self.assertIn('id', result.columns)
            
    def test_get_transgene_expression_formatted(self):
        """Test get_transgene_expression_here with formatted output"""
        result = get_transgene_expression_here(self.anatomy_term, return_dataframe=False, limit=5)
        self.assertIsNotNone(result)
        
        if isinstance(result, dict):
            self.assertIn('headers', result)
            self.assertIn('rows', result)
            
    def test_schema_functions_exist(self):
        """Test that publication/transgene schema functions exist and are callable"""
        schema_functions = [
            TermsForPub_to_schema,
            TransgeneExpressionHere_to_schema
        ]
        
        for func in schema_functions:
            self.assertTrue(callable(func), f"{func.__name__} should be callable")
            
    def test_limit_parameter(self):
        """Test that limit parameter works correctly"""
        result = get_terms_for_pub(self.pub_term, return_dataframe=True, limit=3)
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            self.assertLessEqual(len(result), 3, "Result should respect limit parameter")
            
    def test_empty_results_handling(self):
        """Test that queries handle empty results gracefully"""
        # Use a term unlikely to have references
        result = get_terms_for_pub('INVALID_PUB_123', return_dataframe=True, limit=5)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
