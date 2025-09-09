#!/usr/bin/env python3

"""Debug what's actually stored and retrieved from cache"""

import sys
import os
sys.path.insert(0, 'src')
import json
import requests

def debug_cache_storage():
    """Debug what's stored in the cache field"""
    
    cache_url = "https://solr.virtualflybrain.org/solr/vfb_json"
    term_id = "FBbt_00003686"
    field_name = "vfb_query_term_info_str"
    
    print(f"=== Debugging cache storage for {term_id} ===")
    
    # Check what's actually stored
    response = requests.get(f"{cache_url}/select", params={
        "q": f"id:{term_id}",
        "fl": f"id,{field_name}",
        "wt": "json"
    }, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        
        if docs and field_name in docs[0]:
            cached_field = docs[0][field_name]
            print(f"Raw cached field: {type(cached_field)} = {cached_field}")
            
            if isinstance(cached_field, list):
                cached_value = cached_field[0]
            else:
                cached_value = cached_field
                
            print(f"Cached value: {type(cached_value)} = {cached_value[:200]}...")
            
            try:
                # Try to parse as JSON
                parsed_data = json.loads(cached_value)
                print(f"Parsed data type: {type(parsed_data)}")
                print(f"Parsed data keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
                
                if isinstance(parsed_data, dict) and "result" in parsed_data:
                    result = parsed_data["result"]
                    print(f"Result type: {type(result)}")
                    print(f"Result: {result}")
                    
                    if isinstance(result, dict) and "label" in result:
                        print(f"Label: {result['label']}")
                    else:
                        print(f"Result is not a dict or has no label: {result}")
                        
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
        else:
            print(f"Field {field_name} not found in document")
    else:
        print(f"Request failed: {response.status_code}")

if __name__ == "__main__":
    debug_cache_storage()
