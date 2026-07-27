"""Unit tests for the /xref shaping helpers.

These are the parts of ``/xref`` that decide *correctness* rather than
plumbing: which xrefs a ``db`` filter keeps, and what a row looks like. They run
offline against fixture ``term_info`` so a failure means the logic changed, not
that Solr was slow. The round-trip against the live index is exercised by the
client's ``VFB_LIVE_TESTS`` smoke test instead.
"""
import json

import pytest

from vfbquery.ha_api import (_parse_term_info, _xref_matches_db, _xref_rows,
                             _xref_site_names)

# Trimmed from the real VFB_jrchjtdb document: two sites, one of which is the
# data source, and a link that has to be assembled from base + accession.
TERM_INFO = {
    "term": {"core": {"short_form": "VFB_jrchjtdb", "symbol": "DA1_lPN_R",
                      "label": "DA1_lPN_R (FlyEM-HB:1734350908)"}},
    "xrefs": [
        {"accession": "1734350908", "is_data_source": True,
         "link_base": "https://neuprint.janelia.org/results?q=", "link_postfix": "",
         "site": {"symbol": "hb",
                  "short_form": "neuprint_JRC_Hemibrain_1point2point1",
                  "label": "Neuprint web interface - hemibrain:v1.2.1"}},
        {"accession": "hemibrain:1734350908", "is_data_source": False,
         "link_base": "https://neuronbridge.janelia.org/search?q=",
         "link_postfix": "&x=1",
         "site": {"symbol": "", "short_form": "neuronbridge",
                  "label": "neuronbridge"}},
    ],
}


def test_rows_carry_id_label_and_assembled_link():
    rows = _xref_rows("VFB_jrchjtdb", TERM_INFO)
    assert [r["accession"] for r in rows] == ["1734350908", "hemibrain:1734350908"]
    assert all(r["id"] == "VFB_jrchjtdb" for r in rows)
    assert all(r["label"] == "DA1_lPN_R (FlyEM-HB:1734350908)" for r in rows)
    assert rows[0]["link"].endswith("q=1734350908")
    assert rows[1]["link"].endswith("q=hemibrain:1734350908&x=1")   # postfix kept
    assert rows[0]["is_data_source"] is True and rows[1]["is_data_source"] is False


def test_db_falls_back_to_short_form_when_symbol_is_blank():
    """neuronbridge has no symbol, so `db` has to match on short_form/label.

    Without the fallback that site would be unaddressable — silently, since an
    unmatched filter just returns nothing.
    """
    rows = _xref_rows("VFB_jrchjtdb", TERM_INFO, db="neuronbridge")
    assert len(rows) == 1 and rows[0]["accession"] == "hemibrain:1734350908"
    assert rows[0]["db"] == "neuronbridge"      # display falls back too


@pytest.mark.parametrize("db", ["hb", "neuprint_JRC_Hemibrain_1point2point1",
                                "Neuprint web interface - hemibrain:v1.2.1", "HB"])
def test_db_accepts_symbol_short_form_or_label_case_insensitively(db):
    rows = _xref_rows("VFB_jrchjtdb", TERM_INFO, db=db)
    assert [r["accession"] for r in rows] == ["1734350908"]


def test_db_is_matched_whole_not_as_a_substring():
    """'neuprint' must not match 'neuprint_JRC_Hemibrain_1point2point1'.

    A substring match would make `db` quietly ambiguous across sites that share
    a prefix, which is worse than returning nothing and being asked again.
    """
    assert _xref_rows("VFB_jrchjtdb", TERM_INFO, db="neuprint") == []


def test_no_db_returns_every_xref():
    assert len(_xref_rows("VFB_jrchjtdb", TERM_INFO)) == 2


def test_missing_or_malformed_pieces_do_not_raise():
    assert _xref_rows("X", {}) == []
    assert _xref_rows("X", {"xrefs": None}) == []
    assert _xref_rows("X", {"term": None, "xrefs": [{"accession": "1"}]})[0]["label"] == ""
    # No link_base -> no invented link, rather than a broken one.
    assert _xref_rows("X", {"xrefs": [{"accession": "1"}]})[0]["link"] == ""
    assert _xref_site_names(None) == []
    assert _xref_matches_db(None, "hb") is False
    assert _xref_matches_db(None, None) is True     # no filter, nothing to fail


def test_label_falls_back_to_symbol_when_absent():
    info = {"term": {"core": {"symbol": "DA1_lPN_R"}}, "xrefs": [{"accession": "1"}]}
    assert _xref_rows("X", info)[0]["label"] == "DA1_lPN_R"


def test_parse_term_info_unwraps_solr_list_and_survives_junk():
    assert _parse_term_info({"term_info": [json.dumps({"a": 1})]}) == {"a": 1}
    assert _parse_term_info({"term_info": json.dumps({"a": 1})}) == {"a": 1}
    assert _parse_term_info({"term_info": None}) is None
    assert _parse_term_info({}) is None
    assert _parse_term_info({"term_info": "{not json"}) is None
