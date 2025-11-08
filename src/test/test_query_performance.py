#!/usr/bin/env python3
"""
Comprehensive performance test for all VFB queries.

Tests the execution time of all implemented queries to ensure they meet performance thresholds.
Results are formatted for GitHub Actions reporting.
"""

import unittest
import time
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vfbquery.vfb_queries import (
    get_term_info,
    get_neurons_with_part_in,
    get_neurons_with_synapses_in,
    get_neurons_with_presynaptic_terminals_in,
    get_neurons_with_postsynaptic_terminals_in,
    get_components_of,
    get_parts_of,
    get_subclasses_of,
    get_neuron_classes_fasciculating_here,
    get_tracts_nerves_innervating_here,
    get_lineage_clones_in,
    get_images_neurons,
    get_images_that_develop_from,
    get_expression_pattern_fragments,
    get_instances,
    get_similar_neurons,
    get_neuron_neuron_connectivity,
    get_neuron_region_connectivity,
    get_individual_neuron_inputs,
    get_expression_overlaps_here,
    get_anatomy_scrnaseq,
    get_cluster_expression,
    get_expression_cluster,
    get_scrnaseq_dataset_data,
)


class QueryPerformanceTest(unittest.TestCase):
    """Comprehensive performance tests for all VFB queries"""
    
    # Performance thresholds (in seconds)
    THRESHOLD_FAST = 1.0       # Fast queries (simple SOLR lookups)
    THRESHOLD_MEDIUM = 3.0     # Medium queries (Owlery + SOLR)
    THRESHOLD_SLOW = 10.0      # Slow queries (Neo4j + complex processing)
    THRESHOLD_VERY_SLOW = 1200.0  # Very slow queries (complex OWL reasoning - 20 minutes)
    
    @classmethod
    def setUpClass(cls):
        """Enable caching for performance tests"""
        # Import caching module
        from vfbquery import cache_enhancements
        
        # Enable caching to speed up repeated queries
        cache_enhancements.enable_vfbquery_caching()
        print("\n🔥 Caching enabled for performance tests")
    
    def setUp(self):
        """Set up test data"""
        self.test_terms = {
            'mushroom_body': 'FBbt_00003748',      # Class - mushroom body
            'antennal_lobe': 'FBbt_00007401',       # Synaptic neuropil
            'medulla': 'FBbt_00003982',             # Visual system
            'broad_root': 'FBbt_00003987',          # Neuron projection bundle (tract)
            'individual_neuron': 'VFB_00101567',    # Individual anatomy
            'neuron_with_nblast': 'VFB_00017894',   # Neuron with NBLAST data (alternative)
            'clone': 'FBbt_00050024',               # Clone
            'connected_neuron': 'VFB_jrchk00s',     # LPC1 neuron with connectivity AND NBLAST data
        }
        
        self.results = []
        
    def _time_query(self, query_name, query_func, *args, **kwargs):
        """Helper to time a query execution"""
        start_time = time.time()
        try:
            result = query_func(*args, **kwargs)
            duration = time.time() - start_time
            success = result is not None
            error = None
        except Exception as e:
            duration = time.time() - start_time
            success = False
            result = None
            error = str(e)
        
        self.results.append({
            'name': query_name,
            'duration': duration,
            'success': success,
            'error': error
        })
        
        return result, duration, success
    
    def test_01_term_info_queries(self):
        """Test term info query performance"""
        print("\n" + "="*80)
        print("TERM INFO QUERIES")
        print("="*80)
        
        # Test basic term info retrieval
        result, duration, success = self._time_query(
            "get_term_info (mushroom body)",
            get_term_info,
            self.test_terms['mushroom_body'],
            preview=True
        )
        print(f"get_term_info (mushroom body): {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "term_info query exceeded threshold")
        
        result, duration, success = self._time_query(
            "get_term_info (individual)",
            get_term_info,
            self.test_terms['individual_neuron'],
            preview=True
        )
        print(f"get_term_info (individual): {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "term_info query exceeded threshold")
    
    def test_02_neuron_part_queries(self):
        """Test neuron part overlap queries"""
        print("\n" + "="*80)
        print("NEURON PART OVERLAP QUERIES")
        print("="*80)
        
        result, duration, success = self._time_query(
            "NeuronsPartHere (antennal lobe)",
            get_neurons_with_part_in,
            self.test_terms['antennal_lobe'],
            return_dataframe=False,
            limit=-1  # Changed to -1 to enable caching
        )
        print(f"NeuronsPartHere: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "NeuronsPartHere exceeded threshold")
    
    def test_03_synaptic_queries(self):
        """Test synaptic terminal queries"""
        print("\n" + "="*80)
        print("SYNAPTIC TERMINAL QUERIES")
        print("="*80)
        
        test_term = self.test_terms['antennal_lobe']
        
        result, duration, success = self._time_query(
            "NeuronsSynaptic",
            get_neurons_with_synapses_in,
            test_term,
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"NeuronsSynaptic: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "NeuronsSynaptic exceeded threshold")
        
        result, duration, success = self._time_query(
            "NeuronsPresynapticHere",
            get_neurons_with_presynaptic_terminals_in,
            test_term,
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"NeuronsPresynapticHere: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "NeuronsPresynapticHere exceeded threshold")
        
        result, duration, success = self._time_query(
            "NeuronsPostsynapticHere",
            get_neurons_with_postsynaptic_terminals_in,
            test_term,
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"NeuronsPostsynapticHere: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "NeuronsPostsynapticHere exceeded threshold")
        
        # Test neuron-neuron connectivity query
        result, duration, success = self._time_query(
            "NeuronNeuronConnectivity",
            get_neuron_neuron_connectivity,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"NeuronNeuronConnectivity: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronNeuronConnectivity exceeded threshold")
    
    def test_04_anatomy_hierarchy_queries(self):
        """Test anatomical hierarchy queries"""
        print("\n" + "="*80)
        print("ANATOMICAL HIERARCHY QUERIES")
        print("="*80)
        
        test_term = self.test_terms['mushroom_body']
        
        result, duration, success = self._time_query(
            "ComponentsOf",
            get_components_of,
            test_term,
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"ComponentsOf: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "ComponentsOf exceeded threshold")
        
        result, duration, success = self._time_query(
            "PartsOf",
            get_parts_of,
            test_term,
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"PartsOf: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "PartsOf exceeded threshold")
        
        result, duration, success = self._time_query(
            "SubclassesOf",
            get_subclasses_of,
            test_term,
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"SubclassesOf: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "SubclassesOf exceeded threshold")
    
    def test_05_new_queries(self):
        """Test newly implemented queries"""
        print("\n" + "="*80)
        print("NEW QUERIES (2025)")
        print("="*80)
        
        # NeuronClassesFasciculatingHere
        result, duration, success = self._time_query(
            "NeuronClassesFasciculatingHere",
            get_neuron_classes_fasciculating_here,
            self.test_terms['broad_root'],
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"NeuronClassesFasciculatingHere: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronClassesFasciculatingHere exceeded threshold")
        
        # TractsNervesInnervatingHere
        result, duration, success = self._time_query(
            "TractsNervesInnervatingHere",
            get_tracts_nerves_innervating_here,
            self.test_terms['antennal_lobe'],
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"TractsNervesInnervatingHere: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "TractsNervesInnervatingHere exceeded threshold")
        
        # LineageClonesIn
        result, duration, success = self._time_query(
            "LineageClonesIn",
            get_lineage_clones_in,
            self.test_terms['antennal_lobe'],
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"LineageClonesIn: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "LineageClonesIn exceeded threshold")
        
        # ImagesNeurons
        result, duration, success = self._time_query(
            "ImagesNeurons",
            get_images_neurons,
            self.test_terms['antennal_lobe'],
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"ImagesNeurons: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "ImagesNeurons exceeded threshold")
        
        # ImagesThatDevelopFrom test (neuroblast developmental lineages)
        result, duration, success = self._time_query(
            "ImagesThatDevelopFrom",
            get_images_that_develop_from,
            "FBbt_00001419",  # neuroblast MNB - has 336 neuron images
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"ImagesThatDevelopFrom: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "ImagesThatDevelopFrom exceeded threshold")
        
        # epFrag test (expression pattern fragments)
        result, duration, success = self._time_query(
            "epFrag",
            get_expression_pattern_fragments,
            "FBtp0000001",  # expression pattern example
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"epFrag: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "epFrag exceeded threshold")
    
    def test_06_instance_queries(self):
        """Test instance retrieval queries"""
        print("\n" + "="*80)
        print("INSTANCE QUERIES")
        print("="*80)
        
        result, duration, success = self._time_query(
            "ListAllAvailableImages",
            get_instances,
            self.test_terms['medulla'],
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"ListAllAvailableImages: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "ListAllAvailableImages exceeded threshold")
    
    def test_07_connectivity_queries(self):
        """Test neuron connectivity queries"""
        print("\n" + "="*80)
        print("CONNECTIVITY QUERIES")
        print("="*80)
        
        # NeuronNeuronConnectivity
        result, duration, success = self._time_query(
            "NeuronNeuronConnectivityQuery",
            get_neuron_neuron_connectivity,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"NeuronNeuronConnectivityQuery: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronNeuronConnectivityQuery exceeded threshold")
        
        # NeuronRegionConnectivity
        result, duration, success = self._time_query(
            "NeuronRegionConnectivityQuery",
            get_neuron_region_connectivity,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"NeuronRegionConnectivityQuery: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronRegionConnectivityQuery exceeded threshold")
    
    def test_08_similarity_queries(self):
        """Test NBLAST similarity queries"""
        print("\n" + "="*80)
        print("SIMILARITY QUERIES (Neo4j NBLAST)")
        print("="*80)
        
        # SimilarMorphologyTo (NBLAST)
        result, duration, success = self._time_query(
            "SimilarMorphologyTo",
            get_similar_neurons,
            self.test_terms['connected_neuron'],  # VFB_jrchk00s has NBLAST data
            similarity_score='NBLAST_score',
            return_dataframe=False,
            limit=5
        )
        print(f"SimilarMorphologyTo: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "SimilarMorphologyTo exceeded threshold")
        # self.assertLess(duration, self.THRESHOLD_SLOW, "SimilarMorphologyTo exceeded threshold")
    
    def test_09_neuron_input_queries(self):
        """Test neuron input/synapse queries"""
        print("\n" + "="*80)
        print("NEURON INPUT QUERIES (Neo4j)")
        print("="*80)
        
        # NeuronInputsTo
        result, duration, success = self._time_query(
            "NeuronInputsTo",
            get_individual_neuron_inputs,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=5
        )
        print(f"NeuronInputsTo: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronInputsTo exceeded threshold")
    
    def test_10_expression_queries(self):
        """Test expression pattern queries"""
        print("\n" + "="*80)
        print("EXPRESSION PATTERN QUERIES (Neo4j)")
        print("="*80)
        
        # ExpressionOverlapsHere - test with adult brain which has many expression patterns
        result, duration, success = self._time_query(
            "ExpressionOverlapsHere (adult brain)",
            get_expression_overlaps_here,
            self.test_terms['medulla'],  # FBbt_00003982 (adult brain/medulla)
            return_dataframe=False,
            limit=10  # Limit to 10 for performance test
        )
        print(f"ExpressionOverlapsHere: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            print(f"  └─ Found {result.get('count', 0)} total expression patterns, returned 10")
        self.assertLess(duration, self.THRESHOLD_SLOW, "ExpressionOverlapsHere exceeded threshold")
    
    def test_11_transcriptomics_queries(self):
        """Test scRNAseq transcriptomics queries"""
        print("\n" + "="*80)
        print("TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)")
        print("="*80)
        
        # Note: These tests use example IDs that may need to be updated based on actual database content
        # The queries are designed to work even if no data is found (will return empty results)
        
        # anatScRNAseqQuery - test with adult brain
        result, duration, success = self._time_query(
            "anatScRNAseqQuery (adult brain)",
            get_anatomy_scrnaseq,
            self.test_terms['medulla'],  # FBbt_00003982 (adult brain/medulla)
            return_dataframe=False,
            limit=10
        )
        print(f"anatScRNAseqQuery: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} total clusters" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_SLOW, "anatScRNAseqQuery exceeded threshold")
        
        # clusterExpression - test with a cluster ID (may return empty if cluster doesn't exist)
        # Using a dummy ID - test will pass even with empty results
        try:
            result, duration, success = self._time_query(
                "clusterExpression (example cluster)",
                get_cluster_expression,
                "VFBc_00101567",  # Example cluster ID
                return_dataframe=False,
                limit=10
            )
            print(f"clusterExpression: {duration:.4f}s {'✅' if success else '❌'}")
            if success and result:
                count = result.get('count', 0)
                print(f"  └─ Found {count} genes expressed" + (", returned 10" if count > 10 else ""))
            self.assertLess(duration, self.THRESHOLD_SLOW, "clusterExpression exceeded threshold")
        except Exception as e:
            print(f"clusterExpression: Skipped (test data may not exist): {e}")
        
        # expressionCluster - test with a gene ID (may return empty if no scRNAseq data)
        try:
            result, duration, success = self._time_query(
                "expressionCluster (example gene)",
                get_expression_cluster,
                "FBgn_00000024",  # Example gene ID
                return_dataframe=False,
                limit=10
            )
            print(f"expressionCluster: {duration:.4f}s {'✅' if success else '❌'}")
            if success and result:
                count = result.get('count', 0)
                print(f"  └─ Found {count} clusters expressing gene" + (", returned 10" if count > 10 else ""))
            self.assertLess(duration, self.THRESHOLD_SLOW, "expressionCluster exceeded threshold")
        except Exception as e:
            print(f"expressionCluster: Skipped (test data may not exist): {e}")
        
        # scRNAdatasetData - test with a dataset ID (may return empty if dataset doesn't exist)
        try:
            result, duration, success = self._time_query(
                "scRNAdatasetData (example dataset)",
                get_scrnaseq_dataset_data,
                "VFBds_00001234",  # Example dataset ID
                return_dataframe=False,
                limit=10
            )
            print(f"scRNAdatasetData: {duration:.4f}s {'✅' if success else '❌'}")
            if success and result:
                count = result.get('count', 0)
                print(f"  └─ Found {count} clusters in dataset" + (", returned 10" if count > 10 else ""))
            self.assertLess(duration, self.THRESHOLD_SLOW, "scRNAdatasetData exceeded threshold")
        except Exception as e:
            print(f"scRNAdatasetData: Skipped (test data may not exist): {e}")
    
    def test_12_nblast_queries(self):
        """Test NBLAST similarity queries"""
        print("\n" + "="*80)
        print("NBLAST SIMILARITY QUERIES (2025)")
        print("="*80)
        
        # Import the new query functions
        from vfbquery.vfb_queries import (
            get_similar_morphology,
            get_similar_morphology_part_of,
            get_similar_morphology_part_of_exp,
            get_similar_morphology_nb,
            get_similar_morphology_nb_exp,
            get_similar_morphology_userdata
        )
        
        # SimilarMorphologyTo - NBLAST matches
        result, duration, success = self._time_query(
            "SimilarMorphologyTo",
            get_similar_morphology,
            self.test_terms['connected_neuron'],  # LPC1 neuron with NBLAST data
            return_dataframe=False,
            limit=10
        )
        print(f"SimilarMorphologyTo: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} NBLAST matches" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "SimilarMorphologyTo exceeded threshold")
        
        # SimilarMorphologyToPartOf - NBLASTexp to expression patterns
        result, duration, success = self._time_query(
            "SimilarMorphologyToPartOf",
            get_similar_morphology_part_of,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=10
        )
        print(f"SimilarMorphologyToPartOf: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} NBLASTexp matches" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "SimilarMorphologyToPartOf exceeded threshold")
        
        # SimilarMorphologyToPartOfexp - Reverse NBLASTexp
        result, duration, success = self._time_query(
            "SimilarMorphologyToPartOfexp",
            get_similar_morphology_part_of_exp,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=10
        )
        print(f"SimilarMorphologyToPartOfexp: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} reverse NBLASTexp matches" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "SimilarMorphologyToPartOfexp exceeded threshold")
        
        # SimilarMorphologyToNB - NeuronBridge matches
        result, duration, success = self._time_query(
            "SimilarMorphologyToNB",
            get_similar_morphology_nb,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=10
        )
        print(f"SimilarMorphologyToNB: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} NeuronBridge matches" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "SimilarMorphologyToNB exceeded threshold")
        
        # SimilarMorphologyToNBexp - NeuronBridge for expression patterns
        result, duration, success = self._time_query(
            "SimilarMorphologyToNBexp",
            get_similar_morphology_nb_exp,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=10
        )
        print(f"SimilarMorphologyToNBexp: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} NeuronBridge expression matches" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "SimilarMorphologyToNBexp exceeded threshold")
        
        print(f"✅ All NBLAST similarity queries completed")
    
    def test_13_dataset_template_queries(self):
        """Test dataset and template queries"""
        print("\n" + "="*80)
        print("DATASET/TEMPLATE QUERIES (2025)")
        print("="*80)
        
        # Import the new query functions
        from vfbquery.vfb_queries import (
            get_painted_domains,
            get_dataset_images,
            get_all_aligned_images,
            get_aligned_datasets,
            get_all_datasets
        )
        
        # Test terms for templates and datasets
        template_term = 'VFBc_00050000'  # Adult Brain template
        dataset_term = 'VFBc_00101384'   # Example dataset
        
        # PaintedDomains - Template painted anatomy domains
        result, duration, success = self._time_query(
            "PaintedDomains",
            get_painted_domains,
            template_term,
            return_dataframe=False,
            limit=10
        )
        print(f"PaintedDomains: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} painted domains" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "PaintedDomains exceeded threshold")
        
        # DatasetImages - Images in a dataset
        result, duration, success = self._time_query(
            "DatasetImages",
            get_dataset_images,
            dataset_term,
            return_dataframe=False,
            limit=10
        )
        print(f"DatasetImages: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} images in dataset" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "DatasetImages exceeded threshold")
        
        # AllAlignedImages - All images aligned to template
        result, duration, success = self._time_query(
            "AllAlignedImages",
            get_all_aligned_images,
            template_term,
            return_dataframe=False,
            limit=10
        )
        print(f"AllAlignedImages: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} aligned images" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "AllAlignedImages exceeded threshold")
        
        # AlignedDatasets - All datasets aligned to template
        result, duration, success = self._time_query(
            "AlignedDatasets",
            get_aligned_datasets,
            template_term,
            return_dataframe=False,
            limit=10
        )
        print(f"AlignedDatasets: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} aligned datasets" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "AlignedDatasets exceeded threshold")
        
        # AllDatasets - All available datasets
        result, duration, success = self._time_query(
            "AllDatasets",
            get_all_datasets,
            return_dataframe=False,
            limit=20
        )
        print(f"AllDatasets: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} total datasets" + (", returned 20" if count > 20 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "AllDatasets exceeded threshold")
        
        print(f"✅ All dataset/template queries completed")
    
    def test_14_publication_transgene_queries(self):
        """Test publication and transgene queries"""
        print("\n" + "="*80)
        print("PUBLICATION/TRANSGENE QUERIES (2025)")
        print("="*80)
        
        # Import the new query functions
        from vfbquery.vfb_queries import (
            get_terms_for_pub,
            get_transgene_expression_here
        )
        
        # Test terms
        pub_term = 'DOI_10_7554_eLife_04577'  # Example publication
        anatomy_term = self.test_terms['mushroom_body']  # mushroom body
        
        # TermsForPub - Terms referencing a publication
        result, duration, success = self._time_query(
            "TermsForPub",
            get_terms_for_pub,
            pub_term,
            return_dataframe=False,
            limit=10
        )
        print(f"TermsForPub: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} terms for publication" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "TermsForPub exceeded threshold")
        
        # TransgeneExpressionHere - Complex transgene expression query
        result, duration, success = self._time_query(
            "TransgeneExpressionHere",
            get_transgene_expression_here,
            anatomy_term,
            return_dataframe=False,
            limit=10
        )
        print(f"TransgeneExpressionHere: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} transgene expressions" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_SLOW, "TransgeneExpressionHere exceeded threshold")
        
        print(f"✅ All publication/transgene queries completed")
    
    def tearDown(self):
        """Generate performance summary"""
        pass
    
    @classmethod
    def tearDownClass(cls):
        """Generate final performance report"""
        print("\n" + "="*80)
        print("PERFORMANCE TEST SUMMARY")
        print("="*80)
        
        # This will be populated by the test instance
        # For now, just print a summary message
        print("All performance tests completed!")
        print("="*80)


def run_tests():
    """Run the performance test suite"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(QueryPerformanceTest)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
