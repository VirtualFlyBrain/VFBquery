"""
Test suite for ExpressionOverlapsHere query (get_expression_overlaps_here)

This test verifies the Neo4j query implementation that finds expression patterns
overlapping with specified anatomical regions.

XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
Query: anat_2_ep_query
"""

import unittest
import sys
import pandas as pd

# Add src directory to path for imports
sys.path.insert(0, '/Users/rcourt/GIT/VFBquery/src')

from vfbquery import vfb_queries as vq


class TestExpressionOverlapsHere(unittest.TestCase):
    """Test cases for get_expression_overlaps_here function"""

    def test_expression_overlaps_basic_dataframe(self):
        """Test basic query returns DataFrame with expected columns"""
        # Test with adult brain (FBbt_00003982) - known to have expression patterns
        result = vq.get_expression_overlaps_here('FBbt_00003982', return_dataframe=True)
        
        self.assertIsInstance(result, pd.DataFrame, "Should return pandas DataFrame")
        
        if not result.empty:
            # Check for expected columns
            expected_columns = ['id', 'name', 'tags', 'pubs']
            for col in expected_columns:
                self.assertIn(col, result.columns, f"DataFrame should contain '{col}' column")
            
            # Verify data types
            self.assertTrue(all(isinstance(x, str) for x in result['id']), "IDs should be strings")
            self.assertTrue(all(isinstance(x, str) for x in result['name']), "Names should be strings")
            
            print(f"\n✓ Found {len(result)} expression patterns overlapping FBbt_00003982")
            print(f"✓ Sample results: {result.head(3)[['id', 'name']].to_dict('records')}")

    def test_expression_overlaps_formatted_output(self):
        """Test query returns properly formatted dictionary output"""
        result = vq.get_expression_overlaps_here('FBbt_00003982', return_dataframe=False)
        
        self.assertIsInstance(result, dict, "Should return dictionary when return_dataframe=False")
        
        # Check structure
        self.assertIn('headers', result, "Result should contain 'headers'")
        self.assertIn('rows', result, "Result should contain 'rows'")
        self.assertIn('count', result, "Result should contain 'count'")
        
        # Check headers structure
        headers = result['headers']
        expected_headers = ['id', 'name', 'tags', 'pubs']
        for header in expected_headers:
            self.assertIn(header, headers, f"Headers should contain '{header}'")
            self.assertIn('title', headers[header], f"Header '{header}' should have 'title'")
            self.assertIn('type', headers[header], f"Header '{header}' should have 'type'")
            self.assertIn('order', headers[header], f"Header '{header}' should have 'order'")
        
        # Verify header types
        self.assertEqual(headers['id']['type'], 'selection_id')
        self.assertEqual(headers['name']['type'], 'markdown')
        self.assertEqual(headers['tags']['type'], 'tags')
        self.assertEqual(headers['pubs']['type'], 'metadata')
        
        if result['rows']:
            # Check row structure
            first_row = result['rows'][0]
            for key in expected_headers:
                self.assertIn(key, first_row, f"Row should contain '{key}'")
            
            print(f"\n✓ Formatted output contains {result['count']} expression patterns")
            print(f"✓ Sample row keys: {list(first_row.keys())}")

    def test_expression_overlaps_limit(self):
        """Test limit parameter restricts number of results"""
        limit = 3
        result = vq.get_expression_overlaps_here('FBbt_00003982', return_dataframe=True, limit=limit)
        
        if not result.empty:
            self.assertLessEqual(len(result), limit, f"Should return at most {limit} results")
            print(f"\n✓ Limit parameter working: requested {limit}, got {len(result)}")

    def test_expression_overlaps_empty_result(self):
        """Test query with anatomy that has no expression patterns"""
        # Use a very specific anatomy term unlikely to have expression patterns
        result = vq.get_expression_overlaps_here('FBbt_99999999', return_dataframe=True)
        
        # Should return empty DataFrame, not error
        self.assertIsInstance(result, pd.DataFrame, "Should return DataFrame even for no results")
        print(f"\n✓ Empty result handling works correctly")

    def test_expression_overlaps_publication_data(self):
        """Test that publication data is properly formatted when present"""
        result = vq.get_expression_overlaps_here('FBbt_00003982', return_dataframe=True, limit=10)
        
        if not result.empty:
            # Check if pubs column exists and contains data
            self.assertIn('pubs', result.columns, "Should have 'pubs' column")
            
            # Check structure of publication data
            for idx, row in result.iterrows():
                if row['pubs']:  # If publications exist
                    pubs = row['pubs']
                    self.assertIsInstance(pubs, list, "Publications should be a list")
                    
                    if pubs:  # If list is not empty
                        first_pub = pubs[0]
                        self.assertIsInstance(first_pub, dict, "Publication should be a dict")
                        
                        # Check expected publication fields
                        if 'core' in first_pub:
                            self.assertIn('short_form', first_pub['core'], "Publication should have short_form")
                        
                        print(f"\n✓ Publication data properly structured")
                        break

    def test_expression_overlaps_markdown_encoding(self):
        """Test that markdown links are properly formatted"""
        result = vq.get_expression_overlaps_here('FBbt_00003982', return_dataframe=True, limit=5)
        
        if not result.empty:
            # Check that names contain markdown link format [label](url)
            for name in result['name']:
                # Should have markdown link format
                self.assertIn('[', name, "Name should contain markdown link start")
                self.assertIn('](', name, "Name should contain markdown link separator")
                self.assertIn(')', name, "Name should contain markdown link end")
            
            print(f"\n✓ Markdown links properly formatted")

    def test_expression_overlaps_tags_format(self):
        """Test that tags are properly formatted as pipe-separated strings"""
        result = vq.get_expression_overlaps_here('FBbt_00003982', return_dataframe=True, limit=5)
        
        if not result.empty and 'tags' in result.columns:
            for tags in result['tags']:
                if pd.notna(tags) and tags:
                    # Tags should be pipe-separated strings
                    self.assertIsInstance(tags, str, "Tags should be string type")
                    # Could contain pipes for multiple tags
                    parts = tags.split('|')
                    self.assertTrue(all(isinstance(p, str) for p in parts), "Tag parts should be strings")
            
            print(f"\n✓ Tags format verified")


class TestExpressionOverlapsHereSchema(unittest.TestCase):
    """Test cases for ExpressionOverlapsHere_to_schema function"""

    def test_schema_function_exists(self):
        """Test that the schema function is properly defined"""
        self.assertTrue(hasattr(vq, 'ExpressionOverlapsHere_to_schema'), 
                       "ExpressionOverlapsHere_to_schema function should exist")

    def test_schema_structure(self):
        """Test that schema function returns proper Query object"""
        from vfbquery.vfb_queries import ExpressionOverlapsHere_to_schema
        
        schema = ExpressionOverlapsHere_to_schema("test anatomy", {"short_form": "FBbt_00003982"})
        
        # Check Query object attributes
        self.assertEqual(schema.query, "ExpressionOverlapsHere")
        self.assertEqual(schema.function, "get_expression_overlaps_here")
        self.assertIn("Expression patterns overlapping", schema.label)
        self.assertEqual(schema.preview, 5)
        self.assertEqual(schema.preview_columns, ["id", "name", "tags", "pubs"])
        
        # Check takes structure
        self.assertIn("short_form", schema.takes)
        self.assertIn("default", schema.takes)
        self.assertEqual(schema.takes["short_form"], {"$and": ["Class", "Anatomy"]})
        
        print("\n✓ Schema structure verified")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
