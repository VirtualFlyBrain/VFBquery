#!/usr/bin/env python3
"""
Test correct SOLR atomic update using the proper endpoint and format
"""

import json
import requests

def test_correct_atomic_update():
    """Test proper atomic update that preserves existing fields"""
    
    print("🔬 Correct SOLR Atomic Update Test")
    print("=" * 40)
    
    # Check initial state
    print("1️⃣ Initial document state:")
    response = requests.get("https://solr.virtualflybrain.org/solr/vfb_json/select", params={
        "q": "id:FBbt_00003686",
        "fl": "*",
        "wt": "json"
    })
    
    initial_fields = []
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if docs:
            doc = docs[0]
            initial_fields = list(doc.keys())
            print(f"   Total fields: {len(doc)}")
            print(f"   Fields: {initial_fields}")
    
    # Test proper atomic update using /update endpoint with JSON
    print("\n2️⃣ Testing proper atomic update:")
    
    # Method 1: Using /update with JSON format
    update_data = [
        {
            "id": "FBbt_00003686",
            "vfb_query_test": {"set": "atomic_test_value"}
        }
    ]
    
    response = requests.post(
        "https://solr.virtualflybrain.org/solr/vfb_json/update",
        json=update_data,
        headers={"Content-Type": "application/json"},
        params={"commit": "true"}
    )
    
    print(f"   Update status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    # Verify the update preserved existing fields
    print("\n3️⃣ Verifying field preservation:")
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
            final_fields = list(doc.keys())
            print(f"   Total fields after update: {len(doc)}")
            print(f"   Fields: {final_fields}")
            
            # Check preservation of original fields
            original_fields = ["anat_query", "term_info", "anat_2_ep_query", "ep_2_anat_query"]
            preserved = [field for field in original_fields if field in doc]
            print(f"   Preserved original fields: {len(preserved)}/{len(original_fields)} - {preserved}")
            
            # Check new field
            new_field_exists = "vfb_query_test" in doc
            print(f"   New field added: {'✅' if new_field_exists else '❌'}")
            
            if len(preserved) >= 3 and new_field_exists:
                print("   ✅ SUCCESS: Atomic update working correctly!")
                return True
            else:
                print("   ❌ FAILURE: Fields lost or not added properly")
                return False
    
    return False

if __name__ == "__main__":
    success = test_correct_atomic_update()
    if success:
        print("\n🎉 Atomic updates working - can proceed with cache implementation!")
    else:
        print("\n❌ Need to investigate SOLR atomic update configuration")
