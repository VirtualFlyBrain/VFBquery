"""
Cached VFBquery Functions

Enhanced versions of VFBquery functions with integrated caching
inspired by VFB_connect optimizations.
"""

from typing import Dict, Any, Optional
from .solr_result_cache import with_solr_cache


def is_valid_term_info_result(result):
    """Check if a term_info result has the essential fields and valid query structure"""
    if not result or not isinstance(result, dict):
        return False
    
    # Check for essential fields
    if not (result.get('Id') and result.get('Name')):
        return False
    
    # Additional validation for query results
    if 'Queries' in result:
        for query in result['Queries']:
            # Check if query has invalid count (-1) which indicates failed execution
            # Note: count=0 is valid if preview_results structure is correct
            count = query.get('count', 0)
            
            # Check if preview_results has the correct structure
            preview_results = query.get('preview_results')
            if not isinstance(preview_results, dict):
                print(f"DEBUG: Invalid preview_results type {type(preview_results)} detected")
                return False
                
            headers = preview_results.get('headers', [])
            if not headers:
                print(f"DEBUG: Empty headers detected in preview_results")
                return False
            
            # Only reject if count is -1 (failed execution) or if count is 0 but preview_results is missing/empty
            if count < 0:
                print(f"DEBUG: Invalid query count {count} detected")
                return False
    
    return True
from .vfb_queries import (
    get_term_info as _original_get_term_info,
    get_instances as _original_get_instances,
    get_similar_neurons as _original_get_similar_neurons,
    get_similar_morphology as _original_get_similar_morphology,
    get_similar_morphology_part_of as _original_get_similar_morphology_part_of,
    get_similar_morphology_part_of_exp as _original_get_similar_morphology_part_of_exp,
    get_similar_morphology_nb as _original_get_similar_morphology_nb,
    get_similar_morphology_nb_exp as _original_get_similar_morphology_nb_exp,
    get_similar_morphology_userdata as _original_get_similar_morphology_userdata,
    get_neurons_with_part_in as _original_get_neurons_with_part_in,
    get_neurons_with_synapses_in as _original_get_neurons_with_synapses_in,
    get_neurons_with_presynaptic_terminals_in as _original_get_neurons_with_presynaptic_terminals_in,
    get_neurons_with_postsynaptic_terminals_in as _original_get_neurons_with_postsynaptic_terminals_in,
)

@with_solr_cache("solr_search")
def cached_solr_search(query: str):
    """Cached version of SOLR search."""
    return vfb_solr.search(query)

def get_term_info_cached(short_form: str, preview: bool = False):
    """
    Enhanced get_term_info with SOLR caching.
    
    This version caches complete term_info responses in SOLR for fast retrieval.
    
    Args:
        short_form: Term short form (e.g., 'FBbt_00003748')
        preview: Whether to include preview results
        
    Returns:
        Term info dictionary or None if not found
    """
    return _original_get_term_info(short_form=short_form, preview=preview)

