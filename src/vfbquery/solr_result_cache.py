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
        
    def _get_cache_field_name(self, query_type):
        """Get the field name for a specific query type"""
        return f"vfb_query_{query_type}_ss"
    
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
        Retrieve cached result from existing vfb_json SOLR document
        
        Args:
            query_type: Type of query ('term_info', 'instances', etc.)
            term_id: Term identifier (SOLR document ID)
            **params: Query parameters for field name generation
            
        Returns:
            Cached result or None if not found/expired
        """
        field_name = self._get_cache_field_name(query_type)
        
        try:
            # Query existing vfb_json document for cached VFBquery result
            response = requests.get(f"{self.cache_url}/select", params={
                "q": f"id:{term_id}",
                "fl": f"{field_name}",
                "wt": "json"
            }, timeout=5)  # Short timeout for cache lookups
            
            if response.status_code != 200:
                logger.debug(f"Cache miss: HTTP {response.status_code}")
                return None
                
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            
            if not docs or field_name not in docs[0]:
                logger.debug(f"Cache miss: No {field_name} field found for {term_id}")
                return None
                
            cached_field = docs[0][field_name][0] if isinstance(docs[0][field_name], list) else docs[0][field_name]
            
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
                    self._clear_expired_field(term_id, field_name)
                    return None
                    
                # Log cache age for monitoring
                age_hours = (now - cached_at).total_seconds() / 3600
                logger.debug(f"Cache hit for {query_type}({term_id}) - age: {age_hours:.1f} hours")
                    
            except (KeyError, ValueError) as e:
                logger.warning(f"Invalid cache metadata for {term_id}: {e}")
                self._clear_expired_field(term_id, field_name)
                return None
            
            # Increment hit count asynchronously
            self._increment_field_hit_count(term_id, field_name, cached_data.get("hit_count", 0))
            
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
        Store result as field in existing vfb_json SOLR document
        
        Args:
            query_type: Type of query being cached
            term_id: Term identifier (SOLR document ID)
            result: Query result to cache
            **params: Query parameters for field name generation
            
        Returns:
            True if successfully cached, False otherwise
        """
        if not result:
            logger.debug("Empty result, not caching")
            return False
            
        field_name = self._get_cache_field_name(query_type)
        
        try:
            # Create cached metadata and result
            cached_data = self._create_cache_metadata(result)
            if not cached_data:
                return False  # Result too large or other issue
                
            # First, get the existing document to ensure it exists
            existing_response = requests.get(f"{self.cache_url}/select", params={
                "q": f"id:{term_id}",
                "wt": "json",
                "fl": "id"
            }, timeout=5)
            
            if existing_response.status_code != 200:
                logger.error(f"Cannot access document {term_id} for caching")
                return False
            
            existing_data = existing_response.json()
            existing_docs = existing_data.get("response", {}).get("docs", [])
            
            if not existing_docs:
                logger.warning(f"Document {term_id} does not exist - cannot add cache field")
                return False
            
            # Fetch complete existing document to preserve all fields
            complete_doc_response = requests.get(f"{self.cache_url}/select", params={
                "q": f"id:{term_id}",
                "wt": "json",
                "rows": "1"
            }, timeout=5)
            
            if complete_doc_response.status_code != 200:
                logger.error(f"Cannot fetch complete document {term_id}")
                return False
                
            complete_data = complete_doc_response.json()
            complete_docs = complete_data.get("response", {}).get("docs", [])
            
            if not complete_docs:
                logger.error(f"Document {term_id} not found for complete fetch")
                return False
            
            # Get the existing document and add our cache field
            existing_doc = complete_docs[0].copy()
            existing_doc[field_name] = json.dumps(cached_data)  # Add cache field
            
            # Replace entire document (like VFB indexer does)
            response = requests.post(
                f"{self.cache_url}/update",
                data=json.dumps([existing_doc]),
                headers={"Content-Type": "application/json"},
                params={"commit": "true"},  # Immediate commit for availability
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Cached {field_name} for {term_id}, size: {cached_data['result_size']/1024:.1f}KB")
                return True
            else:
                logger.error(f"Failed to cache result: HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error caching result: {e}")
            return False
    
    def _increment_field_hit_count(self, term_id: str, field_name: str, current_count: int):
        """Asynchronously increment hit count for cached field"""
        try:
            # First get the current cached data
            response = requests.get(f"{self.cache_url}/select", params={
                "q": f"id:{term_id}",
                "fl": field_name,
                "wt": "json"
            }, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                
                if docs and field_name in docs[0]:
                    cached_field = docs[0][field_name][0] if isinstance(docs[0][field_name], list) else docs[0][field_name]
                    cached_data = json.loads(cached_field)
                    
                    # Update hit count
                    cached_data["hit_count"] = current_count + 1
                    
                    # Update the field
                    update_doc = {
                        "id": term_id,
                        field_name: {"set": json.dumps(cached_data)}
                    }
                    
                    requests.post(
                        f"{self.cache_url}/update/json/docs",
                        json=[update_doc],
                        headers={"Content-Type": "application/json"},
                        params={"commit": "false"},  # Don't commit immediately for performance
                        timeout=2
                    )
        except Exception as e:
            logger.debug(f"Failed to update hit count: {e}")
    
    def _clear_expired_field(self, term_id: str, field_name: str):
        """Clear expired field from SOLR document"""
        try:
            # Remove the expired field from the document
            update_doc = {
                "id": term_id,
                field_name: {"set": None}  # Remove field by setting to null
            }
            
            requests.post(
                f"{self.cache_url}/update/json/docs",
                json=[update_doc],
                headers={"Content-Type": "application/json"},
                params={"commit": "false"},
                timeout=2
            )
        except Exception as e:
            logger.debug(f"Failed to clear expired field: {e}")
    
    def get_cache_age(self, query_type: str, term_id: str, **params) -> Optional[Dict[str, Any]]:
        """
        Get cache age information for a specific cached result
        
        Returns:
            Dictionary with cache age info or None if not cached
        """
        field_name = self._get_cache_field_name(query_type)
        
        try:
            response = requests.get(f"{self.cache_url}/select", params={
                "q": f"id:{term_id}",
                "fl": field_name,
                "wt": "json"
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                
                if docs and field_name in docs[0]:
                    cached_field = docs[0][field_name][0] if isinstance(docs[0][field_name], list) else docs[0][field_name]
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
                        "hit_count": cached_data.get("hit_count", 0),
                        "size_kb": cached_data.get("result_size", 0) / 1024
                    }
        except Exception as e:
            logger.debug(f"Error getting cache age: {e}")
            
        return None
    
    def cleanup_expired_entries(self) -> int:
        """
        Clean up expired VFBquery cache fields from documents
        
        Note: Since we're storing cache data as fields in existing vfb_json documents,
        this method scans for documents with VFBquery cache fields and removes expired ones.
        
        Returns:
            Number of expired fields cleaned up
        """
        try:
            now = datetime.now().astimezone()
            cleaned_count = 0
            
            # Search for documents that have VFBquery cache fields
            response = requests.get(f"{self.cache_url}/select", params={
                "q": "vfb_query_term_info_ss:[* TO *] OR vfb_query_anatomy_ss:[* TO *] OR vfb_query_neuron_ss:[* TO *]",
                "fl": "id,vfb_query_*",  # Get ID and all VFBquery fields
                "rows": "1000",  # Process in batches
                "wt": "json"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                
                for doc in docs:
                    doc_id = doc["id"]
                    updates = {}
                    
                    # Check each VFBquery field for expiration
                    for field_name, field_value in doc.items():
                        if field_name.startswith("vfb_query_"):
                            try:
                                # Handle both list and string field values
                                cached_field = field_value[0] if isinstance(field_value, list) else field_value
                                cached_data = json.loads(cached_field)
                                
                                expires_at = datetime.fromisoformat(cached_data["expires_at"].replace('Z', '+00:00'))
                                
                                if now > expires_at:
                                    # Mark field for removal
                                    updates[field_name] = {"set": None}
                                    cleaned_count += 1
                                    logger.debug(f"Marking {field_name} for removal from {doc_id}")
                                    
                            except (json.JSONDecodeError, KeyError, ValueError) as e:
                                # Invalid cache data - remove it
                                updates[field_name] = {"set": None}
                                cleaned_count += 1
                                logger.debug(f"Removing invalid cache field {field_name} from {doc_id}: {e}")
                    
                    # Apply updates if any fields need removal
                    if updates:
                        updates["id"] = doc_id
                        
                        update_response = requests.post(
                            f"{self.cache_url}/update/json/docs",
                            json=[updates],
                            headers={"Content-Type": "application/json"},
                            params={"commit": "false"},  # Batch commit at end
                            timeout=10
                        )
                        
                        if update_response.status_code != 200:
                            logger.warning(f"Failed to update {doc_id}: HTTP {update_response.status_code}")
                
                # Commit all changes
                if cleaned_count > 0:
                    requests.post(f"{self.cache_url}/update", params={"commit": "true"}, timeout=10)
                    logger.info(f"Cleaned up {cleaned_count} expired cache fields")
                
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get VFBquery cache statistics from field-based storage
        
        Returns:
            Dictionary with cache statistics including field counts and age distribution
        """
        try:
            # Get documents with VFBquery cache fields
            # Use a specific field search since wildcards may not work in all SOLR versions
            response = requests.get(f"{self.cache_url}/select", params={
                "q": "vfb_query_term_info_ss:[* TO *] OR vfb_query_anatomy_ss:[* TO *] OR vfb_query_neuron_ss:[* TO *]",
                "fl": "id,vfb_query_*",  # Get ID and all VFBquery fields
                "rows": "1000",  # Process in batches 
                "wt": "json"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                total_docs_with_cache = data.get("response", {}).get("numFound", 0)
                
                field_stats = {}
                total_fields = 0
                total_size = 0
                expired_count = 0
                age_buckets = {"0-1d": 0, "1-7d": 0, "7-30d": 0, "30-90d": 0, ">90d": 0}
                
                now = datetime.now().astimezone()
                
                # Analyze each document's cache fields
                for doc in docs:
                    for field_name, field_value in doc.items():
                        if field_name.startswith("vfb_query_"):
                            total_fields += 1
                            
                            # Extract query type from field name (remove vfb_query_ prefix and _ss suffix)
                            query_type = field_name.replace("vfb_query_", "").replace("_ss", "")
                            field_stats[query_type] = field_stats.get(query_type, 0) + 1
                            
                            try:
                                # Handle both list and string field values
                                cached_field = field_value[0] if isinstance(field_value, list) else field_value
                                cached_data = json.loads(cached_field)
                                
                                # Calculate age and size
                                cached_at = datetime.fromisoformat(cached_data["cached_at"].replace('Z', '+00:00'))
                                expires_at = datetime.fromisoformat(cached_data["expires_at"].replace('Z', '+00:00'))
                                
                                age_days = (now - cached_at).days
                                total_size += len(cached_field)
                                
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
                                    
                            except (json.JSONDecodeError, KeyError, ValueError):
                                # Invalid cache data
                                expired_count += 1
                
                return {
                    "total_cache_fields": total_fields,
                    "documents_with_cache": total_docs_with_cache,
                    "cache_by_type": field_stats,
                    "expired_fields": expired_count,
                    "age_distribution": age_buckets,
                    "estimated_size_bytes": total_size,
                    "estimated_size_mb": round(total_size / (1024 * 1024), 2),
                    "cache_efficiency": round((total_fields - expired_count) / max(total_fields, 1) * 100, 1)
                }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            
        return {
            "total_cache_fields": 0,
            "documents_with_cache": 0,
            "cache_by_type": {},
            "expired_fields": 0,
            "age_distribution": {},
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
        def get_term_info(short_form, **kwargs):
            # ... existing implementation
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract term_id from first argument or kwargs
            term_id = args[0] if args else kwargs.get('short_form') or kwargs.get('term_id')
            
            if not term_id:
                logger.warning("No term_id found for caching")
                return func(*args, **kwargs)
            
            cache = get_solr_cache()
            
            # Try cache first
            cached_result = cache.get_cached_result(query_type, term_id, **kwargs)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            # Cache the result asynchronously to avoid blocking
            if result:
                try:
                    cache.cache_result(query_type, term_id, result, **kwargs)
                except Exception as e:
                    logger.debug(f"Failed to cache result: {e}")
            
            return result
        
        return wrapper
    return decorator
