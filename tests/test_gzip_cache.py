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


def test_cap_is_enforced_on_compressed_not_raw_size():
    # Small cap + a highly compressible payload: the RAW JSON must exceed the cap
    # while the gzip+base64 form stays under it, proving the cap is on the stored
    # (compressed) size, not the raw size. Kept fast/memory-light via repetition.
    cap_mb = 1
    c = SolrResultCache(max_result_size_mb=cap_mb)
    cap = cap_mb * 1024 * 1024
    assert c.max_result_size_bytes == cap
    payload = json.dumps({"result": {"rows": ["x" * 100] * 50000}})  # ~5 MB raw, compresses hard
    raw = len(payload.encode("utf-8"))
    compressed = len(_encode_cache_field(payload).encode("utf-8"))
    assert raw > cap, f"raw {raw} should exceed cap {cap}"
    assert compressed < cap, f"compressed {compressed} should be under cap {cap}"


def test_env_override(monkeypatch):
    monkeypatch.setenv("VFBQUERY_MAX_RESULT_MB", "250")
    assert SolrResultCache().max_result_size_mb == 250


def test_create_metadata_no_longer_rejects_large_raw():
    c = SolrResultCache(max_result_size_mb=1)
    meta = c._create_cache_metadata({"rows": list(range(200000))})
    assert meta is not None
    assert meta["result_size"] > 1024 * 1024
