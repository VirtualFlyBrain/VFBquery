"""Tests for the private cache namespace (VFBQUERY_CACHE_NAMESPACE).

The point of the namespace is a safety property, not a feature: a process that
has one must be *incapable* of addressing a production cache document for
writing or deleting. These tests assert that property directly on the generated
Solr ids and on the request bodies, so a future refactor that reintroduces a
hand-built ``f"vfb_query_..."`` somewhere fails here rather than in production.

No Solr server is contacted: requests is stubbed.
"""
import os
import importlib

import pytest

from vfbquery import solr_result_cache as src_mod


@pytest.fixture
def env(monkeypatch):
    """Clean namespace env for each test."""
    for var in ("VFBQUERY_CACHE_NAMESPACE", "VFBQUERY_CACHE_NAMESPACE_FALLBACK",
                "VFBQUERY_CACHE_READONLY", "VFBQUERY_CACHE_ENABLED",
                "VFBQUERY_CACHE_TTL_HOURS"):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


# ---------------------------------------------------------------------------
# id construction
# ---------------------------------------------------------------------------

def test_production_ids_are_unchanged(env):
    """The whole cache depends on this: no namespace => byte-identical ids."""
    assert src_mod.cache_doc_id_for("term_info", "FBbt_00003748") == \
        "vfb_query_term_info_FBbt_00003748"
    assert src_mod.cache_doc_glob() == "vfb_query_*"


def test_namespace_prefixes_the_id(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci-pr83")
    assert src_mod.cache_doc_id_for("term_info", "FBbt_00003748") == \
        "ns_ci_pr83__vfb_query_term_info_FBbt_00003748"


def test_namespace_glob_excludes_production(env):
    """The production sweep and the CI sweep must not see each other's docs."""
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    ns_glob = src_mod.cache_doc_glob()
    assert ns_glob == "ns_ci__vfb_query_*"
    prod_id = src_mod.cache_doc_id_for("term_info", "X", namespace="")
    assert not prod_id.startswith("ns_ci__"), "production id caught by CI glob"
    ns_id = src_mod.cache_doc_id_for("term_info", "X")
    assert not ns_id.startswith("vfb_query_"), "CI id caught by production glob"


def test_branch_names_are_sanitised_into_a_safe_solr_term(env):
    """A raw branch name would break the unescaped `q=id:` term."""
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "fix/silent-noop AND params")
    ns = src_mod.cache_namespace()
    assert ns == "fix_silent_noop_and_params"
    assert all(c.isalnum() or c == "_" for c in ns)


def test_namespace_is_length_capped(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "b" * 200)
    assert len(src_mod.cache_namespace()) == 48


def test_blank_namespace_is_production(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "   ")
    assert src_mod.cache_namespace() == ""
    assert src_mod.cache_doc_id_for("t", "x") == "vfb_query_t_x"


# ---------------------------------------------------------------------------
# TTL
# ---------------------------------------------------------------------------

def test_production_ttl_is_three_months(env):
    assert src_mod.SolrResultCache().ttl_hours == 2160