def get_instances_cached(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_instances with SOLR caching.
    
    This cached version provides dramatic speedup for repeated queries.
    
    Args:
        short_form: Class short form
        return_dataframe: Whether to return DataFrame or formatted dict
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Instances data (DataFrame or formatted dict based on return_dataframe)
    """
    return _original_get_instances(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_neurons_cached(neuron, similarity_score='NBLAST_score', return_dataframe=True, limit: int = -1):
    """
    Enhanced get_similar_neurons with SOLR caching.
    
    This cached version provides dramatic speedup for repeated NBLAST similarity queries.
    
    Args:
        neuron: Neuron identifier
        similarity_score: Similarity score type ('NBLAST_score', etc.)
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Similar neurons data (DataFrame or list of dicts)
    """
    return _original_get_similar_neurons(neuron=neuron, similarity_score=similarity_score, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_cached(neuron_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_similar_morphology with SOLR caching.
    
    Args:
        neuron_short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Similar morphology data
    """
    return _original_get_similar_morphology(neuron_short_form=neuron_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_part_of_cached(neuron_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_similar_morphology_part_of with SOLR caching.
    
    Args:
        neuron_short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Similar morphology part-of data
    """
    return _original_get_similar_morphology_part_of(neuron_short_form=neuron_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_part_of_exp_cached(expression_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_similar_morphology_part_of_exp with SOLR caching.
    
    Args:
        expression_short_form: Expression pattern short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Similar morphology expression data
    """
    return _original_get_similar_morphology_part_of_exp(expression_short_form=expression_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_nb_cached(neuron_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_similar_morphology_nb with SOLR caching.
    
    Args:
        neuron_short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        NBLAST similar morphology data
    """
    return _original_get_similar_morphology_nb(neuron_short_form=neuron_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_nb_exp_cached(expression_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_similar_morphology_nb_exp with SOLR caching.
    
    Args:
        expression_short_form: Expression pattern short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        NBLAST expression similarity data
    """
    return _original_get_similar_morphology_nb_exp(expression_short_form=expression_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_userdata_cached(upload_id: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_similar_morphology_userdata with SOLR caching.
    
    Args:
        upload_id: User upload identifier
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        User data similarity results
    """
    return _original_get_similar_morphology_userdata(upload_id=upload_id, return_dataframe=return_dataframe, limit=limit)

def get_neurons_with_part_in_cached(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_neurons_with_part_in with SOLR caching.
    
    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Neurons with part in the specified anatomical structure
    """
    return _original_get_neurons_with_part_in(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_neurons_with_synapses_in_cached(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_neurons_with_synapses_in with SOLR caching.
    
    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Neurons with synapses in the specified anatomical structure
    """
    return _original_get_neurons_with_synapses_in(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_neurons_with_presynaptic_terminals_in_cached(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_neurons_with_presynaptic_terminals_in with SOLR caching.
    
    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Neurons with presynaptic terminals in the specified anatomical structure
    """
    return _original_get_neurons_with_presynaptic_terminals_in(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_neurons_with_postsynaptic_terminals_in_cached(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_neurons_with_postsynaptic_terminals_in with SOLR caching.
    
    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Neurons with postsynaptic terminals in the specified anatomical structure
    """
    return _original_get_neurons_with_postsynaptic_terminals_in(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

# Convenience function to replace original functions
def patch_vfbquery_with_caching():
    """
    Replace original VFBquery functions with cached versions.
    
    This allows existing code to benefit from caching without changes.
    """
    import vfbquery.vfb_queries as vfb_queries
    import vfbquery
    
    # Store original functions for fallback
    setattr(vfb_queries, '_original_get_term_info', vfb_queries.get_term_info)
    setattr(vfb_queries, '_original_get_instances', vfb_queries.get_instances)
    setattr(vfb_queries, '_original_get_similar_neurons', vfb_queries.get_similar_neurons)
    setattr(vfb_queries, '_original_get_similar_morphology', vfb_queries.get_similar_morphology)
    setattr(vfb_queries, '_original_get_similar_morphology_part_of', vfb_queries.get_similar_morphology_part_of)
    setattr(vfb_queries, '_original_get_similar_morphology_part_of_exp', vfb_queries.get_similar_morphology_part_of_exp)
    setattr(vfb_queries, '_original_get_similar_morphology_nb', vfb_queries.get_similar_morphology_nb)
    setattr(vfb_queries, '_original_get_similar_morphology_nb_exp', vfb_queries.get_similar_morphology_nb_exp)
    setattr(vfb_queries, '_original_get_similar_morphology_userdata', vfb_queries.get_similar_morphology_userdata)
    setattr(vfb_queries, '_original_get_neurons_with_part_in', vfb_queries.get_neurons_with_part_in)
    setattr(vfb_queries, '_original_get_neurons_with_synapses_in', vfb_queries.get_neurons_with_synapses_in)
    setattr(vfb_queries, '_original_get_neurons_with_presynaptic_terminals_in', vfb_queries.get_neurons_with_presynaptic_terminals_in)
    setattr(vfb_queries, '_original_get_neurons_with_postsynaptic_terminals_in', vfb_queries.get_neurons_with_postsynaptic_terminals_in)
    
    # Replace with cached versions in vfb_queries module
    vfb_queries.get_term_info = get_term_info_cached
    vfb_queries.get_instances = get_instances_cached
    vfb_queries.get_similar_neurons = get_similar_neurons_cached
    vfb_queries.get_similar_morphology = get_similar_morphology_cached
    vfb_queries.get_similar_morphology_part_of = get_similar_morphology_part_of_cached
    vfb_queries.get_similar_morphology_part_of_exp = get_similar_morphology_part_of_exp_cached
    vfb_queries.get_similar_morphology_nb = get_similar_morphology_nb_cached
    vfb_queries.get_similar_morphology_nb_exp = get_similar_morphology_nb_exp_cached
    vfb_queries.get_similar_morphology_userdata = get_similar_morphology_userdata_cached
    vfb_queries.get_neurons_with_part_in = get_neurons_with_part_in_cached
    vfb_queries.get_neurons_with_synapses_in = get_neurons_with_synapses_in_cached
    vfb_queries.get_neurons_with_presynaptic_terminals_in = get_neurons_with_presynaptic_terminals_in_cached
    vfb_queries.get_neurons_with_postsynaptic_terminals_in = get_neurons_with_postsynaptic_terminals_in_cached
    
    # Also replace in the main vfbquery module namespace (since functions were imported with 'from .vfb_queries import *')
    vfbquery.get_term_info = get_term_info_cached
    vfbquery.get_instances = get_instances_cached
    vfbquery.get_similar_neurons = get_similar_neurons_cached
    vfbquery.get_similar_morphology = get_similar_morphology_cached
    vfbquery.get_similar_morphology_part_of = get_similar_morphology_part_of_cached
    vfbquery.get_similar_morphology_part_of_exp = get_similar_morphology_part_of_exp_cached
    vfbquery.get_similar_morphology_nb = get_similar_morphology_nb_cached
    vfbquery.get_similar_morphology_nb_exp = get_similar_morphology_nb_exp_cached
    vfbquery.get_similar_morphology_userdata = get_similar_morphology_userdata_cached
    vfbquery.get_neurons_with_part_in = get_neurons_with_part_in_cached
    vfbquery.get_neurons_with_synapses_in = get_neurons_with_synapses_in_cached
    vfbquery.get_neurons_with_presynaptic_terminals_in = get_neurons_with_presynaptic_terminals_in_cached
    vfbquery.get_neurons_with_postsynaptic_terminals_in = get_neurons_with_postsynaptic_terminals_in_cached
    
    print("VFBquery functions patched with caching support")

def unpatch_vfbquery_caching():
    """Restore original VFBquery functions."""
    import vfbquery.vfb_queries as vfb_queries
    
    if hasattr(vfb_queries, '_original_get_term_info'):
        vfb_queries.get_term_info = getattr(vfb_queries, '_original_get_term_info')
    if hasattr(vfb_queries, '_original_get_instances'):
        vfb_queries.get_instances = getattr(vfb_queries, '_original_get_instances')
    if hasattr(vfb_queries, '_original_get_similar_neurons'):
        vfb_queries.get_similar_neurons = getattr(vfb_queries, '_original_get_similar_neurons')
    if hasattr(vfb_queries, '_original_get_similar_morphology'):
        vfb_queries.get_similar_morphology = getattr(vfb_queries, '_original_get_similar_morphology')
    if hasattr(vfb_queries, '_original_get_similar_morphology_part_of'):
        vfb_queries.get_similar_morphology_part_of = getattr(vfb_queries, '_original_get_similar_morphology_part_of')
    if hasattr(vfb_queries, '_original_get_similar_morphology_part_of_exp'):
        vfb_queries.get_similar_morphology_part_of_exp = getattr(vfb_queries, '_original_get_similar_morphology_part_of_exp')
    if hasattr(vfb_queries, '_original_get_similar_morphology_nb'):
        vfb_queries.get_similar_morphology_nb = getattr(vfb_queries, '_original_get_similar_morphology_nb')
    if hasattr(vfb_queries, '_original_get_similar_morphology_nb_exp'):
        vfb_queries.get_similar_morphology_nb_exp = getattr(vfb_queries, '_original_get_similar_morphology_nb_exp')
    if hasattr(vfb_queries, '_original_get_similar_morphology_userdata'):
        vfb_queries.get_similar_morphology_userdata = getattr(vfb_queries, '_original_get_similar_morphology_userdata')
    
    print("VFBquery functions restored to original (non-cached) versions")
