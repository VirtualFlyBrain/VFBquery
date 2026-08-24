"""Regression tests: query `count` must match the rows returned at limit=-1.

These guard against the enrichment-CALL row-drop bug fixed alongside the
expression-pattern stock work: a thumbnail/image `CALL {}` subquery that ended
in `WHERE i IS NOT NULL` silently eliminated every result row with no aligned
image, so the table under-reported (or, for AnatomyExpressedIn, emptied out)
while `count` — computed by a separate, image-agnostic query — stayed correct.

The pre-existing per-query tests missed this because they guard their
assertions behind `if not result.empty:` / `if rows:`, so a wrongly-empty
result skips every assertion and passes. Here we assert the opposite for known-
populated example terms deliberately chosen to have FEW results, so `limit=-1`
(which forces every row through the per-row enrichment CALLs) stays fast:

  - count > 0 and len(rows) > 0   (the term really does have data)
  - count == len(rows)            (no counted item was dropped from the table)

A backend/connection failure skips rather than fails (the query raises, or
returns count 0 with no rows), so these don't turn into false negatives when
run without a live VFB backend.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import (
    get_transgene_expression_here,
    get_expression_overlaps_here,
    get_aligned_datasets,
)


class QueryCountRowsConsistencyTest(unittest.TestCase):
    """Every counted item must appear as a row when nothing is limited."""

    def _assert_count_equals_rows(self, fn, term, query_name):
        try:
            result = fn(term, return_dataframe=False, limit=-1)
        except Exception as e:
            self.skipTest(f"{query_name} backend unavailable: {e}")
        if not result or 'rows' not in result:
            self.skipTest(f"{query_name}: no result (no live VFB backend)")

        count = result.get('count', 0)
        rows = result.get('rows', [])
        if count == 0 and not rows:
            # Genuinely empty AND uncounted: treat as backend hiccup rather than
            # assert, since these terms are known-populated. A real regression
            # shows as count > 0 with fewer (or zero) rows, caught below.
            self.skipTest(f"{query_name}: empty result for {term} (likely no live backend)")

        self.assertGreater(count, 0, f"{query_name}: expected a non-zero count for {term}")
        self.assertGreater(len(rows), 0, f"{query_name}: expected rows for {term}")
        # A count that exceeds the rows returned at limit=-1 is the signature of
        # an enrichment CALL dropping rows (the `WHERE i IS NOT NULL` bug).
        self.assertEqual(
            count, len(rows),
            f"{query_name}: count ({count}) != rows returned ({len(rows)}) at "
            f"limit=-1 for {term} — rows are being dropped after counting",
        )

    def test_transgene_expression_here_count_matches_rows(self):
        # FBbt_00100253 (alpha'/beta' middle Kenyon cell): 11 expression
        # patterns, 3 of them image-less splits that the bug dropped (11 -> 7).
        self._assert_count_equals_rows(
            get_transgene_expression_here, 'FBbt_00100253', 'TransgeneExpressionHere')

    def test_anatomy_expressed_in_count_matches_rows(self):
        # A split with 2 overlapping anatomy classes. Anatomy classes rarely
        # have the image path, so the bug emptied this table (2 -> 0).
        self._assert_count_equals_rows(
            get_expression_overlaps_here, 'VFBexp_FBtp0122383FBtp0119521', 'AnatomyExpressedIn')

    def test_aligned_datasets_count_matches_rows(self):
        # VFB_00101384 (JRC_FlyEM_Hemibrain): 2 aligned datasets. Same
        # enrichment-CALL shape; here the count path already requires an image,
        # so this mainly locks the invariant against future regressions.
        self._assert_count_equals_rows(
            get_aligned_datasets, 'VFB_00101384', 'AlignedDatasets')


if __name__ == "__main__":
    unittest.main(verbosity=2)
