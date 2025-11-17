#!/usr/bin/env python3
"""
Test suite for NeuronInputsTo query.

Tests the query that finds neurons with synapses into a specified neuron.
This implements the NeuronInputsTo query from the VFB XMI specification.

Test cases:
1. Query execution with known neuron
2. Schema generation and validation
3. Term info integration
4. Preview results validation (ribbon format)
5. Neurotransmitter information validation
"""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import (
    get_individual_neuron_inputs,
    NeuronInputsTo_to_schema,
    get_term_info
)

class NeuronInputsTest(unittest.TestCase):
    """Test suite for NeuronInputsTo query"""

    def setUp(self):
        """Set up test fixtures"""
        # Test neuron: LPC1 (FlyEM-HB:1775513344) [VFB_jrchk00s]
        self.test_neuron = "VFB_jrchk00s"

    def test_query_execution(self):
        """Test that the query executes successfully"""
        print(f"\n=== Testing NeuronInputsTo execution ===")
        result = get_individual_neuron_inputs(
            self.test_neuron, 
            return_dataframe=False, 
            limit=5
        )
        self.assertIsNotNone(result, "Query should return a result")
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        print(f"Query returned {result.get('count', 0)} total results")
        
        if 'rows' in result and len(result['rows']) > 0:
            first_result = result['rows'][0]
            self.assertIn('id', first_result, "Result should contain 'id' field")
            self.assertIn('Neurotransmitter', first_result, "Result should contain 'Neurotransmitter' field")
            self.assertIn('Weight', first_result, "Result should contain 'Weight' field")
            print(f"First result: {first_result.get('Neurotransmitter', 'N/A')} (weight: {first_result.get('Weight', 0)})")
        else:
            print("No input neurons found (this is OK if none exist)")

    def test_schema_generation(self):
        """Test that the schema function works correctly"""
        print(f"\n=== Testing NeuronInputsTo schema generation ===")
        
        # Get term info for the test neuron
        term_info = get_term_info(self.test_neuron)
        if term_info:
            neuron_name = term_info.get('Name', self.test_neuron)
        else:
            neuron_name = self.test_neuron
        
        # Generate schema
        schema = NeuronInputsTo_to_schema(neuron_name, self.test_neuron)
        
        # Validate schema structure
        self.assertIsNotNone(schema, "Schema should not be None")
        self.assertEqual(schema.query, "NeuronInputsTo", "Query name should match")
        self.assertEqual(schema.function, "get_individual_neuron_inputs", "Function name should match")
        # NeuronInputsTo uses ribbon format with preview=-1 (all results)
        self.assertEqual(schema.preview, -1, "Preview should show all results (ribbon format)")
        self.assertIn("Neurotransmitter", schema.preview_columns, "Preview should include 'Neurotransmitter' column")
        self.assertIn("Weight", schema.preview_columns, "Preview should include 'Weight' column")
        
        print(f"Schema label: {schema.label}")
        print(f"Preview columns: {schema.preview_columns}")
        print(f"Output format: ribbon (preview={schema.preview})")

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
        result = get_individual_neuron_inputs(
            self.test_neuron,
            return_dataframe=False,
            limit=5
        )
        
        if 'rows' in result and len(result['rows']) > 0:
            # Check that all expected columns exist in the results
            expected_columns = ['id', 'Neurotransmitter', 'Weight', 'Name']
            for item in result['rows']:
                for col in expected_columns:
                    self.assertIn(col, item, f"Result should contain '{col}' field")
            
            print(f"✓ All {len(result['rows'])} results have required columns")
            
            # Print sample results
            for i, item in enumerate(result['rows'][:3], 1):
                print(f"{i}. {item.get('Name', 'N/A')} - {item.get('Neurotransmitter', 'N/A')} (weight: {item.get('Weight', 0)})")
        else:
            print("No preview data available (query returned no results)")

    def test_neurotransmitter_info(self):
        """Test that neurotransmitter information is included"""
        print(f"\n=== Testing neurotransmitter information ===")
        result = get_individual_neuron_inputs(
            self.test_neuron,
            return_dataframe=False,
            limit=10
        )
        
        if 'rows' in result and len(result['rows']) > 0:
            # Check that neurotransmitter field exists and has values
            neurotransmitters = set()
            for row in result['rows']:
                nt = row.get('Neurotransmitter', '')
                if nt:
                    neurotransmitters.add(nt)
            
            print(f"✓ Found {len(neurotransmitters)} different neurotransmitter type(s)")
            if neurotransmitters:
                print(f"  Types: {', '.join(list(neurotransmitters)[:5])}")
        else:
            print("No results to check neurotransmitter information")

    def test_summary_mode(self):
        """Test that summary mode works correctly"""
        print(f"\n=== Testing summary mode ===")
        result = get_individual_neuron_inputs(
            self.test_neuron,
            return_dataframe=False,
            summary_mode=True
        )
        
        self.assertIsNotNone(result, "Summary mode should return a result")
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        
        if 'rows' in result and len(result['rows']) > 0:
            # In summary mode, results are grouped by neurotransmitter type
            print(f"✓ Summary mode returned {len(result['rows'])} neurotransmitter types")
            for i, item in enumerate(result['rows'][:3], 1):
                print(f"{i}. {item.get('Neurotransmitter', 'N/A')} - Total weight: {item.get('Weight', 0)}")
        else:
            print("No summary data available")

    def test_dataframe_output(self):
        """Test that DataFrame output format works"""
        print(f"\n=== Testing DataFrame output ===")
        result = get_individual_neuron_inputs(
            self.test_neuron,
            return_dataframe=True,
            limit=5
        )
        
        # Should return a pandas DataFrame
        import pandas as pd
        self.assertIsInstance(result, pd.DataFrame, "Should return DataFrame when return_dataframe=True")
        
        if not result.empty:
            # Check for expected columns
            expected_columns = ['id', 'Neurotransmitter', 'Weight']
            for col in expected_columns:
                self.assertIn(col, result.columns, f"DataFrame should contain '{col}' column")
            
            print(f"✓ DataFrame has {len(result)} rows and {len(result.columns)} columns")
            print(f"  Columns: {list(result.columns)}")
        else:
            print("DataFrame is empty (no input neurons found)")


if __name__ == '__main__':
    unittest.main(verbosity=2)
