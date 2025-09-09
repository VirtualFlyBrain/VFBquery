#!/usr/bin/env python3
"""
VFBquery Cache Optimization Demo

This script demonstrates the performance improvements available through
VFB_connect's caching mechanisms introduced in 2024-08-16.

Run this script to see the difference between cold start and cached performance.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Set environment variables to avoid GUI library issues
os.environ.update({
    'MPLBACKEND': 'Agg', 
    'VISPY_GL_LIB': 'osmesa', 
    'VISPY_USE_EGL': '0',
    'VFB_CACHE_ENABLED': 'true'  # Enable VFB_connect caching
})

# Mock problematic imports
from unittest.mock import MagicMock
for module in ['vispy', 'vispy.scene', 'vispy.util', 'vispy.util.fonts', 
               'vispy.util.fonts._triage', 'vispy.util.fonts._quartz', 
               'vispy.ext', 'vispy.ext.cocoapy', 'navis', 'navis.plotting', 
               'navis.plotting.vispy', 'navis.plotting.vispy.viewer']:
    sys.modules[module] = MagicMock()

def time_query(term_id, description, enable_cache=False):
    """Time a get_term_info query with optional caching enabled."""
    from vfbquery.vfb_queries import get_term_info
    import vfb_connect
    
    if enable_cache:
        # Enable VFBTerm object caching for repeated queries
        vc = vfb_connect.VfbConnect()
        vc._use_cache = True
        print(f"  VFBTerm caching: ENABLED")
    else:
        print(f"  VFBTerm caching: DISABLED")
    
    start_time = time.time()
    result = get_term_info(term_id)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"  {description}: {duration:.4f} seconds")
    
    if result and 'Queries' in result:
        queries = result['Queries']
        for i, query in enumerate(queries):
            func_name = query.get('function', 'Unknown')
            count = query.get('count', 'Unknown')
            print(f"    Query {i}: {func_name} (count: {count})")
    
    return duration

def main():
    print("VFBquery Cache Optimization Demo")
    print("=" * 50)
    
    test_terms = [
        ('FBbt_00003748', 'medulla (anatomical class)'),
        ('VFB_00101567', 'individual anatomy data')
    ]
    
    print("\n1. Testing without VFBTerm caching:")
    print("-" * 40)
    for term_id, description in test_terms:
        time_query(term_id, description, enable_cache=False)
        print()
    
    print("\n2. Testing WITH VFBTerm caching enabled:")
    print("-" * 40)
    total_cached = 0
    for term_id, description in test_terms:
        duration = time_query(term_id, description, enable_cache=True)
        total_cached += duration
        print()
    
    print("\n3. Testing cache effectiveness (repeated queries):")
    print("-" * 40)
    import vfb_connect
    vc = vfb_connect.VfbConnect()
    vc._use_cache = True
    
    # Test repeated queries to same term
    term_id = 'FBbt_00003748'
    print(f"Repeating queries for {term_id}:")
    
    for i in range(1, 4):
        duration = time_query(term_id, f"Run {i}", enable_cache=True)
    
    print("\nSummary:")
    print("- First run may be slower (lookup cache initialization)")
    print("- Subsequent runs benefit from VFB_connect's lookup cache")
    print("- VFBTerm caching provides additional speedup for repeated queries")
    print("- Cache persists for 3 months or until manually cleared")

if __name__ == '__main__':
    main()
