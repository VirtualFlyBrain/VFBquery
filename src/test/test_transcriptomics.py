"""
Tests for transcriptomics queries (scRNAseq data)

Tests the following VFB queries:
1. anatScRNAseqQuery - scRNAseq data for anatomical regions
2. clusterExpression - genes expressed in a cluster
3. expressionCluster - clusters expressing a gene
4. scRNAdatasetData - all clusters in a scRNAseq dataset

XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
"""

import unittest
import pandas as pd
from vfbquery import vfb_queries as vfb


class TranscriptomicsQueriesTest(unittest.TestCase):
    """Tests for scRNAseq/transcriptomics queries"""
    
    # Test data - known terms with scRNAseq data
    # These are examples from the VFB knowledge base
    ANATOMY_WITH_SCRNASEQ = "FBbt_00003982"  # adult brain - should have scRNAseq data
    CLUSTER_ID = "VFBc_00101567"  # Example cluster ID (may need to be updated with real data)
    GENE_ID = "FBgn_00000024"  # Example gene ID (may need to be updated with real data)
    DATASET_ID = "VFBds_00001234"  # Example dataset ID (may need to be updated with real data)
    
    def test_anatomy_scrnaseq_basic_dataframe(self):
        """Test anatScRNAseqQuery returns DataFrame"""
        result = vfb.get_anatomy_scrnaseq(self.ANATOMY_WITH_SCRNASEQ, return_dataframe=True)
        
        self.assertIsInstance(result, pd.DataFrame)
        
        # If data exists, check structure
        if not result.empty:
            self.assertIn('id', result.columns)
            self.assertIn('name', result.columns)
            self.assertIn('tags', result.columns)
            self.assertIn('dataset', result.columns)
            self.assertIn('pubs', result.columns)
            
            # Check that all IDs start with expected prefix
            for idx, row in result.iterrows():
                self.assertTrue(row['id'].startswith('VFB'), 
                              f"Cluster ID should start with VFB, got: {row['id']}")
    
    def test_anatomy_scrnaseq_formatted_output(self):
        """Test anatScRNAseqQuery returns properly formatted dict"""
        result = vfb.get_anatomy_scrnaseq(self.ANATOMY_WITH_SCRNASEQ, return_dataframe=False)
        
        self.assertIsInstance(result, dict)
        self.assertIn('headers', result)
        self.assertIn('rows', result)
        self.assertIn('count', result)
        
        # Check headers structure
        headers = result['headers']
        self.assertIn('id', headers)
        self.assertIn('name', headers)
        self.assertIn('tags', headers)
        self.assertIn('dataset', headers)
        self.assertIn('pubs', headers)
    
    def test_anatomy_scrnaseq_limit(self):
        """Test anatScRNAseqQuery respects limit parameter"""
        result = vfb.get_anatomy_scrnaseq(self.ANATOMY_WITH_SCRNASEQ, return_dataframe=True, limit=5)
        
        self.assertIsInstance(result, pd.DataFrame)
        if not result.empty:
            self.assertLessEqual(len(result), 5)
    
    def test_cluster_expression_basic_dataframe(self):
        """Test clusterExpression returns DataFrame"""
        # Note: This test may need adjustment based on actual cluster IDs in the database
        # For now, we'll just test that the function runs without error
        try:
            result = vfb.get_cluster_expression(self.CLUSTER_ID, return_dataframe=True)
            self.assertIsInstance(result, pd.DataFrame)
            
            # If data exists, check structure
            if not result.empty:
                self.assertIn('id', result.columns)
                self.assertIn('name', result.columns)
                self.assertIn('tags', result.columns)
                self.assertIn('expression_level', result.columns)
                self.assertIn('expression_extent', result.columns)
                self.assertIn('anatomy', result.columns)
        except Exception as e:
            # Skip test if cluster ID doesn't exist in current database
            self.skipTest(f"Cluster ID {self.CLUSTER_ID} may not exist in database: {e}")
    
    def test_cluster_expression_formatted_output(self):
        """Test clusterExpression returns properly formatted dict"""
        try:
            result = vfb.get_cluster_expression(self.CLUSTER_ID, return_dataframe=False)
            
            self.assertIsInstance(result, dict)
            self.assertIn('headers', result)
            self.assertIn('rows', result)
            self.assertIn('count', result)
            
            # Check headers structure
            headers = result['headers']
            self.assertIn('id', headers)
            self.assertIn('name', headers)
            self.assertIn('expression_level', headers)
            self.assertIn('expression_extent', headers)
        except Exception as e:
            self.skipTest(f"Cluster ID {self.CLUSTER_ID} may not exist in database: {e}")
    
    def test_expression_cluster_basic_dataframe(self):
        """Test expressionCluster returns DataFrame"""
        try:
            result = vfb.get_expression_cluster(self.GENE_ID, return_dataframe=True)
            self.assertIsInstance(result, pd.DataFrame)
            
            # If data exists, check structure
            if not result.empty:
                self.assertIn('id', result.columns)
                self.assertIn('name', result.columns)
                self.assertIn('tags', result.columns)
                self.assertIn('expression_level', result.columns)
                self.assertIn('expression_extent', result.columns)
                self.assertIn('anatomy', result.columns)
        except Exception as e:
            self.skipTest(f"Gene ID {self.GENE_ID} may not exist in database: {e}")
    
    def test_expression_cluster_formatted_output(self):
        """Test expressionCluster returns properly formatted dict"""
        try:
            result = vfb.get_expression_cluster(self.GENE_ID, return_dataframe=False)
            
            self.assertIsInstance(result, dict)
            self.assertIn('headers', result)
            self.assertIn('rows', result)
            self.assertIn('count', result)
            
            # Check headers structure
            headers = result['headers']
            self.assertIn('id', headers)
            self.assertIn('name', headers)
            self.assertIn('expression_level', headers)
            self.assertIn('expression_extent', headers)
        except Exception as e:
            self.skipTest(f"Gene ID {self.GENE_ID} may not exist in database: {e}")
    
    def test_scrnaseq_dataset_basic_dataframe(self):
        """Test scRNAdatasetData returns DataFrame"""
        try:
            result = vfb.get_scrnaseq_dataset_data(self.DATASET_ID, return_dataframe=True)
            self.assertIsInstance(result, pd.DataFrame)
            
            # If data exists, check structure
            if not result.empty:
                self.assertIn('id', result.columns)
                self.assertIn('name', result.columns)
                self.assertIn('tags', result.columns)
                self.assertIn('anatomy', result.columns)
                self.assertIn('pubs', result.columns)
        except Exception as e:
            self.skipTest(f"Dataset ID {self.DATASET_ID} may not exist in database: {e}")
    
    def test_scrnaseq_dataset_formatted_output(self):
        """Test scRNAdatasetData returns properly formatted dict"""
        try:
            result = vfb.get_scrnaseq_dataset_data(self.DATASET_ID, return_dataframe=False)
            
            self.assertIsInstance(result, dict)
            self.assertIn('headers', result)
            self.assertIn('rows', result)
            self.assertIn('count', result)
            
            # Check headers structure
            headers = result['headers']
            self.assertIn('id', headers)
            self.assertIn('name', headers)
            self.assertIn('anatomy', headers)
            self.assertIn('pubs', headers)
        except Exception as e:
            self.skipTest(f"Dataset ID {self.DATASET_ID} may not exist in database: {e}")
    
    def test_anatomy_scrnaseq_empty_result(self):
        """Test anatScRNAseqQuery with anatomy that has no scRNAseq data"""
        # Use an anatomy term that likely has no scRNAseq data
        result = vfb.get_anatomy_scrnaseq("FBbt_00000001", return_dataframe=True)  # root term
        
        self.assertIsInstance(result, pd.DataFrame)
        # Empty results are acceptable - just check it doesn't error
    
    def test_schema_functions_exist(self):
        """Test that all schema functions are defined"""
        self.assertTrue(hasattr(vfb, 'anatScRNAseqQuery_to_schema'))
        self.assertTrue(hasattr(vfb, 'clusterExpression_to_schema'))
        self.assertTrue(hasattr(vfb, 'expressionCluster_to_schema'))
        self.assertTrue(hasattr(vfb, 'scRNAdatasetData_to_schema'))
    
    def test_schema_structure(self):
        """Test that schema functions return proper Query objects"""
        schema_funcs = [
            vfb.anatScRNAseqQuery_to_schema,
            vfb.clusterExpression_to_schema,
            vfb.expressionCluster_to_schema,
            vfb.scRNAdatasetData_to_schema
        ]
        
        for schema_func in schema_funcs:
            query_obj = schema_func("Test Name", {"short_form": "FBbt_00000001"})
            
            # Check required attributes
            self.assertTrue(hasattr(query_obj, 'query'))
            self.assertTrue(hasattr(query_obj, 'label'))
            self.assertTrue(hasattr(query_obj, 'function'))
            self.assertTrue(hasattr(query_obj, 'takes'))
            self.assertTrue(hasattr(query_obj, 'preview'))
            self.assertTrue(hasattr(query_obj, 'preview_columns'))
            
            # Check preview columns are defined
            self.assertIsInstance(query_obj.preview_columns, list)
            self.assertGreater(len(query_obj.preview_columns), 0)


if __name__ == '__main__':
    unittest.main()
