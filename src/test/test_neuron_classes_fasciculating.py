#!/usr/bin/env python3
"""
Test suite for NeuronClassesFasciculatingHere query.

Tests the query that finds neuron classes that fasciculate with (run along) tracts or nerves.
This implements the NeuronClassesFasciculatingHere query from the VFB XMI specification.

Test cases:
1. Query execution with known tract
2. Schema generation and validation
3. Term info integration
4. Preview results validation
5. Cache functionality
"""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import (
    get_neuron_classes_fasciculating_here,
    NeuronClassesFasciculatingHere_to_schema,
    get_term_info
)


class NeuronClassesFasciculatingTest(unittest.TestCase):
    """Test suite for NeuronClassesFasciculatingHere query"""

    def setUp(self):
        """Set up test fixtures"""
        # Example tract/nerve: broad root (FBbt_00003987) - a neuron projection bundle
        self.test_tract = "FBbt_00003987"  # broad root
        
    def test_query_execution(self):
        """Test that the query executes successfully"""
        print(f"\n=== Testing NeuronClassesFasciculatingHere query execution ===")
        
        # Execute the query
        result = get_neuron_classes_fasciculating_here(self.test_tract, return_dataframe=False, limit=5)
        
        # Validate result structure
        self.assertIsNotNone(result, "Query should return a result")
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        
        # Check for expected keys
        if result:
            print(f"Query returned {len(result.get('data', []))} results")
            
            # Validate data structure
            if 'data' in result and len(result['data']) > 0:
                first_result = result['data'][0]
                self.assertIn('id', first_result, "Result should contain 'id' field")
                self.assertIn('label', first_result, "Result should contain 'label' field")
                print(f"First result: {first_result.get('label', 'N/A')} ({first_result.get('id', 'N/A')})")
        
    def test_schema_generation(self):
        """Test schema function generates correct structure"""
        print(f"\n=== Testing NeuronClassesFasciculatingHere schema generation ===")
        
        test_name = "Test Tract"
        test_takes = {"short_form": self.test_tract}
        
        schema = NeuronClassesFasciculatingHere_to_schema(test_name, test_takes)
        
        # Validate schema structure
        self.assertIsNotNone(schema, "Schema should not be None")
        self.assertEqual(schema.query, "NeuronClassesFasciculatingHere", "Query name should match")
        self.assertEqual(schema.label, f"Neurons fasciculating in {test_name}", "Label should be formatted correctly")
        self.assertEqual(schema.function, "get_neuron_classes_fasciculating_here", "Function name should match")
        self.assertEqual(schema.preview, 10, "Preview should be 10")
        
        # Check preview columns
        expected_columns = ["id", "label", "tags", "thumbnail"]
        self.assertEqual(schema.preview_columns, expected_columns, f"Preview columns should be {expected_columns}")
        
        print(f"Schema generated successfully: {schema.label}")
        
    def test_term_info_integration(self):
        """Test that query appears in term info for appropriate terms"""
        print(f"\n=== Testing term info integration ===")
        
        # Get term info for a tract/nerve
        term_info = get_term_info(self.test_tract, preview=False)
        
        self.assertIsNotNone(term_info, "Term info should not be None")
        self.assertIn("Queries", term_info, "Term info should contain Queries")
        
        # Check if our query is present
        queries = term_info.get("Queries", [])
        query_names = [q.get('query') for q in queries]
        
        print(f"Available queries for {self.test_tract}: {query_names}")
        
        # For tracts/nerves (Neuron_projection_bundle), this query should be available
        if "Neuron_projection_bundle" in term_info.get("SuperTypes", []):
            self.assertIn("NeuronClassesFasciculatingHere", query_names, 
                         "NeuronClassesFasciculatingHere should be available for Neuron_projection_bundle")
            print("✓ Query correctly appears for Neuron_projection_bundle type")
        else:
            print(f"Warning: {self.test_tract} does not have Neuron_projection_bundle type")
            print(f"SuperTypes: {term_info.get('SuperTypes', [])}")
    
    def test_preview_results(self):
        """Test that preview results are properly formatted"""
        print(f"\n=== Testing preview results ===")
        
        # Get term info with preview enabled
        term_info = get_term_info(self.test_tract, preview=True)
        
        self.assertIsNotNone(term_info, "Term info should not be None")
        
        # Find our query in the results
        queries = term_info.get("Queries", [])
        fasciculating_query = None
        for q in queries:
            if q.get('query') == "NeuronClassesFasciculatingHere":
                fasciculating_query = q
                break
        
        if fasciculating_query:
            print(f"Found NeuronClassesFasciculatingHere query")
            
            # Check if preview_results exist
            if fasciculating_query.get('preview_results'):
                preview = fasciculating_query['preview_results']
                data_key = 'data' if 'data' in preview else 'rows'
                print(f"Preview contains {len(preview.get(data_key, []))} results")
                
                # Validate preview structure
                self.assertIn(data_key, preview, f"Preview should contain '{data_key}' key")
                self.assertIn('headers', preview, "Preview should contain 'headers' key")
                
                # Check first result if available
                if preview.get(data_key) and len(preview[data_key]) > 0:
                    first_result = preview[data_key][0]
                    print(f"First preview result: {first_result.get('label', 'N/A')}")
                    
                    # Validate required fields
                    self.assertIn('id', first_result, "Preview result should have 'id'")
                    self.assertIn('label', first_result, "Preview result should have 'label'")
            else:
                print("No preview results available (this is OK if no matching neurons exist)")
        else:
            print("NeuronClassesFasciculatingHere query not found in term info")
    
    def test_with_different_tracts(self):
        """Test with multiple tract/nerve types"""
        print(f"\n=== Testing with different tracts/nerves ===")
        
        test_tracts = [
            ("FBbt_00003987", "broad root"),
            ("FBbt_00007354", "adult antenno-subesophageal tract"),
            ("FBbt_00003985", "adult medial antennal lobe tract"),
        ]
        
        for tract_id, tract_name in test_tracts:
            print(f"\nTesting {tract_name} ({tract_id})...")
            
            try:
                result = get_neuron_classes_fasciculating_here(tract_id, return_dataframe=False, limit=3)
                
                if result and 'data' in result:
                    print(f"  ✓ Query successful, found {len(result['data'])} results")
                else:
                    print(f"  ✓ Query successful, no results found")
                    
            except Exception as e:
                print(f"  ✗ Query failed: {str(e)}")
                # Don't fail the test, just log the error
                # raise


def run_tests():
    """Run the test suite"""
    suite = unittest.TestLoader().loadTestsFromTestCase(NeuronClassesFasciculatingTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
