#!/usr/bin/env python3

"""Debug document existence check"""

import sys
import os
sys.path.insert(0, 'src')
import json
import requests

def test_document_existence():
    """Test if document existence check works"""
    
    cache_url = "https://solr.virtualflybrain.org/solr/vfb_json"
    term_id = "FBbt_00003686"
    
    print(f"Testing document existence for {term_id}...")
    
    # Check if document exists
    response = requests.get(f"{cache_url}/select", params={
        "q": f"id:{term_id}",
        "rows": "1", 
        "wt": "json"
    }, timeout=10)
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response data: {json.dumps(data, indent=2)[:500]}...")
        
        docs = data.get("response", {}).get("docs", [])
        num_found = data.get("response", {}).get("numFound", 0)
        
        print(f"Number found: {num_found}")
        print(f"Documents returned: {len(docs)}")
        
        if docs:
            doc = docs[0]
            print(f"Document ID: {doc.get('id', 'No ID')}")
            print(f"Document fields: {list(doc.keys())}")
            return True
        else:
            print("No documents found")
            return False
    else:
        print(f"Request failed: {response.text}")
        return False

if __name__ == "__main__":
    exists = test_document_existence()
    print(f"Document exists: {exists}")
