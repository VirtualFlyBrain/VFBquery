"""
Test suite for AnatomyExpressedIn query (get_expression_overlaps_here).

INVERSE-direction query — given an expression pattern, return the anatomy
classes whose Individuals overlap with the pattern's Individuals. The
forward direction (anatomy -> expression patterns) is solely owned by
TransgeneExpressionHere.

XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
Query: AnatomyExpressedIn ("Anatomy where $NAME is expressed")
"""

import unittest
import sys
import pandas as pd

# Add src directory to path for imports
sys.path.insert(0, '/Users/rcourt/GIT/VFBquery/src')

from vfbquery import vfb_queries as vq


class TestAnatomyExpressedIn(unittest.TestCase):
    """Test cases for get_expression_overlaps_here function"""

    def test_anatomy_expressed_in_basic_dataframe(self):
        """Test basic query returns DataFrame with expected columns"""
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True)

        self.assertIsInstance(result, pd.DataFrame, "Should return pandas DataFrame")

        if not result.empty:
            expected_columns = ['id', 'name', 'tags', 'pubs']
            for col in expected_columns:
                self.assertIn(col, result.columns, f"DataFrame should contain '{col}' column")

            self.assertTrue(all(isinstance(x, str) for x in result['id']), "IDs should be strings")
            self.assertTrue(all(isinstance(x, str) for x in result['name']), "Names should be strings")

            print(f"\nFound {len(result)} anatomy classes where VFBexp_FBtp0001321 is expressed")
            print(f"Sample results: {result.head(3)[['id', 'name']].to_dict('records')}")

    def test_anatomy_expressed_in_formatted_output(self):
        """Test query returns properly formatted dictionary output"""
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=False)

        self.assertIsInstance(result, dict, "Should return dictionary when return_dataframe=False")

        self.assertIn('headers', result, "Result should contain 'headers'")
        self.assertIn('rows', result, "Result should contain 'rows'")
        self.assertIn('count', result, "Result should contain 'count'")

        headers = result['headers']
        expected_headers = ['id', 'name', 'tags', 'pubs']
        for header in expected_headers:
            self.assertIn(header, headers, f"Headers should contain '{header}'")
            self.assertIn('title', headers[header], f"Header '{header}' should have 'title'")
            self.assertIn('type', headers[header], f"Header '{header}' should have 'type'")
            self.assertIn('order', headers[header], f"Header '{header}' should have 'order'")

        self.assertEqual(headers['id']['type'], 'selection_id')
        self.assertEqual(headers['name']['type'], 'markdown')
        self.assertEqual(headers['tags']['type'], 'tags')
        self.assertEqual(headers['pubs']['type'], 'metadata')

        if result['rows']:
            first_row = result['rows'][0]
            for key in expected_headers:
                self.assertIn(key, first_row, f"Row should contain '{key}'")

            print(f"\nFormatted output contains {result['count']} anatomy classes")
            print(f"Sample row keys: {list(first_row.keys())}")

    def test_anatomy_expressed_in_limit(self):
        """Test limit parameter restricts number of results"""
        limit = 3
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True, limit=limit)

        if not result.empty:
            self.assertLessEqual(len(result), limit, f"Should return at most {limit} results")
            print(f"\nLimit parameter working: requested {limit}, got {len(result)}")

    def test_anatomy_expressed_in_empty_result(self):
        """Test query with an id that has no expression overlaps"""
        result = vq.get_expression_overlaps_here('VFBexp_99999999', return_dataframe=True)

        # Should return empty DataFrame, not error
        self.assertIsInstance(result, pd.DataFrame, "Should return DataFrame even for no results")
        print(f"\nEmpty result handling works correctly")

    def test_anatomy_expressed_in_publication_data(self):
        """Test that publication data is properly formatted when present"""
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True, limit=10)

        if not result.empty:
            self.assertIn('pubs', result.columns, "Should have 'pubs' column")

            for idx, row in result.iterrows():
                if row['pubs']:
                    pubs = row['pubs']
                    self.assertIsInstance(pubs, list, "Publications should be a list")

                    if pubs:
                        first_pub = pubs[0]
                        self.assertIsInstance(first_pub, dict, "Publication should be a dict")

                        if 'core' in first_pub:
                            self.assertIn('short_form', first_pub['core'], "Publication should have short_form")

                        print(f"\nPublication data properly structured")
                        break

    def test_anatomy_expressed_in_markdown_encoding(self):
        """Test that markdown links are properly formatted"""
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True, limit=5)

        if not result.empty:
            for name in result['name']:
                self.assertIn('[', name, "Name should contain markdown link start")
                self.assertIn('](', name, "Name should contain markdown link separator")
                self.assertIn(')', name, "Name should contain markdown link end")

            print(f"\nMarkdown links properly formatted")

    def test_anatomy_expressed_in_tags_format(self):
        """Test that tags are properly formatted as pipe-separated strings"""
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True, limit=5)

        if not result.empty and 'tags' in result.columns:
            for tags in result['tags']:
                if pd.notna(tags) and tags:
                    self.assertIsInstance(tags, str, "Tags should be string type")
                    parts = tags.split('|')
                    self.assertTrue(all(isinstance(p, str) for p in parts), "Tag parts should be strings")

            print(f"\nTags format verified")


class TestAnatomyExpressedInSchema(unittest.TestCase):
    """Test cases for AnatomyExpressedIn_to_schema."""

    def test_schema_function_exists(self):
        """Canonical schema function is defined; legacy alias is gone."""
        self.assertTrue(hasattr(vq, 'AnatomyExpressedIn_to_schema'),
                        "AnatomyExpressedIn_to_schema function should exist")
        self.assertFalse(hasattr(vq, 'ExpressionOverlapsHere_to_schema'),
                         "Legacy ExpressionOverlapsHere_to_schema alias must be removed")

    def test_schema_structure(self):
        """Schema function returns the expected Query object."""
        from vfbquery.vfb_queries import AnatomyExpressedIn_to_schema

        schema = AnatomyExpressedIn_to_schema(
            "P{GAL4-per.BS} expression pattern",
            {"short_form": "VFBexp_FBtp0001321"},
        )

        self.assertEqual(schema.query, "AnatomyExpressedIn")
        self.assertEqual(schema.function, "get_expression_overlaps_here")
        self.assertIn("Anatomy where", schema.label)
        self.assertEqual(schema.preview, 5)
        self.assertEqual(schema.preview_columns, ["id", "name", "tags", "pubs"])

        # takes constrains the input to an expression pattern (or fragment)
        self.assertIn("short_form", schema.takes)
        self.assertIn("default", schema.takes)
        self.assertEqual(
            schema.takes["short_form"],
            {"$or": [
                {"$and": ["Class", "Expression_pattern"]},
                {"$and": ["Class", "Expression_pattern_fragment"]},
            ]},
        )

        print("\nSchema structure verified")


class TestAnatomyExpressedInWireMapping(unittest.TestCase):
    """ha_api.QUERY_TYPE_MAP — canonical key only, legacy alias removed."""

    def test_query_type_map(self):
        from vfbquery.ha_api import QUERY_TYPE_MAP
        self.assertIn("AnatomyExpressedIn", QUERY_TYPE_MAP,
                      "AnatomyExpressedIn must be a recognised query_type")
        self.assertEqual(QUERY_TYPE_MAP["AnatomyExpressedIn"],
                         "get_expression_overlaps_here")
        self.assertNotIn("ExpressionOverlapsHere", QUERY_TYPE_MAP,
                         "Legacy ExpressionOverlapsHere alias must be removed")


if __name__ == '__main__':
    unittest.main(verbosity=2)
