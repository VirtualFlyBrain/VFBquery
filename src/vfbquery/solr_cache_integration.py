"""
Integration layer for SOLR-based result caching in VFBquery

This module patches existing VFBquery functions to use SOLR caching,
providing significant performance improvements for cold starts.
"""

import functools
from typing import Any, Dict
from vfbquery.solr_result_cache import get_solr_cache, with_solr_cache
import vfbquery.vfb_queries as vfb_queries
import logging

logger = logging.getLogger(__name__)

class SolrCacheIntegration:
    """
    Integration layer for SOLR caching in VFBquery
    
    Provides methods to enable/disable SOLR caching for query functions
    and fallback mechanisms in case SOLR cache is unavailable.
    """
    
    def __init__(self):
        self.original_functions = {}
        self.cache_enabled = True
        
    def enable_solr_caching(self):
        """Enable SOLR-based result caching for VFBquery functions"""
        if not self.cache_enabled:
            self._patch_functions()
            self.cache_enabled = True
            logger.info("SOLR result caching enabled")
    
    def disable_solr_caching(self):
        """Disable SOLR caching and restore original functions"""
        if self.cache_enabled:
            self._unpatch_functions()
            self.cache_enabled = False
            logger.info("SOLR result caching disabled")
    
    def _patch_functions(self):
        """Patch VFBquery functions with SOLR caching"""
        # Store original functions
        self.original_functions['get_term_info'] = vfb_queries.get_term_info
        self.original_functions['get_instances'] = vfb_queries.get_instances
        
        # Create cached versions
        vfb_queries.get_term_info = self._create_cached_get_term_info()
        vfb_queries.get_instances = self._create_cached_get_instances()
        
    def _unpatch_functions(self):
        """Restore original functions"""
        for func_name, original_func in self.original_functions.items():
            setattr(vfb_queries, func_name, original_func)
        self.original_functions.clear()
    
    def _create_cached_get_term_info(self):
        """Create SOLR-cached version of get_term_info"""
        original_func = self.original_functions['get_term_info']
        
        @functools.wraps(original_func)
        def cached_get_term_info(short_form: str, preview: bool = False):
            cache = get_solr_cache()
            cache_params = {"preview": preview}
            
            try:
                # Try SOLR cache first
                cached_result = cache.get_cached_result(
                    "term_info", short_form, **cache_params
                )
                if cached_result is not None:
                    logger.debug(f"SOLR cache hit for term_info({short_form})")
                    return cached_result
                
            except Exception as e:
                logger.warning(f"SOLR cache lookup failed, falling back: {e}")
            
            # Execute original function
            logger.debug(f"SOLR cache miss for term_info({short_form}), computing...")
            result = original_func(short_form, preview)
            
            # Cache result asynchronously
            if result:
                try:
                    cache.cache_result("term_info", short_form, result, **cache_params)
                    logger.debug(f"Cached term_info result for {short_form}")
                except Exception as e:
                    logger.debug(f"Failed to cache term_info result: {e}")
            
            return result
        
        return cached_get_term_info
    
    def _create_cached_get_instances(self):
        """Create SOLR-cached version of get_instances"""
        original_func = self.original_functions['get_instances']
        
        @functools.wraps(original_func) 
        def cached_get_instances(short_form: str, return_dataframe=True, limit: int = -1):
            cache = get_solr_cache()
            cache_params = {
                "return_dataframe": return_dataframe,
                "limit": limit
            }
            
            try:
                # Try SOLR cache first
                cached_result = cache.get_cached_result(
                    "instances", short_form, **cache_params
                )
                if cached_result is not None:
                    logger.debug(f"SOLR cache hit for get_instances({short_form})")
                    return cached_result
                
            except Exception as e:
                logger.warning(f"SOLR cache lookup failed, falling back: {e}")
            
            # Execute original function
            logger.debug(f"SOLR cache miss for get_instances({short_form}), computing...")
            result = original_func(short_form, return_dataframe, limit)
            
            # Cache result asynchronously
            if result is not None:
                try:
                    cache.cache_result("instances", short_form, result, **cache_params)
                    logger.debug(f"Cached get_instances result for {short_form}")
                except Exception as e:
                    logger.debug(f"Failed to cache get_instances result: {e}")
            
            return result
        
        return cached_get_instances


# Global integration instance
_solr_integration = None

def get_solr_integration() -> SolrCacheIntegration:
    """Get global SOLR cache integration instance"""
    global _solr_integration
    if _solr_integration is None:
        _solr_integration = SolrCacheIntegration()
    return _solr_integration

def enable_solr_result_caching():
    """Enable SOLR-based result caching for VFBquery"""
    integration = get_solr_integration()
    integration.enable_solr_caching()

def disable_solr_result_caching():
    """Disable SOLR-based result caching"""
    integration = get_solr_integration()
    integration.disable_solr_caching()

def warmup_solr_cache(term_ids: list, query_types: list = ["term_info", "instances"]):
    """
    Warm up SOLR cache by pre-computing results for common terms
    
    This function can be run during deployment or maintenance windows
    to pre-populate the cache with frequently requested terms.
    
    Args:
        term_ids: List of term IDs to warm up
        query_types: Types of queries to warm up ('term_info', 'instances')
    """
    logger.info(f"Warming up SOLR cache for {len(term_ids)} terms")
    
    # Temporarily enable SOLR caching if not already enabled
    integration = get_solr_integration()
    was_enabled = integration.cache_enabled
    if not was_enabled:
        integration.enable_solr_caching()
    
    try:
        for term_id in term_ids:
            for query_type in query_types:
                try:
                    if query_type == "term_info":
                        vfb_queries.get_term_info(term_id)
                    elif query_type == "instances":
                        vfb_queries.get_instances(term_id, limit=100)  # Reasonable limit for warmup
                    
                    logger.debug(f"Warmed up {query_type} for {term_id}")
                    
                except Exception as e:
                    logger.warning(f"Failed to warm up {query_type} for {term_id}: {e}")
        
        logger.info("SOLR cache warmup completed")
        
    finally:
        # Restore original state if we changed it
        if not was_enabled:
            integration.disable_solr_caching()

def get_solr_cache_stats() -> Dict[str, Any]:
    """Get SOLR cache statistics"""
    try:
        cache = get_solr_cache()
        return cache.get_cache_stats()
    except Exception as e:
        logger.error(f"Failed to get SOLR cache stats: {e}")
        return {}

def cleanup_solr_cache() -> int:
    """Clean up expired entries in SOLR cache"""
    try:
        cache = get_solr_cache()
        return cache.cleanup_expired_entries()
    except Exception as e:
        logger.error(f"Failed to cleanup SOLR cache: {e}")
        return 0
