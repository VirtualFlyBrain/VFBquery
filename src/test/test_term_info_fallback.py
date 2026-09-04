"""Unit tests for the term_info SOLR fallback.

No backend and no indexer checkout required: the parts that talk to Neo4j
and SOLR are exercised elsewhere (live) and are deliberately not mocked
here. What is worth pinning without a backend is the type dispatch, the
exclusions, the write guard and the ``src`` import shim -- the pieces that
decide *whether* the fallback acts, and that would fail silently.
"""
import os
import sys

import pytest

from vfbquery import term_info_fallback as tif


# ---------------------------------------------------------------------------
# Type dispatch -- mirrors the indexers' get_parameters_query predicates
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("labels,expected", [
    # The case that prompted all this: a painted domain with no SOLR doc.
    (["Entity", "Individual", "Adult", "Anatomy", "Nervous_system",
      "Synaptic_neuropil", "Synaptic_neuropil_domain", "has_image"],
     "anatomical_ind"),
    # Individual sub-types are checked before the catch-all, exactly as the
    # anatomical indexer's query excludes each of them.
    (["Individual", "Template", "Anatomy"], "template"),
    (["Individual", "License"], "license"),
    (["Individual", "DataSet"], "dataset"),
    (["Individual", "pub"], "pub"),
    (["Individual", "Cluster"], "cluster"),
    # Classes split three ways.
    (["Class", "Neuron"], "neuron_class"),
    (["Class", "Split"], "split_class"),
    (["Class", "Anatomy"], "class"),
])
def test_dispatch_matches_the_indexer_populations(labels, expected):
    assert tif.choose_indexer(labels) == expected


def test_dispatch_declines_what_no_indexer_covers():
    assert tif.choose_indexer(["Property"]) is None
    assert tif.choose_indexer([]) is None
    assert tif.choose_indexer(None) is None


def test_template_wins_over_individual():
    """A Template is an Individual; the template indexer must claim it, or we
    would build an anatomical-individual document for a template."""
    assert tif.choose_indexer(["Individual", "Template"]) == "template"


# ---------------------------------------------------------------------------
# Exclusions -- anatomical-branch only
# ---------------------------------------------------------------------------

def test_exclusions_are_scoped_to_the_anatomical_branch():
    """FBlc ids are Clusters, which have their own indexer. The anatomical
    indexer's parameter query excludes them; the term_info index as a whole
    does not. Applying the list globally would refuse every Cluster."""
    assert "FBlc" in tif.ANATOMICAL_EXCLUDED_ID_PREFIXES
    assert tif.choose_indexer(["Individual", "Cluster"]) == "cluster"
    assert tif.choose_indexer(["Individual", "Anatomy"]) == "anatomical_ind"


# ---------------------------------------------------------------------------
# Write guard
# ---------------------------------------------------------------------------

def test_no_write_when_the_cache_is_disabled(monkeypatch):
    """A live-data test run must never write into the shared production
    collection. VFB has been bitten by exactly that before."""
    monkeypatch.setenv("VFBQUERY_CACHE_ENABLED", "false")
    monkeypatch.setattr(tif, "_INDEXERS", {"class": object})
    sent = []
    monkeypatch.setattr(tif, "_send_solr_docs",
                        lambda docs, service: sent.append((docs, service)) or True)
    assert tif.write_term_info({"id": "FBbt_00003748"}) is False
    assert sent == []


def test_write_uses_the_indexers_service_name(monkeypatch):
    monkeypatch.setenv("VFBQUERY_CACHE_ENABLED", "true")
    monkeypatch.setattr(tif, "_INDEXERS", {"class": object})
    sent = []
    monkeypatch.setattr(tif, "_send_solr_docs",
                        lambda docs, service: sent.append((list(docs), service)) or True)
    doc = {"id": "FBbt_00003748", "term_info": {"set": "{}"}}
    assert tif.write_term_info(doc) is True
    assert sent == [([doc], "term_info")]


def test_a_failing_write_is_not_fatal(monkeypatch):
    monkeypatch.setenv("VFBQUERY_CACHE_ENABLED", "true")
    monkeypatch.setattr(tif, "_INDEXERS", {"class": object})

    def boom(docs, service):
        raise RuntimeError("solr down")

    monkeypatch.setattr(tif, "_send_solr_docs", boom)
    assert tif.write_term_info({"id": "x"}) is False


# ---------------------------------------------------------------------------
# Schema version stamping
# ---------------------------------------------------------------------------

def test_schema_version_prefers_the_environment(monkeypatch):
    monkeypatch.setenv("VFB_JSON_SCHEMA_SHA", "deadbee")
    assert tif.schema_version() == "deadbee"


