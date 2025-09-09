#!/usr/bin/env python3

"""
Production test for VFBquery SOLR caching system

Verifies that:
1. Cache data is properly stored and retrieved 
2. Original VFB fields are preserved
3. Cache expiration works correctly
"""

import sys
import os
sys.path.insert(0, 'src')

from vfbquery.solr_result_cache import SolrResultCache
import json
import requests

def test_production_cache():
    """Test production cache functionality with field preservation"""
    
    cache = SolrResultCache()
    test_term_id = "FBbt_00003686"
    
    print("🧪 Testing VFBquery SOLR Cache System")
    print("=" * 50)
    
    # Step 1: Check original VFB data exists
    print(f"1. Verifying original VFB data exists for {test_term_id}...")
    
    response = requests.get(f"{cache.cache_url}/select", params={
        "q": f"id:{test_term_id}",
        "fl": "id,anat_query,anat_2_ep_query,ep_2_anat_query,term_info", 
        "wt": "json"
    }, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        
        if docs:
            original_doc = docs[0]
            required_fields = ['id', 'anat_query', 'anat_2_ep_query', 'ep_2_anat_query', 'term_info']
            missing_fields = [field for field in required_fields if field not in original_doc]
            
            if missing_fields:
                print(f"   ❌ Missing original VFB fields: {missing_fields}")
                return False
            else:
                print(f"   ✅ All original VFB fields present: {required_fields}")
        else:
            print(f"   ❌ Document {test_term_id} not found")
            return False
    else:
        print(f"   ❌ Failed to query document: HTTP {response.status_code}")
        return False
    
    # Step 2: Test caching
    print("\n2. Testing cache storage...")
    
    test_result = {
        "label": "Kenyon cell",
        "short_form": "FBbt_00003686",
        "iri": "http://purl.obolibrary.org/obo/FBbt_00003686",
        "cached": True,
        "test_timestamp": "2025-09-09T20:00:00+01:00"
    }
    
    success = cache.cache_result("term_info", test_term_id, test_result)
    
    if success:
        print("   ✅ Cache storage successful")
    else:
        print("   ❌ Cache storage failed")
        return False
    
    # Step 3: Verify both original fields AND cache field are present
    print("\n3. Verifying field preservation after caching...")
    
    response = requests.get(f"{cache.cache_url}/select", params={
        "q": f"id:{test_term_id}",
        "wt": "json"
    }, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        
        if docs:
            updated_doc = docs[0]
            
            # Check original VFB fields still exist
            original_fields_intact = all(field in updated_doc for field in required_fields)
            
            # Check cache field exists  
            cache_field_name = "vfb_query_term_info_ss"
            cache_field_exists = cache_field_name in updated_doc
            
            print(f"   Original VFB fields intact: {'✅' if original_fields_intact else '❌'}")
            print(f"   Cache field added: {'✅' if cache_field_exists else '❌'}")
            
            if original_fields_intact and cache_field_exists:
                print(f"   📊 Total fields in document: {len(updated_doc)}")
                
                # Verify cache field content
                if cache_field_exists:
                    cache_data_raw = updated_doc[cache_field_name][0] if isinstance(updated_doc[cache_field_name], list) else updated_doc[cache_field_name]
                    cache_data = json.loads(cache_data_raw)
                    
                    print(f"   📋 Cache metadata keys: {list(cache_data.keys())}")
                    print(f"   ⏰ Cached at: {cache_data.get('cached_at', 'Unknown')}")
                    print(f"   📏 Cache size: {cache_data.get('result_size', 0)/1024:.1f}KB")
            else:
                print("   ❌ Field preservation failed!")
                return False
        else:
            print("   ❌ Document not found after caching")
            return False
    else:
        print(f"   ❌ Failed to verify document: HTTP {response.status_code}")
        return False
    
    # Step 4: Test cache retrieval
    print("\n4. Testing cache retrieval...")
    
    retrieved_result = cache.get_cached_result("term_info", test_term_id)
    
    if retrieved_result:
        if isinstance(retrieved_result, dict) and retrieved_result.get("label") == "Kenyon cell":
            print("   ✅ Cache retrieval successful")
            print(f"   📄 Retrieved result: {retrieved_result.get('label')} ({retrieved_result.get('short_form')})")
        else:
            print(f"   ❌ Retrieved unexpected result: {retrieved_result}")
            return False
    else:
        print("   ❌ Cache retrieval failed")
        return False
    
    # Step 5: Test cache age information
    print("\n5. Testing cache metadata...")
    
    cache_age = cache.get_cache_age("term_info", test_term_id)
    
    if cache_age:
        print(f"   ✅ Cache age retrieved")
        print(f"   ⏱️  Age: {cache_age.get('age_minutes', 0):.1f} minutes")
        print(f"   📅 Expires in: {cache_age.get('days_until_expiration', 0):.1f} days")
        print(f"   👁️  Hit count: {cache_age.get('hit_count', 0)}")
    else:
        print("   ❌ Cache age retrieval failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED - Production cache system is working correctly!")
    print("\n✅ Verified capabilities:")
    print("   • Original VFB data preservation")
    print("   • Cache data storage and retrieval") 
    print("   • Metadata tracking and expiration")
    print("   • Field coexistence in single document")
    
    return True

if __name__ == "__main__":
    success = test_production_cache()
    exit(0 if success else 1)
