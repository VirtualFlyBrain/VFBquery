#!/usr/bin/env python3
"""
Test suite for SimilarMorphologyTo query.

Tests the query that finds neurons with similar morphology using NBLAST scoring.
This implements the SimilarMorphologyTo query from the VFB XMI specification.

Test cases:
1. Query execution with known neuron with NBLAST data
2. Schema generation and validation
3. Term info integration
4. Preview results validation
5. Score ordering validation
"""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import (
    get_similar_neurons,
    SimilarMorphologyTo_to_schema,
    get_term_info
)

class SimilarMorphologyTest(unittest.TestCase):
    """Test suite for SimilarMorphologyTo query"""

    def setUp(self):
        """Set up test fixtures"""
        # Test neuron: LPC1 (FlyEM-HB:1775513344) [VFB_jrchk00s] - has both NBLAST and connectivity data
        self.test_neuron = "VFB_jrchk00s"
        self.similarity_score = "NBLAST_score"

    def test_query_execution(self):
        """Test that the query executes successfully"""
        print(f"\n=== Testing SimilarMorphologyTo execution ===")
        result = get_similar_neurons(
            self.test_neuron, 
            similarity_score=self.similarity_score,
            return_dataframe=False, 
            limit=5
        )
        self.assertIsNotNone(result, "Query should return a result")
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        print(f"Query returned {result.get('count', 0)} total results")
        
        if 'rows' in result and len(result['rows']) > 0:
            first_result = result['rows'][0]
            self.assertIn('id', first_result, "Result should contain 'id' field")
            self.assertIn('name', first_result, "Result should contain 'name' field")
            self.assertIn('score', first_result, "Result should contain 'score' field")
            print(f"First result: {first_result.get('name', 'N/A')} (score: {first_result.get('score', 0)})")
        else:
            print("No similar neurons found (this is OK if none exist)")

    def test_schema_generation(self):
        """Test that the schema function works correctly"""
        print(f"\n=== Testing SimilarMorphologyTo schema generation ===")
        
        # Get term info for the test neuron
        term_info = get_term_info(self.test_neuron)
        if term_info:
            neuron_name = term_info.get('Name', self.test_neuron)
        else:
            neuron_name = self.test_neuron
        
        # Generate schema
        schema = SimilarMorphologyTo_to_schema(neuron_name, self.test_neuron)
        
        # Validate schema structure
        self.assertIsNotNone(schema, "Schema should not be None")
        self.assertEqual(schema.query, "SimilarMorphologyTo", "Query name should match")
        self.assertEqual(schema.function, "get_similar_neurons", "Function name should match")
        self.assertEqual(schema.preview, 5, "Preview should show 5 results")
        self.assertIn("score", schema.preview_columns, "Preview should include 'score' column")
        self.assertIn("name", schema.preview_columns, "Preview should include 'name' column")
        
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
        result = get_similar_neurons(
            self.test_neuron,
            similarity_score=self.similarity_score,
            return_dataframe=False,
            limit=5
        )
        
        if 'rows' in result and len(result['rows']) > 0:
            # Check that all preview columns exist in the results
            expected_columns = ['id', 'name', 'score', 'tags']
            for item in result['rows']:
                for col in expected_columns:
                    self.assertIn(col, item, f"Result should contain '{col}' field")
            
            print(f"✓ All {len(result['rows'])} results have required preview columns")
            
            # Print sample results
            for i, item in enumerate(result['rows'][:3], 1):
                print(f"{i}. {item.get('name', 'N/A')} - Score: {item.get('score', 0)}")
        else:
            print("No preview data available (query returned no results)")

    def test_score_ordering(self):
        """Test that results are ordered by score descending"""
        print(f"\n=== Testing score ordering ===")
        result = get_similar_neurons(
            self.test_neuron,
            similarity_score=self.similarity_score,
            return_dataframe=False,
            limit=10
        )
        
        if 'rows' in result and len(result['rows']) > 1:
            scores = [float(row.get('score', 0)) for row in result['rows']]
            # Check that scores are in descending order
            for i in range(len(scores) - 1):
                self.assertGreaterEqual(
                    scores[i], 
                    scores[i + 1],
                    f"Scores should be in descending order: {scores[i]} >= {scores[i+1]}"
                )
            print(f"✓ Scores are properly ordered (descending)")
            print(f"  Highest score: {scores[0]}")
            print(f"  Lowest score: {scores[-1]}")
        else:
            print("Not enough results to test ordering")

    def test_dataframe_output(self):
        """Test that DataFrame output format works"""
        print(f"\n=== Testing DataFrame output ===")
        result = get_similar_neurons(
            self.test_neuron,
            similarity_score=self.similarity_score,
            return_dataframe=True,
            limit=5
        )
        
        # Should return a pandas DataFrame
        import pandas as pd
        self.assertIsInstance(result, pd.DataFrame, "Should return DataFrame when return_dataframe=True")
        
        if not result.empty:
            # Check for expected columns
            expected_columns = ['id', 'name', 'score', 'tags']
            for col in expected_columns:
                self.assertIn(col, result.columns, f"DataFrame should contain '{col}' column")
            
            print(f"✓ DataFrame has {len(result)} rows and {len(result.columns)} columns")
            print(f"  Columns: {list(result.columns)}")
        else:
            print("DataFrame is empty (no similar neurons found)")


if __name__ == '__main__':
    unittest.main(verbosity=2)
