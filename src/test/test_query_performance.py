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
            'neuron_with_nblast': 'VFB_00017894',   # Neuron with NBLAST data
            'clone': 'FBbt_00050024',               # Clone
            'connected_neuron': 'VFB_jrchk00s',     # LPC1 neuron with connectivity data
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
