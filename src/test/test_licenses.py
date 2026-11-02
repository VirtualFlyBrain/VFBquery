"""Licence records: a term with no licence comes back from the term query as one
all-null record, which the page would show as an empty Licence row."""
from vfbquery.vfb_queries import _real_licenses

LIC = {"iri": "http://virtualflybrain.org/reports/VFBlicense_CC_BY_4_0",
       "short_form": "VFBlicense_CC_BY_4_0", "label": "CC-BY_4.0", "icon": "",
       "source_iri": "", "source": ""}
NULL = {"iri": None, "short_form": None, "label": "", "icon": "", "source_iri": None, "source": ""}


def test_null_licence_dropped():
    assert _real_licenses({0: NULL}) == {}


def test_real_licences_kept_and_renumbered():
    assert _real_licenses({0: NULL, 1: LIC}) == {0: LIC}
    assert _real_licenses({0: LIC}) == {0: LIC}


def test_stock_page_has_no_empty_licence():
    """Live: a FlyBase stock has no licence; its term info must not carry an
    all-null one. A dataset keeps its licence."""
    from vfbquery.vfb_queries import get_term_info
    from .scrnaseq_fixtures import dataset_with_clusters
    stock = get_term_info("FBst0005905")
    assert stock and stock["Licenses"] == {}
    dataset = get_term_info(dataset_with_clusters("VFBseq_00001468"))
    assert dataset and any(l.get("short_form") for l in dataset["Licenses"].values())
