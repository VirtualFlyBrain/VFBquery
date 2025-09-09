#!/usr/bin/env python3
"""
Test different field naming patterns to find what's allowed in the SOLR schema
"""

import json
import requests

def test_field_patterns():
    """Test different field naming patterns"""
    
    print("🔬 Testing SOLR Field Naming Patterns")
    print("=" * 45)
    
    # Restore data first
    print("0️⃣ Restoring data...")
    exec(open('restore_solr_data.py').read())
    
    field_patterns = [
        "test_field",
        "cache_test", 
        "vfb_cache_test",
        "query_cache_test",
        "temp_field",
        "custom_field"
    ]
    
    for i, pattern in enumerate(field_patterns, 1):
        print(f"\n{i}️⃣ Testing pattern: {pattern}")
        
        update_data = [{
            "id": "FBbt_00003686",
            pattern: {"set": f"test_value_{i}"}
        }]
        
        response = requests.post(
            "https://solr.virtualflybrain.org/solr/vfb_json/update",
            json=update_data,
            headers={"Content-Type": "application/json"},
            params={"commit": "true"}
        )
        
        if response.status_code == 200:
            print(f"   ✅ Pattern '{pattern}' WORKS!")
            
            # Verify it was added
            verify_response = requests.get("https://solr.virtualflybrain.org/solr/vfb_json/select", params={
                "q": "id:FBbt_00003686",
                "fl": f"id,{pattern}",
                "wt": "json"
            })
            
            if verify_response.status_code == 200:
                data = verify_response.json()
                docs = data.get("response", {}).get("docs", [])
                if docs and pattern in docs[0]:
                    print(f"   ✅ Field verified in document")
                else:
                    print(f"   ⚠️  Field not found in document after update")
        else:
            print(f"   ❌ Pattern '{pattern}' failed: {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("msg", "Unknown error")
                print(f"      Error: {error_msg}")
            except:
                print(f"      Raw error: {response.text[:100]}")
    
    # Check final document state
    print(f"\n🔍 Final document state:")
    response = requests.get("https://solr.virtualflybrain.org/solr/vfb_json/select", params={
        "q": "id:FBbt_00003686",
        "fl": "*",
        "wt": "json"
    })
    
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if docs:
            doc = docs[0]
            all_fields = list(doc.keys())
            original_fields = ["anat_query", "term_info", "anat_2_ep_query", "ep_2_anat_query"]
            preserved = [field for field in original_fields if field in doc]
            test_fields = [field for field in all_fields if field.startswith(("test_", "cache_", "vfb_", "query_", "temp_", "custom_"))]
            
            print(f"   Total fields: {len(all_fields)}")
            print(f"   Preserved original: {len(preserved)}/{len(original_fields)}")
            print(f"   Added test fields: {test_fields}")
            
            if len(preserved) >= 3:
                print("   ✅ Original fields preserved!")
            else:
                print("   ❌ Original fields lost!")

if __name__ == "__main__":
    test_field_patterns()
