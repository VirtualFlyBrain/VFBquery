"""Xref.link(): an accession is only joined onto a link_base; without one the
link falls back to the site's homepage, then its iri, instead of emitting the
bare accession as a broken relative URL (seen as
``/org.geppetto.frontend/sample-1099`` on the Randel2026 dataset page)."""
from vfbquery.term_info_queries import MinimalEntityInfo, Xref

SITE = MinimalEntityInfo(short_form="larva1099_activity", iri="http://virtualflybrain.org/reports/larva1099_activity",
                         label="Larva1099 whole-brain calcium imaging")


def test_accession_with_link_base_builds_the_external_link():
    x = Xref(site=SITE, link_base="https://vfb.neuroglass.io/studies/", accession="06aeb579", link_postfix="")
    assert x.link() == "https://vfb.neuroglass.io/studies/06aeb579"


def test_accession_without_link_base_falls_back_to_homepage():
    x = Xref(site=SITE, homepage="https://vfb.neuroglass.io/studies/06aeb579", accession="sample-1099")
    assert x.link() == "https://vfb.neuroglass.io/studies/06aeb579"


def test_accession_without_link_base_or_homepage_falls_back_to_site_iri():
    x = Xref(site=SITE, accession="463")
    assert x.link() == SITE.iri


def test_none_postfix_is_tolerated():
    x = Xref(site=SITE, link_base="https://example.org/?q=", accession="1", link_postfix=None)
    assert x.link() == "https://example.org/?q=1"
