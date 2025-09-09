#!/usr/bin/env python3

"""Test correct SOLR atomic update syntax"""

import json
import requests

def test_correct_atomic_syntax():
    """Test the correct atomic update syntax for SOLR"""
    
    cache_url = "https://solr.virtualflybrain.org/solr/vfb_json"
    term_id = "FBbt_00003686"
    field_name = "vfb_query_term_info_str"
    
    test_data = {
        "result": {"label": "Kenyon cell", "test": "corrected syntax"},
        "cached_at": "2025-09-09T19:59:00+01:00",
        "expires_at": "2025-12-08T19:59:00+01:00"
    }
    
    print("Testing correct atomic update syntax...")
    
    # Method 1: Try without the "set" wrapper (direct field assignment)
    print("\n1. Testing direct field assignment...")
    update_doc = {
        "id": term_id,
        field_name: json.dumps(test_data)
    }
    
    print(f"Update doc: {json.dumps(update_doc, indent=2)[:200]}...")
    
    response = requests.post(
        f"{cache_url}/update",
        data=json.dumps([update_doc]),
        headers={"Content-Type": "application/json"},
        params={"commit": "true"},
        timeout=10
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        # Check the result
        check_response = requests.get(f"{cache_url}/select", params={
            "q": f"id:{term_id}",
            "wt": "json",
            "indent": "true"
        })
        
        if check_response.status_code == 200:
            result_data = check_response.json()
            docs = result_data.get("response", {}).get("docs", [])
            if docs:
                doc = docs[0]
                print(f"\nDocument fields after update: {list(doc.keys())}")
                
                # Check if original fields are preserved
                expected_fields = ["id", "anat_query", "anat_2_ep_query", "ep_2_anat_query", "term_info"]
                preserved_fields = [f for f in expected_fields if f in doc]
                print(f"Preserved original fields: {preserved_fields}")
                
                if field_name in doc:
                    print(f"✅ Cache field {field_name} created successfully")
                    cached_value = doc[field_name]
                    print(f"Cached value type: {type(cached_value)}")
                    print(f"Cached value: {str(cached_value)[:100]}...")
                else:
                    print(f"❌ Cache field {field_name} not found")
                    # Check for any variations
                    cache_related_fields = [f for f in doc.keys() if 'vfb_query' in f]
                    print(f"Found cache-related fields: {cache_related_fields}")

if __name__ == "__main__":
    test_correct_atomic_syntax()