def test_schema_version_falls_back_to_the_image_file(monkeypatch, tmp_path):
    monkeypatch.delenv("VFB_JSON_SCHEMA_SHA", raising=False)
    versions = tmp_path / "vfb_versions.env"
    versions.write_text("VFB_INDEXER_SHA=aaaaaaa\nVFB_JSON_SCHEMA_SHA=bbbbbbb\n")
    monkeypatch.setattr(tif, "VERSIONS_FILE", str(versions))
    assert tif.schema_version() == "bbbbbbb"


def test_schema_version_is_never_a_git_call(monkeypatch, tmp_path):
    """query_roller.get_version_tag shells out to git and raises outside a
    repository, which a running container never is. Whatever happens, this
    must return a string rather than blow up mid-query."""
    monkeypatch.delenv("VFB_JSON_SCHEMA_SHA", raising=False)
    monkeypatch.setattr(tif, "VERSIONS_FILE", str(tmp_path / "absent"))
    assert tif.schema_version() == "unpinned"


# ---------------------------------------------------------------------------
# Pointing the indexer at VFBquery's own backends
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("url,expected", [
    ("http://solr.virtualflybrain.org/solr/vfb_json/",
     ("http://solr.virtualflybrain.org/solr", "vfb_json")),
    ("https://solr.virtualflybrain.org/solr/vfb_json",
     ("https://solr.virtualflybrain.org/solr", "vfb_json")),
    ("", (None, None)),
    (None, (None, None)),
])
def test_solr_url_splits_into_the_indexers_two_env_vars(url, expected):
    assert tif._split_solr_url(url) == expected


def test_seeding_sets_a_usable_solr_update_url(monkeypatch):
    """The regression this exists for: solr_client builds its update URL from
    SOLRserver/SOLRcollection, neither of which a VFBquery deployment sets.
    get_solr_update_url() then returns None and send_solr_payload returns
    False without making a request, so a rebuilt document is served but never
    indexed -- silently, and only in production, because the cache-disabled
    guard short-circuits before the URL is ever needed."""
    for key in ("SOLRserver", "SOLRcollection", "PDBserver", "PDBuser",
                "PDBpassword"):
        monkeypatch.delenv(key, raising=False)
    tif._seed_indexer_env()
    from vfbquery.vfb_queries import vfb_solr
    server, collection = tif._split_solr_url(vfb_solr.url)
    assert os.environ["SOLRserver"] == server
    assert os.environ["SOLRcollection"] == collection
    # and the two together must produce a real update endpoint
    assert f"{server}/{collection}/update" == (
        f"{os.environ['SOLRserver'].rstrip('/')}/"
        f"{os.environ['SOLRcollection']}/update")


def test_seeding_does_not_override_a_deployment(monkeypatch):
    monkeypatch.setenv("SOLRserver", "http://elsewhere/solr")
    monkeypatch.setenv("SOLRcollection", "other_core")
    tif._seed_indexer_env()
    assert os.environ["SOLRserver"] == "http://elsewhere/solr"
    assert os.environ["SOLRcollection"] == "other_core"


# ---------------------------------------------------------------------------
# The `src` package collision
# ---------------------------------------------------------------------------

def test_import_shim_restores_the_previous_src():
    """VFBquery's own source directory is a regular package called `src`, the
    same name as the indexer's. The shim must put ours back afterwards or the
    rest of the process loses it."""
    import src as before
    with tif._indexer_importable():
        assert sys.path[0] == tif.INDEXER_ROOT
    import src as after
    assert after is before
    assert tif.INDEXER_ROOT not in sys.path


def test_import_shim_restores_even_when_the_body_raises():
    import src as before
    with pytest.raises(ValueError):
        with tif._indexer_importable():
            raise ValueError("boom")
    import src as after
    assert after is before
    assert tif.INDEXER_ROOT not in sys.path


# ---------------------------------------------------------------------------
# Degrading without the indexer
# ---------------------------------------------------------------------------

def test_reports_why_it_cannot_build(monkeypatch):
    monkeypatch.setattr(tif, "_INDEXERS", None)
    monkeypatch.setattr(tif, "_IMPORT_ERROR", ImportError("no indexer here"))
    assert tif.fallback_available() is False
    assert "no indexer here" in tif.fallback_unavailable_reason()
    assert tif.backfill_term_info("FBbt_00003748") is None


# ---------------------------------------------------------------------------
# Per-field query index rebuilds
# ---------------------------------------------------------------------------

class _StubNeo:
    def commit_list(self, queries):
        return None


class _StubConnect:
    """vc.nc is a read-only property, so stand in for vc itself."""
    nc = _StubNeo()

def test_query_field_fallback_only_claims_fields_it_can_build(monkeypatch):
    monkeypatch.setattr(tif, "_QUERY_FIELD_INDEXERS", {"anat_query": object})
    monkeypatch.setattr(tif, "_INDEXERS", {"class": object})
    assert tif.query_field_fallback_available("anat_query") is True
    assert tif.query_field_fallback_available("term_info") is False
    assert tif.query_field_fallback_available("something_else") is False


