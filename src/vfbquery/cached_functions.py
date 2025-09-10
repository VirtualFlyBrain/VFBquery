"""
Cached VFBquery Functions

Enhanced versions of VFBquery functions with integrated caching
inspired by VFB_connect optimizations.
"""

from typing import Dict, Any, Optional
from .cache_enhancements import cache_result, get_cache


def is_valid_term_info_result(result):
    """Check if a term_info result has the essential fields"""
    if not result or not isinstance(result, dict):
        return False
    # Check for essential fields
    return result.get('Id') and result.get('Name')
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
    print(f"DEBUG: Cache lookup for {short_form}: {'HIT' if cached_result is not None else 'MISS'}")
    if cached_result is not None:
        # Validate that cached result has essential fields
        if not is_valid_term_info_result(cached_result):
            print(f"DEBUG: Cached result incomplete for {short_form}, falling back to original function")
            print(f"DEBUG: cached_result keys: {list(cached_result.keys()) if cached_result else 'None'}")
            print(f"DEBUG: cached_result Id: {cached_result.get('Id', 'MISSING') if cached_result else 'None'}")
            print(f"DEBUG: cached_result Name: {cached_result.get('Name', 'MISSING') if cached_result else 'None'}")
            
            # Fall back to original function and cache the complete result
            fallback_result = _original_get_term_info(short_form, preview)
            if is_valid_term_info_result(fallback_result):
                print(f"DEBUG: Fallback successful, caching complete result for {short_form}")
                cache.set(cache_key, fallback_result)
            return fallback_result
        else:
            print(f"DEBUG: Using valid cached result for {short_form}")
            return cached_result
    
    parsed_object = None
    try:
        # Use cached SOLR search
        results = cached_solr_search('id:' + short_form)
        
        # Use cached term info parsing
        parsed_object = cached_term_info_parse_object(results, short_form)
        
        if parsed_object:
            # Use cached query result filling (skip if queries would fail)
            if parsed_object.get('Queries') and len(parsed_object['Queries']) > 0:
                try:
                    term_info = cached_fill_query_results(parsed_object)
                    if term_info:
                        # Validate result before caching
                        if term_info.get('Id') and term_info.get('Name'):
                            # Cache the complete result
                            cache.set(cache_key, term_info)
                            return term_info
                        else:
                            print(f"Query result for {short_form} is incomplete, falling back to original function...")
                            return _original_get_term_info(short_form, preview)
                    else:
                        print("Failed to fill query preview results!")
                        # Validate result before caching
                        if parsed_object.get('Id') and parsed_object.get('Name'):
                            # Cache the complete result
                            cache.set(cache_key, parsed_object)
                            return parsed_object
                        else:
                            print(f"Parsed object for {short_form} is incomplete, falling back to original function...")
                            return _original_get_term_info(short_form, preview)
                except Exception as e:
                    print(f"Error filling query results (continuing without query data): {e}")
                    # Validate result before caching
                    if is_valid_term_info_result(parsed_object):
                        cache.set(cache_key, parsed_object)
                        return parsed_object
                    else:
                        print(f"DEBUG: Exception case - parsed object incomplete for {short_form}, falling back to original function")
                        fallback_result = _original_get_term_info(short_form, preview)
                        if is_valid_term_info_result(fallback_result):
                            cache.set(cache_key, fallback_result)
                        return fallback_result
            else:
                # No queries to fill, validate result before caching
                if parsed_object.get('Id') and parsed_object.get('Name'):
                    # Cache and return parsed object directly
                    cache.set(cache_key, parsed_object)
                    return parsed_object
                else:
                    print(f"DEBUG: No queries case - parsed object incomplete for {short_form}, falling back to original function...")
                    fallback_result = _original_get_term_info(short_form, preview)
                    if is_valid_term_info_result(fallback_result):
                        cache.set(cache_key, fallback_result)
                    return fallback_result
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
