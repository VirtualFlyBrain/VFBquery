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
