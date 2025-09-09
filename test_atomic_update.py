#!/usr/bin/env python3
"""
Test the corrected SOLR atomic update implementation
"""

import json
from src.vfbquery.solr_result_cache import SolrResultCache
import requests

def test_atomic_update():
    """Test that atomic updates preserve existing VFB fields"""
    print("🧪 Testing Atomic Update Implementation")
    print("=" * 50)
    
    # First, verify current state
    print("1️⃣ Verifying current document state...")
    response = requests.get("https://solr.virtualflybrain.org/solr/vfb_json/select", params={
        "q": "id:FBbt_00003686",
        "wt": "json",
        "fl": "*"
    })
    
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if docs:
            doc = docs[0]
            original_fields = [k for k in doc.keys() if not k.startswith("vfb_query_") and k != "_version_"]
            cache_fields = [k for k in doc.keys() if k.startswith("vfb_query_")]
            print(f"   Original VFB fields: {len(original_fields)}")
            print(f"   Existing cache fields: {len(cache_fields)}")
            
    # Test cache storage with atomic update
    print("\n2️⃣ Testing cache storage with atomic update...")
    cache = SolrResultCache()
    
    test_result = {
        "label": "Kenyon cell",
        "type": "neuron",
        "test_data": "atomic update test"
    }
    
    # Store using atomic update
    success = cache.cache_result("term_info", "FBbt_00003686", test_result)
    print(f"   Cache storage result: {'✅ Success' if success else '❌ Failed'}")
    
    # Verify document integrity after caching
    print("\n3️⃣ Verifying document integrity after caching...")
    response = requests.get("https://solr.virtualflybrain.org/solr/vfb_json/select", params={
        "q": "id:FBbt_00003686", 
        "wt": "json",
        "fl": "*"
    })
    
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if docs:
            doc = docs[0]
            new_original_fields = [k for k in doc.keys() if not k.startswith("vfb_query_") and k != "_version_"]
            new_cache_fields = [k for k in doc.keys() if k.startswith("vfb_query_")]
            
            print(f"   Original VFB fields after caching: {len(new_original_fields)}")
            print(f"   Cache fields after caching: {len(new_cache_fields)}")
            print(f"   Field names: {new_cache_fields}")
            
            # Check if original data is intact
            if "anat_query" in doc and "term_info" in doc:
                print("   ✅ Original VFB fields preserved!")
            else:
                print("   ❌ Original VFB fields missing!")
                
            # Check cache field contents
            if new_cache_fields:
                cache_field_name = new_cache_fields[0]
                cache_data = doc[cache_field_name]
                print(f"   Cache field type: {type(cache_data)}")
                if isinstance(cache_data, list):
                    cache_data = cache_data[0]
                print(f"   Cache data sample: {str(cache_data)[:100]}...")
    
    # Test retrieval
    print("\n4️⃣ Testing cache retrieval...")
    cached_result = cache.get_cached_result("term_info", "FBbt_00003686")
    
    if cached_result:
        print("   ✅ Cache retrieval successful!")
        print(f"   Retrieved keys: {list(cached_result.keys())}")
        if cached_result.get("label") == "Kenyon cell":
            print("   ✅ Data integrity confirmed!")
    else:
        print("   ❌ Cache retrieval failed!")
    
    print("\n" + "=" * 50)
    return success and cached_result is not None

if __name__ == "__main__":
    success = test_atomic_update()
    if success:
        print("🎉 Atomic update implementation working correctly!")
    else:
        print("⚠️  Issues detected with atomic update implementation")
