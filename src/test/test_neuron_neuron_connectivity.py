#!/usr/bin/env python3
"""
Test suite for NeuronNeuronConnectivityQuery.

Tests the query that finds neurons connected to a given neuron.
This implements the neuron_neuron_connectivity_query from the VFB XMI specification.

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
    get_neuron_neuron_connectivity,
    NeuronNeuronConnectivityQuery_to_schema,
    get_term_info
)

class NeuronNeuronConnectivityTest(unittest.TestCase):
    """Test suite for neuron_neuron_connectivity_query"""

    def setUp(self):
        """Set up test fixtures"""
        # Test neuron: LPC1 (FlyEM-HB:1775513344) [VFB_jrchk00s]
        self.test_neuron = "VFB_jrchk00s"

    def test_query_execution(self):
        """Test that the query executes successfully"""
        print(f"\n=== Testing neuron_neuron_connectivity_query execution ===")
        result = get_neuron_neuron_connectivity(self.test_neuron, return_dataframe=False, limit=5)
        self.assertIsNotNone(result, "Query should return a result")
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        print(f"Query returned {result.get('count', 0)} results")
        if 'data' in result and len(result['data']) > 0:
            first_result = result['data'][0]
            self.assertIn('id', first_result, "Result should contain 'id' field")
            self.assertIn('label', first_result, "Result should contain 'label' field")
            print(f"First result: {first_result.get('label', 'N/A')} ({first_result.get('id', 'N/A')})")
        else:
            print("No connected neurons found (this is OK if none exist)")

    def test_schema_generation(self):
        """Test schema function generates correct structure"""
        print(f"\n=== Testing neuron_neuron_connectivity_query schema generation ===")
        test_name = "LPC1"
        test_takes = {"short_form": self.test_neuron}
        schema = NeuronNeuronConnectivityQuery_to_schema(test_name, test_takes)
        self.assertIsNotNone(schema, "Schema should not be None")
        self.assertEqual(schema.query, "NeuronNeuronConnectivityQuery", "Query name should match")
        self.assertEqual(schema.label, f"Neurons connected to {test_name}", "Label should be formatted correctly")
        self.assertEqual(schema.function, "get_neuron_neuron_connectivity", "Function name should match")
        self.assertEqual(schema.preview, 5, "Preview should be 5")
        expected_columns = ["id", "label", "outputs", "inputs", "tags"]
        self.assertEqual(schema.preview_columns, expected_columns, f"Preview columns should be {expected_columns}")
        print(f"Schema generated successfully: {schema.label}")

    def test_preview_results(self):
        """Test that preview results are properly formatted"""
        print(f"\n=== Testing preview results ===")
        result = get_neuron_neuron_connectivity(self.test_neuron, return_dataframe=False, limit=3)
        self.assertIsNotNone(result, "Query should return a result")
        if 'data' in result and len(result['data']) > 0:
            first_result = result['data'][0]
            self.assertIn('id', first_result, "Preview result should have 'id'")
            self.assertIn('label', first_result, "Preview result should have 'label'")
            print(f"First preview result: {first_result.get('label', 'N/A')}")
        else:
            print("No preview results available (this is OK if no connected neurons exist)")


def run_tests():
    """Run the test suite"""
    suite = unittest.TestLoader().loadTestsFromTestCase(NeuronNeuronConnectivityTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
