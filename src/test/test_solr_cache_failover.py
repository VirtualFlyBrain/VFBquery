import unittest
from unittest.mock import MagicMock, patch

import requests

from vfbquery.solr_result_cache import SolrResultCache


class SolrResultCacheFailoverTest(unittest.TestCase):
    def test_disable_and_reenable_on_solr_failure(self):
        cache = SolrResultCache()
        cache._solr_backoff_seconds = 10

        # First, cause a caching failure (Solr write times out)
        with patch("vfbquery.solr_result_cache.time.time", return_value=1000), \
             patch("vfbquery.solr_result_cache.requests.post") as post:
            post.side_effect = requests.exceptions.ReadTimeout()
            ok = cache.cache_result("term_info", "FBbt_00000000", {"foo": "bar"})
            self.assertFalse(ok)
            self.assertTrue(cache._solr_disabled)
            self.assertGreater(cache._solr_disabled_until, 1000)
            self.assertEqual(post.call_count, 1)

            # Subsequent cache attempts should not hit Solr again during backoff
            ok2 = cache.cache_result("term_info", "FBbt_00000000", {"foo": "bar"})
            self.assertFalse(ok2)
            self.assertEqual(post.call_count, 1)

        # Advance time past backoff and allow a successful Solr health check
        with patch("vfbquery.solr_result_cache.time.time", return_value=cache._solr_disabled_until + 1), \
             patch("vfbquery.solr_result_cache.requests.get") as get:
            get.return_value = MagicMock(status_code=200, json=lambda: {"response": {"docs": []}})

            # get_cached_result triggers a health check and should re-enable caching
            res = cache.get_cached_result("term_info", "FBbt_00000000")
            self.assertIsNone(res)
            self.assertFalse(cache._solr_disabled)
            # One call for the health check, one for the cache query itself
            self.assertGreaterEqual(get.call_count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
