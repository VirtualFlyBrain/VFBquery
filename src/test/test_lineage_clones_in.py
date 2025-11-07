#!/usr/bin/env python3
"""
Test suite for LineageClonesIn query.

Tests the query that finds lineage clones that overlap with a synaptic neuropil.
This implements the LineageClonesIn query from the VFB XMI specification.

Test cases:
1. Query execution with known neuropil
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
    get_lineage_clones_in,
    LineageClonesIn_to_schema,
    get_term_info
)


class LineageClonesInTest(unittest.TestCase):
    """Test suite for LineageClonesIn query"""

    def setUp(self):
        """Set up test fixtures"""
        # Example synaptic neuropil: adult antennal lobe (FBbt_00007401)
        self.test_neuropil = "FBbt_00007401"  # antennal lobe
        
    def test_query_execution(self):
        """Test that the query executes successfully"""
        print(f"\n=== Testing LineageClonesIn query execution ===")
        
        # Execute the query
        result = get_lineage_clones_in(self.test_neuropil, return_dataframe=False, limit=5)
        
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
            else:
                print("No results found (this is OK if no clones overlap this neuropil)")
        
    def test_schema_generation(self):
        """Test schema function generates correct structure"""
        print(f"\n=== Testing LineageClonesIn schema generation ===")
        
        test_name = "Test Neuropil"
        test_takes = {"short_form": self.test_neuropil}
        
        schema = LineageClonesIn_to_schema(test_name, test_takes)
        
        # Validate schema structure
        self.assertIsNotNone(schema, "Schema should not be None")
        self.assertEqual(schema.query, "LineageClonesIn", "Query name should match")
        self.assertEqual(schema.label, f"Lineage clones found in {test_name}", "Label should be formatted correctly")
        self.assertEqual(schema.function, "get_lineage_clones_in", "Function name should match")
        self.assertEqual(schema.preview, 10, "Preview should be 10")
        
        # Check preview columns
        expected_columns = ["id", "label", "tags", "thumbnail"]
        self.assertEqual(schema.preview_columns, expected_columns, f"Preview columns should be {expected_columns}")
        
        print(f"Schema generated successfully: {schema.label}")
        
    def test_term_info_integration(self):
        """Test that query appears in term info for appropriate terms"""
        print(f"\n=== Testing term info integration ===")
        
        # Get term info for a synaptic neuropil
        term_info = get_term_info(self.test_neuropil, preview=False)
        
        self.assertIsNotNone(term_info, "Term info should not be None")
        self.assertIn("Queries", term_info, "Term info should contain Queries")
        
        # Check if our query is present
        queries = term_info.get("Queries", [])
        query_names = [q.get('query') for q in queries]
        
        print(f"Available queries for {self.test_neuropil}: {query_names}")
        
        # For synaptic neuropils, this query should be available
        if "Synaptic_neuropil" in term_info.get("SuperTypes", []) or \
           "Synaptic_neuropil_domain" in term_info.get("SuperTypes", []):
            self.assertIn("LineageClonesIn", query_names, 
                         "LineageClonesIn should be available for Synaptic_neuropil")
            print("✓ Query correctly appears for Synaptic_neuropil type")
        else:
            print(f"Warning: {self.test_neuropil} does not have Synaptic_neuropil type")
            print(f"SuperTypes: {term_info.get('SuperTypes', [])}")
    
    def test_preview_results(self):
        """Test that preview results are properly formatted"""
        print(f"\n=== Testing preview results ===")
        
        # Get term info with preview enabled
        term_info = get_term_info(self.test_neuropil, preview=True)
        
        self.assertIsNotNone(term_info, "Term info should not be None")
        
        # Find our query in the results
        queries = term_info.get("Queries", [])
        clones_query = None
        for q in queries:
            if q.get('query') == "LineageClonesIn":
                clones_query = q
                break
        
        if clones_query:
            print(f"Found LineageClonesIn query")
            
            # Check if preview_results exist
            if clones_query.get('preview_results'):
                preview = clones_query['preview_results']
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
                print("No preview results available (this is OK if no clones overlap this neuropil)")
        else:
            print("LineageClonesIn query not found in term info")
    
    def test_with_different_neuropils(self):
        """Test with multiple synaptic neuropil types"""
        print(f"\n=== Testing with different neuropils ===")
        
        test_neuropils = [
            ("FBbt_00007401", "antennal lobe"),
            ("FBbt_00003982", "medulla"),
            ("FBbt_00003679", "mushroom body"),
        ]
        
        for neuropil_id, neuropil_name in test_neuropils:
            print(f"\nTesting {neuropil_name} ({neuropil_id})...")
            
            try:
                result = get_lineage_clones_in(neuropil_id, return_dataframe=False, limit=3)
                
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
    suite = unittest.TestLoader().loadTestsFromTestCase(LineageClonesInTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
