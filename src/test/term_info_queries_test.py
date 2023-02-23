import unittest
import time
from src.term_info_queries import deserialize_term_info, deserialize_term_info_from_dict, process
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
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['VFB_00010001'], "Get JSON for Individual")[0]
        print(term_info_dict)
        start_time = time.time()
        serialized = process(term_info_dict, self.variable)
        print("--- %s seconds ---" % (time.time() - start_time))

        self.assertEqual("fru-F-500075 [VFB_00010001]", serialized["label"])
        self.assertFalse("title" in serialized)
        self.assertFalse("symbol" in serialized)
        self.assertFalse("logo" in serialized)
        self.assertFalse("link" in serialized)
        self.assertEqual(12, len(serialized["types"]))
        self.assertEqual("OutAge: Adult 5~15 days", serialized["description"])
        self.assertFalse("synonyms" in serialized)
        self.assertFalse("source" in serialized)
        self.assertFalse("license" in serialized)

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
        self.assertTrue("thumbnail" in serialized)
        self.assertEqual(2, len(serialized["thumbnail"]))
        print(serialized["thumbnail"])
        self.assertTrue({'data': 'https://www.virtualflybrain.org/data/VFB/i/0001/0001/VFB_00101567/thumbnailT.png',
                         'format': 'PNG',
                         'name': 'fru-F-500075',
                         'reference': 'VFB_00010001'} in serialized["thumbnail"])
        self.assertTrue({'data': 'https://www.virtualflybrain.org/data/VFB/i/0001/0001/thumbnailT.png',
                         'format': 'PNG',
                         'name': 'fru-F-500075 [adult brain template JFRC2]',
                         'reference': '[VFB_00017894,VFB_00010001]'} in serialized["thumbnail"])

        self.assertFalse("references" in serialized)
        self.assertFalse("targetingSplits" in serialized)
        self.assertFalse("targetingNeurons" in serialized)

        self.assertTrue("downloads_label" in serialized)
        self.assertEqual("JRC2018Unisex", serialized["downloads_label"])
        self.assertTrue("downloads" in serialized)
        self.assertEqual(5, len(serialized["downloads"]))
        self.assertTrue("[my_id_pointCloud.obj](/data/VFB/i/0001/0001/VFB_00101567/volume.obj)" in serialized["downloads"])
        self.assertTrue("[my_id.swc](/data/VFB/i/0001/0001/VFB_00101567/volume.swc)" in serialized["downloads"])
        self.assertTrue("[my_id.wlz](/data/VFB/i/0001/0001/VFB_00101567/volume.wlz)" in serialized["downloads"])
        self.assertTrue("[my_id.nrrd](/data/VFB/i/0001/0001/VFB_00101567/volume.nrrd)" in serialized["downloads"])
        self.assertTrue("[my_id.bibtex](/data/VFB/i/0001/0001/VFB_00101567/citations.bibtex)" in serialized["downloads"])

        self.assertTrue("filemeta" in serialized)
        self.assertEqual(5, len(serialized["filemeta"]))
        self.assertEqual({'obj': {'local': 'VFB_00101567/PointCloudFiles(OBJ)/',
                                  'url': 'https://v2.virtualflybrain.org/data/VFB/i/0001/0001/VFB_00101567/volume.obj'}},
                         serialized["filemeta"][0])
        self.assertEqual({'swc': {'local': 'VFB_00101567/MeshFiles(OBJ)/',
                                  'url': 'https://v2.virtualflybrain.org/data/VFB/i/0001/0001/VFB_00101567/volume.swc'}},
                         serialized["filemeta"][1])
        self.assertEqual({'wlz': {'local': 'VFB_00101567/Slices(WOOLZ)/',
                                  'url': 'https://v2.virtualflybrain.org/data/VFB/i/0001/0001/VFB_00101567/volume.wlz'}},
                         serialized["filemeta"][2])
        self.assertEqual({'nrrd': {'local': 'VFB_00101567/SignalFiles(NRRD)/',
                                   'url': 'https://v2.virtualflybrain.org/data/VFB/i/0001/0001/VFB_00101567/volume.nrrd'}},
                         serialized["filemeta"][3])
        self.assertEqual({'bibtex': {'local': 'VFB_00101567/RequiredCitations(BIBTEX)/',
                                     'url': 'https://v2.virtualflybrain.org/data/VFB/i/0001/0001/VFB_00101567/citations.bibtex'}},
                         serialized["filemeta"][4])

        self.assertTrue("template" in serialized)
        self.assertEqual("[JRC2018Unisex](VFB_00101567)", serialized["template"])

    def test_term_info_serialization_class(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['FBbt_00048531'], "Get JSON for Class")[0]
        print(term_info_dict)
        start_time = time.time()
        serialized = process(term_info_dict, self.variable)
        print("--- %s seconds ---" % (time.time() - start_time))

        self.assertEqual("female germline 2-cell cyst [FBbt_00048531]", serialized["label"])
        self.assertFalse("title" in serialized)
        self.assertFalse("symbol" in serialized)
        self.assertFalse("logo" in serialized)
        self.assertFalse("link" in serialized)
        self.assertEqual(4, len(serialized["types"]))
        self.assertTrue("Anatomy" in serialized["types"])
        self.assertEqual("Cyst composed of two cyst cells following the division of a newly-formed cystoblast in the germarium. The two cells are connected by a cytoplasmic bridge.\n([Spradling, 1993](FBrf0064777), [King, 1970](FBrf0021038))", serialized["description"])
        self.assertTrue("synonyms" in serialized)
        self.assertEqual(1, len(serialized["synonyms"]))
        self.assertEqual("has_exact_synonym: germarial 2-cell cluster ([King, 1970](FBrf0021038))", serialized["synonyms"][0])
        self.assertFalse("source" in serialized)
        self.assertFalse("license" in serialized)

        self.assertTrue("Classification" in serialized)
        self.assertEqual(1, len(serialized["Classification"]))
        self.assertEqual("[female germline cyst](FBbt_00007137)", serialized["Classification"][0])

        self.assertTrue("relationships" in serialized)
        self.assertEqual(1, len(serialized["relationships"]))
        self.assertEqual("is part of [germarium](FBbt_00004866)", serialized["relationships"][0])

        self.assertFalse("related_individuals" in serialized)

        self.assertFalse("xrefs" in serialized)
        self.assertFalse("examples" in serialized)
        self.assertFalse("thumbnail" in serialized)
        self.assertTrue("references" in serialized)
        self.assertEqual(2, len(serialized["references"]))
        self.assertEqual({'link': '[Spradling, 1993, Bate, Martinez Arias, 1993: 1--70](FBrf0064777)',
                          'refs': [],
                          'types': ' Entity Individual pub'}, serialized["references"][0])
        self.assertEqual({'link': '[King, 1970, Ovarian Development in Drosophila melanogaster. ](FBrf0021038)',
                          'refs': [],
                          'types': ' Entity Individual pub'}, serialized["references"][1])
        self.assertFalse("targetingSplits" in serialized)
        self.assertFalse("targetingNeurons" in serialized)

        self.assertFalse("downloads_label" in serialized)
        self.assertFalse("downloads" in serialized)
        self.assertFalse("filemeta" in serialized)
        self.assertFalse("template" in serialized)

    def test_term_info_serialization_neuron_class(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['FBbt_00048999'], "Get JSON for Neuron Class")[0]
        print(term_info_dict)
        start_time = time.time()
        serialized = process(term_info_dict, self.variable)
        print("--- %s seconds ---" % (time.time() - start_time))

        self.assertEqual("adult Drosulfakinin neuron [FBbt_00048999]", serialized["label"])
        self.assertFalse("title" in serialized)
        self.assertFalse("symbol" in serialized)
        self.assertFalse("logo" in serialized)
        self.assertFalse("link" in serialized)
        self.assertEqual(7, len(serialized["types"]))
        self.assertTrue("Neuron" in serialized["types"])
        self.assertEqual("Any adult neuron that expresses the neuropeptide Drosulfakinin (Dsk).\n([Söderberg et al., 2012](FBrf0219451))", serialized["description"])
        self.assertTrue("synonyms" in serialized)
        self.assertEqual(4, len(serialized["synonyms"]))
        self.assertTrue("has_exact_synonym: adult dsk neuron ([Söderberg et al., 2012](FBrf0219451))" in serialized["synonyms"])
        self.assertFalse("source" in serialized)
        self.assertFalse("license" in serialized)

        self.assertTrue("Classification" in serialized)
        self.assertEqual(2, len(serialized["Classification"]))
        self.assertEqual("[adult neuron](FBbt_00047095)", serialized["Classification"][0])

        self.assertFalse("relationships" in serialized)
        self.assertFalse("related_individuals" in serialized)
        self.assertFalse("xrefs" in serialized)
        self.assertTrue("examples" in serialized)
        self.assertEqual(5, len(serialized["examples"]))
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/jrch/jti2/VFB_00101567/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'DSKMP1A_R (FlyEM-HB:1135837629)',
                          'reference': 'VFB_jrchjti2'}, serialized["examples"][0])
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/jrch/jti2/VFB_00101384/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'DSKMP1A_R (FlyEM-HB:1135837629)',
                          'reference': 'VFB_jrchjti2'}, serialized["examples"][1])
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/jrch/jti4/VFB_00101567/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'DSKMP1B_R (FlyEM-HB:1352077058)',
                          'reference': 'VFB_jrchjti4'}, serialized["examples"][2])
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/jrch/jti4/VFB_00101384/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'DSKMP1B_R (FlyEM-HB:1352077058)',
                          'reference': 'VFB_jrchjti4'}, serialized["examples"][3])
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/jrch/jti3/VFB_00101567/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'DSKMP1A(PVM02)_L (FlyEM-HB:1260833150)',
                          'reference': 'VFB_jrchjti3'}, serialized["examples"][4])

        self.assertFalse("thumbnail" in serialized)
        self.assertTrue("references" in serialized)
        self.assertEqual(1, len(serialized["references"]))
        self.assertEqual({'link': '[Söderberg et al., 2012, Front. Endocrinol. 3: 109](FBrf0219451)',
                          'refs': ['https://doi.org/10.3389/fendo.2012.00109',
                                   'http://www.ncbi.nlm.nih.gov/pubmed/?term=22969751'],
                          'types': ' Entity Individual pub'}, serialized["references"][0])
        self.assertFalse("targetingSplits" in serialized)
        self.assertFalse("targetingNeurons" in serialized)

        self.assertFalse("downloads_label" in serialized)
        self.assertFalse("downloads" in serialized)
        self.assertFalse("filemeta" in serialized)
        self.assertFalse("template" in serialized)

    def test_term_info_serialization_neuron_class2(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['FBbt_00047030'], "Get JSON for Neuron Class")[0]
        print(term_info_dict)
        start_time = time.time()
        serialized = process(term_info_dict, self.variable)
        print("--- %s seconds ---" % (time.time() - start_time))

        self.assertEqual("adult ellipsoid body-protocerebral bridge 1 glomerulus-dorsal/ventral gall neuron [FBbt_00047030]", serialized["label"])
        self.assertFalse("title" in serialized)
        self.assertTrue("symbol" in serialized)
        self.assertEqual("EPG", serialized["symbol"])
        self.assertFalse("logo" in serialized)
        self.assertFalse("link" in serialized)
        self.assertEqual(8, len(serialized["types"]))
        self.assertTrue("Neuron" in serialized["types"])
        self.assertTrue("Cholinergic" in serialized["types"])
        self.assertEqual("Small field neuron of the central complex with dendritic and axonal arbors in the inner, outer and posterior layers of either a half or a full ellipsoid body (EB) slice (wedge), and axon terminals in the dorsal or ventral gall and a single protocerebral bridge glomerulus (excluding glomerulus 9) (Lin et al., 2013; Wolff et al., 2015). Neurons that target odd or even numbered protocerebral bridge glomeruli target the dorsal or ventral gall, respectively (Lin et al., 2013; Wolff et al., 2015). These neurons receive inhibitory input from delta 7 (PB 18 glomeruli) neurons and they are cholinergic (Turner-Evans et al., 2020). These cells output to P-EN1 neurons and P-EG neurons of the same glomerulus in the protocerebral bridge, and form less specific 'hyper-local' feedback loops with P-EN1 neurons in the EB (Turner-Evans et al., 2020). It also receives input from R4d ring neurons and P-EN2 neurons in the EB (Turner-Evans et al., 2020). "
                         "\n Based on images/diagrams in Lin et al. (2013), Wolff et al. (2015) and Turner-Evans et al. (2020), these appear to innervate the ipsilateral PB and contralateral gall, but could not find confirmation of this [FBC:CP]."
                         "\n([Lin et al., 2013](FBrf0221742), [Wolff et al., 2015](FBrf0227801), [Wolff and Rubin, 2018](FBrf0240744), [Turner-Evans et al., 2020](FBrf0246945))", serialized["description"])
        self.assertTrue("synonyms" in serialized)
        self.assertEqual(8, len(serialized["synonyms"]))
        print(serialized["synonyms"][0])
        self.assertTrue("has_exact_synonym: EB-PB 1 glomerulus-D/Vgall neuron" in serialized["synonyms"])
        self.assertFalse("source" in serialized)
        self.assertFalse("license" in serialized)

        self.assertTrue("Classification" in serialized)
        self.assertEqual(2, len(serialized["Classification"]))
        self.assertEqual("[adult ellipsoid body-protocerebral bridge-gall neuron](FBbt_00003637)", serialized["Classification"][0])

        self.assertTrue("relationships" in serialized)
        self.assertEqual(10, len(serialized["relationships"]))
        print(serialized["relationships"][0])
        self.assertEqual("sends_synaptic_output_to_region [protocerebral bridge glomerulus](FBbt_00003669)", serialized["relationships"][0])
        self.assertFalse("related_individuals" in serialized)
        self.assertFalse("xrefs" in serialized)
        self.assertTrue("examples" in serialized)
        self.assertEqual(5, len(serialized["examples"]))
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/0010/12b9/VFB_00101567/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'EPG-6R#1 (FAFB:1274114)',
                          'reference': 'VFB_001012b9'}, serialized["examples"][0])

        self.assertFalse("thumbnail" in serialized)

        self.assertTrue("references" in serialized)
        self.assertEqual(5, len(serialized["references"]))
        self.assertEqual({'link': '[Lin et al., 2013, Cell Rep. 3(5): 1739--1753](FBrf0221742)',
                          'refs': ['https://doi.org/10.1016/j.celrep.2013.04.022',
                                   'http://www.ncbi.nlm.nih.gov/pubmed/?term=23707064'],
                          'types': ' Entity Individual pub'}, serialized["references"][0])

        self.assertTrue("targetingSplits" in serialized)
        self.assertEqual(4, len(serialized["targetingSplits"]))
        self.assertTrue("[P{R93G12-GAL4.DBD} ∩ P{R19G02-p65.AD} expression pattern](VFBexp_FBtp0122505FBtp0117182)"
                        in serialized["targetingSplits"])
        self.assertFalse("targetingNeurons" in serialized)

        self.assertFalse("downloads_label" in serialized)
        self.assertFalse("downloads" in serialized)
        self.assertFalse("filemeta" in serialized)
        self.assertFalse("template" in serialized)

    def test_term_info_serialization_split_class(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['VFBexp_FBtp0124468FBtp0133404'], "Get JSON for Split Class")[0]
        print(term_info_dict)
        start_time = time.time()
        serialized = process(term_info_dict, self.variable)
        print("--- %s seconds ---" % (time.time() - start_time))

        self.assertEqual("P{VT043927-GAL4.DBD} ∩ P{VT017491-p65.AD} expression pattern [VFBexp_FBtp0124468FBtp0133404]", serialized["label"])
        self.assertFalse("title" in serialized)
        self.assertTrue("symbol" in serialized)
        self.assertEqual("SS50574", serialized["symbol"])
        self.assertFalse("logo" in serialized)
        self.assertFalse("link" in serialized)
        self.assertEqual(5, len(serialized["types"]))
        self.assertTrue("Split" in serialized["types"])
        self.assertEqual("The sum of all cells at the intersection between the expression patterns of P{VT043927-GAL4.DBD} and P{VT017491-p65.AD}.", serialized["description"])
        self.assertTrue("synonyms" in serialized)
        self.assertEqual(2, len(serialized["synonyms"]))
        self.assertTrue("has_exact_synonym: VT017491-x-VT043927" in serialized["synonyms"])
        self.assertFalse("source" in serialized)
        self.assertFalse("license" in serialized)

        self.assertTrue("Classification" in serialized)
        self.assertEqual(1, len(serialized["Classification"]))
        self.assertEqual("[intersectional expression pattern](VFBext_0000010)", serialized["Classification"][0])

        self.assertTrue("relationships" in serialized)
        self.assertEqual(2, len(serialized["relationships"]))
        self.assertEqual("has hemidriver [P{VT043927-GAL4.DBD}](FBtp0124468)", serialized["relationships"][0])

        self.assertFalse("related_individuals" in serialized)
        self.assertTrue("xrefs" in serialized)
        self.assertEqual(2, len(serialized["xrefs"]))
        self.assertEqual({'icon': 'http://www.virtualflybrain.org/data/VFB/logos/fly_light_color.png',
                          'label': '[P{VT043927-GAL4.DBD} ∩ P{VT017491-p65.AD} expression pattern on '
                                   'Driver Line on the FlyLight Split-GAL4 Site]'
                                   '(http://splitgal4.janelia.org/cgi-bin/view_splitgal4_imagery.cgi?line=SS50574)',
                          'site': '[FlyLightSplit]'
                                  '(http://splitgal4.janelia.org/cgi-bin/view_splitgal4_imagery.cgi?line=SS50574) '},
                         serialized["xrefs"][0])

        self.assertFalse("examples" in serialized)
        self.assertFalse("thumbnail" in serialized)
        self.assertFalse("references" in serialized)
        self.assertFalse("targetingSplits" in serialized)
        self.assertTrue("targetingNeurons" in serialized)
        self.assertEqual(1, len(serialized["targetingNeurons"]))
        self.assertEqual("[adult ellipsoid body-protocerebral bridge 1 glomerulus-dorsal/ventral gall neuron](FBbt_00047030)", serialized["targetingNeurons"][0])

        self.assertFalse("downloads_label" in serialized)
        self.assertFalse("downloads" in serialized)
        self.assertFalse("filemeta" in serialized)
        self.assertFalse("template" in serialized)

    def test_term_info_serialization_dataset(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['Ito2013'], "Get JSON for DataSet")[0]
        print(term_info_dict)
        start_time = time.time()
        serialized = process(term_info_dict, self.variable)
        print("--- %s seconds ---" % (time.time() - start_time))

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
        self.assertFalse("license" in serialized)
        self.assertFalse("Classification" in serialized)
        self.assertFalse("relationships" in serialized)
        self.assertFalse("related_individuals" in serialized)

        self.assertFalse("xrefs" in serialized)
        self.assertTrue("examples" in serialized)
        self.assertEqual(5, len(serialized["examples"]))
        self.assertEqual({'name': 'VPNp&v1 clone of Ito 2013',
                          'data': 'https://www.virtualflybrain.org/data/VFB/i/0002/0254/thumbnailT.png',
                          'reference': 'VFB_00020254',
                          'format': 'PNG'}, serialized["examples"][0])
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/0002/0204/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'DM6 clone of Ito 2013',
                          'reference': 'VFB_00020204'}, serialized["examples"][1])
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/0002/0194/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'CLp1 clone of Ito 2013',
                          'reference': 'VFB_00020194'}, serialized["examples"][2])
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/0002/0254/VFB_00101567/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'VPNp&v1 clone of Ito 2013',
                          'reference': 'VFB_00020254'}, serialized["examples"][3])
        self.assertEqual({'data': 'https://www.virtualflybrain.org/data/VFB/i/0002/0204/VFB_00101567/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'DM6 clone of Ito 2013',
                          'reference': 'VFB_00020204'}, serialized["examples"][4])

        self.assertFalse("thumbnail" in serialized)
        self.assertTrue("references" in serialized)
        self.assertEqual(1, len(serialized["references"]))
        self.assertEqual({'link': '[Ito et al., 2013, Curr. Biol. 23(8): 644--655](FBrf0221438)',
                          'refs': ['http://flybase.org/reports/FBrf0221438',
                                   'https://doi.org/10.1016/j.cub.2013.03.015',
                                   'http://www.ncbi.nlm.nih.gov/pubmed/?term=23541729'],
                          'types': ' Entity Individual pub'}, serialized["references"][0])
        self.assertFalse("targetingSplits" in serialized)
        self.assertFalse("targetingNeurons" in serialized)

        self.assertFalse("downloads_label" in serialized)
        self.assertFalse("downloads" in serialized)
        self.assertFalse("filemeta" in serialized)
        self.assertFalse("template" in serialized)

    def test_term_info_serialization_license(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['VFBlicense_CC_BY_NC_3_0'], "Get JSON for License")[0]
        print(term_info_dict)
        start_time = time.time()
        serialized = process(term_info_dict, self.variable)
        print("--- %s seconds ---" % (time.time() - start_time))

        self.assertEqual("CC-BY-NC_3.0 [VFBlicense_CC_BY_NC_3_0]", serialized["label"])
        self.assertFalse("title" in serialized)
        self.assertFalse("symbol" in serialized)
        self.assertTrue("logo" in serialized)
        self.assertEqual(
            "[https://creativecommons.org/licenses/by-nc/3.0/legalcode]"
            "(http://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc.png)", serialized["logo"])
        self.assertTrue("link" in serialized)
        self.assertEqual("[https://creativecommons.org/licenses/by-nc/3.0/legalcode](https://creativecommons.org/licenses/by-nc/3.0/legalcode)", serialized["link"])
        self.assertEqual(3, len(serialized["types"]))
        self.assertTrue("License" in serialized["types"])
        self.assertFalse("description" in serialized)
        self.assertFalse("synonyms" in serialized)
        self.assertFalse("source" in serialized)
        self.assertFalse("license" in serialized)
        self.assertFalse("Classification" in serialized)
        self.assertFalse("relationships" in serialized)
        self.assertFalse("related_individuals" in serialized)
        self.assertFalse("xrefs" in serialized)
        self.assertFalse("examples" in serialized)
        self.assertFalse("thumbnail" in serialized)
        self.assertFalse("references" in serialized)
        self.assertFalse("targetingSplits" in serialized)
        self.assertFalse("targetingNeurons" in serialized)

        self.assertFalse("downloads_label" in serialized)
        self.assertFalse("downloads" in serialized)
        self.assertFalse("filemeta" in serialized)
        self.assertFalse("template" in serialized)

    def test_term_info_serialization_template(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['VFB_00200000'], "Get JSON for Template")[0]
        print(term_info_dict)
        start_time = time.time()
        serialized = process(term_info_dict, self.variable)
        print("--- %s seconds ---" % (time.time() - start_time))

        self.assertEqual("JRC2018UnisexVNC [VFB_00200000]", serialized["label"])
        self.assertFalse("title" in serialized)
        self.assertFalse("symbol" in serialized)
        self.assertFalse("logo" in serialized)
        self.assertFalse("link" in serialized)
        self.assertEqual(8, len(serialized["types"]))
        self.assertTrue("Template" in serialized["types"])
        self.assertFalse("description" in serialized)
        self.assertFalse("synonyms" in serialized)
        self.assertFalse("source" in serialized)
        self.assertFalse("license" in serialized)
        self.assertTrue("Classification" in serialized)
        self.assertEqual(1, len(serialized["Classification"]))
        self.assertEqual("[adult ventral nerve cord](FBbt_00004052)", serialized["Classification"][0])
        self.assertFalse("relationships" in serialized)
        self.assertFalse("related_individuals" in serialized)
        self.assertFalse("xrefs" in serialized)
        self.assertFalse("examples" in serialized)
        self.assertTrue("thumbnail" in serialized)
        self.assertEqual(1, len(serialized["thumbnail"]))
        self.assertEqual({'data': 'http://www.virtualflybrain.org/data/VFB/i/0020/0000/VFB_00200000/thumbnailT.png',
                          'format': 'PNG',
                          'name': 'JRC2018UnisexVNC',
                          'reference': 'VFB_00200000'}, serialized["thumbnail"][0])

        self.assertFalse("references" in serialized)
        self.assertFalse("targetingSplits" in serialized)
        self.assertFalse("targetingNeurons" in serialized)

        self.assertFalse("downloads_label" in serialized)
        self.assertTrue("downloads" in serialized)
        self.assertEqual(3, len(serialized["downloads"]))
        self.assertEqual("[my_id_mesh.obj](/data/VFB/i/0020/0000/VFB_00200000/volume_man.obj)", serialized["downloads"][0])
        self.assertEqual("[my_id.wlz](/data/VFB/i/0020/0000/VFB_00200000/volume.wlz)", serialized["downloads"][1])
        self.assertEqual("[my_id.nrrd](/data/VFB/i/0020/0000/VFB_00200000/volume.nrrd)", serialized["downloads"][2])

        self.assertTrue("filemeta" in serialized)
        self.assertEqual(3, len(serialized["filemeta"]))
        self.assertEqual({'obj': {'local': '/MeshFiles(OBJ)/my_id_(my_name).obj',
                                  'url': 'https://v2.virtualflybrain.org/data/VFB/i/0020/0000/VFB_00200000/volume_man.obj'}},
                         serialized["filemeta"][0])
        self.assertEqual({'wlz': {'local': '/Slices(WOOLZ)/my_id_(my_name).wlz',
                                  'url': 'https://v2.virtualflybrain.org/data/VFB/i/0020/0000/VFB_00200000/volume.wlz'}},
                         serialized["filemeta"][1])
        self.assertEqual({'nrrd': {'local': '/SignalFiles(NRRD)/my_id_(my_name).nrrd',
                                   'url': 'https://v2.virtualflybrain.org/data/VFB/i/0020/0000/VFB_00200000/volume.nrrd'}},
                         serialized["filemeta"][2])

        self.assertTrue("template" in serialized)
        self.assertEqual("[JRC2018UnisexVNC](VFB_00200000)", serialized["template"])

    def test_term_info_serialization_pub(self):
        term_info_dict = self.vc.neo_query_wrapper._get_TermInfo(['FBrf0243986'], "Get JSON for pub")[0]
        print(term_info_dict)
        start_time = time.time()
        serialized = process(term_info_dict, self.variable)
        print("--- %s seconds ---" % (time.time() - start_time))

        self.assertEqual("Sayin et al., 2019, Neuron 104(3): 544--558.e6 [FBrf0243986]", serialized["label"])
        self.assertTrue("title" in serialized)
        self.assertEqual("A Neural Circuit Arbitrates between Persistence and Withdrawal in Hungry Drosophila.", serialized["title"])
        self.assertFalse("symbol" in serialized)
        self.assertFalse("logo" in serialized)
        self.assertFalse("link" in serialized)
        self.assertEqual(3, len(serialized["types"]))
        self.assertTrue("pub" in serialized["types"])
        self.assertFalse("description" in serialized)
        self.assertFalse("synonyms" in serialized)
        self.assertFalse("source" in serialized)
        self.assertFalse("license" in serialized)
        self.assertFalse("Classification" in serialized)
        self.assertFalse("relationships" in serialized)
        self.assertFalse("related_individuals" in serialized)

        self.assertTrue("xrefs" in serialized)
        self.assertEqual(3, len(serialized["xrefs"]))
        self.assertEqual("FBrf0243986", serialized["xrefs"][0])
        self.assertEqual("31471123", serialized["xrefs"][1])
        self.assertEqual("10.1016/j.neuron.2019.07.028", serialized["xrefs"][2])

        self.assertFalse("examples" in serialized)
        self.assertFalse("thumbnail" in serialized)
        self.assertFalse("references" in serialized)
        self.assertFalse("targetingSplits" in serialized)
        self.assertFalse("targetingNeurons" in serialized)

        self.assertFalse("downloads_label" in serialized)
        self.assertFalse("downloads" in serialized)
        self.assertFalse("filemeta" in serialized)
        self.assertFalse("template" in serialized)


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
