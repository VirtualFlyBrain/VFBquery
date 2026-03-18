"""Tests for flybase_combo_pubs module — combination resolution and publication lookup."""
import pytest

from vfbquery.flybase_combo_pubs import resolve_combination, find_combo_publications

KNOWN_COMBO_ID = "FBco0000052"
KNOWN_COMBO_SYNONYM = "MB002B"
KNOWN_PUB_FBRF = "FBrf0227179"
NONEXISTENT_COMBO = "NONEXISTENT_COMBO_XYZ"


# ---------------------------------------------------------------------------
# resolve_combination tests
# ---------------------------------------------------------------------------


class TestResolveCombinationByID:
    @pytest.mark.integration
    def test_known_combo_id(self):
        result = resolve_combination(KNOWN_COMBO_ID)
        assert result["match_type"] == "EXACT"
        assert any(r["uniquename"] == KNOWN_COMBO_ID for r in result["results"])


class TestResolveCombinationSynonym:
    @pytest.mark.integration
    def test_synonym_resolves(self):
        result = resolve_combination(KNOWN_COMBO_SYNONYM)
        assert result["match_type"] == "SYNONYM"
        assert any(r["uniquename"] == KNOWN_COMBO_ID for r in result["results"])

    @pytest.mark.integration
    def test_synonym_shows_matched_synonym(self):
        result = resolve_combination(KNOWN_COMBO_SYNONYM)
        assert any(
            r.get("matched_synonym") == KNOWN_COMBO_SYNONYM
            for r in result["results"]
        )


class TestResolveCombinationBroadMatch:
    @pytest.mark.integration
    def test_broad_match_partial_name(self):
        result = resolve_combination("R14C08")
        assert result["match_type"] in ("EXACT", "SYNONYM", "BROAD")
        assert any("FBco" in r["uniquename"] for r in result["results"])


class TestResolveCombinationNotFound:
    @pytest.mark.integration
    def test_nonexistent_name(self):
        result = resolve_combination(NONEXISTENT_COMBO)
        assert result["match_type"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# find_combo_publications tests
# ---------------------------------------------------------------------------


class TestFindComboPublications:
    @pytest.mark.integration
    def test_find_pubs_for_known_combo(self):
        pubs = find_combo_publications(KNOWN_COMBO_ID)
        assert len(pubs) > 0
        assert any(p["fbrf"] == KNOWN_PUB_FBRF for p in pubs)

    @pytest.mark.integration
    def test_pubs_have_expected_keys(self):
        pubs = find_combo_publications(KNOWN_COMBO_ID)
        assert len(pubs) > 0
        expected_keys = {"fbrf", "title", "year", "miniref", "pub_type", "doi", "pmid", "pmcid"}
        for p in pubs:
            assert expected_keys.issubset(p.keys())

    @pytest.mark.integration
    def test_pubs_have_doi(self):
        pubs = find_combo_publications(KNOWN_COMBO_ID)
        has_doi = any(p.get("doi", "").startswith("10.") for p in pubs)
        assert has_doi, "Expected at least one publication with a DOI"


class TestFindComboPublicationsEdgeCases:
    @pytest.mark.integration
    def test_nonexistent_combo(self):
        pubs = find_combo_publications("FBco9999999")
        assert pubs == []

    def test_invalid_id_prefix(self):
        with pytest.raises(ValueError, match="Expected FBco"):
            find_combo_publications("FBgn0000490")
