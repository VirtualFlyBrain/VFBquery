"""
Cached VFBquery Functions

Enhanced versions of VFBquery functions with integrated caching
inspired by VFB_connect optimizations.
"""

from typing import Dict, Any, Optional
from .cache_enhancements import cache_result, get_cache
from .vfb_queries import (
    get_term_info as _original_get_term_info,
    get_instances as _original_get_instances,
    vfb_solr,
    term_info_parse_object as _original_term_info_parse_object,
    fill_query_results as _original_fill_query_results
)

@cache_result("solr_search", "solr_cache_enabled")
def cached_solr_search(query: str):
    """Cached version of SOLR search."""
    return vfb_solr.search(query)

@cache_result("term_info_parse", "term_info_cache_enabled")
def cached_term_info_parse_object(results, short_form: str):
    """Cached version of term_info_parse_object."""
    return _original_term_info_parse_object(results, short_form)

@cache_result("query_results", "query_result_cache_enabled")
def cached_fill_query_results(term_info: Dict[str, Any]):
    """Cached version of fill_query_results."""
    return _original_fill_query_results(term_info)

@cache_result("get_instances", "query_result_cache_enabled")
def cached_get_instances(short_form: str, return_dataframe=True, limit: int = -1):
    """Cached version of get_instances."""
    return _original_get_instances(short_form, return_dataframe, limit)

def get_term_info_cached(short_form: str, preview: bool = False):
    """
    Enhanced get_term_info with multi-layer caching.
    
    This version uses caching at multiple levels:
    1. Final result caching (entire term_info response)
    2. SOLR query result caching 
    3. Term info parsing caching
    4. Query result caching
    
    Args:
        short_form: Term short form (e.g., 'FBbt_00003748')
        preview: Whether to include preview results
        
    Returns:
        Term info dictionary or None if not found
    """
    cache = get_cache()
    
    # Check for complete result in cache first
    cache_key = cache._generate_cache_key("term_info_complete", short_form, preview)
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    parsed_object = None
    try:
        # Use cached SOLR search
        results = cached_solr_search('id:' + short_form)
        
        # Use cached term info parsing
        parsed_object = cached_term_info_parse_object(results, short_form)
        
        if parsed_object:
            # Use cached query result filling
            term_info = cached_fill_query_results(parsed_object)
            if not term_info:
                print("Failed to fill query preview results!")
                return parsed_object
            
            # Cache the complete result
            cache.set(cache_key, parsed_object)
            return parsed_object
        else:
            print(f"No valid term info found for ID '{short_form}'")
            return None
            
    except Exception as e:
        print(f"Error in cached get_term_info: {type(e).__name__}: {e}")
        # Fall back to original function if caching fails
        return _original_get_term_info(short_form, preview)

def get_instances_cached(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Enhanced get_instances with caching.
    
    This cached version can provide dramatic speedup for repeated queries,
    especially useful for:
    - UI applications with repeated browsing
    - Data analysis workflows
    - Testing and development
    
    Args:
        short_form: Class short form
        return_dataframe: Whether to return DataFrame or formatted dict
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Instances data (DataFrame or formatted dict based on return_dataframe)
    """
    return cached_get_instances(short_form, return_dataframe, limit)

# Convenience function to replace original functions
def patch_vfbquery_with_caching():
    """
    Replace original VFBquery functions with cached versions.
    
    This allows existing code to benefit from caching without changes.
    """
    import vfbquery.vfb_queries as vfb_queries
    
    # Store original functions for fallback
    setattr(vfb_queries, '_original_get_term_info', vfb_queries.get_term_info)
    setattr(vfb_queries, '_original_get_instances', vfb_queries.get_instances)
    
    # Replace with cached versions
    vfb_queries.get_term_info = get_term_info_cached
    vfb_queries.get_instances = get_instances_cached
    
    print("VFBquery functions patched with caching support")

def unpatch_vfbquery_caching():
    """Restore original VFBquery functions."""
    import vfbquery.vfb_queries as vfb_queries
    
    if hasattr(vfb_queries, '_original_get_term_info'):
        vfb_queries.get_term_info = getattr(vfb_queries, '_original_get_term_info')
    if hasattr(vfb_queries, '_original_get_instances'):
        vfb_queries.get_instances = getattr(vfb_queries, '_original_get_instances')
    
    print("VFBquery functions restored to original (non-cached) versions")
