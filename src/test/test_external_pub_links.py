"""Pubs cited by URL link out to their iri, not to a VFB page.

vfb-pipeline-polishing resolves synonym refs that are an ORCID or a curator pseudonym (GOC:dos, FBC:DOS) to the
curator's Person node (labelled :pub, iri https://orcid.org/<ORCID>), and other http(s) refs to a pub keyed on the
URL. Neither has a VFB report page, so term info must link them to their iri: [David Osumi-Sutherland](https://orcid.org/...).
Ordinary pubs (FlyBase / DOI / PubMed) keep their internal short_form links. Offline: hand-built term_info documents.
"""

import dataclasses
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.term_info_queries import Pub, MinimalEntityInfo, VfbTerminfo, external_pub_url
from vfbquery.vfb_queries import term_info_parse_object, format_edge_xrefs

ORCID_DOS = "https://orcid.org/0000-0002-7073-9172"
CATMAID = "https://larva1099.catmaid.virtualflybrain.org"


def _pub(short_form, iri, label, **ids):
    return Pub(core=MinimalEntityInfo(short_form=short_form, iri=iri, label=label,
                                      types=["Entity", "Individual", "pub"]), **ids)


class _FakeSolrResults:
    def __init__(self, term_info_json):
        self.hits = 1
        self.docs = [{"term_info": [term_info_json]}]


def _term_info_with_synonyms(pub_syns):
    doc = {"term": {"core": {"short_form": "VFB_00050029", "iri": "http://virtualflybrain.org/reports/VFB_00050029",
                             "label": "DNvnc-20 left (Larva1099:542)", "types": ["Entity", "Individual", "VFB", "Neuron"],
                             "unique_facets": ["Neuron"], "symbol": ""}, "description": [], "comment": []},
           "version": "test", "pub_syn": pub_syns}
    for field in dataclasses.fields(VfbTerminfo):
        doc.setdefault(field.name, None)
    return json.dumps(doc)


def _syn(label, scope, core, microref="", **ids):
    return {"synonym": {"label": label, "scope": scope, "type": ""},
            "pub": dict({"core": core, "microref": microref}, **ids)}


class ExternalPubUrlTest(unittest.TestCase):

    def test_orcid_and_web_iris_are_external(self):
        self.assertEqual(external_pub_url(ORCID_DOS), ORCID_DOS)
        self.assertEqual(external_pub_url(CATMAID), CATMAID)   # VFB-hosted resource without a report page links out
        self.assertEqual(external_pub_url("https://example.org/dataset"), "https://example.org/dataset")

    def test_publications_and_vfb_iris_are_not(self):
        self.assertEqual(external_pub_url("https://doi.org/10.1101/2025.09.25.678485", "", "10.1101/2025.09.25.678485", ""), "")
        self.assertEqual(external_pub_url("http://flybase.org/reports/FBrf0255988"), "")
        self.assertEqual(external_pub_url("http://virtualflybrain.org/reports/VFB_00050000"), "")
        self.assertEqual(external_pub_url(""), "")

    def test_curator_pub_links_to_orcid(self):
        p = _pub("orcidS_0000_0002_7073_9172", ORCID_DOS, "David Osumi-Sutherland")
        self.assertEqual(p.get_microref(), f"[David Osumi-Sutherland]({ORCID_DOS})")
        mini = p.get_miniref()
        self.assertEqual(mini["refs"], [ORCID_DOS])
        self.assertIn(f"]({ORCID_DOS})", mini["link"])

    def test_flybase_pub_unchanged(self):
        p = _pub("FBrf0255988", "http://flybase.org/reports/FBrf0255988", "Winding et al., 2023, Science", FlyBase="FBrf0255988")
        self.assertEqual(p.get_microref(), "[Winding et al., 2023](FBrf0255988)")
        self.assertEqual(p.get_miniref()["refs"], ["http://flybase.org/reports/FBrf0255988"])


class SynonymAndReferenceLinksTest(unittest.TestCase):

    def _parse(self, pub_syns):
        result = term_info_parse_object(_FakeSolrResults(_term_info_with_synonyms(pub_syns)), "VFB_00050029")
        self.assertIsNotNone(result)
        return result

    def test_synonym_cited_by_curator_links_to_orcid(self):
        result = self._parse([_syn("DNvnc-20", "has_exact_synonym",
                                   {"short_form": "orcidS_0000_0002_7073_9172", "iri": ORCID_DOS,
                                    "label": "David Osumi-Sutherland", "types": ["Entity", "Individual", "Person", "pub"]})])
        entry = next(s for s in result["Synonyms"] if s["label"] == "DNvnc-20")
        self.assertEqual(entry["publication"], f"[David Osumi-Sutherland]({ORCID_DOS})")
        pubs = {p["short_form"]: p for p in result.get("Publications", [])}
        self.assertIn(ORCID_DOS, pubs["orcidS_0000_0002_7073_9172"]["refs"])

    def test_synonym_cited_by_doi_keeps_internal_link(self):
        result = self._parse([_syn("BLVp12 descending left", "has_related_synonym",
                                   {"short_form": "doi_10_1101_2025_09_25_678485", "iri": "https://doi.org/10.1101/2025.09.25.678485",
                                    "label": "Randel et al., 2026", "types": ["Entity", "Individual", "pub"]},
                                   microref="Randel et al., 2026", DOI="10.1101/2025.09.25.678485")])
        entry = next(s for s in result["Synonyms"] if s["label"] == "BLVp12 descending left")
        self.assertEqual(entry["publication"], "[Randel et al., 2026](doi_10_1101_2025_09_25_678485)")


class EdgeXrefTest(unittest.TestCase):

    def test_orcid_and_url_xrefs_link_out(self):
        out = format_edge_xrefs([ORCID_DOS, "https://example.org/x/", "FlyBase:FBrf0255988"])
        self.assertIn(f"[ORCID 0000-0002-7073-9172]({ORCID_DOS})", out)
        self.assertIn("[example.org/x](https://example.org/x/)", out)
        self.assertIn("[FlyBase:FBrf0255988](http://flybase.org/reports/FBrf0255988)", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
