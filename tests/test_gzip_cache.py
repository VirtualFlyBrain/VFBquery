"""Unit tests for gzip-compressed Solr cache payloads (no network)."""
import json
from vfbquery.solr_result_cache import (
    _encode_cache_field, _decode_cache_field, _CACHE_GZIP_PREFIX, SolrResultCache,
)


def test_roundtrip_compresses_and_restores():
    env = json.dumps({"result": {"rows": list(range(5000))}, "cached_at": "x"})
    enc = _encode_cache_field(env)
    assert enc.startswith(_CACHE_GZIP_PREFIX)
    assert len(enc) < len(env)
    assert _decode_cache_field(enc) == env


def test_decode_handles_legacy_plain_json_and_list_shape():
    legacy = json.dumps({"result": 1})
    assert _decode_cache_field(legacy) == legacy
    assert _decode_cache_field([legacy]) == legacy
    enc = _encode_cache_field(legacy)
    assert _decode_cache_field([enc]) == legacy


def test_cap_is_on_compressed_size():
    c = SolrResultCache(max_result_size_mb=100)
    assert c.max_result_size_bytes == 100 * 1024 * 1024
    big = {"result": {"rows": [{"id": i, "name": "n"} for i in range(300000)]},
           "cached_at": "2026-01-01T00:00:00+00:00",
           "expires_at": "2026-04-01T00:00:00+00:00", "result_size": 0}
    enc = _encode_cache_field(json.dumps(big))
    assert len(enc.encode("utf-8")) < c.max_result_size_bytes


def test_env_override(monkeypatch):
    monkeypatch.setenv("VFBQUERY_MAX_RESULT_MB", "250")
    assert SolrResultCache().max_result_size_mb == 250


def test_create_metadata_no_longer_rejects_large_raw():
    c = SolrResultCache(max_result_size_mb=1)
    meta = c._create_cache_metadata({"rows": list(range(200000))})
    assert meta is not None
    assert meta["result_size"] > 1024 * 1024
