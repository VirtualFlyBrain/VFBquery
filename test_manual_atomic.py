#!/usr/bin/env python3
"""
Minimal test to debug SOLR atomic update behavior
"""

import json
import requests

def test_manual_atomic_update():
    """Test manual atomic update to understand SOLR behavior"""
    
    print("🔬 Manual SOLR Atomic Update Test")
    print("=" * 40)
    
    # First check current state
    print("1️⃣ Current document state:")
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
            print(f"   Total fields: {len(doc)}")
            print(f"   Fields: {list(doc.keys())}")
    
    # Test 1: Simple atomic update using /update/json/docs
    print("\n2️⃣ Testing /update/json/docs endpoint:")
    
    update_doc_1 = {
        "id": "FBbt_00003686",
        "test_field_1": {"set": "test_value_1"}
    }
    
    response = requests.post(
        "https://solr.virtualflybrain.org/solr/vfb_json/update/json/docs",
        json=[update_doc_1],
        headers={"Content-Type": "application/json"},
        params={"commit": "true"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    
    # Check result
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
            print(f"   After update - Total fields: {len(doc)}")
            print(f"   Fields: {list(doc.keys())}")
            
            # Check if original fields still exist
            original_fields = ["anat_query", "term_info", "anat_2_ep_query"]
            preserved = [field for field in original_fields if field in doc]
            print(f"   Preserved original fields: {preserved}")
            
            if "test_field_1" in doc:
                print(f"   ✅ New field added successfully")
            
            if len(preserved) >= 2:
                print(f"   ✅ Original fields preserved")
            else:
                print(f"   ❌ Original fields lost!")

if __name__ == "__main__":
    test_manual_atomic_update()
