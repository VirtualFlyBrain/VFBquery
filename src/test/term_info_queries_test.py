import unittest
from src.term_info_queries import deserialize_term_info


class TermInfoQueriesTest(unittest.TestCase):

    def test_term_info_deserialization(self):
        terminfo_json = """
        {"term": {"core": {"iri": "http://purl.obolibrary.org/obo/FBbt_00048514", "symbol": "", "types": ["Entity", "Adult", "Anatomy", "Cell", "Class", "Mechanosensory_system", "Nervous_system", "Neuron", "Sensory_neuron"], "short_form": "FBbt_00048514", "unique_facets": ["Adult", "Mechanosensory_system", "Nervous_system", "Sensory_neuron"], "label": "labial taste bristle mechanosensory neuron"}, "description": ["Any mechanosensory neuron (FBbt:00005919) that has sensory dendrite in some labellar taste bristle (FBbt:00004162)."], "comment": []}, "query": "Get JSON for Neuron Class", "version": "3d2a474", "parents": [{"symbol": "", "iri": "http://purl.obolibrary.org/obo/FBbt_00048508", "types": ["Entity", "Anatomy", "Cell", "Class", "Mechanosensory_system", "Nervous_system", "Neuron", "Sensory_neuron"], "short_form": "FBbt_00048508", "unique_facets": ["Mechanosensory_system", "Nervous_system", "Sensory_neuron"], "label": "mechanosensory neuron of chaeta"}, {"symbol": "", "iri": "http://purl.obolibrary.org/obo/FBbt_00051420", "types": ["Entity", "Adult", "Anatomy", "Cell", "Class", "Mechanosensory_system", "Nervous_system", "Neuron", "Sensory_neuron"], "short_form": "FBbt_00051420", "unique_facets": ["Adult", "Mechanosensory_system", "Nervous_system", "Sensory_neuron"], "label": "adult mechanosensory neuron"}, {"symbol": "", "iri": "http://purl.obolibrary.org/obo/FBbt_00048029", "types": ["Entity", "Adult", "Anatomy", "Cell", "Class", "Nervous_system", "Neuron", "Sensory_neuron"], "short_form": "FBbt_00048029", "unique_facets": ["Adult", "Nervous_system", "Sensory_neuron"], "label": "labellar taste bristle sensory neuron"}], "relationships": [{"relation": {"iri": "http://purl.obolibrary.org/obo/BFO_0000050", "label": "is part of", "type": "part_of"}, "object": {"symbol": "", "iri": "http://purl.obolibrary.org/obo/FBbt_00005892", "types": ["Entity", "Adult", "Anatomy", "Class", "Nervous_system"], "short_form": "FBbt_00005892", "unique_facets": ["Adult", "Nervous_system"], "label": "adult peripheral nervous system"}}], "xrefs": [], "anatomy_channel_image": [], "pub_syn": [{"synonym": {"scope": "has_exact_synonym", "label": "labellar taste bristle mechanosensitive neuron", "type": ""}, "pub": {"core": {"symbol": "", "iri": "http://flybase.org/reports/Unattributed", "types": ["Entity", "Individual", "pub"], "short_form": "Unattributed", "unique_facets": ["pub"], "label": ""}, "FlyBase": "", "PubMed": "", "DOI": ""}}, {"synonym": {"scope": "has_exact_synonym", "label": "labellar taste bristle mechanosensory neuron", "type": ""}, "pub": {"core": {"symbol": "", "iri": "http://flybase.org/reports/Unattributed", "types": ["Entity", "Individual", "pub"], "short_form": "Unattributed", "unique_facets": ["pub"], "label": ""}, "FlyBase": "", "PubMed": "", "DOI": ""}}, {"synonym": {"scope": "has_exact_synonym", "label": "labial taste bristle mechanosensitive neuron", "type": ""}, "pub": {"core": {"symbol": "", "iri": "http://flybase.org/reports/Unattributed", "types": ["Entity", "Individual", "pub"], "short_form": "Unattributed", "unique_facets": ["pub"], "label": ""}, "FlyBase": "", "PubMed": "", "DOI": ""}}], "def_pubs": [{"core": {"symbol": "", "iri": "http://flybase.org/reports/FBrf0242472", "types": ["Entity", "Individual", "pub"], "short_form": "FBrf0242472", "unique_facets": ["pub"], "label": "Zhou et al., 2019, Sci. Adv. 5(5): eaaw5141"}, "FlyBase": "", "PubMed": "31131327", "DOI": "10.1126/sciadv.aaw5141"}], "targeting_splits": []}
        """

        terminfo = deserialize_term_info(terminfo_json)
        print(terminfo)

        self.assertEqual("Get JSON for Neuron Class", terminfo.query)

        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00048514", terminfo.term.core.iri)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00048514", terminfo.term.core.iri)
        self.assertEqual("", terminfo.term.core.symbol)
        self.assertEqual(4, len(terminfo.term.core.unique_facets))
        self.assertTrue("Adult" in terminfo.term.core.unique_facets)
        self.assertTrue("Mechanosensory_system" in terminfo.term.core.unique_facets)
        self.assertTrue("Nervous_system" in terminfo.term.core.unique_facets)
        self.assertTrue("Sensory_neuron" in terminfo.term.core.unique_facets)

        self.assertEqual(0, len(terminfo.xrefs))

        self.assertEqual(3, len(terminfo.pub_syn))

        self.assertEqual("labellar taste bristle mechanosensitive neuron", terminfo.pub_syn[0].synonym.label)
        self.assertEqual("Unattributed", terminfo.pub_syn[0].pub.core.short_form)
        self.assertEqual("", terminfo.pub_syn[0].pub.PubMed)

