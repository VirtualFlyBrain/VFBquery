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
        # limit=5 keeps this structural check fast and robust: at limit=-1 the
        # per-row enrichment over all ~79 overlapping anatomy classes can time
        # out under parallel CI load and come back empty, which this test (now
        # asserting non-empty) would read as a failure.
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True, limit=5)

        self.assertIsInstance(result, pd.DataFrame, "Should return pandas DataFrame")

        # VFBexp_FBtp0001321 is a known-populated expression pattern: an empty
        # result is a defect, not an acceptable outcome (a backend outage skips
        # this test upstream via conftest.py rather than reaching here empty).
        self.assertFalse(result.empty, "Query for a known-populated expression pattern returned no rows")
        expected_columns = ['id', 'name', 'tags', 'pubs']
        for col in expected_columns:
            self.assertIn(col, result.columns, f"DataFrame should contain '{col}' column")

        self.assertTrue(all(isinstance(x, str) for x in result['id']), "IDs should be strings")
        self.assertTrue(all(isinstance(x, str) for x in result['name']), "Names should be strings")

        print(f"\nFound {len(result)} anatomy classes where VFBexp_FBtp0001321 is expressed")
        print(f"Sample results: {result.head(3)[['id', 'name']].to_dict('records')}")

    def test_anatomy_expressed_in_formatted_output(self):
        """Test query returns properly formatted dictionary output"""
        # limit the enrichment (per-row Stage/Template/Technique/Thumbnail
        # walks) to keep this structural check fast; `count` is independent of
        # the limit so the printed total is still the full result size.
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=False, limit=5)

        self.assertIsInstance(result, dict, "Should return dictionary when return_dataframe=False")

        self.assertIn('headers', result, "Result should contain 'headers'")
        self.assertIn('rows', result, "Result should contain 'rows'")
        self.assertIn('count', result, "Result should contain 'count'")

        headers = result['headers']
        # v1.14.2: full column shape (Name / Reference / Gross_Type / Stage /
        # Template_Space / Imaging_Technique / Images).
        expected_types = {
            'id': 'selection_id',
            'name': 'markdown',
            'pubs': 'markdown',
            'tags': 'tags',
            'stages': 'text',
            'template': 'markdown',
            'technique': 'text',
            'thumbnail': 'markdown',
        }
        for header, expected_type in expected_types.items():
            self.assertIn(header, headers, f"Headers should contain '{header}'")
            self.assertIn('title', headers[header], f"Header '{header}' should have 'title'")
            self.assertIn('type', headers[header], f"Header '{header}' should have 'type'")
            self.assertIn('order', headers[header], f"Header '{header}' should have 'order'")
            self.assertEqual(headers[header]['type'], expected_type,
                             f"Header '{header}' should be type '{expected_type}'")

        self.assertTrue(result['rows'], "Query for a known-populated expression pattern returned no rows")
        first_row = result['rows'][0]
        for key in expected_types:
            self.assertIn(key, first_row, f"Row should contain '{key}'")

        print(f"\nFormatted output contains {result['count']} anatomy classes")
        print(f"Sample row keys: {list(first_row.keys())}")

    def test_anatomy_expressed_in_limit(self):
        """Test limit parameter restricts number of results"""
        limit = 3
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True, limit=limit)

        self.assertFalse(result.empty, "Query for a known-populated expression pattern returned no rows")
        self.assertLessEqual(len(result), limit, f"Should return at most {limit} results")
        print(f"\nLimit parameter working: requested {limit}, got {len(result)}")

    def test_anatomy_expressed_in_empty_result(self):
        """Test query with an id that has no expression overlaps"""
        result = vq.get_expression_overlaps_here('VFBexp_99999999', return_dataframe=True)

        # Should return empty DataFrame, not error
        self.assertIsInstance(result, pd.DataFrame, "Should return DataFrame even for no results")
        print(f"\nEmpty result handling works correctly")

    def test_anatomy_expressed_in_publication_data(self):
        """Test that publication data is formatted as markdown links when present.

        v1.14.7: the pubs column is a `; `-joined string of `[label](id)`
        markdown links (rendered by V2's QueryLinkArrayComponent), not the
        legacy list-of-pub-dicts. An anatomy row with no citation is an empty
        string.
        """
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True, limit=10)

        self.assertFalse(result.empty, "Query for a known-populated expression pattern returned no rows")
        self.assertIn('pubs', result.columns, "Should have 'pubs' column")

        for idx, row in result.iterrows():
            pubs = row['pubs']
            self.assertIsInstance(pubs, str, "Publications should be a markdown string")
            if pubs:
                # Each entry is a `[label](id)` markdown link.
                self.assertIn('[', pubs, "Publication should contain markdown link start")
                self.assertIn('](', pubs, "Publication should contain markdown link separator")
                self.assertIn(')', pubs, "Publication should contain markdown link end")
                print(f"\nPublication data properly structured: {pubs}")
                break

    def test_anatomy_expressed_in_markdown_encoding(self):
        """Test that markdown links are properly formatted"""
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True, limit=5)

        self.assertFalse(result.empty, "Query for a known-populated expression pattern returned no rows")
        for name in result['name']:
            self.assertIn('[', name, "Name should contain markdown link start")
            self.assertIn('](', name, "Name should contain markdown link separator")
            self.assertIn(')', name, "Name should contain markdown link end")

        print(f"\nMarkdown links properly formatted")

    def test_anatomy_expressed_in_tags_format(self):
        """Test that tags are properly formatted as pipe-separated strings"""
        result = vq.get_expression_overlaps_here('VFBexp_FBtp0001321', return_dataframe=True, limit=5)

        self.assertFalse(result.empty, "Query for a known-populated expression pattern returned no rows")
        self.assertIn('tags', result.columns, "Should have 'tags' column")
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
        # v1.14.2: gained Stage / Template / Imaging Technique / Thumbnail
        # columns to match the legacy ExpressionOverlapsHere column shape.
        self.assertEqual(
            schema.preview_columns,
            ["id", "name", "pubs", "tags", "stages", "template", "technique", "thumbnail"],
        )

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
