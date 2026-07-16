"""
Regression test for get_term_info on templates that have NO painted anatomical
domains.

VFB_00050000 (L1 larval CNS ssTEM - Cardona/Janelia, the "Seymour" L1EM larval
template) carries a single *empty* template_domain from the pipeline
(index: [], null anatomical_individual). The term_info parser used to do
``int(image.index[0])`` on every domain unconditionally, so the empty index
list raised ``IndexError: list index out of range``. That exception propagated
to get_term_info's ``except IndexError`` handler, which mis-reported it as a
SOLR access failure ("Error accessing SOLR server!") and returned ``None`` —
i.e. the endpoint served ``null`` for a perfectly valid, indexed template.

This test asserts the template resolves to a real term-info object with the
degenerate domain skipped rather than crashing the whole lookup.
"""

import os
import unittest
import sys

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vfbquery.vfb_queries import get_term_info


class TemplateNoPaintedDomainsTest(unittest.TestCase):
    """A template with no painted domains must still resolve, not return null."""

    NO_DOMAIN_TEMPLATE = 'VFB_00050000'  # L1EM larval template ("Seymour")

    def setUp(self):
        # Force the live, synchronous parse path (bypass the two-phase preview
        # warm and the shared production cache) so the fix is actually exercised.
        self._prev_cache = os.environ.get('VFBQUERY_CACHE_ENABLED')
        os.environ['VFBQUERY_CACHE_ENABLED'] = 'false'

    def tearDown(self):
        if self._prev_cache is None:
            os.environ.pop('VFBQUERY_CACHE_ENABLED', None)
        else:
            os.environ['VFBQUERY_CACHE_ENABLED'] = self._prev_cache

    def test_template_without_painted_domains_resolves(self):
        result = get_term_info(self.NO_DOMAIN_TEMPLATE)
        # The regression: this used to be None (-> null over HTTP).
        self.assertIsNotNone(
            result,
            f"get_term_info('{self.NO_DOMAIN_TEMPLATE}') returned None; the empty "
            f"template_domain must be skipped, not crash the whole lookup."
        )
        self.assertEqual(result.get('Id'), self.NO_DOMAIN_TEMPLATE)
        self.assertTrue(result.get('IsTemplate'), "Template flag should be set")
        # An empty/degenerate domain must be dropped, never emitted with a bogus index.
        for idx in (result.get('Domains') or {}):
            self.assertIsNotNone(idx)


if __name__ == '__main__':
    unittest.main()
