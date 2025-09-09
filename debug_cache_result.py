#!/usr/bin/env python3

"""Debug the exact cache_result implementation"""

import sys
import os
sys.path.insert(0, 'src')
import json
import requests

def debug_cache_result():
    """Debug the exact steps in cache_result"""
    
    cache_url = "https://solr.virtualflybrain.org/solr/vfb_json"
    term_id = "FBbt_00003686"
    field_name = "vfb_query_term_info_str"
    
    test_result = {
        "label": "Kenyon cell",  
        "cached": True,
        "test_data": "debug test"
    }
    
    print(f"=== Debugging cache_result for {term_id} ===")
    
    # Step 1: Create cache metadata (simplified version)
    print("1. Creating cache metadata...")
    cached_data = {
        "result": test_result,
        "cached_at": "2025-09-09T19:45:00+01:00",
        "expires_at": "2025-12-08T19:45:00+01:00"
    }
    print(f"   Cached data: {json.dumps(cached_data)[:100]}...")
    
    # Step 2: Check if document exists (exact same logic)
    print("2. Checking if document exists...")
    existing_response = requests.get(f"{cache_url}/select", params={
        "q": f"id:{term_id}",
        "wt": "json",
        "fl": "id"
    }, timeout=5)
    
    print(f"   Response status: {existing_response.status_code}")
    
    if existing_response.status_code != 200:
        print(f"   ERROR: Cannot access document {term_id} for caching")
        return False
    
    existing_data = existing_response.json()
    existing_docs = existing_data.get("response", {}).get("docs", [])
    
    print(f"   Found {len(existing_docs)} documents")
    
    if not existing_docs:
        print(f"   ERROR: Document {term_id} does not exist - cannot add cache field")
        return False
    
    print(f"   ✓ Document exists: {existing_docs[0].get('id')}")
    
    # Step 3: Perform atomic update 
    print("3. Performing atomic update...")
    
    update_doc = {
        "id": term_id,
        field_name: {"set": json.dumps(cached_data)}
    }
    
    print(f"   Update document: {json.dumps(update_doc)[:150]}...")
    
    response = requests.post(
        f"{cache_url}/update",
        data=json.dumps([update_doc]),
        headers={"Content-Type": "application/json"},
        params={"commit": "true"},
        timeout=10
    )
    
    print(f"   Update response status: {response.status_code}")
    print(f"   Update response: {response.text[:200]}...")
    
    if response.status_code == 200:
        print("   ✓ Cache update successful")
        
        # Step 4: Verify the update worked
        print("4. Verifying update...")
        verify_response = requests.get(f"{cache_url}/select", params={
            "q": f"id:{term_id}",
            "fl": f"id,{field_name}",
            "wt": "json"
        }, timeout=5)
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            verify_docs = verify_data.get("response", {}).get("docs", [])
            
            if verify_docs and field_name in verify_docs[0]:
                print(f"   ✓ Field {field_name} successfully added")
                cached_value = verify_docs[0][field_name][0]
                print(f"   Cached value: {cached_value[:100]}...")
                return True
            else:
                print(f"   ✗ Field {field_name} not found after update")
                return False
        else:
            print(f"   ERROR: Cannot verify update: {verify_response.status_code}")
            return False
    else:
        print(f"   ERROR: Update failed: {response.text}")
        return False

if __name__ == "__main__":
    success = debug_cache_result()
    print(f"\nFinal result: {'SUCCESS' if success else 'FAILED'}")
