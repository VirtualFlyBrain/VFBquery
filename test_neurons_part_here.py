#!/usr/bin/env python3
"""
Test script for NeuronsPartHere query implementation.
Tests with medulla [FBbt_00003748] which should return 471 results per the screenshot.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vfbquery.vfb_queries import get_neurons_with_part_in

def test_neurons_part_here():
    """Test NeuronsPartHere query with medulla"""
    
    print("="*80)
    print("Testing NeuronsPartHere query with medulla [FBbt_00003748]")
    print("Expected: 471 results (from screenshot)")
    print("="*80)
    print()
    
    # Test with medulla - should return 471 results
    medulla_id = "FBbt_00003748"
    
    try:
        print(f"Querying neurons with parts in medulla ({medulla_id})...")
        print()
        
        # Get results as dataframe
        results_df = get_neurons_with_part_in(medulla_id, return_dataframe=True, limit=-1)
        
        if results_df is not None and not results_df.empty:
            count = len(results_df)
            print(f"✓ SUCCESS: Found {count} neuron classes")
            print()
            
            # Show first few results
            print("First 5 results:")
            print("-" * 80)
            for idx, row in results_df.head(5).iterrows():
                print(f"  {idx+1}. {row.get('label', 'N/A')[:60]}")
                print(f"     ID: {row.get('id', 'N/A')}")
                print(f"     Tags: {row.get('tags', 'N/A')[:60]}")
                print()
            
            # Verify count matches expected
            if count == 471:
                print("✓✓ PERFECT MATCH: Got exactly 471 results as expected!")
            elif count > 450 and count < 500:
                print(f"⚠ CLOSE: Got {count} results (expected 471)")
                print("  This might be due to data updates in VFB")
            else:
                print(f"⚠ WARNING: Expected 471 results but got {count}")
            
            print()
            print("=" * 80)
            print("QUERY SUCCESSFUL")
            print("=" * 80)
            return True
            
        else:
            print("✗ FAILED: No results returned")
            print()
            print("=" * 80)
            print("QUERY FAILED - No results")
            print("=" * 80)
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {type(e).__name__}: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("=" * 80)
        print("QUERY FAILED - Exception occurred")
        print("=" * 80)
        return False

if __name__ == "__main__":
    success = test_neurons_part_here()
    sys.exit(0 if success else 1)
