"""
SOLR-based Result Caching for VFBquery

This module implements server-side caching by storing computed VFBquery results 
directly in the SOLR server, eliminating cold start delays for frequently 
requested terms.

The approach uses a dedicated SOLR collection 'vfbquery_cache' to store 
pre-computed results that can be retrieved instantly without expensive 
Neo4j queries and data processing.
"""

import json
import requests
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass, asdict
from vfbquery.term_info_queries import NumpyEncoder

logger = logging.getLogger(__name__)

@dataclass 
class CacheMetadata:
    """Metadata for cached results"""
    query_type: str          # 'term_info', 'instances', etc.
    term_id: str            # The queried term ID
    query_params: str       # Hashed parameters for unique identification
    created_at: str         # ISO timestamp
    expires_at: str         # ISO timestamp  
    result_size: int        # Size in bytes
    version: str            # VFBquery version
    hit_count: int = 0      # How many times this cache entry was used

class SolrResultCache:
    """
    SOLR-based result caching system for VFBquery
    
    Stores computed query results in a dedicated SOLR collection to enable
    instant retrieval without expensive computation on cold starts.
    """
    
    def __init__(self, 
                 cache_url: str = "https://solr.virtualflybrain.org/solr/vfb_json",
                 ttl_hours: int = 2160,  # 3 months like VFB_connect
                 max_result_size_mb: int = 10):
        """
        Initialize SOLR result cache
        
        Args:
            cache_url: SOLR collection URL for caching
            ttl_hours: Time-to-live for cache entries in hours
            max_result_size_mb: Maximum result size to cache in MB
        """
        self.cache_url = cache_url
        self.ttl_hours = ttl_hours
        self.max_result_size_mb = max_result_size_mb
        self.max_result_size_bytes = max_result_size_mb * 1024 * 1024
        
    def _create_cache_metadata(self, result: Any) -> Optional[Dict[str, Any]]:
        """Create metadata for cached result with 3-month expiration"""
        serialized_result = json.dumps(result, cls=NumpyEncoder)
        result_size = len(serialized_result.encode('utf-8'))
        
        # Don't cache if result is too large
        if result_size > self.max_result_size_bytes:
            logger.warning(f"Result too large to cache: {result_size/1024/1024:.2f}MB > {self.max_result_size_mb}MB")
            return None
            
        now = datetime.now().astimezone()
        expires_at = now + timedelta(hours=self.ttl_hours)  # 2160 hours = 90 days = 3 months
        
        return {
            "result": result,  # Store original object, not serialized string
            "cached_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "result_size": result_size,
            "hit_count": 0,
            "cache_version": "1.0",  # For future compatibility
            "ttl_hours": self.ttl_hours  # Store TTL for debugging
        }
    
    def get_cached_result(self, query_type: str, term_id: str, **params) -> Optional[Any]:
        """
        Retrieve cached result from separate cache document
        
        Args:
            query_type: Type of query ('term_info', 'instances', etc.)
            term_id: Term identifier 
            **params: Query parameters for field name generation
            
        Returns:
            Cached result or None if not found/expired
        """
        try:
            # Query for cache document with prefixed ID
            cache_doc_id = f"vfb_query_{term_id}"
            
            response = requests.get(f"{self.cache_url}/select", params={
                "q": f"id:{cache_doc_id} AND query_type:{query_type}",
                "fl": "cache_data",
                "wt": "json"
            }, timeout=5)  # Short timeout for cache lookups
            
            if response.status_code != 200:
                logger.debug(f"Cache miss: HTTP {response.status_code}")
                return None
                
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            
            if not docs:
                logger.debug(f"Cache miss: No cache document found for {query_type}:{term_id}")
                return None
                
            cached_field = docs[0].get("cache_data")
            if not cached_field:
                logger.debug(f"Cache miss: No cache_data field found for {term_id}")
                return None
                
            # Handle both list and string formats
            if isinstance(cached_field, list):
                cached_field = cached_field[0]
            
            # Parse the cached metadata and result
            cached_data = json.loads(cached_field)
            
            # Check expiration (3-month max age)
            try:
                expires_at = datetime.fromisoformat(cached_data["expires_at"].replace('Z', '+00:00'))
                cached_at = datetime.fromisoformat(cached_data["cached_at"].replace('Z', '+00:00'))
                now = datetime.now().astimezone()
                
                if now > expires_at:
                    age_days = (now - cached_at).days
                    logger.info(f"Cache expired for {query_type}({term_id}) - age: {age_days} days")
                    self._clear_expired_cache_document(cache_doc_id)
                    return None
                    
                # Log cache age for monitoring
                age_hours = (now - cached_at).total_seconds() / 3600
                logger.debug(f"Cache hit for {query_type}({term_id}) - age: {age_hours:.1f} hours")
                    
            except (KeyError, ValueError) as e:
                logger.warning(f"Invalid cache metadata for {term_id}: {e}")
                self._clear_expired_cache_document(cache_doc_id)
                return None
            
            # Increment hit count asynchronously
            self._increment_cache_hit_count(cache_doc_id, cached_data.get("hit_count", 0))
            
            # Return cached result 
            result = cached_data["result"]
            # If result is a string, parse it as JSON
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse cached result for {term_id}")
                    return None
            
            logger.info(f"Cache hit for {query_type}({term_id})")
            return result
            
        except Exception as e:
            logger.debug(f"Error retrieving cached result: {e}")
            return None
    
    def cache_result(self, query_type: str, term_id: str, result: Any, **params) -> bool:
        """
        Store result as separate cache document with prefixed ID
        
        This approach is safer as it never touches original VFB documents,
        eliminating risk of data loss.
        
        Args:
            query_type: Type of query being cached
            term_id: Term identifier 
            result: Query result to cache
            **params: Query parameters for field name generation
            
        Returns:
            True if successfully cached, False otherwise
        """
        if not result:
            logger.debug("Empty result, not caching")
            return False
            
        try:
            # Create cached metadata and result
            cached_data = self._create_cache_metadata(result)
            if not cached_data:
                return False  # Result too large or other issue
                
            # Create cache document with prefixed ID
            cache_doc_id = f"vfb_query_{term_id}"
            
            cache_doc = {
                "id": cache_doc_id,
                "original_term_id": term_id,
                "query_type": query_type,
                "cache_data": json.dumps(cached_data, cls=NumpyEncoder),
                "cached_at": cached_data["cached_at"],
                "expires_at": cached_data["expires_at"]
            }
            
            # Store cache document 
            response = requests.post(
                f"{self.cache_url}/update",
                data=json.dumps([cache_doc]),
                headers={"Content-Type": "application/json"},
                params={"commit": "true"},  # Immediate commit for availability
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Cached {query_type} for {term_id} as {cache_doc_id}, size: {cached_data['result_size']/1024:.1f}KB")
                return True
            else:
                logger.error(f"Failed to cache result: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error caching result: {e}")
            return False
    

    def _clear_expired_cache_document(self, cache_doc_id: str):
        """Delete expired cache document from SOLR"""
        try:
            requests.post(
                f"{self.cache_url}/update",
                data=f'<delete><id>{cache_doc_id}</id></delete>',
                headers={"Content-Type": "application/xml"},
                params={"commit": "false"},  # Don't commit immediately for performance
                timeout=2
            )
        except Exception as e:
            logger.debug(f"Failed to clear expired cache document: {e}")
    
    def clear_cache_entry(self, query_type: str, term_id: str) -> bool:
        """
        Manually clear a specific cache entry to force refresh
        
        Args:
            query_type: Type of query ('term_info', 'instances', etc.)
            term_id: Term identifier
            
        Returns:
            True if successfully cleared, False otherwise
        """
        try:
            cache_doc_id = f"vfb_query_{term_id}"
            response = requests.post(
                f"{self.cache_url}/update",
                data=f'<delete><id>{cache_doc_id}</id></delete>',
                headers={"Content-Type": "application/xml"},
                params={"commit": "true"},  # Commit immediately to ensure it's cleared
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Cleared cache entry for {query_type}({term_id})")
                return True
            else:
                logger.error(f"Failed to clear cache entry: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error clearing cache entry: {e}")
            return False
    
    def _increment_cache_hit_count(self, cache_doc_id: str, current_count: int):
        """Increment hit count for cache document (background operation)"""
        try:
            # Update hit count in cache document
            new_count = current_count + 1
            update_doc = {
                "id": cache_doc_id,
                "hit_count": {"set": new_count},
                "last_accessed": {"set": datetime.now().isoformat() + "Z"}
            }
            
            requests.post(
                f"{self.cache_url}/update",
                data=json.dumps([update_doc]),
                headers={"Content-Type": "application/json"},
                params={"commit": "false"},  # Don't commit immediately for performance
                timeout=2
            )
        except Exception as e:
            logger.debug(f"Failed to update hit count: {e}")
    
    def get_cache_age(self, query_type: str, term_id: str, **params) -> Optional[Dict[str, Any]]:
        """
        Get cache age information for a specific cached result
        
        Returns:
            Dictionary with cache age info or None if not cached
        """
        try:
            cache_doc_id = f"vfb_query_{term_id}"
            
            response = requests.get(f"{self.cache_url}/select", params={
                "q": f"id:{cache_doc_id} AND query_type:{query_type}",
                "fl": "cache_data,hit_count,last_accessed",
                "wt": "json"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                
                if docs:
                    doc = docs[0]
                    cached_field = doc.get("cache_data")
                    if cached_field:
                        # Handle both list and string formats
                        if isinstance(cached_field, list):
                            cached_field = cached_field[0]
                        
                        cached_data = json.loads(cached_field)
                        
                        cached_at = datetime.fromisoformat(cached_data["cached_at"].replace('Z', '+00:00'))
                        expires_at = datetime.fromisoformat(cached_data["expires_at"].replace('Z', '+00:00'))
                        now = datetime.now().astimezone()
                        
                        age = now - cached_at
                        time_to_expiry = expires_at - now
                        
                        return {
                            "cached_at": cached_at.isoformat(),
                            "expires_at": expires_at.isoformat(),
                            "age_days": age.days,
                            "age_hours": age.total_seconds() / 3600,
                            "time_to_expiry_days": time_to_expiry.days,
                            "time_to_expiry_hours": time_to_expiry.total_seconds() / 3600,
                            "is_expired": now > expires_at,
                            "hit_count": doc.get("hit_count", cached_data.get("hit_count", 0)),
                            "size_kb": cached_data.get("result_size", 0) / 1024,
                            "last_accessed": doc.get("last_accessed", ["Never"])[0] if isinstance(doc.get("last_accessed"), list) else doc.get("last_accessed", "Never")
                        }
        except Exception as e:
            logger.debug(f"Error getting cache age: {e}")
            
        return None
    
    def cleanup_expired_entries(self) -> int:
        """
        Clean up expired VFBquery cache documents
        
        This method scans for cache documents (IDs starting with vfb_query_) and removes expired ones.
        
        Returns:
            Number of expired cache documents cleaned up
        """
        try:
            now = datetime.now().astimezone()
            cleaned_count = 0
            
            # Search for all cache documents
            response = requests.get(f"{self.cache_url}/select", params={
                "q": "id:vfb_query_*",
                "fl": "id,cache_data,expires_at",
                "rows": "1000",  # Process in batches
                "wt": "json"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                expired_ids = []
                
                for doc in docs:
                    doc_id = doc["id"]
                    
                    try:
                        # Check expiration using expires_at field if available, or cache_data
                        expires_at = None
                        
                        if "expires_at" in doc:
                            expires_at_field = doc["expires_at"]
                            expires_at_str = expires_at_field[0] if isinstance(expires_at_field, list) else expires_at_field
                            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                        elif "cache_data" in doc:
                            # Fallback to parsing cache_data
                            cached_field = doc["cache_data"]
                            if isinstance(cached_field, list):
                                cached_field = cached_field[0]
                            cached_data = json.loads(cached_field)
                            expires_at = datetime.fromisoformat(cached_data["expires_at"].replace('Z', '+00:00'))
                        
                        if expires_at and now > expires_at:
                            expired_ids.append(doc_id)
                            cleaned_count += 1
                            logger.debug(f"Marking cache document {doc_id} for removal (expired)")
                            
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        # Invalid cache data - remove it
                        expired_ids.append(doc_id)
                        cleaned_count += 1
                        logger.debug(f"Marking invalid cache document {doc_id} for removal: {e}")
                
                # Delete expired cache documents in batch
                if expired_ids:
                    delete_xml = "<delete>" + "".join(f"<id>{doc_id}</id>" for doc_id in expired_ids) + "</delete>"
                    
                    delete_response = requests.post(
                        f"{self.cache_url}/update",
                        data=delete_xml,
                        headers={"Content-Type": "application/xml"},
                        params={"commit": "true"},  # Commit deletions immediately
                        timeout=10
                    )
                    
                    if delete_response.status_code != 200:
                        logger.warning(f"Failed to delete expired cache documents: HTTP {delete_response.status_code}")
                    else:
                        logger.info(f"Cleaned up {cleaned_count} expired cache documents")
                
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get VFBquery cache statistics from cache documents
        
        Returns:
            Dictionary with cache statistics including document counts and age distribution
        """
        try:
            # Get all cache documents
            response = requests.get(f"{self.cache_url}/select", params={
                "q": "id:vfb_query_*",
                "fl": "id,query_type,cache_data,hit_count,last_accessed,cached_at,expires_at",
                "rows": "1000",  # Process in batches 
                "wt": "json"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                total_cache_docs = data.get("response", {}).get("numFound", 0)
                
                type_stats = {}
                total_size = 0
                expired_count = 0
                total_hits = 0
                age_buckets = {"0-1d": 0, "1-7d": 0, "7-30d": 0, "30-90d": 0, ">90d": 0}
                
                now = datetime.now().astimezone()
                
                # Analyze each cache document
                for doc in docs:
                    query_type_field = doc.get("query_type", "unknown")
                    # Handle both list and string formats
                    query_type = query_type_field[0] if isinstance(query_type_field, list) else query_type_field
                    type_stats[query_type] = type_stats.get(query_type, 0) + 1
                    
                    try:
                        # Get cache data and metadata
                        cached_field = doc.get("cache_data")
                        if cached_field:
                            # Handle both list and string formats
                            if isinstance(cached_field, list):
                                cached_field = cached_field[0]
                            
                            cached_data = json.loads(cached_field)
                            total_size += len(cached_field)
                            
                            # Get timestamps from document fields or cache_data
                            cached_at = None
                            expires_at = None
                            
                            # Try document fields first
                            if "cached_at" in doc:
                                cached_at_field = doc["cached_at"]
                                cached_at_str = cached_at_field[0] if isinstance(cached_at_field, list) else cached_at_field
                                cached_at = datetime.fromisoformat(cached_at_str.replace('Z', '+00:00'))
                            
                            if "expires_at" in doc:
                                expires_at_field = doc["expires_at"]
                                expires_at_str = expires_at_field[0] if isinstance(expires_at_field, list) else expires_at_field
                                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                            
                            # Fallback to cache_data
                            if not cached_at and "cached_at" in cached_data:
                                cached_at = datetime.fromisoformat(cached_data["cached_at"].replace('Z', '+00:00'))
                            if not expires_at and "expires_at" in cached_data:
                                expires_at = datetime.fromisoformat(cached_data["expires_at"].replace('Z', '+00:00'))
                            
                            if cached_at and expires_at:
                                age_days = (now - cached_at).days
                                
                                # Check if expired
                                if now > expires_at:
                                    expired_count += 1
                                
                                # Categorize by age
                                if age_days <= 1:
                                    age_buckets["0-1d"] += 1
                                elif age_days <= 7:
                                    age_buckets["1-7d"] += 1
                                elif age_days <= 30:
                                    age_buckets["7-30d"] += 1
                                elif age_days <= 90:
                                    age_buckets["30-90d"] += 1
                                else:
                                    age_buckets[">90d"] += 1
                            
                            # Get hit count
                            hit_count = doc.get("hit_count", cached_data.get("hit_count", 0))
                            if isinstance(hit_count, list):
                                hit_count = hit_count[0]
                            total_hits += int(hit_count) if hit_count else 0
                                    
                    except (json.JSONDecodeError, KeyError, ValueError):
                        # Invalid cache data
                        expired_count += 1
                
                return {
                    "total_cache_documents": total_cache_docs,
                    "cache_by_type": type_stats,
                    "expired_documents": expired_count,
                    "age_distribution": age_buckets,
                    "total_hits": total_hits,
                    "estimated_size_bytes": total_size,
                    "estimated_size_mb": round(total_size / (1024 * 1024), 2),
                    "cache_efficiency": round((total_cache_docs - expired_count) / max(total_cache_docs, 1) * 100, 1)
                }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            
        return {
            "total_cache_documents": 0,
            "cache_by_type": {},
            "expired_documents": 0,
            "age_distribution": {},
            "total_hits": 0,
            "estimated_size_bytes": 0,
            "estimated_size_mb": 0.0,
            "cache_efficiency": 0.0
        }


# Global cache instance
_solr_cache = None

def get_solr_cache() -> SolrResultCache:
    """Get global SOLR cache instance"""
    global _solr_cache
    if _solr_cache is None:
        _solr_cache = SolrResultCache()
    return _solr_cache

def with_solr_cache(query_type: str):
    """
    Decorator to add SOLR caching to query functions
    
    Usage:
        @with_solr_cache('term_info')
        def get_term_info(short_form, force_refresh=False, **kwargs):
            # ... existing implementation
    
    The decorated function can accept a 'force_refresh' parameter to bypass cache.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check if force_refresh is requested (pop it before passing to function)
            force_refresh = kwargs.pop('force_refresh', False)
            
            # Extract term_id from first argument or kwargs
            term_id = args[0] if args else kwargs.get('short_form') or kwargs.get('term_id')
            
            # For functions like get_templates that don't have a term_id, use query_type as cache key
            if not term_id:
                if query_type == 'templates':
                    # Use a fixed cache key for templates since it doesn't take a term_id
                    term_id = 'all_templates'
                else:
                    logger.warning(f"No term_id found for caching {query_type}")
                    return func(*args, **kwargs)
            
            # Include preview parameter in cache key for term_info queries
            # This ensures preview=True and preview=False have separate cache entries
            cache_term_id = term_id
            if query_type == 'term_info':
                preview = kwargs.get('preview', True)  # Default is True
                cache_term_id = f"{term_id}_preview_{preview}"
            
            cache = get_solr_cache()
            
            # Clear cache if force_refresh is True
            if force_refresh:
                logger.info(f"Force refresh requested for {query_type}({term_id})")
                cache.clear_cache_entry(query_type, cache_term_id)
            
            # Try cache first (will be empty if force_refresh was True)
            if not force_refresh:
                cached_result = cache.get_cached_result(query_type, cache_term_id, **kwargs)
                if cached_result is not None:
                    # Validate that cached result has essential fields for term_info
                    if query_type == 'term_info':
                        is_valid = (cached_result and isinstance(cached_result, dict) and 
                                   cached_result.get('Id') and cached_result.get('Name'))
                        
                        # Additional validation for query results
                        if is_valid and 'Queries' in cached_result:
                            logger.debug(f"Validating {len(cached_result['Queries'])} queries for {term_id}")
                            for i, query in enumerate(cached_result['Queries']):
                                count = query.get('count', 0)
                                preview_results = query.get('preview_results')
                                headers = preview_results.get('headers', []) if isinstance(preview_results, dict) else []
                                
                                logger.debug(f"Query {i}: count={count}, preview_results_type={type(preview_results)}, headers={headers}")
                                
                                # Check if query has unrealistic count (0 or -1) which indicates failed execution
                                if count <= 0:
                                    is_valid = False
                                    logger.debug(f"Cached result has invalid query count {count} for {term_id}")
                                    break
                                # Check if preview_results is missing or has empty headers when it should have data
                                if not isinstance(preview_results, dict) or not headers:
                                    is_valid = False
                                    logger.debug(f"Cached result has invalid preview_results structure for {term_id}")
                                    break
                        
                        if is_valid:
                            logger.debug(f"Using valid cached result for {term_id}")
                            return cached_result
                        else:
                            logger.warning(f"Cached result incomplete for {term_id}, re-executing function")
                            # Don't return the incomplete cached result, continue to execute function
                    else:
                        return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            # Cache the result asynchronously to avoid blocking
            # Handle DataFrame, dict, and other result types properly
            result_is_valid = False
            if result is not None:
                if hasattr(result, 'empty'):  # DataFrame
                    result_is_valid = not result.empty
                elif isinstance(result, dict):
                    result_is_valid = bool(result)
                elif isinstance(result, (list, str)):
                    result_is_valid = len(result) > 0
                else:
                    result_is_valid = True
            
            if result_is_valid:
                # Validate result before caching for term_info
                if query_type == 'term_info':
                    if (result and isinstance(result, dict) and 
                        result.get('Id') and result.get('Name')):
                        try:
                            cache.cache_result(query_type, cache_term_id, result, **kwargs)
                            logger.debug(f"Cached complete result for {term_id}")
                        except Exception as e:
                            logger.debug(f"Failed to cache result: {e}")
                    else:
                        logger.warning(f"Not caching incomplete result for {term_id}")
                else:
                    try:
                        cache.cache_result(query_type, cache_term_id, result, **kwargs)
                    except Exception as e:
                        logger.debug(f"Failed to cache result: {e}")
            
            return result
        
        return wrapper
    return decorator