def test_no_ids_means_no_work(monkeypatch):
    def explode(*a, **k):
        raise AssertionError("should not have queried anything")
    monkeypatch.setattr(tif, "_QUERY_FIELD_INDEXERS", {"anat_query": explode})
    assert tif.backfill_query_field([], "anat_query") == {}


def test_backfill_batches_rather_than_truncating(monkeypatch):
    """Batched at the indexer's own size, and every id is rebuilt. Measured
    against the live PDB a rebuild is one round trip -- 500 ids in 1.5s
    against 0.37s for a single id -- so batching is what keeps it cheap, and
    a set larger than one batch is looped, never trimmed."""
    seen = {}

    class FakeIndexer:
        def get_vfb_json_query(self, ids):
            seen["ids"] = list(ids)
            seen.setdefault("batches", []).append(len(ids))
            return "MATCH (n) RETURN n"

        def generate_solr_doc(self, result, request=None):
            return {"id": result["term"]["core"]["short_form"],
                    "anat_query": {"set": '{"ok": true}'}}

    monkeypatch.setattr(tif, "_QUERY_FIELD_INDEXERS", {"anat_query": FakeIndexer})
    monkeypatch.setattr(tif, "_INDEXERS", {"class": object})
    monkeypatch.setattr(tif, "_write_query_docs", lambda docs, field: True)

    ids = ["FBbt_%07d" % i for i in range(tif.BACKFILL_BATCH_SIZE + 25)]
    rows = [{"term": {"core": {"short_form": i}}} for i in ids]
    import vfbquery.vfb_queries as vq
    calls = {"n": 0}

    def cursor(r):
        i = calls["n"]; calls["n"] += 1
        return rows[i * tif.BACKFILL_BATCH_SIZE:(i + 1) * tif.BACKFILL_BATCH_SIZE] \
            if i == 0 else rows[tif.BACKFILL_BATCH_SIZE:]

    monkeypatch.setattr(vq, "get_dict_cursor", lambda: cursor)
    monkeypatch.setattr(vq, "vc", _StubConnect())

    rebuilt = tif.backfill_query_field(ids, "anat_query")
    # Batched, not truncated: the last batch is the 25-id remainder, and every
    # id came back. Dropping the tail would return a quietly short answer,
    # which is the thing this whole module exists to stop.
    assert len(seen["ids"]) == 25
    assert seen["batches"] == [tif.BACKFILL_BATCH_SIZE, 25]
    assert rebuilt[ids[0]] == '{"ok": true}'            # payload returned, not re-read


def test_backfill_returns_payloads_for_the_current_request(monkeypatch):
    """The indexer writes with commitWithin 60s, so re-reading SOLR in this
    request would still miss. The payloads have to come back in memory."""
    class FakeIndexer:
        def get_vfb_json_query(self, ids):
            return "MATCH (n) RETURN n"

        def generate_solr_doc(self, result, request=None):
            return {"id": "VFB_00107fob",
                    "anat_image_query": {"set": '{"term": {}}'}}

    monkeypatch.setattr(tif, "_QUERY_FIELD_INDEXERS",
                        {"anat_image_query": FakeIndexer})
    monkeypatch.setattr(tif, "_INDEXERS", {"class": object})
    written = []
    monkeypatch.setattr(tif, "_write_query_docs",
                        lambda docs, field: written.append((len(docs), field)) or True)
    import vfbquery.vfb_queries as vq
    monkeypatch.setattr(vq, "get_dict_cursor", lambda: (lambda r: [{"x": 1}]))
    monkeypatch.setattr(vq, "vc", _StubConnect())

    out = tif.backfill_query_field(["VFB_00107fob"], "anat_image_query")
    assert out == {"VFB_00107fob": '{"term": {}}'}
    assert written == [(1, "anat_image_query")]


def test_a_failed_rebuild_returns_nothing_rather_than_raising(monkeypatch):
    class FakeIndexer:
        def get_vfb_json_query(self, ids):
            return "MATCH (n) RETURN n"

    monkeypatch.setattr(tif, "_QUERY_FIELD_INDEXERS", {"anat_query": FakeIndexer})
    monkeypatch.setattr(tif, "_INDEXERS", {"class": object})
    import vfbquery.vfb_queries as vq

    def boom(*a, **k):
        raise RuntimeError("neo4j down")

    monkeypatch.setattr(vq, "get_dict_cursor", lambda: boom)
    monkeypatch.setattr(vq, "vc", _StubConnect())
    assert tif.backfill_query_field(["FBbt_00003748"], "anat_query") == {}


def test_query_writes_honour_the_cache_guard(monkeypatch):
    monkeypatch.setenv("VFBQUERY_CACHE_ENABLED", "false")
    monkeypatch.setattr(tif, "_INDEXERS", {"class": object})
    sent = []
    monkeypatch.setattr(tif, "_send_solr_docs",
                        lambda d, f: sent.append(f) or True)
    assert tif._write_query_docs([{"id": "x"}], "anat_query") is False
    assert sent == []
