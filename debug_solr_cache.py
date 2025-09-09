#!/usr/bin/env python3
"""
Debug script to diagnose SOLR cache implementation issues
"""

import json
import logging
from src.vfbquery.solr_result_cache import SolrResultCache
import requests

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_solr_connection():
    """Test basic SOLR connectivity"""
    print("🔍 Debugging SOLR Connection")
    print("=" * 50)
    
    cache = SolrResultCache()
    print(f"SOLR URL: {cache.cache_url}")
    
    try:
        # Test basic connection
        response = requests.get(f"{cache.cache_url}/select", params={
            "q": "*:*",
            "rows": "1",
            "wt": "json"
        }, timeout=10)
        
        print(f"Connection Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total docs in collection: {data['response']['numFound']}")
            print("✅ SOLR connection working")
        else:
            print(f"❌ SOLR error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

def debug_cache_storage():
    """Debug cache storage mechanism"""
    print("\n🔍 Debugging Cache Storage")
    print("=" * 50)
    
    cache = SolrResultCache()
    
    # Test with a simple document that should exist
    test_id = "FBbt_00003686"
    test_result = {"label": "test brain", "debug": True}
    
    print(f"Attempting to cache result for {test_id}...")
    
    try:
        # Store the cache
        cache_key = cache.cache_result("term_info", test_id, test_result)
        print(f"Cache storage returned: {cache_key}")
        
        # Try to retrieve immediately
        print("Attempting immediate retrieval...")
        cached_result = cache.get_cached_result("term_info", test_id)
        print(f"Immediate retrieval: {cached_result is not None}")
        
        if cached_result:
            print(f"Retrieved result keys: {list(cached_result.keys())}")
        
        # Check if the document exists in SOLR
        print("Checking SOLR document...")
        response = requests.get(f"{cache.cache_url}/select", params={
            "q": f"id:{test_id}",
            "wt": "json",
            "fl": "*"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            if docs:
                doc = docs[0]
                print(f"Document found with {len(doc)} fields")
                
                # Check for VFBquery fields
                vfb_fields = [k for k in doc.keys() if k.startswith("vfb_query_")]
                print(f"VFBquery fields: {vfb_fields}")
                
                if vfb_fields:
                    field_data = doc[vfb_fields[0]]
                    print(f"Field data type: {type(field_data)}")
                    print(f"Field data sample: {str(field_data)[:200]}...")
            else:
                print(f"❌ No document found with ID {test_id}")
        
    except Exception as e:
        print(f"❌ Cache storage error: {e}")
        import traceback
        traceback.print_exc()

def debug_field_search():
    """Debug field-based search"""
    print("\n🔍 Debugging Field Search")
    print("=" * 50)
    
    cache = SolrResultCache()
    
    try:
        # Search for any documents with VFBquery fields
        response = requests.get(f"{cache.cache_url}/select", params={
            "q": "vfb_query_term_info:[* TO *] OR vfb_query_anatomy:[* TO *] OR vfb_query_neuron:[* TO *]",
            "rows": "10",
            "wt": "json",
            "fl": "*"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Documents with VFBquery fields: {data['response']['numFound']}")
            
            docs = data.get("response", {}).get("docs", [])
            for i, doc in enumerate(docs):
                print(f"\nDocument {i+1}:")
                print(f"  ID: {doc.get('id', 'unknown')}")
                
                vfb_fields = [k for k in doc.keys() if k.startswith("vfb_query_")]
                print(f"  VFBquery fields: {vfb_fields}")
                
                for field in vfb_fields[:2]:  # Show first 2 fields
                    field_value = doc[field]
                    print(f"  {field}: {type(field_value)} - {str(field_value)[:100]}...")
        else:
            print(f"❌ Field search error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Field search error: {e}")

def main():
    """Run debug analysis"""
    print("🐛 SOLR Cache Debug Analysis")
    
    debug_solr_connection()
    debug_cache_storage()
    debug_field_search()
    
    print(f"\n📋 Debug Complete")
    print("Check the logs above for specific issues.")

if __name__ == "__main__":
    main()
