import unittest
import time
from src.term_info_queries import deserialize_term_info, deserialize_term_info_from_dict, serialize_term_info_to_dict
from vfb_connect.cross_server_tools import VfbConnect


class TermInfoQueriesTest(unittest.TestCase):

    def setUp(self):
        self.vc = VfbConnect()
        self.variable = TestVariable("my_id", "my_name")

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

    def test_term_info_deserialization_from_dict(self):
        vfbTerm = self.vc.neo_query_wrapper._get_TermInfo(['FBbt_00048514'], "Get JSON for Neuron Class")[0]
        start_time = time.time()
        terminfo = deserialize_term_info_from_dict(vfbTerm)
        print("--- %s seconds ---" % (time.time() - start_time))
        print(vfbTerm)
        print(terminfo)

        self.assertEqual("Get JSON for Neuron Class", terminfo.query)

        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00048514", terminfo.term.core.iri)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00048514", terminfo.term.core.iri)
        self.assertEqual("", terminfo.term.core.symbol)
        # TODO: XXX unique facets are not in vfb_connect release
        # self.assertEqual(4, len(terminfo.term.core.unique_facets))
        # self.assertTrue("Adult" in terminfo.term.core.unique_facets)
        # self.assertTrue("Mechanosensory_system" in terminfo.term.core.unique_facets)
        # self.assertTrue("Nervous_system" in terminfo.term.core.unique_facets)
        # self.assertTrue("Sensory_neuron" in terminfo.term.core.unique_facets)

        self.assertEqual(0, len(terminfo.xrefs))

        self.assertEqual(3, len(terminfo.pub_syn))

        # TODO: XXX check vfb_connect version
        # self.assertEqual("labellar taste bristle mechanosensitive neuron", terminfo.pub_syn[0].synonym.label)
        self.assertEqual("labellar taste bristle mechanosensory neuron", terminfo.pub_syn[0].synonym.label)
        self.assertEqual("Unattributed", terminfo.pub_syn[0].pub.core.short_form)
        self.assertEqual("", terminfo.pub_syn[0].pub.PubMed)

    def test_term_info_serialization_individual_anatomy(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['VFB_00010001'], "Get JSON for Individual:Anatomy")[0]
        print(term_info_dict)
        start_time = time.time()
        term_info = deserialize_term_info_from_dict(term_info_dict)
        print(term_info)
        print("--- %s seconds ---" % (time.time() - start_time))
        serialized = serialize_term_info_to_dict(term_info, self.variable)

        self.assertEqual("fru-F-500075 [VFB_00010001]", serialized["label"])
        self.assertFalse("title" in serialized)
        self.assertFalse("symbol" in serialized)
        self.assertFalse("logo" in serialized)
        self.assertFalse("link" in serialized)
        self.assertEqual(12, len(serialized["types"]))
        self.assertEqual("OutAge: Adult 5~15 days", serialized["description"])
        self.assertFalse("synonyms" in serialized)
        self.assertFalse("source" in serialized)

        self.assertTrue("license" in serialized)
        # TODO check with Robbie None or [{'label': '[None](None)'}]
        self.assertEqual(1, len(serialized["license"]))
        self.assertEqual("[None](None)", serialized["license"][0]["label"])

        self.assertTrue("Classification" in serialized)
        self.assertEqual(2, len(serialized["Classification"]))
        self.assertEqual("[expression pattern fragment](VFBext_0000004)", serialized["Classification"][0])

        self.assertTrue("relationships" in serialized)
        self.assertEqual(6, len(serialized["relationships"]))
        self.assertEqual("expresses [Scer\\GAL4[fru.P1.D]](FBal0276838)", serialized["relationships"][0])

        self.assertFalse("related_individuals" in serialized)

        self.assertTrue("xrefs" in serialized)
        self.assertEqual(1, len(serialized["xrefs"]))
        self.assertEqual("[fru-F-500075 on FlyCircuit 1.0](http://flycircuit.tw/modules.php?name=clearpage&op=detail_table&neuron=fru-F-500075)", serialized["xrefs"][0]["label"])

        self.assertFalse("examples" in serialized)
        self.assertFalse("thumbnail" in serialized)
        self.assertFalse("references" in serialized)

    def test_term_info_serialization_dataset(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['Ito2013'], "Get JSON for DataSet")[0]
        print(term_info_dict)
        start_time = time.time()
        term_info = deserialize_term_info_from_dict(term_info_dict)
        print(term_info)
        print("--- %s seconds ---" % (time.time() - start_time))
        serialized = serialize_term_info_to_dict(term_info, self.variable)

        self.assertEqual("Ito lab adult brain lineage clone image set [Ito2013]", serialized["label"])
        self.assertFalse("title" in serialized)
        self.assertFalse("symbol" in serialized)
        self.assertFalse("logo" in serialized)
        self.assertTrue("link" in serialized)
        self.assertEqual("[http://flybase.org/reports/FBrf0221438.html](http://flybase.org/reports/FBrf0221438.html)", serialized["link"])
        self.assertEqual(3, len(serialized["types"]))
        self.assertTrue("DataSet" in serialized["types"])
        self.assertEqual("An exhaustive set of lineage clones covering the adult brain from Kei Ito's  lab.", serialized["description"])
        self.assertFalse("synonyms" in serialized)
        self.assertFalse("source" in serialized)

        self.assertTrue("license" in serialized)
        # TODO check with Robbie None or [{'label': '[None](None)'}]
        self.assertEqual(1, len(serialized["license"]))
        self.assertEqual("[None](None)", serialized["license"][0]["label"])

        self.assertFalse("Classification" in serialized)
        self.assertFalse("relationships" in serialized)
        self.assertFalse("related_individuals" in serialized)

        self.assertFalse("xrefs" in serialized)
        self.assertTrue("examples" in serialized)
        self.assertEqual(3, len(serialized["examples"]))
        self.assertEqual({'name': 'VPNp&v1 clone of Ito 2013',
                          'data': 'https://www.virtualflybrain.org/data/VFB/i/0002/0254/thumbnailT.png',
                          'reference': 'VFB_00020254',
                          'format': 'PNG'}, serialized["examples"][0])

        self.assertFalse("thumbnail" in serialized)
        self.assertTrue("references" in serialized)
        self.assertEqual(1, len(serialized["references"]))
        self.assertEqual({'link': '[Ito et al., 2013, Curr. Biol. 23(8): 644--655](FBrf0221438)',
                          'refs': ['http://flybase.org/reports/FBrf0221438',
                                   'https://doi.org/10.1016/j.cub.2013.03.015',
                                   'http://www.ncbi.nlm.nih.gov/pubmed/?term=23541729'],
                          'types': ' Entity Individual pub'}, serialized["references"][0])


class TestVariable:

    def __init__(self, _id, name):
        self.id = _id
        self.name = name

    def getId(self):
        return self.id

    def getName(self):
        return self.name


if __name__ == '__main__':
    unittest.main()
