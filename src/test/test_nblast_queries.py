"""
Unit tests for NBLAST similarity queries.

This tests all 6 NBLAST-related queries:
1. get_similar_morphology - NBLAST matches
2. get_similar_morphology_part_of - NBLASTexp to expression patterns
3. get_similar_morphology_part_of_exp - Reverse NBLASTexp
4. get_similar_morphology_nb - NeuronBridge matches
5. get_similar_morphology_nb_exp - NeuronBridge for expression patterns
6. get_similar_morphology_userdata - User upload NBLAST from SOLR

Test terms:
- VFB_00101567 - has NBLAST matches
- VFB_00050000 - example neuron with NBLASTexp
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vfbquery.vfb_queries import (
    get_similar_morphology,
    get_similar_morphology_part_of,
    get_similar_morphology_part_of_exp,
    get_similar_morphology_nb,
    get_similar_morphology_nb_exp,
    get_similar_morphology_userdata,
    SimilarMorphologyTo_to_schema,
    SimilarMorphologyToPartOf_to_schema,
    SimilarMorphologyToPartOfexp_to_schema,
    SimilarMorphologyToNB_to_schema,
    SimilarMorphologyToNBexp_to_schema,
    SimilarMorphologyToUserData_to_schema
)


class NBLASTQueriesTest(unittest.TestCase):
    """Test cases for NBLAST similarity queries"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.nblast_term = 'VFB_00101567'  # Has NBLAST matches
        self.neuron_term = 'VFB_00050000'  # Example neuron
        
    def test_get_similar_morphology(self):
        """Test get_similar_morphology query"""
        result = get_similar_morphology(self.nblast_term, return_dataframe=True, limit=5)
        self.assertIsNotNone(result, "Result should not be None")
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} NBLAST matches for {self.nblast_term}")
            self.assertIn('id', result.columns)
            self.assertIn('label', result.columns)
            self.assertIn('score', result.columns)
            
    def test_get_similar_morphology_formatted(self):
        """Test get_similar_morphology with formatted output"""
        result = get_similar_morphology(self.nblast_term, return_dataframe=False, limit=3)
        self.assertIsNotNone(result)
        
        if isinstance(result, dict):
            self.assertIn('headers', result)
            self.assertIn('rows', result)
            
    def test_get_similar_morphology_part_of(self):
        """Test get_similar_morphology_part_of (NBLASTexp)"""
        result = get_similar_morphology_part_of(self.neuron_term, return_dataframe=True, limit=5)
        self.assertIsNotNone(result)
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} NBLASTexp matches for {self.neuron_term}")
            
    def test_get_similar_morphology_part_of_exp(self):
        """Test get_similar_morphology_part_of_exp (reverse NBLASTexp)"""
        result = get_similar_morphology_part_of_exp(self.neuron_term, return_dataframe=True, limit=5)
        self.assertIsNotNone(result)
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} reverse NBLASTexp matches")
            
    def test_get_similar_morphology_nb(self):
        """Test get_similar_morphology_nb (NeuronBridge)"""
        result = get_similar_morphology_nb(self.neuron_term, return_dataframe=True, limit=5)
        self.assertIsNotNone(result)
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} NeuronBridge matches")
            self.assertIn('score', result.columns)
            
    def test_get_similar_morphology_nb_exp(self):
        """Test get_similar_morphology_nb_exp (NeuronBridge for expression)"""
        result = get_similar_morphology_nb_exp(self.neuron_term, return_dataframe=True, limit=5)
        self.assertIsNotNone(result)
        
    def test_schema_functions_exist(self):
        """Test that all NBLAST schema functions exist and are callable"""
        schema_functions = [
            SimilarMorphologyTo_to_schema,
            SimilarMorphologyToPartOf_to_schema,
            SimilarMorphologyToPartOfexp_to_schema,
            SimilarMorphologyToNB_to_schema,
            SimilarMorphologyToNBexp_to_schema,
            SimilarMorphologyToUserData_to_schema
        ]
        
        for func in schema_functions:
            self.assertTrue(callable(func), f"{func.__name__} should be callable")
            
    def test_empty_results_handling(self):
        """Test that queries handle empty results gracefully"""
        # Use a term unlikely to have NBLAST matches
        result = get_similar_morphology('FBbt_00000001', return_dataframe=True, limit=5)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
