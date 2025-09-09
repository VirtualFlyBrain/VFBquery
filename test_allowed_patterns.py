#!/usr/bin/env python3
"""
Test using allowed dynamic field patterns for VFBquery caching
"""

import json
import requests

def test_allowed_patterns():
    """Test dynamic field patterns that are allowed"""
    
    print("🧪 Testing Allowed Dynamic Field Patterns")
    print("=" * 45)
    
    # Restore data first
    print("0️⃣ Restoring original data...")
    exec(open('restore_solr_data.py').read())
    
    # Test patterns that should work
    test_patterns = [
        ("vfb_query_term_info_str", "strings - for JSON cache data"),
        ("vfb_query_term_info_s", "string - for single JSON cache"),
        ("vfb_query_term_info_txt", "text_general - for searchable cache"),
    ]
    
    for pattern, description in test_patterns:
        print(f"\n🔬 Testing: {pattern}")
        print(f"   Type: {description}")
        
        cache_data = {
            "result": {"label": "Kenyon cell", "cached": True},
            "cached_at": "2025-09-09T19:45:00+01:00",
            "expires_at": "2025-12-08T19:45:00+01:00"
        }
        
        update_data = [{
            "id": "FBbt_00003686",
            pattern: {"set": json.dumps(cache_data)}
        }]
        
        response = requests.post(
            "https://solr.virtualflybrain.org/solr/vfb_json/update",
            json=update_data,
            headers={"Content-Type": "application/json"},
            params={"commit": "true"}
        )
        
        if response.status_code == 200:
            print(f"   ✅ Update successful!")
            
            # Verify the field was added and retrieve it
            verify_response = requests.get("https://solr.virtualflybrain.org/solr/vfb_json/select", params={
                "q": "id:FBbt_00003686",
                "fl": f"id,{pattern}",
                "wt": "json"
            })
            
            if verify_response.status_code == 200:
                data = verify_response.json()
                docs = data.get("response", {}).get("docs", [])
                if docs and pattern in docs[0]:
                    field_value = docs[0][pattern]
                    print(f"   ✅ Field stored successfully")
                    print(f"   Type in SOLR: {type(field_value)}")
                    
                    # Try to parse the JSON back
                    try:
                        if isinstance(field_value, list):
                            field_value = field_value[0]
                        parsed_cache = json.loads(field_value)
                        print(f"   ✅ JSON parsing successful")
                        print(f"   Cached result: {parsed_cache['result']['label']}")
                        break  # Found a working pattern, stop testing
                    except Exception as e:
                        print(f"   ❌ JSON parsing failed: {e}")
                else:
                    print(f"   ⚠️  Field not found in document")
        else:
            print(f"   ❌ Update failed: {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("msg", "Unknown error")
                print(f"      Error: {error_msg}")
            except:
                print(f"      Raw error: {response.text[:100]}")
    
    # Final verification
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
            cache_fields = [field for field in all_fields if "vfb_query" in field]
            
            print(f"   Total fields: {len(all_fields)}")
            print(f"   Preserved original: {len(preserved)}/{len(original_fields)}")
            print(f"   Cache fields: {cache_fields}")
            
            return len(preserved) >= 3 and len(cache_fields) > 0

if __name__ == "__main__":
    success = test_allowed_patterns()
    if success:
        print("\n🎉 Found working field pattern for VFBquery caching!")
    else:
        print("\n❌ No suitable field patterns found")
