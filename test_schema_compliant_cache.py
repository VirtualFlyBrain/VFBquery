#!/usr/bin/env python3

"""Test the schema-compliant SOLR cache implementation"""

import sys
import os
sys.path.insert(0, 'src')

from vfbquery.solr_result_cache import SolrResultCache

def test_schema_compliant_cache():
    """Test that cache works with schema-compliant field names"""
    
    # Initialize cache
    cache = SolrResultCache()
    
    # Test data
    test_term_id = "FBbt_00003686"
    test_result = {
        "label": "Kenyon cell",  
        "cached": True,
        "test_data": "schema compliant test"
    }
    
    print(f"Testing schema-compliant caching for {test_term_id}...")
    
    # Test caching
    print("1. Caching result...")
    success = cache.cache_result("term_info", test_term_id, test_result)
    print(f"   Cache success: {success}")
    
    # Test retrieval
    print("2. Retrieving cached result...")
    cached_result = cache.get_cached_result("term_info", test_term_id)
    
    if cached_result:
        print(f"   Retrieved result: {cached_result.get('result', {}).get('label', 'No label')}")
        print(f"   Has cached_at: {'cached_at' in cached_result}")
        print(f"   Has expires_at: {'expires_at' in cached_result}")
    else:
        print("   No cached result found")
        
    # Test cache age
    print("3. Checking cache age...")
    cache_age = cache.get_cache_age("term_info", test_term_id)
    if cache_age:
        print(f"   Cache age: {cache_age.get('age_minutes', 0):.1f} minutes")
        print(f"   Days until expiration: {cache_age.get('days_until_expiration', 0):.1f}")
    else:
        print("   No cache age info found")
    
    # Test field name generation
    print("4. Testing field name generation...")
    field_name = cache._get_cache_field_name("term_info")
    print(f"   Field name for 'term_info': {field_name}")
    
    expected_field = "vfb_query_term_info_str"
    if field_name == expected_field:
        print(f"   ✓ Field name matches expected: {expected_field}")
    else:
        print(f"   ✗ Expected {expected_field}, got {field_name}")

if __name__ == "__main__":
    test_schema_compliant_cache()
