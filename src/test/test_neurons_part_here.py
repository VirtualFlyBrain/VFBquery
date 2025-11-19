import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vfbquery.vfb_queries import get_neurons_with_part_in, get_term_info


class NeuronsPartHereTest(unittest.TestCase):
    """Test suite for NeuronsPartHere query implementation"""

    def setUp(self):
        """Set up test fixtures"""
        self.medulla_id = 'FBbt_00003748'
        # Expected count based on VFB data (as of test creation)
        # Data can grow over time, so we test for minimum expected count
        self.expected_count = 470  # Minimum expected count (actual was 472)
        self.count_tolerance = 5    # Allow some tolerance for variations

    def test_neurons_part_here_returns_results(self):
        """Test that NeuronsPartHere query returns results for medulla"""
        print("\n" + "=" * 80)
        print("Testing NeuronsPartHere query - Basic functionality")
        print("=" * 80)
        
        results_df = get_neurons_with_part_in(
            self.medulla_id, 
            return_dataframe=True, 
            limit=-1
        )
        
        self.assertIsNotNone(results_df, "Results should not be None")
        self.assertGreater(len(results_df), 0, "Should return at least one result")
        
        print(f"✓ Query returned {len(results_df)} neuron classes")

    def test_neurons_part_here_result_count(self):
        """Test that NeuronsPartHere returns expected number of results for medulla"""
        print("\n" + "=" * 80)
        print(f"Testing NeuronsPartHere result count (expected ~{self.expected_count})")
        print("=" * 80)
        
        results_df = get_neurons_with_part_in(
            self.medulla_id, 
            return_dataframe=True, 
            limit=-1
        )
        
        actual_count = len(results_df)
        count_diff = actual_count - self.expected_count
        
        print(f"Expected: at least {self.expected_count} results")
        print(f"Actual: {actual_count} results")
        
        # Data can grow over time, so we require at least the expected minimum
        self.assertGreaterEqual(
            actual_count, 
            self.expected_count,
            f"Result count {actual_count} is less than expected minimum {self.expected_count}"
        )
        
        if count_diff > 0:
            print(f"✓ Count increased by {count_diff} (data growth)")
        else:
            print(f"✓ Minimum count met: {actual_count}")

    def test_neurons_part_here_result_structure(self):
        """Test that results have the expected structure with required columns"""
        print("\n" + "=" * 80)
        print("Testing NeuronsPartHere result structure")
        print("=" * 80)
        
        results_df = get_neurons_with_part_in(
            self.medulla_id, 
            return_dataframe=True, 
            limit=5
        )
        
        # Check required columns
        required_columns = ['id', 'label', 'tags', 'thumbnail']
        for col in required_columns:
            self.assertIn(col, results_df.columns, f"Column '{col}' should be present")
        
        print(f"✓ All required columns present: {', '.join(required_columns)}")
        
        # Check that we have data in the columns
        first_row = results_df.iloc[0]
        self.assertIsNotNone(first_row['id'], "ID should not be None")
        self.assertIsNotNone(first_row['label'], "Label should not be None")
        
        print(f"✓ Sample result: {first_row['label']}")

    def test_neurons_part_here_has_examples(self):
        """Test that neuron class results include example images (thumbnails)"""
        print("\n" + "=" * 80)
        print("Testing NeuronsPartHere includes example images")
        print("=" * 80)
        
        results_df = get_neurons_with_part_in(
            self.medulla_id, 
            return_dataframe=True, 
            limit=10
        )
        
        # Count how many results have thumbnails
        has_thumbnails = results_df['thumbnail'].notna().sum()
        total_results = len(results_df)
        
        print(f"Results with thumbnails: {has_thumbnails}/{total_results}")
        
        # At least some results should have thumbnails (example instances)
        self.assertGreater(
            has_thumbnails, 
            0,
            "At least some neuron classes should have example images"
        )
        
        # Show example thumbnails
        sample_with_thumbnail = results_df[results_df['thumbnail'].notna()].iloc[0]
        print(f"\n✓ Example with thumbnail:")
        print(f"  {sample_with_thumbnail['label']}")
        print(f"  Thumbnail: {sample_with_thumbnail['thumbnail'][:100]}...")

    def test_neurons_part_here_preview_in_term_info(self):
        """Test that NeuronsPartHere query appears with preview results in term_info"""
        print("\n" + "=" * 80)
        print("Testing NeuronsPartHere preview results in term_info")
        print("=" * 80)
        
        term_info = get_term_info(self.medulla_id, preview=True)
        
        self.assertIsNotNone(term_info, "term_info should not be None")
        self.assertIn('Queries', term_info, "term_info should have Queries")
        
        # Find NeuronsPartHere query
        neurons_part_here_query = None
        for query in term_info.get('Queries', []):
            if query.get('query') == 'NeuronsPartHere':
                neurons_part_here_query = query
                break
        
        self.assertIsNotNone(
            neurons_part_here_query,
            "NeuronsPartHere query should be present in term_info"
        )
        
        print(f"✓ NeuronsPartHere query found")
        print(f"  Label: {neurons_part_here_query.get('label', 'Unknown')}")
        print(f"  Preview limit: {neurons_part_here_query.get('preview', 0)}")
        
        # Check preview results
        preview_results = neurons_part_here_query.get('preview_results', {})
        preview_rows = preview_results.get('rows', [])
        
        self.assertGreater(
            len(preview_rows),
            0,
            "Preview results should be populated"
        )
        
        print(f"  Preview results: {len(preview_rows)} items")
        
        # Check that preview results include thumbnails
        with_thumbnails = sum(1 for row in preview_rows if row.get('thumbnail', ''))
        print(f"  Results with example images: {with_thumbnails}/{len(preview_rows)}")
        
        self.assertGreater(
            with_thumbnails,
            0,
            "At least some preview results should have example images"
        )
        
        print(f"\n✓ Preview includes example images")

    def test_neurons_part_here_limit_parameter(self):
        """Test that the limit parameter works correctly"""
        print("\n" + "=" * 80)
        print("Testing NeuronsPartHere limit parameter")
        print("=" * 80)
        
        limit = 10
        results_df = get_neurons_with_part_in(
            self.medulla_id, 
            return_dataframe=True, 
            limit=limit
        )
        
        actual_count = len(results_df)
        
        self.assertLessEqual(
            actual_count,
            limit,
            f"Result count {actual_count} should not exceed limit {limit}"
        )
        
        print(f"✓ Limit parameter working: requested {limit}, got {actual_count}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
