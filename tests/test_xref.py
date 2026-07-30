"""Unit tests for the /xref shaping helpers.

These are the parts of ``/xref`` that decide *correctness* rather than
plumbing: which xrefs a ``db`` filter keeps, and what a row looks like. They run
offline against fixture ``term_info`` so a failure means the logic changed, not
that Solr was slow. The round-trip against the live index is exercised by the
client's ``VFB_LIVE_TESTS`` smoke test instead.
"""
import json

import pytest

from vfbquery.ha_api import (_parse_term_info, _xref_available_dbs,
                             _xref_db_candidates, _xref_filter_by_db,
                             _xref_matches_db, _xref_normalise, _xref_rows,
                             _xref_site_names, _xref_tokens)

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


@pytest.mark.parametrize("db,expect", [
    # A whole word of a site name resolves. These are the strings a caller
    # reaches for first — the live report's usability trap was `db=flywire`
    # returning nothing because only the symbol `fw` was accepted.
    ("neuprint", ["1734350908"]),
    ("hemibrain", ["1734350908"]),
    ("Hemibrain", ["1734350908"]),
    ("neuprint hemibrain", ["1734350908"]),
    # ...and a prefix, as the last resort.
    ("neuronbr", ["hemibrain:1734350908"]),
])
def test_db_accepts_a_nickname_when_nothing_matches_exactly(db, expect):
    assert [r["accession"] for r in
            _xref_rows("VFB_jrchjtdb", TERM_INFO, db=db)] == expect


def test_an_exact_name_wins_outright_over_any_nickname_pass():
    """`db=hb` is the symbol of one site, so it must not widen.

    This is the invariant that keeps the nickname passes safe: they are only
    consulted when the exact pass found nothing, so adding them cannot change
    the meaning of a `db` that was already a real name. Without it, `fw` would
    start dragging in anything whose label happens to contain those letters.
    """
    assert [r["accession"] for r in
            _xref_rows("VFB_jrchjtdb", TERM_INFO, db="hb")] == ["1734350908"]
    # 'neuronbridge' is an exact short_form/label, and stays exact even though
    # it is also a prefix of nothing else here.
    assert [r["accession"] for r in
            _xref_rows("VFB_jrchjtdb", TERM_INFO, db="neuronbridge")] == \
        ["hemibrain:1734350908"]


def test_db_is_not_matched_as_a_bare_substring():
    """No substring-anywhere pass: 'rint' and 'cns' must stay meaningless.

    Whole words and prefixes are guessable by a human; an arbitrary substring is
    not, and a filter that matches on one stops narrowing anything.
    """
    assert _xref_rows("VFB_jrchjtdb", TERM_INFO, db="rint") == []
    assert _xref_rows("VFB_jrchjtdb", TERM_INFO, db="ridge") == []
    assert _xref_rows("VFB_jrchjtdb", TERM_INFO, db="notadatabase") == []


def test_a_db_naming_two_sites_returns_both():
    """'neuprint' really does name two live sites; both rows is the honest answer."""
    info = {"term": {"core": {"label": "L"}}, "xrefs": [
        {"accession": "1", "site": {
            "symbol": "hb", "short_form": "neuprint_JRC_Hemibrain_1point2point1",
            "label": "Neuprint web interface - hemibrain:v1.2.1"}},
        {"accession": "2", "site": {
            "symbol": "mc", "short_form": "male_cns_v0_9",
            "label": "Neuprint web interface - male-cns:v0.9"}},
    ]}
    assert [r["accession"] for r in _xref_rows("X", info, db="neuprint")] == \
        ["1", "2"]
    # ...while each site's own symbol still selects exactly one of them.
    assert [r["accession"] for r in _xref_rows("X", info, db="hb")] == ["1"]
    assert [r["accession"] for r in _xref_rows("X", info, db="male-cns")] == ["2"]


def test_flywire_nickname_resolves_the_fw_site():
    """The exact case from the live test report: db=flywire used to give 0 rows."""
    info = {"term": {"core": {"label": "L"}}, "xrefs": [
        {"accession": "720575940604407468", "site": {
            "symbol": "fw", "short_form": "flywire783",
            "label": "FlyWire web interface v783"}},
    ]}
    for db in ("flywire", "FlyWire", "flywire783", "fw",
               "FlyWire web interface v783", "flywire web interface v783"):
        assert len(_xref_rows("X", info, db=db)) == 1, db


def test_normalise_and_tokens():
    assert _xref_normalise("Neuprint web interface - hemibrain:v1.2.1") == \
        "neuprintwebinterfacehemibrainv121"
    assert _xref_normalise(None) == ""
    # Digits split from letters, so 'flywire783' offers 'flywire' as a word.
    assert _xref_tokens("flywire783") == {"flywire", "783"}
    assert _xref_tokens("male_cns_v0_9") == {"male", "cns", "v", "0", "9"}


def test_db_candidates_is_empty_for_an_unmatched_name():
    assert _xref_db_candidates([{"symbol": "fw"}], "zzz") == set()
    assert _xref_db_candidates([], "fw") == set()
    assert _xref_db_candidates([{"symbol": "fw"}], "") == set()


def test_filter_reports_what_matched_and_what_was_available():
    rows = _xref_rows("VFB_jrchjtdb", TERM_INFO)
    kept, matched = _xref_filter_by_db(rows, "hemibrain")
    assert [r["accession"] for r in kept] == ["1734350908"]
    assert matched == {"hb"}

    # A miss is distinguishable from "no xrefs": empty rows, empty matched set.
    kept, matched = _xref_filter_by_db(rows, "notadatabase")
    assert kept == [] and matched == set()

    # No filter at all -> everything, and matched is None rather than empty,
    # so a handler can tell "did not filter" from "filtered and missed".
    kept, matched = _xref_filter_by_db(rows, None)
    assert len(kept) == 2 and matched is None

    assert _xref_available_dbs(rows) == [
        {"db": "hb", "db_label": "Neuprint web interface - hemibrain:v1.2.1"},
        {"db": "neuronbridge"},     # label equals db, so not repeated
    ]


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
