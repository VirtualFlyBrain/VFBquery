"""
Tests for newly implemented Owlery-based queries:
- NeuronsSynaptic
- NeuronsPresynapticHere
- NeuronsPostsynapticHere
- ComponentsOf
- PartsOf
- SubclassesOf
"""

import unittest
from vfbquery.vfb_queries import (
    get_neurons_with_synapses_in,
    get_neurons_with_presynaptic_terminals_in,
    get_neurons_with_postsynaptic_terminals_in,
    get_components_of,
    get_parts_of,
    get_subclasses_of,
    get_term_info
)


class TestNeuronsSynaptic(unittest.TestCase):
    """Tests for NeuronsSynaptic query"""
    
    def setUp(self):
        self.medulla_id = 'FBbt_00003748'  # medulla - synaptic neuropil
    
    def test_neurons_synaptic_returns_results(self):
        """Test that NeuronsSynaptic query returns results for medulla"""
        result = get_neurons_with_synapses_in(
            self.medulla_id,
            return_dataframe=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn('headers', result)
        self.assertIn('rows', result)
        self.assertIn('count', result)
    
    def test_neurons_synaptic_has_expected_columns(self):
        """Test that result has expected column structure"""
        result = get_neurons_with_synapses_in(
            self.medulla_id,
            return_dataframe=False
        )
        
        headers = result['headers']
        self.assertIn('id', headers)
        self.assertIn('label', headers)
        self.assertIn('tags', headers)
        self.assertIn('thumbnail', headers)
    
    def test_neurons_synaptic_in_term_info(self):
        """Test that NeuronsSynaptic appears in term_info queries"""
        term_info = get_term_info(self.medulla_id, preview=True)
        
        self.assertIn('Queries', term_info)  # Note: Capital 'Q'
        query_labels = [q['label'] for q in term_info['Queries']]
        
        # Check if our query is present
        expected_label = f"Neurons with synaptic terminals in {term_info['Name']}"
        self.assertIn(expected_label, query_labels)


class TestNeuronsPresynapticHere(unittest.TestCase):
    """Tests for NeuronsPresynapticHere query"""
    
    def setUp(self):
        self.medulla_id = 'FBbt_00003748'  # medulla - synaptic neuropil
    
    def test_neurons_presynaptic_returns_results(self):
        """Test that NeuronsPresynapticHere query returns results for medulla"""
        result = get_neurons_with_presynaptic_terminals_in(
            self.medulla_id,
            return_dataframe=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn('headers', result)
        self.assertIn('rows', result)
        self.assertIn('count', result)
    
    def test_neurons_presynaptic_has_expected_columns(self):
        """Test that result has expected column structure"""
        result = get_neurons_with_presynaptic_terminals_in(
            self.medulla_id,
            return_dataframe=False
        )
        
        headers = result['headers']
        self.assertIn('id', headers)
        self.assertIn('label', headers)
        self.assertIn('tags', headers)
        self.assertIn('thumbnail', headers)
    
    def test_neurons_presynaptic_in_term_info(self):
        """Test that NeuronsPresynapticHere appears in term_info queries"""
        term_info = get_term_info(self.medulla_id, preview=True)
        
        self.assertIn('Queries', term_info)  # Note: Capital 'Q'
        query_labels = [q['label'] for q in term_info['Queries']]
        
        # Check if our query is present
        expected_label = f"Neurons with presynaptic terminals in {term_info['Name']}"
        self.assertIn(expected_label, query_labels)


class TestNeuronsPostsynapticHere(unittest.TestCase):
    """Tests for NeuronsPostsynapticHere query"""
    
    def setUp(self):
        self.medulla_id = 'FBbt_00003748'  # medulla - synaptic neuropil
    
    def test_neurons_postsynaptic_returns_results(self):
        """Test that NeuronsPostsynapticHere query returns results for medulla"""
        result = get_neurons_with_postsynaptic_terminals_in(
            self.medulla_id,
            return_dataframe=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn('headers', result)
        self.assertIn('rows', result)
        self.assertIn('count', result)
    
    def test_neurons_postsynaptic_has_expected_columns(self):
        """Test that result has expected column structure"""
        result = get_neurons_with_postsynaptic_terminals_in(
            self.medulla_id,
            return_dataframe=False
        )
        
        headers = result['headers']
        self.assertIn('id', headers)
        self.assertIn('label', headers)
        self.assertIn('tags', headers)
        self.assertIn('thumbnail', headers)
    
    def test_neurons_postsynaptic_in_term_info(self):
        """Test that NeuronsPostsynapticHere appears in term_info queries"""
        term_info = get_term_info(self.medulla_id, preview=True)
        
        self.assertIn('Queries', term_info)  # Note: Capital 'Q'
        query_labels = [q['label'] for q in term_info['Queries']]
        
        # Check if our query is present
        expected_label = f"Neurons with postsynaptic terminals in {term_info['Name']}"
        self.assertIn(expected_label, query_labels)


class TestComponentsOf(unittest.TestCase):
    """Tests for ComponentsOf query"""
    
    def setUp(self):
        self.clone_id = 'FBbt_00110369'  # adult SLPpm4 lineage clone
    
    def test_components_of_returns_results(self):
        """Test that ComponentsOf query returns results for clone"""
        result = get_components_of(
            self.clone_id,
            return_dataframe=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn('headers', result)
        self.assertIn('rows', result)
        self.assertIn('count', result)
    
    def test_components_of_has_expected_columns(self):
        """Test that result has expected column structure"""
        result = get_components_of(
            self.clone_id,
            return_dataframe=False
        )
        
        headers = result['headers']
        self.assertIn('id', headers)
        self.assertIn('label', headers)
        self.assertIn('tags', headers)
        self.assertIn('thumbnail', headers)
    
    def test_components_of_in_term_info(self):
        """Test that ComponentsOf appears in term_info queries"""
        term_info = get_term_info(self.clone_id, preview=True)
        
        self.assertIn('Queries', term_info)  # Note: Capital 'Q'
        query_labels = [q['label'] for q in term_info['Queries']]
        
        # Check if our query is present
        expected_label = f"Components of {term_info['Name']}"
        self.assertIn(expected_label, query_labels)


class TestPartsOf(unittest.TestCase):
    """Tests for PartsOf query"""
    
    def setUp(self):
        self.medulla_id = 'FBbt_00003748'  # medulla - any Class
    
    def test_parts_of_returns_results(self):
        """Test that PartsOf query returns results for medulla"""
        result = get_parts_of(
            self.medulla_id,
            return_dataframe=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn('headers', result)
        self.assertIn('rows', result)
        self.assertIn('count', result)
    
    def test_parts_of_has_expected_columns(self):
        """Test that result has expected column structure"""
        result = get_parts_of(
            self.medulla_id,
            return_dataframe=False
        )
        
        headers = result['headers']
        self.assertIn('id', headers)
        self.assertIn('label', headers)
        self.assertIn('tags', headers)
        self.assertIn('thumbnail', headers)
    
    def test_parts_of_in_term_info(self):
        """Test that PartsOf appears in term_info queries"""
        term_info = get_term_info(self.medulla_id, preview=True)
        
        self.assertIn('Queries', term_info)  # Note: Capital 'Q'
        query_labels = [q['label'] for q in term_info['Queries']]
        
        # Check if our query is present
        expected_label = f"Parts of {term_info['Name']}"
        self.assertIn(expected_label, query_labels)


class TestSubclassesOf(unittest.TestCase):
    """Tests for SubclassesOf query"""
    
    def setUp(self):
        self.wedge_pn_id = 'FBbt_00048516'  # wedge projection neuron (>45 subclasses)
    
    def test_subclasses_of_returns_results(self):
        """Test that SubclassesOf query returns results for wedge projection neuron"""
        result = get_subclasses_of(
            self.wedge_pn_id,
            return_dataframe=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn('headers', result)
        self.assertIn('rows', result)
        self.assertIn('count', result)
    
    def test_subclasses_of_has_expected_columns(self):
        """Test that result has expected column structure"""
        result = get_subclasses_of(
            self.wedge_pn_id,
            return_dataframe=False
        )
        
        headers = result['headers']
        self.assertIn('id', headers)
        self.assertIn('label', headers)
        self.assertIn('tags', headers)
        self.assertIn('thumbnail', headers)
    
    def test_subclasses_of_in_term_info(self):
        """Test that SubclassesOf appears in term_info queries"""
        term_info = get_term_info(self.wedge_pn_id, preview=True)
        
        self.assertIn('Queries', term_info)  # Note: Capital 'Q'
        query_labels = [q['label'] for q in term_info['Queries']]
        
        # Check if our query is present
        expected_label = f"Subclasses of {term_info['Name']}"
        self.assertIn(expected_label, query_labels)


if __name__ == '__main__':
    unittest.main()
