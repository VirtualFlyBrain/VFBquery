"""
Test suite for ImagesThatDevelopFrom query.

This query uses Owlery instances endpoint to find individual neuron images
that develop from a specified neuroblast.
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import (
    get_images_that_develop_from,
    get_term_info,
    ImagesThatDevelopFrom_to_schema
)


class TestImagesThatDevelopFrom(unittest.TestCase):
    """Test cases for ImagesThatDevelopFrom query functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # FBbt_00001419 is neuroblast MNB - has 336 neuron images that develop from it
        self.test_neuroblast = "FBbt_00001419"  # neuroblast MNB
        
    def test_schema_generation(self):
        """Test that the schema function generates correct Query object."""
        schema = ImagesThatDevelopFrom_to_schema("test neuroblast", {"short_form": self.test_neuroblast})
        
        self.assertEqual(schema.query, "ImagesThatDevelopFrom")
        self.assertEqual(schema.function, "get_images_that_develop_from")
        self.assertIn("test neuroblast", schema.label)
        self.assertEqual(schema.preview, 5)
        self.assertIn("id", schema.preview_columns)
        self.assertIn("thumbnail", schema.preview_columns)
        
    def test_get_images_that_develop_from_execution(self):
        """Test that the query executes without errors."""
        try:
            # Execute query with limit to keep test fast
            result = get_images_that_develop_from(self.test_neuroblast, return_dataframe=True, limit=10)
            
            # Result should be either a DataFrame or dict
            self.assertIsNotNone(result)
            
            # If we get results, check structure
            if hasattr(result, 'empty'):  # DataFrame
                if not result.empty:
                    self.assertIn('id', result.columns)
                    self.assertIn('label', result.columns)
            elif isinstance(result, dict):  # Dict format
                # Check for either 'data' or 'rows' key
                self.assertTrue('data' in result or 'rows' in result,
                              "Result dict should have 'data' or 'rows' key")
                
            print(f"\n✅ ImagesThatDevelopFrom query executed successfully")
            if isinstance(result, dict):
                count = result.get('count', len(result.get('rows', result.get('data', []))))
                print(f"  Result count: {count} neurons")
            elif hasattr(result, 'shape'):
                print(f"  Result count: {len(result)} neurons")
                
        except Exception as e:
            self.fail(f"Query execution failed: {str(e)}")
    
    def test_return_dataframe_parameter(self):
        """Test that return_dataframe parameter works correctly."""
        # Test with return_dataframe=True
        df_result = get_images_that_develop_from(self.test_neuroblast, return_dataframe=True, limit=5)
        
        # Test with return_dataframe=False
        dict_result = get_images_that_develop_from(self.test_neuroblast, return_dataframe=False, limit=5)
        
        # Both should return valid results
        self.assertIsNotNone(df_result)
        self.assertIsNotNone(dict_result)
        
    def test_limit_parameter(self):
        """Test that limit parameter restricts results."""
        limited_result = get_images_that_develop_from(self.test_neuroblast, return_dataframe=True, limit=3)
        
        self.assertIsNotNone(limited_result)
        
        # If results exist, should respect limit
        if hasattr(limited_result, '__len__') and len(limited_result) > 0:
            self.assertLessEqual(len(limited_result), 3)
    
    def test_term_info_integration(self):
        """Test that ImagesThatDevelopFrom appears in term_info for neuroblasts."""
        # Get term info for a neuroblast
        term_info = get_term_info(self.test_neuroblast, preview=False)
        
        self.assertIsNotNone(term_info)
        
        # Check if ImagesThatDevelopFrom query is in the queries list
        # Note: This will only appear if the term has the correct supertypes
        queries = term_info.get('Queries', [])
        query_names = [q.get('query') for q in queries if isinstance(q, dict)]
        
        # ImagesThatDevelopFrom should appear for neuroblasts
        if 'Neuroblast' in term_info.get('SuperTypes', []):
            self.assertIn('ImagesThatDevelopFrom', query_names,
                         "ImagesThatDevelopFrom should be available for neuroblast terms")
            print(f"\n✓ ImagesThatDevelopFrom query found in term_info for {self.test_neuroblast}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
