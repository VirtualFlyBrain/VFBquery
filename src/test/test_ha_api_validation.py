"""Unit tests for HA API resolver query normalization and rewriting."""

import pytest

import vfbquery.ha_api as ha_api


def test_parse_resolver_query_trims_whitespace():
    query = ha_api._parse_resolver_query("  P{VT054895-GAL4.DBD}  ")

    assert query == "P{VT054895-GAL4.DBD}"


def test_rewrite_resolve_entity_query_uses_name_for_feature_ids(monkeypatch):
    class DummyVfb:
        def get_term_info(self, query, preview=False):
            assert query == "FBgn0000490"
            assert preview is False
            return {"Name": "dpp"}

    monkeypatch.setattr(ha_api, "_vfb", DummyVfb(), raising=False)

    query = ha_api._rewrite_resolve_entity_query("fbGN0000490")

    assert query == "dpp"


def test_rewrite_resolve_combination_query_uses_name_for_fbco_ids(monkeypatch):
    class DummyVfb:
        def get_term_info(self, query, preview=False):
            assert query == "FBco0000052"
            assert preview is False
            return {"Name": "GMR37H08-ZpGAL4DBD in attP2"}

    monkeypatch.setattr(ha_api, "_vfb", DummyVfb(), raising=False)

    query = ha_api._rewrite_resolve_combination_query("fbco0000052")

    assert query == "GMR37H08-ZpGAL4DBD in attP2"


def test_rewrite_resolve_entity_query_returns_none_when_no_term_info_name(monkeypatch):
    class DummyVfb:
        def get_term_info(self, query, preview=False):
            assert query == "FBst0007144"
            assert preview is False
            return None

    monkeypatch.setattr(ha_api, "_vfb", DummyVfb(), raising=False)

    query = ha_api._rewrite_resolve_entity_query("fbst0007144")

    assert query is None


def test_run_resolve_entity_returns_not_found_when_id_cannot_be_rewritten(monkeypatch):
    class DummyVfb:
        def get_term_info(self, query, preview=False):
            assert query == "FBst0007144"
            assert preview is False
            return None

        def resolve_entity(self, query):
            raise AssertionError("Chado resolver should not receive raw IDs")

    monkeypatch.setattr(ha_api, "_vfb", DummyVfb(), raising=False)

    result = ha_api._run_resolve_entity("fbst0007144")

    assert result == {"match_type": "NOT_FOUND", "results": []}


def test_run_resolve_combination_returns_not_found_when_id_cannot_be_rewritten(monkeypatch):
    class DummyVfb:
        def get_term_info(self, query, preview=False):
            assert query == "FBco0000052"
            assert preview is False
            return None

        def resolve_combination(self, query):
            raise AssertionError("Chado resolver should not receive raw IDs")

    monkeypatch.setattr(ha_api, "_vfb", DummyVfb(), raising=False)

    result = ha_api._run_resolve_combination("fbco0000052")

    assert result == {"match_type": "NOT_FOUND", "results": []}


def test_parse_resolver_query_requires_query():
    with pytest.raises(ValueError, match="Missing required parameter: query"):
        ha_api._parse_resolver_query("   ")
