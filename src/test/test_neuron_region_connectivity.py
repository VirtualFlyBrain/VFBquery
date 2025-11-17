#!/usr/bin/env python3
"""
Test suite for NeuronRegionConnectivityQuery.

Tests the query that shows connectivity to regions from a given neuron.
This implements the neuron_region_connectivity_query from the VFB XMI specification.

Test cases:
1. Query execution with known neuron
2. Schema generation and validation
3. Term info integration (if applicable)
4. Preview results validation
"""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import (
    get_neuron_region_connectivity,
    NeuronRegionConnectivityQuery_to_schema,
    get_term_info
)

class NeuronRegionConnectivityTest(unittest.TestCase):
    """Test suite for neuron_region_connectivity_query"""

    def setUp(self):
        """Set up test fixtures"""
        # Test neuron: LPC1 (FlyEM-HB:1775513344) [VFB_jrchk00s]
        self.test_neuron = "VFB_jrchk00s"

    def test_query_execution(self):
        """Test that the query executes successfully"""
        print(f"\n=== Testing neuron_region_connectivity_query execution ===")
        result = get_neuron_region_connectivity(self.test_neuron, return_dataframe=False, limit=5)
        self.assertIsNotNone(result, "Query should return a result")
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        print(f"Query returned {result.get('count', 0)} results")
        if 'data' in result and len(result['data']) > 0:
            first_result = result['data'][0]
            self.assertIn('id', first_result, "Result should contain 'id' field")
            self.assertIn('region', first_result, "Result should contain 'region' field")
            self.assertIn('presynaptic_terminals', first_result, "Result should contain 'presynaptic_terminals' field")
            self.assertIn('postsynaptic_terminals', first_result, "Result should contain 'postsynaptic_terminals' field")
            print(f"First result: {first_result.get('region', 'N/A')} ({first_result.get('id', 'N/A')})")
            print(f"  Pre: {first_result.get('presynaptic_terminals', 0)}, Post: {first_result.get('postsynaptic_terminals', 0)}")
        else:
            print("No regions with connectivity found (this is OK if none exist)")

    def test_schema_generation(self):
        """Test that the schema function works correctly"""
        print(f"\n=== Testing NeuronRegionConnectivityQuery schema generation ===")
        
        # Get term info for the test neuron
        term_info = get_term_info(self.test_neuron)
        if term_info:
            neuron_name = term_info.get('Name', self.test_neuron)
        else:
            neuron_name = self.test_neuron
        
        # Generate schema
        schema = NeuronRegionConnectivityQuery_to_schema(neuron_name, self.test_neuron)
        
        # Validate schema structure
        self.assertIsNotNone(schema, "Schema should not be None")
        self.assertEqual(schema.query, "NeuronRegionConnectivityQuery", "Query name should match")
        self.assertEqual(schema.function, "get_neuron_region_connectivity", "Function name should match")
        self.assertEqual(schema.preview, 5, "Preview should show 5 results")
        self.assertIn("region", schema.preview_columns, "Preview should include 'region' column")
        self.assertIn("presynaptic_terminals", schema.preview_columns, "Preview should include 'presynaptic_terminals' column")
        self.assertIn("postsynaptic_terminals", schema.preview_columns, "Preview should include 'postsynaptic_terminals' column")
        
        print(f"Schema label: {schema.label}")
        print(f"Preview columns: {schema.preview_columns}")

    def test_term_info_integration(self):
        """Test that term info lookup works for the test neuron"""
        print(f"\n=== Testing term_info integration ===")
        term_info = get_term_info(self.test_neuron)
        
        self.assertIsNotNone(term_info, "Term info should not be None")
        if term_info:
            # get_term_info returns a dict with 'Name', 'Id', 'Tags', etc.
            self.assertIn('Name', term_info, "Term info should contain 'Name'")
            self.assertIn('Id', term_info, "Term info should contain 'Id'")
            print(f"Neuron name: {term_info.get('Name', 'N/A')}")
            print(f"Neuron tags: {term_info.get('Tags', [])}")
        else:
            print(f"Note: Term info not found for {self.test_neuron} (may not be in SOLR)")

    def test_preview_validation(self):
        """Test that preview results are properly formatted"""
        print(f"\n=== Testing preview results ===")
        result = get_neuron_region_connectivity(self.test_neuron, return_dataframe=False, limit=5)
        
        if 'data' in result and len(result['data']) > 0:
            # Check that all preview columns exist in the results
            expected_columns = ['id', 'region', 'presynaptic_terminals', 'postsynaptic_terminals', 'tags']
            for item in result['data']:
                for col in expected_columns:
                    self.assertIn(col, item, f"Result should contain '{col}' field")
            
            print(f"✓ All {len(result['data'])} results have required preview columns")
            
            # Print sample results
            for i, item in enumerate(result['data'][:3], 1):
                print(f"{i}. {item.get('region', 'N/A')} - Pre:{item.get('presynaptic_terminals', 0)}, Post:{item.get('postsynaptic_terminals', 0)}")
        else:
            print("No preview data available (query returned no results)")


if __name__ == '__main__':
    unittest.main(verbosity=2)
