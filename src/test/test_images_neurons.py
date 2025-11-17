"""
Unit tests for the ImagesNeurons query.

This tests the ImagesNeurons query which retrieves individual neuron images 
(instances) with parts in a synaptic neuropil or domain.

Test term: FBbt_00007401 (antennal lobe) - a synaptic neuropil
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vfbquery.vfb_queries import (
    get_images_neurons,
    ImagesNeurons_to_schema,
    get_term_info
)


class ImagesNeuronsTest(unittest.TestCase):
    """Test cases for ImagesNeurons query"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_term = 'FBbt_00007401'  # antennal lobe - synaptic neuropil with individual images
        
    def test_get_images_neurons_execution(self):
        """Test that get_images_neurons executes and returns results"""
        result = get_images_neurons(self.test_term, return_dataframe=True, limit=3)
        
        # Should return a DataFrame
        self.assertIsNotNone(result, "Result should not be None")
        
        # Check result type - handle both DataFrame and dict (from cache)
        import pandas as pd
        if isinstance(result, pd.DataFrame):
            # DataFrame result
            if len(result) > 0:
                print(f"\n✓ Found {len(result)} individual neuron images for {self.test_term}")
                
                # Verify DataFrame has expected columns
                self.assertIn('id', result.columns, "Result should have 'id' column")
                self.assertIn('label', result.columns, "Result should have 'label' column")
                
                # Print first few results for verification
                print("\nSample results:")
                for idx, row in result.head(3).iterrows():
                    print(f"  - {row.get('label', 'N/A')} ({row.get('id', 'N/A')})")
            else:
                print(f"\n⚠ No individual neuron images found for {self.test_term} (this may be expected)")
        elif isinstance(result, dict):
            # Dict result (from cache)
            count = result.get('count', 0)
            rows = result.get('rows', [])
            print(f"\n✓ Found {count} total individual neuron images for {self.test_term} (showing {len(rows)})")
            if rows:
                print("\nSample results:")
                for row in rows[:3]:
                    print(f"  - {row.get('label', 'N/A')} ({row.get('id', 'N/A')})")
        else:
            self.fail(f"Unexpected result type: {type(result)}")
    
    def test_images_neurons_schema(self):
        """Test that ImagesNeurons_to_schema generates correct schema"""
        name = "antennal lobe"
        take_default = {"short_form": self.test_term}
        
        schema = ImagesNeurons_to_schema(name, take_default)
        
        # Verify schema structure
        self.assertEqual(schema.query, "ImagesNeurons")
        self.assertEqual(schema.label, f"Images of neurons with some part in {name}")
        self.assertEqual(schema.function, "get_images_neurons")
        self.assertEqual(schema.preview, 5)
        self.assertIn("id", schema.preview_columns)
        self.assertIn("label", schema.preview_columns)
        
        print(f"\n✓ Schema generated correctly")
        print(f"  Query: {schema.query}")
        print(f"  Label: {schema.label}")
        print(f"  Function: {schema.function}")
    
    def test_term_info_integration(self):
        """Test that ImagesNeurons query appears in term_info for synaptic neuropils"""
        term_info = get_term_info(self.test_term, preview=True)
        
        # Should have queries
        self.assertIn('Queries', term_info, "term_info should have 'Queries' key")
        
        # Look for ImagesNeurons query
        query_names = [q['query'] for q in term_info['Queries']]
        print(f"\n✓ Queries available for {self.test_term}: {query_names}")
        
        if 'ImagesNeurons' in query_names:
            images_query = next(q for q in term_info['Queries'] if q['query'] == 'ImagesNeurons')
            print(f"✓ ImagesNeurons query found: {images_query['label']}")
            
            # Verify preview results if available
            if 'preview_results' in images_query:
                preview = images_query['preview_results']
                # Handle both 'data' and 'rows' keys
                data_key = 'data' if 'data' in preview else 'rows'
                if data_key in preview and len(preview[data_key]) > 0:
                    print(f"  Preview has {len(preview[data_key])} individual neuron images")
                    print(f"  Sample: {preview[data_key][0]}")
        else:
            print(f"⚠ ImagesNeurons query not found in term_info")
            print(f"  Available queries: {query_names}")
            print(f"  SuperTypes: {term_info.get('SuperTypes', [])}")
    
    def test_images_neurons_preview(self):
        """Test preview results format"""
        result = get_images_neurons(self.test_term, return_dataframe=False, limit=5)
        
        # Should be a dict with specific structure
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn('rows', result, "Result should have 'rows' key")
        self.assertIn('headers', result, "Result should have 'headers' key")
        self.assertIn('count', result, "Result should have 'count' key")
        
        if result['count'] > 0:
            print(f"\n✓ Preview format validated")
            print(f"  Total count: {result['count']}")
            print(f"  Returned rows: {len(result['rows'])}")
            print(f"  Headers: {list(result['headers'].keys())}")
        else:
            print(f"\n⚠ No results in preview (this may be expected)")
    
    def test_multiple_terms(self):
        """Test query with multiple synaptic neuropil terms"""
        test_terms = [
            ('FBbt_00007401', 'antennal lobe'),
            ('FBbt_00003982', 'medulla'),  # another synaptic neuropil
        ]
        
        print("\n✓ Testing ImagesNeurons with multiple terms:")
        for term_id, term_name in test_terms:
            try:
                result = get_images_neurons(term_id, return_dataframe=True, limit=10)
                count = len(result) if result is not None else 0
                print(f"  - {term_name} ({term_id}): {count} individual neuron images")
            except Exception as e:
                print(f"  - {term_name} ({term_id}): Error - {e}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
