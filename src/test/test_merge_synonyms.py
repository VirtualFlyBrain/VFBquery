import unittest
from vfbquery.term_info_queries import deserialize_term_info, synonym_type_label


# Trimmed real medulla (FBbt_00003748) term_info: the synonym block only, plus
# one synthetic row — an untyped "ME" (Doe et al., 2019) alongside the real typed
# "ME" (BRAIN_NAME_ABV) — so the untyped-distinct-from-typed case is exercised.
MEDULLA = """
{"term": {"core": {"iri": "http://purl.obolibrary.org/obo/FBbt_00003748", "symbol": "", "types": ["Entity", "Class", "Anatomy"], "short_form": "FBbt_00003748", "label": "medulla"}, "description": [], "comment": []},
 "query": "Get JSON for Class", "version": "test", "parents": [], "relationships": [], "xrefs": [], "anatomy_channel_image": [],
 "pub_syn": [
   {"synonym": {"scope": "has_related_synonym", "label": "ME_L", "type": "http://purl.obolibrary.org/obo/fbbt#name_in_flywire_fafb"}, "pub": {"core": {"short_form": "FBrf0260535", "types": ["pub"], "label": "Schlegel et al., 2024"}, "FlyBase": "FBrf0260535", "PubMed": "", "DOI": ""}},
   {"synonym": {"scope": "has_related_synonym", "label": "ME_L", "type": "http://purl.obolibrary.org/obo/fbbt#name_in_banc"}, "pub": {"core": {"short_form": "doi_10_1101_2025_07_31_667571", "types": ["pub"], "label": "Bates et al., 2025"}, "FlyBase": "", "PubMed": "", "DOI": "10.1101/2025.07.31.667571"}},
   {"synonym": {"scope": "has_related_synonym", "label": "ME_L", "type": "http://purl.obolibrary.org/obo/fbbt#name_in_banc"}, "pub": {"core": {"short_form": "Unattributed", "types": ["pub"], "label": ""}, "FlyBase": "", "PubMed": "", "DOI": ""}},
   {"synonym": {"scope": "has_related_synonym", "label": "m", "type": ""}, "pub": {"core": {"short_form": "Unattributed", "types": ["pub"], "label": ""}, "FlyBase": "", "PubMed": "", "DOI": ""}},
   {"synonym": {"scope": "has_exact_synonym", "label": "ME", "type": "http://purl.obolibrary.org/obo/fbbt#BRAIN_NAME_ABV"}, "pub": {"core": {"short_form": "FBrf0224194", "types": ["pub"], "label": "Ito et al., 2014"}, "FlyBase": "FBrf0224194", "PubMed": "", "DOI": ""}},
   {"synonym": {"scope": "has_exact_synonym", "label": "ME", "type": ""}, "pub": {"core": {"short_form": "FBrf0300000", "types": ["pub"], "label": "Doe et al., 2019"}, "FlyBase": "FBrf0300000", "PubMed": "", "DOI": ""}}
 ],
 "def_pubs": [], "targeting_splits": []}
"""


class MergeSynonymsTest(unittest.TestCase):
    def setUp(self):
        self.syns = deserialize_term_info(MEDULLA).get_merged_synonyms()

    def _entry(self, label, type_frag):
        """The single entry for a (label, type) pair. type_frag matches the tail
        of the raw type IRI; pass None for the untyped ('synonym') entry."""
        matches = [
            s for s in self.syns
            if s["label"] == label and (
                s["type"] in ("", "synonym") if type_frag is None
                else s["type"].endswith(type_frag))
        ]
        self.assertEqual(len(matches), 1,
                         f"expected exactly one {label!r}/{type_frag!r} entry, got {len(matches)}")
        return matches[0]

    def test_one_line_per_synonym_type_pair(self):
        # ME_L named in flywire AND banc -> two lines; ME typed (BRAIN_NAME_ABV)
        # AND untyped -> two lines; plus untyped 'm'. Each (label, type) once.
        pairs = sorted((s["label"], s["type"].split("#")[-1].split("/")[-1]) for s in self.syns)
        self.assertEqual(pairs, [
            ("ME", "BRAIN_NAME_ABV"),
            ("ME", "synonym"),
            ("ME_L", "name_in_banc"),
            ("ME_L", "name_in_flywire_fafb"),
            ("m", "synonym"),
        ])
        # no (label, type) pair is duplicated
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_untyped_distinct_from_typed(self):
        # The same label 'ME' asserted with a type and without one are separate
        # lines: the typed line carries its type token, the untyped line does not.
        typed = self._entry("ME", "BRAIN_NAME_ABV")
        untyped = self._entry("ME", None)
        self.assertIn("BRAIN_NAME_ABV", typed["publication"])
        self.assertIn("[Doe et al., 2019](FBrf0300000)", untyped["publication"])
        self.assertNotIn("BRAIN_NAME_ABV", untyped["publication"])

    def test_attributed_pubs_are_markdown_links(self):
        # each typed line carries its own pub as a markdown ref
        self.assertIn("[Schlegel et al., 2024](FBrf0260535)",
                      self._entry("ME_L", "name_in_flywire_fafb")["publication"])
        self.assertIn("[Bates et al., 2025](doi_10_1101_2025_07_31_667571)",
                      self._entry("ME_L", "name_in_banc")["publication"])

    def test_all_types_shown_even_when_pub_attributed(self):
        # A typed synonym whose only assertion is pub-attributed still shows its
        # type token (not just the pub link) — the previous bug hid these.
        self.assertIn("name_in_flywire_fafb",
                      self._entry("ME_L", "name_in_flywire_fafb")["publication"])
        self.assertIn("name_in_banc",
                      self._entry("ME_L", "name_in_banc")["publication"])
        self.assertIn("BRAIN_NAME_ABV",
                      self._entry("ME", "BRAIN_NAME_ABV")["publication"])

    def test_type_token_not_a_link(self):
        pub = self._entry("ME_L", "name_in_banc")["publication"]
        self.assertIn("name_in_banc", pub)
        self.assertNotIn("[name_in_banc]", pub)  # plain text, not a markdown link

    def test_type_token_precedes_its_reference(self):
        # Within the parentheses the naming system leads, then the pub that
        # attributes it: "name_in_banc, [Bates et al., 2025](...)".
        pub = self._entry("ME_L", "name_in_banc")["publication"]
        self.assertLess(pub.index("name_in_banc"), pub.index("Bates et al., 2025"))
        self.assertTrue(pub.startswith("name_in_banc,"), pub)

    def test_attributed_and_unattributed_same_type_collapse(self):
        # ME_L/name_in_banc is asserted twice (Bates + Unattributed). One line,
        # the token once, and no 'Unattributed' text leaks in.
        pub = self._entry("ME_L", "name_in_banc")["publication"]
        self.assertEqual(pub.count("name_in_banc"), 1)
        self.assertNotIn("Unattributed", pub)

    def test_unattributed_only_no_type_has_no_publication(self):
        # 'm' is backed only by Unattributed with no type -> shown with no ref
        self.assertNotIn("publication", self._entry("m", None))


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
