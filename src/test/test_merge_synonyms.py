import unittest
from vfbquery.term_info_queries import deserialize_term_info, synonym_type_label


# Trimmed real medulla (FBbt_00003748) term_info: the synonym block only.
MEDULLA = """
{"term": {"core": {"iri": "http://purl.obolibrary.org/obo/FBbt_00003748", "symbol": "", "types": ["Entity", "Class", "Anatomy"], "short_form": "FBbt_00003748", "label": "medulla"}, "description": [], "comment": []},
 "query": "Get JSON for Class", "version": "test", "parents": [], "relationships": [], "xrefs": [], "anatomy_channel_image": [],
 "pub_syn": [
   {"synonym": {"scope": "has_related_synonym", "label": "ME_L", "type": "http://purl.obolibrary.org/obo/fbbt#name_in_flywire_fafb"}, "pub": {"core": {"short_form": "FBrf0260535", "types": ["pub"], "label": "Schlegel et al., 2024"}, "FlyBase": "FBrf0260535", "PubMed": "", "DOI": ""}},
   {"synonym": {"scope": "has_related_synonym", "label": "ME_L", "type": "http://purl.obolibrary.org/obo/fbbt#name_in_banc"}, "pub": {"core": {"short_form": "doi_10_1101_2025_07_31_667571", "types": ["pub"], "label": "Bates et al., 2025"}, "FlyBase": "", "PubMed": "", "DOI": "10.1101/2025.07.31.667571"}},
   {"synonym": {"scope": "has_related_synonym", "label": "ME_L", "type": "http://purl.obolibrary.org/obo/fbbt#name_in_banc"}, "pub": {"core": {"short_form": "Unattributed", "types": ["pub"], "label": ""}, "FlyBase": "", "PubMed": "", "DOI": ""}},
   {"synonym": {"scope": "has_related_synonym", "label": "m", "type": ""}, "pub": {"core": {"short_form": "Unattributed", "types": ["pub"], "label": ""}, "FlyBase": "", "PubMed": "", "DOI": ""}},
   {"synonym": {"scope": "has_exact_synonym", "label": "ME", "type": "http://purl.obolibrary.org/obo/fbbt#BRAIN_NAME_ABV"}, "pub": {"core": {"short_form": "FBrf0224194", "types": ["pub"], "label": "Ito et al., 2014"}, "FlyBase": "FBrf0224194", "PubMed": "", "DOI": ""}}
 ],
 "def_pubs": [], "targeting_splits": []}
"""


class MergeSynonymsTest(unittest.TestCase):
    def setUp(self):
        self.syns = deserialize_term_info(MEDULLA).get_merged_synonyms()
        self.by_label = {s["label"]: s for s in self.syns}

    def test_each_synonym_appears_once(self):
        labels = [s["label"] for s in self.syns]
        self.assertEqual(sorted(labels), ["ME", "ME_L", "m"])
        self.assertEqual(len(labels), len(set(labels)))

    def test_multi_ref_synonym_merged(self):
        # ME_L asserted by flywire + banc -> single entry, both refs, no Unattributed
        pub = self.by_label["ME_L"]["publication"]
        self.assertIn("Schlegel et al., 2024", pub)
        self.assertIn("Bates et al., 2025", pub)
        self.assertNotIn("Unattributed", pub)

    def test_attributed_pubs_are_markdown_links(self):
        # every pub with a short_form/id must render as a markdown ref
        self.assertIn("[Schlegel et al., 2024](FBrf0260535)", self.by_label["ME_L"]["publication"])
        self.assertIn("[Bates et al., 2025](doi_10_1101_2025_07_31_667571)", self.by_label["ME_L"]["publication"])

    def test_unattributed_with_type_shows_type_token(self):
        # name_in_banc -> Unattributed: surface the type as a plain (unlinked) ref
        pub = self.by_label["ME_L"]["publication"]
        self.assertIn("name_in_banc", pub)
        self.assertNotIn("[name_in_banc]", pub)  # not a link

    def test_unattributed_only_no_type_has_no_publication(self):
        # 'm' is backed only by Unattributed with no type -> shown with no ref
        self.assertNotIn("publication", self.by_label["m"])

    def test_attributed_single_ref_kept(self):
        self.assertIn("[Ito et al., 2014](FBrf0224194)", self.by_label["ME"]["publication"])


class SynonymTypeLabelTest(unittest.TestCase):
    def test_opaque_omo_ids_mapped(self):
        self.assertEqual(synonym_type_label("http://purl.obolibrary.org/obo/OMO_0003000"), "abbreviation")
        self.assertEqual(synonym_type_label("http://purl.obolibrary.org/obo/OMO_0003003"), "layperson synonym")

    def test_fragment_fallback(self):
        self.assertEqual(synonym_type_label("http://purl.obolibrary.org/obo/fbbt#name_in_banc"), "name_in_banc")
        self.assertEqual(synonym_type_label("http://purl.obolibrary.org/obo/ncbitaxon#scientific_name"), "scientific_name")

    def test_empty(self):
        self.assertEqual(synonym_type_label(""), "")


if __name__ == "__main__":
    unittest.main()
