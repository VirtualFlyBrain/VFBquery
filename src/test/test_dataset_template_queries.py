"""
Unit tests for dataset and template queries.

This tests all 5 dataset/template-related queries:
1. get_painted_domains - Template painted anatomy domains
2. get_dataset_images - Images in a dataset
3. get_all_aligned_images - All images aligned to template
4. get_aligned_datasets - All datasets aligned to template
5. get_all_datasets - All available datasets

Test terms:
- VFBc_00050000 - Adult Brain template
- VFBc_00101384 - Example dataset
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vfbquery.vfb_queries import (
    get_painted_domains,
    get_dataset_images,
    get_all_aligned_images,
    get_aligned_datasets,
    get_all_datasets,
    PaintedDomains_to_schema,
    DatasetImages_to_schema,
    AllAlignedImages_to_schema,
    AlignedDatasets_to_schema,
    AllDatasets_to_schema
)


class DatasetTemplateQueriesTest(unittest.TestCase):
    """Test cases for dataset and template queries"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.template_term = 'VFBc_00050000'  # Adult Brain template
        self.dataset_term = 'VFBc_00101384'  # Example dataset
        
    def test_get_painted_domains(self):
        """Test get_painted_domains query"""
        result = get_painted_domains(self.template_term, return_dataframe=True, limit=10)
        self.assertIsNotNone(result, "Result should not be None")
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} painted domains for {self.template_term}")
            self.assertIn('id', result.columns)
            self.assertIn('label', result.columns)
            self.assertIn('thumbnail', result.columns)
            
    def test_get_painted_domains_formatted(self):
        """Test get_painted_domains with formatted output"""
        result = get_painted_domains(self.template_term, return_dataframe=False, limit=5)
        self.assertIsNotNone(result)
        
        if isinstance(result, dict):
            self.assertIn('headers', result)
            self.assertIn('rows', result)
            
    def test_get_dataset_images(self):
        """Test get_dataset_images query"""
        result = get_dataset_images(self.dataset_term, return_dataframe=True, limit=10)
        self.assertIsNotNone(result)
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} images in dataset {self.dataset_term}")
            self.assertIn('id', result.columns)
            
    def test_get_all_aligned_images(self):
        """Test get_all_aligned_images query"""
        result = get_all_aligned_images(self.template_term, return_dataframe=True, limit=10)
        self.assertIsNotNone(result)
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} aligned images for {self.template_term}")
            
    def test_get_aligned_datasets(self):
        """Test get_aligned_datasets query"""
        result = get_aligned_datasets(self.template_term, return_dataframe=True, limit=10)
        self.assertIsNotNone(result)
        
        import pandas as pd
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            print(f"\n✓ Found {len(result)} aligned datasets for {self.template_term}")
            
    def test_get_all_datasets(self):
        """Test get_all_datasets query (no parameters)"""
        result = get_all_datasets(return_dataframe=True, limit=20)
        self.assertIsNotNone(result)
        
        import pandas as pd
        if isinstance(result, pd.DataFrame):
            print(f"\n✓ Found {len(result)} total datasets")
            self.assertGreater(len(result), 0, "Should find at least some datasets")
            self.assertIn('id', result.columns)
            self.assertIn('name', result.columns)
            
    def test_get_all_datasets_formatted(self):
        """Test get_all_datasets with formatted output"""
        result = get_all_datasets(return_dataframe=False, limit=10)
        self.assertIsNotNone(result)
        
        if isinstance(result, dict):
            self.assertIn('headers', result)
            self.assertIn('rows', result)
            
    def test_schema_functions_exist(self):
        """Test that all dataset/template schema functions exist and are callable"""
        schema_functions = [
            PaintedDomains_to_schema,
            DatasetImages_to_schema,
            AllAlignedImages_to_schema,
            AlignedDatasets_to_schema,
            AllDatasets_to_schema
        ]
        
        for func in schema_functions:
            self.assertTrue(callable(func), f"{func.__name__} should be callable")
            
    def test_limit_parameter(self):
        """Test that limit parameter works correctly"""
        result = get_all_datasets(return_dataframe=True, limit=5)
        
        import pandas as pd
        if isinstance(result, pd.DataFrame):
            self.assertLessEqual(len(result), 5, "Result should respect limit parameter")


if __name__ == '__main__':
    unittest.main()
