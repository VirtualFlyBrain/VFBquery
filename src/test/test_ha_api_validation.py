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


def test_rewrite_resolve_entity_query_falls_back_to_canonical_id(monkeypatch):
    class DummyVfb:
        def get_term_info(self, query, preview=False):
            assert query == "FBst0007144"
            assert preview is False
            return None

    monkeypatch.setattr(ha_api, "_vfb", DummyVfb(), raising=False)

    query = ha_api._rewrite_resolve_entity_query("fbst0007144")

    assert query == "FBst0007144"


def test_run_resolve_entity_falls_back_to_canonical_id_when_id_cannot_be_rewritten(monkeypatch):
    class DummyVfb:
        def get_term_info(self, query, preview=False):
            assert query == "FBst0007144"
            assert preview is False
            return None

        def resolve_entity(self, query):
            assert query == "FBst0007144"
            return {"match_type": "EXACT", "results": [{"uniquename": "FBst0007144"}]}

    monkeypatch.setattr(ha_api, "_vfb", DummyVfb(), raising=False)

    result = ha_api._run_resolve_entity("fbst0007144")

    assert result == {"match_type": "EXACT", "results": [{"uniquename": "FBst0007144"}]}


def test_run_resolve_combination_falls_back_to_canonical_id_when_id_cannot_be_rewritten(monkeypatch):
    class DummyVfb:
        def get_term_info(self, query, preview=False):
            assert query == "FBco0000052"
            assert preview is False
            return None

        def resolve_combination(self, query):
            assert query == "FBco0000052"
            return {"match_type": "EXACT", "results": [{"uniquename": "FBco0000052"}]}

    monkeypatch.setattr(ha_api, "_vfb", DummyVfb(), raising=False)

    result = ha_api._run_resolve_combination("fbco0000052")

    assert result == {"match_type": "EXACT", "results": [{"uniquename": "FBco0000052"}]}


def test_parse_resolver_query_requires_query():
    with pytest.raises(ValueError, match="Missing required parameter: query"):
        ha_api._parse_resolver_query("   ")
