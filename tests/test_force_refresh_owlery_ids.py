"""A forced refresh must rebuild the cached Owlery id list, not just the result above it.

Found 2026-10-12: after the BANC v888 load the live Owlery returned 3206 ImagesNeurons for
FBbt_00040051 while the cache held 2678. ``force_refresh`` cleared the ``images_neurons`` result and
recomputed it from the still-cached ``owlery_ids`` list, so every refresh returned the same stale 2678
("Force refresh requested ... Cache hit for owlery_ids" in the server log). The result decorator now
raises a flag for the duration of a forced call and ``_owlery_query_to_results`` passes it on.

Caching is switched off for these tests (VFBQUERY_CACHE_ENABLED=false) so nothing touches Solr: what is
asserted is that the flag reaches the id-list layer, which is the seam that was missing.
"""
import pytest

from vfbquery import solr_result_cache as src
from vfbquery import vfb_queries


@pytest.fixture(autouse=True)
def _no_solr(monkeypatch):
    monkeypatch.setenv("VFBQUERY_CACHE_ENABLED", "false")


def test_flag_is_off_by_default_and_restored():
    @src.with_solr_cache('images_neurons')
    def probe(short_form, **kw):
        return src.force_fresh_active()

    assert probe("FBbt_1") is False
    assert probe("FBbt_1", force_refresh=True) is True
    assert src.force_fresh_active() is False          # reset after the call


def test_term_info_does_not_raise_the_flag():
    # get_term_info's force path fans out to every query preview; it forwards force_refresh itself.
    @src.with_solr_cache('term_info')
    def probe(short_form, **kw):
        return src.force_fresh_active()

    assert probe("FBbt_1", force_refresh=True) is False


def test_flag_reaches_the_owlery_id_list(monkeypatch):
    seen = []

    def fake_ids(owl_key, owl_query, **kw):
        seen.append(kw.get('force_refresh'))
        return []

    monkeypatch.setattr(vfb_queries, "_owlery_ids_cached", fake_ids)
    vfb_queries.get_images_neurons("FBbt_00040051", return_dataframe=False)
    vfb_queries.get_images_neurons("FBbt_00040051", return_dataframe=False, force_refresh=True)
    assert seen == [False, True]
