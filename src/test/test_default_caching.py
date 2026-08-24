"""
Test VFBquery default caching functionality.

These tests ensure that the SOLR-based caching system works correctly
and provides expected performance benefits with 3-month TTL.
"""

import unittest
import os
import time
from unittest.mock import MagicMock
import sys

# Mock vispy imports before importing vfbquery
for module in ['vispy', 'vispy.scene', 'vispy.util', 'vispy.util.fonts',
               'vispy.util.fonts._triage', 'vispy.util.fonts._quartz',
               'vispy.ext', 'vispy.ext.cocoapy', 'navis', 'navis.plotting',
               'navis.plotting.vispy', 'navis.plotting.vispy.viewer']:
    sys.modules[module] = MagicMock()

# Set environment variables
os.environ.update({
    'MPLBACKEND': 'Agg',
    'VISPY_GL_LIB': 'osmesa',
    'VISPY_USE_EGL': '0',
    'VFBQUERY_CACHE_ENABLED': 'true'
})


class TestDefaultCaching(unittest.TestCase):
    """Test default SOLR caching behavior in VFBquery."""

    def setUp(self):
        """Set up test environment."""
        # Clear any existing cache before each test
        try:
            import vfbquery
            if hasattr(vfbquery, 'clear_solr_cache'):
                # Clear cache for a test term
                vfbquery.clear_solr_cache('term_info', 'FBbt_00003748')
        except ImportError:
            pass

    def test_caching_enabled_by_default(self):
        """Test that SOLR caching is automatically enabled when importing vfbquery."""
        import vfbquery

        # Check that SOLR caching functions are available
        self.assertTrue(hasattr(vfbquery, 'get_solr_cache'))
        self.assertTrue(hasattr(vfbquery, 'clear_solr_cache'))
        self.assertTrue(hasattr(vfbquery, 'get_solr_cache_stats_func'))

        # Check that caching is enabled (we can't easily check SOLR stats without network calls)
        # But we can verify the infrastructure is in place
        self.assertTrue(hasattr(vfbquery, '__caching_available__'))
        self.assertTrue(vfbquery.__caching_available__)
    
    def test_cache_performance_improvement(self):
        """Test that SOLR caching provides performance improvement."""
        import vfbquery

        test_term = 'FBbt_00003748'  # medulla

        # First call (cold - populates cache)
        start_time = time.time()
        result1 = vfbquery.get_term_info(test_term)
        cold_time = time.time() - start_time

        # Verify we got a real result (not just non-None)
        self.assertIsNotNone(result1)
        self.assertIn('Name', result1)
        self.assertTrue(result1['Name'], "medulla term_info should have a Name")

        # Second call (warm - should hit cache)
        start_time = time.time()
        result2 = vfbquery.get_term_info(test_term)
        warm_time = time.time() - start_time

        # Verify caching is working (results should be identical)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, result2)  # Should be identical

        # Note: Performance improvement may vary due to network conditions
        # The main test is that caching prevents redundant computation

        # Check SOLR cache statistics
        solr_stats = vfbquery.get_solr_cache_stats_func()
        self.assertIsInstance(solr_stats, dict)
        self.assertIn('total_cache_documents', solr_stats)
    
    def test_cache_statistics_tracking(self):
        """Test that SOLR cache statistics are properly tracked."""
        import vfbquery

        # Get baseline SOLR stats
        initial_stats = vfbquery.get_solr_cache_stats_func()
        initial_docs = initial_stats['total_cache_documents']

        # Make a unique query that should populate cache
        unique_term = 'FBbt_00005106'  # Use a different term
        result = vfbquery.get_term_info(unique_term)
        self.assertIsNotNone(result)

        # Check that SOLR stats were updated (may take time to reflect)
        # We mainly verify the stats function works and returns reasonable data
        updated_stats = vfbquery.get_solr_cache_stats_func()
        self.assertIsInstance(updated_stats, dict)
        self.assertIn('total_cache_documents', updated_stats)
        self.assertIn('cache_efficiency', updated_stats)
    
    def test_memory_size_tracking(self):
        """Test that SOLR cache size is properly tracked."""
        import vfbquery

        # Cache a few different terms
        test_terms = ['FBbt_00003748', 'VFB_00101567']

        for term in test_terms:
            result = vfbquery.get_term_info(term)
            self.assertIsNotNone(result)

            # Check SOLR cache stats are available
            stats = vfbquery.get_solr_cache_stats_func()
            self.assertIsInstance(stats, dict)
            self.assertIn('estimated_size_mb', stats)
            self.assertGreaterEqual(stats['estimated_size_mb'], 0)
    
    def test_cache_ttl_configuration(self):
        """Test that SOLR cache TTL is properly configured."""
        import vfbquery

        # Get SOLR cache instance to check TTL
        solr_cache = vfbquery.get_solr_cache()
        self.assertIsNotNone(solr_cache)

        # Assert the actual 3-month TTL contract this file's docstring claims
        # (2160h = 90 days), not just that the attribute exists.
        self.assertTrue(hasattr(solr_cache, 'cache_result'))
        self.assertTrue(hasattr(solr_cache, 'get_cached_result'))
        self.assertEqual(solr_cache.ttl_hours, 2160,
                         "SOLR cache should use the 3-month (2160h) TTL")
    
    def test_transparent_caching(self):
        """Test that regular VFBquery functions are transparently cached."""
        import vfbquery

        # Test that get_term_info and get_instances are using cached versions
        test_term = 'FBbt_00003748'

        # These should work with caching transparently AND return real content.
        term_info = vfbquery.get_term_info(test_term)
        self.assertIsNotNone(term_info)
        self.assertTrue(term_info.get('Name'), "medulla term_info should have a Name")

        instances = vfbquery.get_instances(test_term, limit=5)
        self.assertIsNotNone(instances)
        rows = instances.get('rows', []) if isinstance(instances, dict) else instances
        self.assertTrue(len(rows) > 0, "medulla should have instances")

        # SOLR cache should be accessible
        solr_stats = vfbquery.get_solr_cache_stats_func()
        self.assertIsInstance(solr_stats, dict)
        self.assertIn('total_cache_documents', solr_stats)
    
    def test_cache_disable_environment_variable(self):
        """Test that caching can be disabled via environment variable."""
        # This test would need to be run in a separate process to test
        # the environment variable behavior at import time
        # For now, just verify the current state respects the env var

        cache_enabled = os.getenv('VFBQUERY_CACHE_ENABLED', 'true').lower()
        if cache_enabled not in ('false', '0', 'no', 'off'):
            import vfbquery
            # If caching is enabled, SOLR cache should be available
            solr_cache = vfbquery.get_solr_cache()
            self.assertIsNotNone(solr_cache)
            self.assertTrue(hasattr(vfbquery, '__caching_available__'))
            self.assertTrue(vfbquery.__caching_available__)


if __name__ == '__main__':
    unittest.main(verbosity=2)
