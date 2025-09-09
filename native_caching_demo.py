#!/usr/bin/env python3
"""
VFBquery Native Caching Demo

This script demonstrates how to implement VFB_connect-style caching
techniques directly in VFBquery to improve performance for repeated queries.

The caching system provides:
1. Memory-based caching for fast repeated access
2. Disk-based caching for persistence across sessions
3. Configurable TTL and cache sizes
4. Multiple cache layers (SOLR, parsing, query results, complete responses)
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Set environment variables
os.environ.update({
    'MPLBACKEND': 'Agg', 
    'VISPY_GL_LIB': 'osmesa', 
    'VISPY_USE_EGL': '0',
    'VFBQUERY_CACHE_ENABLED': 'true'  # Enable our custom caching
})

# Mock problematic imports
from unittest.mock import MagicMock
for module in ['vispy', 'vispy.scene', 'vispy.util', 'vispy.util.fonts', 
               'vispy.util.fonts._triage', 'vispy.util.fonts._quartz', 
               'vispy.ext', 'vispy.ext.cocoapy', 'navis', 'navis.plotting', 
               'navis.plotting.vispy', 'navis.plotting.vispy.viewer']:
    sys.modules[module] = MagicMock()

def demo_basic_caching():
    """Demonstrate basic VFBquery caching functionality."""
    print("=" * 60)
    print("VFBquery Native Caching Demo")
    print("=" * 60)
    
    # Import and enable caching
    from vfbquery.cache_enhancements import enable_vfbquery_caching, get_vfbquery_cache_stats
    from vfbquery.cached_functions import get_term_info_cached, get_instances_cached
    
    # Enable caching with custom settings
    enable_vfbquery_caching(
        cache_ttl_hours=24,      # Cache for 24 hours
        memory_cache_size=500,   # Keep 500 items in memory
        disk_cache_enabled=True  # Persist to disk
    )
    
    test_term = 'FBbt_00003748'  # medulla
    
    print(f"\n1. Testing get_term_info_cached with {test_term}")
    print("-" * 40)
    
    # First call (cold)
    start_time = time.time()
    result1 = get_term_info_cached(test_term)
    cold_time = time.time() - start_time
    print(f"Cold call: {cold_time:.4f} seconds")
    
    # Second call (should be cached)
    start_time = time.time() 
    result2 = get_term_info_cached(test_term)
    warm_time = time.time() - start_time
    print(f"Warm call: {warm_time:.4f} seconds")
    
    speedup = cold_time / warm_time if warm_time > 0 else float('inf')
    print(f"Speedup: {speedup:.1f}x")
    
    # Show cache stats
    stats = get_vfbquery_cache_stats()
    print(f"\\nCache Statistics:")
    print(f"  Hit Rate: {stats['hit_rate_percent']}%")
    print(f"  Memory Items: {stats['memory_cache_size']}")
    print(f"  Hits: {stats['hits']}, Misses: {stats['misses']}")

def demo_instances_caching():
    """Demonstrate get_instances caching."""
    print(f"\n2. Testing get_instances_cached")
    print("-" * 40)
    
    from vfbquery.cached_functions import get_instances_cached
    
    test_term = 'FBbt_00003748'
    
    # Test with different limits to show cache effectiveness
    for limit in [5, 10, -1]:  # -1 means all results
        print(f"\n  Testing with limit={limit}")
        
        # First call
        start_time = time.time()
        result1 = get_instances_cached(test_term, return_dataframe=False, limit=limit)
        cold_time = time.time() - start_time
        
        # Second call (cached)
        start_time = time.time()
        result2 = get_instances_cached(test_term, return_dataframe=False, limit=limit)
        warm_time = time.time() - start_time
        
        count = result1.get('count', 0) if result1 is not None else 0
        speedup = cold_time / warm_time if warm_time > 0 else float('inf')
        
        print(f"    Cold: {cold_time:.4f}s, Warm: {warm_time:.4f}s, "
              f"Speedup: {speedup:.1f}x, Count: {count}")

def demo_patching():
    """Demonstrate monkey-patching existing VFBquery functions."""
    print(f"\n3. Testing function patching (transparent caching)")
    print("-" * 40)
    
    from vfbquery.cached_functions import patch_vfbquery_with_caching
    from vfbquery.vfb_queries import get_term_info  # This will be patched
    
    # Enable patching
    patch_vfbquery_with_caching()
    
    test_term = 'VFB_00101567'  # Different term to avoid cache hits from previous tests
    
    print(f"  Using patched get_term_info() function:")
    
    # First call through patched function
    start_time = time.time()
    result1 = get_term_info(test_term)
    cold_time = time.time() - start_time
    
    # Second call (should hit cache)
    start_time = time.time()
    result2 = get_term_info(test_term)
    warm_time = time.time() - start_time
    
    speedup = cold_time / warm_time if warm_time > 0 else float('inf')
    print(f"    Cold: {cold_time:.4f}s, Warm: {warm_time:.4f}s, Speedup: {speedup:.1f}x")
    print(f"    This demonstrates transparent caching - no code changes needed!")

def demo_cache_persistence():
    """Demonstrate disk cache persistence."""
    print(f"\n4. Testing cache persistence across sessions")
    print("-" * 40)
    
    from vfbquery.cache_enhancements import get_cache, clear_vfbquery_cache
    from vfbquery.cached_functions import get_term_info_cached
    
    cache = get_cache()
    cache_dir = cache.cache_dir if hasattr(cache, 'cache_dir') else None
    
    if cache_dir:
        print(f"  Cache directory: {cache_dir}")
        cache_files_before = list(cache_dir.glob("*.pkl")) if cache_dir.exists() else []
        print(f"  Cache files before: {len(cache_files_before)}")
        
        # Make a query to populate cache
        test_term = 'FBbt_00005106'  # Another term
        result = get_term_info_cached(test_term)
        
        cache_files_after = list(cache_dir.glob("*.pkl")) if cache_dir.exists() else []
        print(f"  Cache files after query: {len(cache_files_after)}")
        print(f"  New cache files created: {len(cache_files_after) - len(cache_files_before)}")
        
        # Show that cache persists by clearing memory and querying again
        cache._memory_cache.clear()  # Clear memory but keep disk
        
        start_time = time.time()
        result2 = get_term_info_cached(test_term)  # Should load from disk
        disk_load_time = time.time() - start_time
        print(f"  Load from disk cache: {disk_load_time:.4f}s")
    else:
        print("  Disk caching not enabled")

def demo_configuration_options():
    """Demonstrate different configuration options."""
    print(f"\n5. Configuration Options")
    print("-" * 40)
    
    from vfbquery.cache_enhancements import CacheConfig, configure_cache, get_vfbquery_cache_stats
    
    # Example configurations
    configs = [
        ("Memory-only (fast)", CacheConfig(
            enabled=True, 
            memory_cache_size=1000, 
            disk_cache_enabled=False,
            cache_ttl_hours=1
        )),
        ("Disk-only (persistent)", CacheConfig(
            enabled=True,
            memory_cache_size=0,
            disk_cache_enabled=True,
            cache_ttl_hours=168  # 1 week
        )),
        ("Balanced", CacheConfig(
            enabled=True,
            memory_cache_size=500,
            disk_cache_enabled=True,
            cache_ttl_hours=24
        ))
    ]
    
    for name, config in configs:
        print(f"  {name}:")
        print(f"    Memory size: {config.memory_cache_size}")
        print(f"    Disk enabled: {config.disk_cache_enabled}")
        print(f"    TTL: {config.cache_ttl_hours} hours")

def main():
    """Run all demonstrations."""
    try:
        demo_basic_caching()
        demo_instances_caching() 
        demo_patching()
        demo_cache_persistence()
        demo_configuration_options()
        
        print(f"\n" + "=" * 60)
        print("Summary: VFBquery Native Caching Benefits")
        print("=" * 60)
        print("✅ Dramatic speedup for repeated queries")
        print("✅ Configurable memory and disk caching")  
        print("✅ Transparent integration (monkey-patching)")
        print("✅ Cache persistence across sessions")
        print("✅ Multiple cache layers for different data types")
        print("✅ Similar performance benefits to VFB_connect")
        
        # Final cache stats
        from vfbquery.cache_enhancements import get_vfbquery_cache_stats
        final_stats = get_vfbquery_cache_stats()
        print(f"\\nFinal Cache Statistics:")
        print(f"  Total Hit Rate: {final_stats['hit_rate_percent']}%")
        print(f"  Memory Cache Size: {final_stats['memory_cache_size']} items")
        print(f"  Total Hits: {final_stats['hits']}")
        print(f"  Total Misses: {final_stats['misses']}")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
