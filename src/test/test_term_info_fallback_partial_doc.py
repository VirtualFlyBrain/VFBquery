"""The term_info fallback must fire on a document that has no term_info,
not only when there is no document at all.

The vfb_json collection is written by several indexers, each setting only
its own field with an atomic update. So a record that one of the
query-result indexers reaches before the term_info indexer does has a
document -- ``hits == 1`` -- with no ``term_info`` in it. Berg2025a and
Bates2026 were exactly that on 2026-09-04: ``all_datasets_query`` present
(listed under All Datasets, thumbnail and all), ``term_info`` absent (blank
term-info panel, ``get_term_info`` -> None), and the fallback never ran
because it was keyed on the hit count.

Offline: SOLR and the PDB rebuild are both stubbed, so these pin the
trigger and the plumbing, not the graph.
"""
import dataclasses
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery import vfb_queries as vq
from vfbquery.term_info_queries import VfbTerminfo


DATASET_TYPES = ["Entity", "Individual", "DataSet", "has_image"]


def _term_info(short_form, label, types):
    """A minimal but schema-complete term_info document (every VfbTerminfo
    field present, as the real SOLR documents are)."""
    doc = {
        "term": {
            "core": {
                "short_form": short_form,
                "iri": "http://virtualflybrain.org/data/" + short_form,
                "label": label,
                "types": types,
                "unique_facets": types,
                "symbol": "",
            },
            "description": [],
            "comment": [],
        },
        "version": "test",
    }
    for field in dataclasses.fields(VfbTerminfo):
        doc.setdefault(field.name, None)
    return json.dumps(doc)


class _SolrResults:
    """What pysolr hands back: ``hits`` plus a list of dict documents."""

    def __init__(self, docs):
        self.hits = len(docs)
        self.docs = docs


# The shape SOLR actually held for Berg2025a: a document, no term_info.
PARTIAL_DOC = {
    "id": "Berg2025a",
    "all_datasets_query": ['{"dataset": {"short_form": "Berg2025a"}}'],
    "template_2_roi_browser_query": ["[]"],
}


# ---------------------------------------------------------------------------
# The trigger
# ---------------------------------------------------------------------------

def test_no_document_is_a_miss():
    assert vq._has_term_info_document(_SolrResults([])) is False


def test_a_document_without_term_info_is_a_miss():
    """The Berg2025a case. hits == 1, nothing to read."""
    assert vq._has_term_info_document(_SolrResults([PARTIAL_DOC])) is False


def test_an_empty_term_info_field_is_a_miss():
    doc = dict(PARTIAL_DOC, term_info=[])
    assert vq._has_term_info_document(_SolrResults([doc])) is False


def test_a_real_term_info_document_is_a_hit():
    doc = {"id": "Berg2025a",
           "term_info": [_term_info("Berg2025a", "Male CNS", DATASET_TYPES)]}
    assert vq._has_term_info_document(_SolrResults([doc])) is True


def test_the_fallbacks_own_stand_in_counts_as_a_hit():
    """_FallbackSolrResult is fed straight back through the same check."""
    payload = _term_info("Berg2025a", "Male CNS", DATASET_TYPES)
    assert vq._has_term_info_document(vq._FallbackSolrResult(payload)) is True


# ---------------------------------------------------------------------------
# get_term_info end to end, with SOLR and the rebuild stubbed
# ---------------------------------------------------------------------------

def test_get_term_info_rebuilds_a_partial_document(monkeypatch):
    """A document with other fields but no term_info must be rebuilt and
    served, exactly as a wholly missing document is."""
    payload = _term_info("Berg2025a",
                         "Male CNS version 1.0 connectome neurons from Berg et al. (2025).",
                         DATASET_TYPES)
    asked = []
    monkeypatch.setattr(vq.vfb_solr, "search",
                        lambda q, **kw: _SolrResults([PARTIAL_DOC]))
    monkeypatch.setattr(vq, "backfill_term_info",
                        lambda short_form: asked.append(short_form) or payload)

    result = vq.get_term_info("Berg2025a", preview=False)

    assert asked == ["Berg2025a"], "the rebuild was not attempted"
    assert result is not None, "a partial document still served nothing"
    assert result["Id"] == "Berg2025a"
    assert result["Name"].startswith("Male CNS version 1.0")


def test_get_term_info_does_not_rebuild_when_term_info_is_present(monkeypatch):
    """The fallback is for gaps only; a served document is left alone."""
    doc = {"id": "Berg2025a",
           "term_info": [_term_info("Berg2025a", "Male CNS", DATASET_TYPES)]}
    asked = []
    monkeypatch.setattr(vq.vfb_solr, "search", lambda q, **kw: _SolrResults([doc]))
    monkeypatch.setattr(vq, "backfill_term_info",
                        lambda short_form: asked.append(short_form) or None)

    result = vq.get_term_info("Berg2025a", preview=False)

    assert asked == []
    assert result is not None and result["Id"] == "Berg2025a"


def test_get_term_info_still_returns_none_when_the_rebuild_fails(monkeypatch):
    """No PDB node / no indexer for the type: behave as before, no crash."""
    monkeypatch.setattr(vq.vfb_solr, "search",
                        lambda q, **kw: _SolrResults([PARTIAL_DOC]))
    monkeypatch.setattr(vq, "backfill_term_info", lambda short_form: None)

    assert vq.get_term_info("Berg2025a", preview=False) is None
