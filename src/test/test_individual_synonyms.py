"""Regression tests: pub-attributed synonyms must be returned for Individuals.

``term_info_parse_object`` gated the ``pub_syn`` block on
``"Class" in termInfo["SuperTypes"]``, so an Individual carrying a
pub-attributed synonym had it silently dropped — e.g. VFB_00101385, whose
"MEon JRC_FlyEM_Hemibrain" synonym never reached the term info. The gate is
gone; these lock that in, and check Classes did not regress with it.

Deliberately offline: the input is a hand-built ``term_info`` document, so these
exercise the parsing branch itself rather than whatever the graph happens to
hold today. No backend means no skip path and no dependence on curation.
"""

import dataclasses
import json
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.term_info_queries import VfbTerminfo
from vfbquery.vfb_queries import term_info_parse_object


class _FakeSolrResults:
    """Minimal stand-in for the pysolr results object term_info_parse_object
    consumes: it reads only ``.hits`` and ``.docs[0]['term_info'][0]``."""

    def __init__(self, term_info_json):
        self.hits = 1
        self.docs = [{"term_info": [term_info_json]}]


def _term_info(short_form, label, types, synonym_label=None):
    """A `term_info` JSON document, optionally carrying one pub-attributed
    synonym.

    Every top-level VfbTerminfo field is emitted (null where unused) because
    dataclasses_json's ``from_json`` requires each key to be present — the real
    SOLR documents are dense in the same way. Deriving the key list from the
    dataclass keeps this fixture correct if a field is ever added.
    """
    doc = {
        "term": {
            "core": {
                "short_form": short_form,
                "iri": f"http://virtualflybrain.org/reports/{short_form}",
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
    if synonym_label is not None:
        doc["pub_syn"] = [{
            "synonym": {"label": synonym_label,
                        "scope": "has_exact_synonym",
                        "type": ""},
            "pub": {
                "core": {
                    "short_form": "FBrf0239540",
                    "iri": "http://flybase.org/reports/FBrf0239540",
                    "label": "Scheffer et al., 2020, eLife 9: e57443",
                    "types": ["Entity", "Individual", "pub"],
                },
                "microref": "Scheffer et al., 2020",
            },
        }]
    for field in dataclasses.fields(VfbTerminfo):
        doc.setdefault(field.name, None)
    return json.dumps(doc)


INDIVIDUAL_TYPES = ["Entity", "Individual", "VFB", "Adult", "Anatomy",
                    "Nervous_system", "Synaptic_neuropil_domain", "has_image"]
CLASS_TYPES = ["Entity", "Class", "Anatomy", "Nervous_system"]

SYNONYM = "MEon JRC_FlyEM_Hemibrain"


class IndividualSynonymsTest(unittest.TestCase):

    def _parse(self, term_info_json, short_form):
        result = term_info_parse_object(_FakeSolrResults(term_info_json),
                                        short_form)
        self.assertIsNotNone(result, f"parse returned None for {short_form}")
        return result, [s["label"] for s in result.get("Synonyms", [])]

    def test_individual_pub_synonym_is_returned(self):
        """The regression: an Individual's pub_syn must survive parsing."""
        result, labels = self._parse(
            _term_info("VFB_00101385", "ME(R) on JRC_FlyEM_Hemibrain",
                       INDIVIDUAL_TYPES, SYNONYM),
            "VFB_00101385")
        self.assertTrue(result["IsIndividual"],
                        "fixture should parse as an Individual, not a Class")
        self.assertIn("Synonyms", result,
                      "an Individual with pub_syn must get a Synonyms block — "
                      "this was gated on 'Class' and silently dropped")
        self.assertIn(SYNONYM, labels)

    def test_class_pub_synonym_still_returned(self):
        """Removing the gate must not have cost Classes their synonyms."""
        result, labels = self._parse(
            _term_info("FBbt_00003748", "medulla", CLASS_TYPES, "ME"),
            "FBbt_00003748")
        self.assertTrue(result["IsClass"])
        self.assertIn("ME", labels)

    def test_synonym_carries_its_publication(self):
        """The merge step must keep the attributing publication, not just the
        label — an unattributed synonym is much less useful."""
        result, _ = self._parse(
            _term_info("VFB_00101385", "ME(R) on JRC_FlyEM_Hemibrain",
                       INDIVIDUAL_TYPES, SYNONYM),
            "VFB_00101385")
        entry = next(s for s in result["Synonyms"] if s["label"] == SYNONYM)
        self.assertTrue(entry.get("publication"),
                        f"expected an attributing publication, got {entry}")
        self.assertIn("FBrf0239540", entry["publication"])

    def test_individual_without_pub_syn_has_no_synonyms(self):
        """No pub_syn means no Synonyms key — the fix must not invent one."""
        result = term_info_parse_object(
            _FakeSolrResults(_term_info("VFB_00101385",
                                        "ME(R) on JRC_FlyEM_Hemibrain",
                                        INDIVIDUAL_TYPES)),
            "VFB_00101385")
        self.assertIsNotNone(result)
        self.assertNotIn("Synonyms", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