def test_namespaced_ttl_is_short(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    assert src_mod.SolrResultCache().ttl_hours == 48


def test_explicit_ttl_overrides_both(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    env.setenv("VFBQUERY_CACHE_TTL_HOURS", "6")
    assert src_mod.SolrResultCache().ttl_hours == 6


def test_invalid_ttl_falls_back_rather_than_raising(env):
    env.setenv("VFBQUERY_CACHE_TTL_HOURS", "half a day")
    assert src_mod.SolrResultCache().ttl_hours == 2160


# ---------------------------------------------------------------------------
# read-through fallback
# ---------------------------------------------------------------------------

class _Recorder:
    """Records the ids Solr was asked for, and answers from a dict."""

    def __init__(self, docs):
        self.docs = docs
        self.gets = []
        self.posts = []

    def get(self, url, params=None, timeout=None):
        q = (params or {}).get("q", "")
        self.gets.append(q)
        doc_id = q.split("id:", 1)[1] if "id:" in q else q
        payload = self.docs.get(doc_id)
        docs = [{"cache_data": payload}] if payload is not None else []
        return _Resp(200, {"response": {"docs": docs}})

    def post(self, url, data=None, headers=None, params=None, timeout=None):
        self.posts.append(data)
        return _Resp(200, {})


class _Resp:
    def __init__(self, status, payload):
        self.status_code = status
        self._payload = payload
        self.text = ""

    def json(self):
        return self._payload


def _envelope(cache, result):
    """A cache_data field the reader will accept as fresh and current."""
    import json
    meta = cache._create_cache_metadata(result)
    return src_mod._encode_cache_field(json.dumps(meta))


def _wire(monkeypatch, recorder):
    monkeypatch.setattr(src_mod.requests, "get", recorder.get)
    monkeypatch.setattr(src_mod.requests, "post", recorder.post)


def test_namespace_miss_does_not_read_production_by_default(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    cache = src_mod.SolrResultCache()
    rec = _Recorder({"vfb_query_term_info_X": _envelope(cache, {"name": "prod"})})
    _wire(env, rec)

    assert cache.get_cached_result("term_info", "X") is None
    assert len(rec.gets) == 1, "fell through to production without being asked"


def test_fallback_serves_the_production_entry(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    env.setenv("VFBQUERY_CACHE_NAMESPACE_FALLBACK", "true")
    cache = src_mod.SolrResultCache()
    rec = _Recorder({"vfb_query_term_info_X": _envelope(cache, {"name": "prod"})})
    _wire(env, rec)

    assert cache.get_cached_result("term_info", "X") == {"name": "prod"}
    assert rec.gets == ["id:ns_ci__vfb_query_term_info_X", "id:vfb_query_term_info_X"]


def test_namespace_hit_never_consults_production(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    env.setenv("VFBQUERY_CACHE_NAMESPACE_FALLBACK", "true")
    cache = src_mod.SolrResultCache()
    rec = _Recorder({
        "ns_ci__vfb_query_term_info_X": _envelope(cache, {"name": "branch"}),
        "vfb_query_term_info_X": _envelope(cache, {"name": "prod"}),
    })
    _wire(env, rec)

    assert cache.get_cached_result("term_info", "X") == {"name": "branch"}
    assert len(rec.gets) == 1


def test_fallback_read_never_purges_the_production_entry(env):
    """A corrupt production doc must be skipped, not deleted, by a CI run."""
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    env.setenv("VFBQUERY_CACHE_NAMESPACE_FALLBACK", "true")
    cache = src_mod.SolrResultCache()
    rec = _Recorder({"vfb_query_term_info_X": "gz:not-actually-gzip"})
    _wire(env, rec)

    assert cache.get_cached_result("term_info", "X") is None
    assert rec.posts == [], "a namespaced run deleted a production document"


# ---------------------------------------------------------------------------
# writes
# ---------------------------------------------------------------------------

def test_writes_land_in_the_namespace_only(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    cache = src_mod.SolrResultCache()
    rec = _Recorder({})
    _wire(env, rec)

    assert cache.cache_result("term_info", "X", {"name": "branch"}) is True
    body = "".join(str(p) for p in rec.posts)
    assert "ns_ci__vfb_query_term_info_X" in body
    assert '"id": "vfb_query_term_info_X"' not in body


def test_clear_entry_targets_the_namespace_only(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    cache = src_mod.SolrResultCache()
    rec = _Recorder({})
    _wire(env, rec)

    cache.clear_cache_entry("term_info", "X")
    assert rec.posts == ["<delete><id>ns_ci__vfb_query_term_info_X</id></delete>"]


# ---------------------------------------------------------------------------
# purge_namespace
# ---------------------------------------------------------------------------

def test_purge_namespace_refuses_to_wipe_production(env):
    cache = src_mod.SolrResultCache()
    rec = _Recorder({})
    _wire(env, rec)

    assert cache.purge_namespace() is False
    assert rec.posts == [], "purge with no namespace issued a delete"


def test_purge_namespace_refuses_an_explicit_empty_namespace(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    cache = src_mod.SolrResultCache()
    rec = _Recorder({})
    _wire(env, rec)

    assert cache.purge_namespace("") is False
    assert rec.posts == []


def test_purge_namespace_deletes_only_its_own_prefix(env):
    env.setenv("VFBQUERY_CACHE_NAMESPACE", "ci")
    cache = src_mod.SolrResultCache()
    rec = _Recorder({})
    _wire(env, rec)

    assert cache.purge_namespace() is True
    assert rec.posts == [
        "<delete><query>id:ns_ci__vfb_query_*</query></delete>"]
