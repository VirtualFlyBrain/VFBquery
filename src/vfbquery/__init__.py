from .vfb_queries import *
from .solr_result_cache import get_solr_cache

# SOLR-based caching (simplified single-layer approach)
try:
    from .cached_functions import (
        get_term_info_cached,
        get_instances_cached,
        get_templates_cached,
        get_related_anatomy_cached,
        get_similar_neurons_cached,
        get_individual_neuron_inputs_cached,
        get_expression_overlaps_here_cached,
        get_neurons_with_part_in_cached,
        get_neurons_with_synapses_in_cached,
        get_neurons_with_presynaptic_terminals_in_cached,
        get_neurons_with_postsynaptic_terminals_in_cached,
        get_components_of_cached,
        get_parts_of_cached,
        get_subclasses_of_cached,
        get_neuron_classes_fasciculating_here_cached,
        get_tracts_nerves_innervating_here_cached,
        get_lineage_clones_in_cached,
        get_neuron_neuron_connectivity_cached,
        get_neuron_region_connectivity_cached,
        get_images_neurons_cached,
        get_images_that_develop_from_cached,
        get_expression_pattern_fragments_cached,
        get_anatomy_scrnaseq_cached,
        get_cluster_expression_cached,
        get_expression_cluster_cached,
        get_scrnaseq_dataset_data_cached,
        get_similar_morphology_cached,
        get_similar_morphology_part_of_cached,
        get_similar_morphology_part_of_exp_cached,
        get_similar_morphology_nb_cached,
        get_similar_morphology_nb_exp_cached,
        get_similar_morphology_userdata_cached,
        get_painted_domains_cached,
        get_dataset_images_cached,
        get_all_aligned_images_cached,
        get_aligned_datasets_cached,
        get_all_datasets_cached,
        get_terms_for_pub_cached,
        get_transgene_expression_here_cached,
    )
    __caching_available__ = True

    # Enable SOLR caching by default with 3-month TTL
    import os
    
    # Check if caching should be disabled via environment variable
    cache_disabled = os.getenv('VFBQUERY_CACHE_ENABLED', 'true').lower() in ('false', '0', 'no', 'off')
    
    if not cache_disabled:
        # Import and patch functions with caching
        from .cached_functions import patch_vfbquery_with_caching
        patch_vfbquery_with_caching()
        print("VFBquery: SOLR caching enabled by default (3-month TTL)")
        print("         Disable with: export VFBQUERY_CACHE_ENABLED=false")

except ImportError:
    __caching_available__ = False
    print("VFBquery: Caching not available (dependencies missing)")# Convenience function for clearing SOLR cache entries
def clear_solr_cache(query_type: str, term_id: str) -> bool:
    """
    Clear a specific SOLR cache entry to force refresh
    
    Args:
        query_type: Type of query ('term_info', 'instances', etc.)
        term_id: Term identifier (e.g., 'FBbt_00003748')
    
    Returns:
        True if successfully cleared, False otherwise
    
    Example:
        >>> import vfbquery as vfb
        >>> vfb.clear_solr_cache('term_info', 'FBbt_00003748')
        >>> result = vfb.get_term_info('FBbt_00003748')  # Will fetch fresh data
    """
    cache = get_solr_cache()
    return cache.clear_cache_entry(query_type, term_id)

# SOLR-based result caching (experimental - for cold start optimization)
try:
    from .solr_cache_integration import (
        enable_solr_result_caching,
        disable_solr_result_caching, 
        warmup_solr_cache,
        get_solr_cache_stats as get_solr_cache_stats_func,
        cleanup_solr_cache
    )
    __solr_caching_available__ = True
except ImportError:
    __solr_caching_available__ = False

# Version information
__version__ = "0.1.0"
