"""
Cached VFBquery Functions

Enhanced versions of VFBquery functions with integrated caching
inspired by VFB_connect optimizations.
"""

from typing import Dict, Any, Optional
from .solr_result_cache import with_solr_cache


def is_valid_term_info_result(result):
    """Check if a term_info result has the essential fields and valid query structure"""
    if not result or not isinstance(result, dict):
        return False
    
    # Check for essential fields
    if not (result.get('Id') and result.get('Name')):
        return False
    
    # Additional validation for query results
    if 'Queries' in result:
        for query in result['Queries']:
            # Check if query has invalid count (-1) which indicates failed execution
            # Note: count=0 is valid if preview_results structure is correct
            count = query.get('count', 0)
            
            # Check if preview_results has the correct structure
            preview_results = query.get('preview_results')
            if not isinstance(preview_results, dict):
                print(f"DEBUG: Invalid preview_results type {type(preview_results)} detected")
                return False
                
            headers = preview_results.get('headers', [])
            if not headers:
                print(f"DEBUG: Empty headers detected in preview_results")
                return False
            
            # Only reject if count is -1 (failed execution) or if count is 0 but preview_results is missing/empty
            if count < 0:
                print(f"DEBUG: Invalid query count {count} detected")
                return False
    
    return True
from .vfb_queries import (
    get_term_info as _original_get_term_info,
    get_instances as _original_get_instances,
    get_templates as _original_get_templates,
    get_related_anatomy as _original_get_related_anatomy,
    get_similar_neurons as _original_get_similar_neurons,
    get_individual_neuron_inputs as _original_get_individual_neuron_inputs,
    get_expression_overlaps_here as _original_get_expression_overlaps_here,
    get_neurons_with_part_in as _original_get_neurons_with_part_in,
    get_neurons_with_synapses_in as _original_get_neurons_with_synapses_in,
    get_neurons_with_presynaptic_terminals_in as _original_get_neurons_with_presynaptic_terminals_in,
    get_neurons_with_postsynaptic_terminals_in as _original_get_neurons_with_postsynaptic_terminals_in,
    get_components_of as _original_get_components_of,
    get_parts_of as _original_get_parts_of,
    get_subclasses_of as _original_get_subclasses_of,
    get_neuron_classes_fasciculating_here as _original_get_neuron_classes_fasciculating_here,
    get_tracts_nerves_innervating_here as _original_get_tracts_nerves_innervating_here,
    get_lineage_clones_in as _original_get_lineage_clones_in,
    get_neuron_neuron_connectivity as _original_get_neuron_neuron_connectivity,
    get_neuron_region_connectivity as _original_get_neuron_region_connectivity,
    get_images_neurons as _original_get_images_neurons,
    get_images_that_develop_from as _original_get_images_that_develop_from,
    get_expression_pattern_fragments as _original_get_expression_pattern_fragments,
    get_anatomy_scrnaseq as _original_get_anatomy_scrnaseq,
    get_cluster_expression as _original_get_cluster_expression,
    get_expression_cluster as _original_get_expression_cluster,
    get_scrnaseq_dataset_data as _original_get_scrnaseq_dataset_data,
    get_similar_morphology as _original_get_similar_morphology,
    get_similar_morphology_part_of as _original_get_similar_morphology_part_of,
    get_similar_morphology_part_of_exp as _original_get_similar_morphology_part_of_exp,
    get_similar_morphology_nb as _original_get_similar_morphology_nb,
    get_similar_morphology_nb_exp as _original_get_similar_morphology_nb_exp,
    get_similar_morphology_userdata as _original_get_similar_morphology_userdata,
    get_painted_domains as _original_get_painted_domains,
    get_dataset_images as _original_get_dataset_images,
    get_all_aligned_images as _original_get_all_aligned_images,
    get_aligned_datasets as _original_get_aligned_datasets,
    get_all_datasets as _original_get_all_datasets,
    get_terms_for_pub as _original_get_terms_for_pub,
    get_transgene_expression_here as _original_get_transgene_expression_here,
)

@with_solr_cache('term_info')
def get_term_info_cached(short_form: str, preview: bool = True, force_refresh: bool = False):
    """
    Enhanced get_term_info with SOLR caching.
    
    This version caches complete term_info responses in SOLR for fast retrieval.
    
    Args:
        short_form: Term short form (e.g., 'FBbt_00003748')
        preview: Whether to include preview results
        force_refresh: Whether to bypass cache and fetch fresh data
        
    Returns:
        Term info dictionary or None if not found
    """
    return _original_get_term_info(short_form=short_form, preview=preview)

def get_instances_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_instances with SOLR caching.
    
    This cached version provides dramatic speedup for repeated queries.
    
    Args:
        short_form: Class short form
        return_dataframe: Whether to return DataFrame or formatted dict
        limit: Maximum number of results (-1 for all)
        force_refresh: Whether to bypass cache and fetch fresh data
        
    Returns:
        Instances data (DataFrame or formatted dict based on return_dataframe)
    """
    return _original_get_instances(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

@with_solr_cache('similar_neurons')
def get_similar_neurons_cached(neuron, similarity_score='NBLAST_score', return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_similar_neurons with SOLR caching.
    
    This cached version provides dramatic speedup for repeated NBLAST similarity queries.
    
    Args:
        neuron: Neuron identifier
        similarity_score: Similarity score type ('NBLAST_score', etc.)
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        force_refresh: Whether to bypass cache and fetch fresh data
        
    Returns:
        Similar neurons data (DataFrame or list of dicts)
    """
    return _original_get_similar_neurons(neuron=neuron, similarity_score=similarity_score, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_cached(neuron_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_similar_morphology with SOLR caching.
    
    Args:
        neuron_short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        force_refresh: Whether to bypass cache and fetch fresh data
        
    Returns:
        Similar morphology data
    """
    return _original_get_similar_morphology(neuron_short_form=neuron_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_part_of_cached(neuron_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_similar_morphology_part_of with SOLR caching.
    
    Args:
        neuron_short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        force_refresh: Whether to bypass cache and fetch fresh data
        
    Returns:
        Similar morphology part-of data
    """
    return _original_get_similar_morphology_part_of(neuron_short_form=neuron_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_part_of_exp_cached(expression_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_similar_morphology_part_of_exp with SOLR caching.
    
    Args:
        expression_short_form: Expression pattern short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        force_refresh: Whether to bypass cache and fetch fresh data
        
    Returns:
        Similar morphology expression data
    """
    return _original_get_similar_morphology_part_of_exp(expression_short_form=expression_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_nb_cached(neuron_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_similar_morphology_nb with SOLR caching.
    
    Args:
        neuron_short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        NBLAST similar morphology data
    """
    return _original_get_similar_morphology_nb(neuron_short_form=neuron_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_nb_exp_cached(expression_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_similar_morphology_nb_exp with SOLR caching.
    
    Args:
        expression_short_form: Expression pattern short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        NBLAST expression similarity data
    """
    return _original_get_similar_morphology_nb_exp(expression_short_form=expression_short_form, return_dataframe=return_dataframe, limit=limit)

def get_similar_morphology_userdata_cached(upload_id: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_similar_morphology_userdata with SOLR caching.
    
    Args:
        upload_id: User upload identifier
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        User data similarity results
    """
    return _original_get_similar_morphology_userdata(upload_id=upload_id, return_dataframe=return_dataframe, limit=limit)

def get_neurons_with_part_in_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_neurons_with_part_in with SOLR caching.
    
    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Neurons with part in the specified anatomical structure
    """
    return _original_get_neurons_with_part_in(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_neurons_with_synapses_in_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_neurons_with_synapses_in with SOLR caching.
    
    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Neurons with synapses in the specified anatomical structure
    """
    return _original_get_neurons_with_synapses_in(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_neurons_with_presynaptic_terminals_in_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_neurons_with_presynaptic_terminals_in with SOLR caching.
    
    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Neurons with presynaptic terminals in the specified anatomical structure
    """
    return _original_get_neurons_with_presynaptic_terminals_in(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_neurons_with_postsynaptic_terminals_in_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_neurons_with_postsynaptic_terminals_in with SOLR caching.
    
    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        
    Returns:
        Neurons with postsynaptic terminals in the specified anatomical structure
    """
    return _original_get_neurons_with_postsynaptic_terminals_in(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_templates_cached(limit: int = -1, return_dataframe: bool = False, force_refresh: bool = False):
    """
    Enhanced get_templates with SOLR caching.

    Args:
        limit: Maximum number of results (-1 for all)
        return_dataframe: Whether to return DataFrame or list of dicts
        force_refresh: Whether to bypass cache and fetch fresh data

    Returns:
        Template data
    """
    return _original_get_templates(limit=limit, return_dataframe=return_dataframe)

def get_related_anatomy_cached(template_short_form: str, limit: int = -1, return_dataframe: bool = False, force_refresh: bool = False):
    """
    Enhanced get_related_anatomy with SOLR caching.

    Args:
        template_short_form: Template short form
        limit: Maximum number of results (-1 for all)
        return_dataframe: Whether to return DataFrame or list of dicts
        force_refresh: Whether to bypass cache and fetch fresh data

    Returns:
        Related anatomy data
    """
    return _original_get_related_anatomy(template_short_form=template_short_form, limit=limit, return_dataframe=return_dataframe)

def get_painted_domains_cached(template_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_painted_domains with SOLR caching.

    Args:
        template_short_form: Template short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Painted domains data
    """
    return _original_get_painted_domains(template_short_form=template_short_form, return_dataframe=return_dataframe, limit=limit)

def get_dataset_images_cached(dataset_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_dataset_images with SOLR caching.

    Args:
        dataset_short_form: Dataset short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Dataset images data
    """
    return _original_get_dataset_images(dataset_short_form=dataset_short_form, return_dataframe=return_dataframe, limit=limit)

def get_all_aligned_images_cached(template_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_all_aligned_images with SOLR caching.

    Args:
        template_short_form: Template short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        All aligned images data
    """
    return _original_get_all_aligned_images(template_short_form=template_short_form, return_dataframe=return_dataframe, limit=limit)

def get_aligned_datasets_cached(template_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_aligned_datasets with SOLR caching.

    Args:
        template_short_form: Template short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Aligned datasets data
    """
    return _original_get_aligned_datasets(template_short_form=template_short_form, return_dataframe=return_dataframe, limit=limit)

def get_all_datasets_cached(return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_all_datasets with SOLR caching.

    Args:
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        All datasets data
    """
    return _original_get_all_datasets(return_dataframe=return_dataframe, limit=limit)

def get_individual_neuron_inputs_cached(neuron_short_form: str, return_dataframe=True, limit: int = -1, summary_mode: bool = False, force_refresh: bool = False):
    """
    Enhanced get_individual_neuron_inputs with SOLR caching.

    Args:
        neuron_short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        summary_mode: Whether to return summary mode

    Returns:
        Individual neuron inputs data
    """
    return _original_get_individual_neuron_inputs(neuron_short_form=neuron_short_form, return_dataframe=return_dataframe, limit=limit, summary_mode=summary_mode)

def get_neuron_neuron_connectivity_cached(short_form: str, return_dataframe=True, limit: int = -1, min_weight: float = 0, direction: str = 'both', force_refresh: bool = False):
    """
    Enhanced get_neuron_neuron_connectivity with SOLR caching.

    Args:
        short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)
        min_weight: Minimum connection weight
        direction: Connection direction ('both', 'incoming', 'outgoing')

    Returns:
        Neuron-neuron connectivity data
    """
    return _original_get_neuron_neuron_connectivity(short_form=short_form, return_dataframe=return_dataframe, limit=limit, min_weight=min_weight, direction=direction)

def get_neuron_region_connectivity_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_neuron_region_connectivity with SOLR caching.

    Args:
        short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Neuron-region connectivity data
    """
    return _original_get_neuron_region_connectivity(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_expression_overlaps_here_cached(anatomy_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_expression_overlaps_here with SOLR caching.

    Args:
        anatomy_short_form: Anatomy short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Expression overlaps data
    """
    return _original_get_expression_overlaps_here(anatomy_short_form=anatomy_short_form, return_dataframe=return_dataframe, limit=limit)

def get_anatomy_scrnaseq_cached(anatomy_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_anatomy_scrnaseq with SOLR caching.

    Args:
        anatomy_short_form: Anatomy short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Anatomy scRNAseq data
    """
    return _original_get_anatomy_scrnaseq(anatomy_short_form=anatomy_short_form, return_dataframe=return_dataframe, limit=limit)

def get_cluster_expression_cached(cluster_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_cluster_expression with SOLR caching.

    Args:
        cluster_short_form: Cluster short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Cluster expression data
    """
    return _original_get_cluster_expression(cluster_short_form=cluster_short_form, return_dataframe=return_dataframe, limit=limit)

def get_expression_cluster_cached(gene_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_expression_cluster with SOLR caching.

    Args:
        gene_short_form: Gene short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Expression cluster data
    """
    return _original_get_expression_cluster(gene_short_form=gene_short_form, return_dataframe=return_dataframe, limit=limit)

def get_scrnaseq_dataset_data_cached(dataset_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_scrnaseq_dataset_data with SOLR caching.

    Args:
        dataset_short_form: Dataset short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        scRNAseq dataset data
    """
    return _original_get_scrnaseq_dataset_data(dataset_short_form=dataset_short_form, return_dataframe=return_dataframe, limit=limit)

def get_transgene_expression_here_cached(anatomy_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_transgene_expression_here with SOLR caching.

    Args:
        anatomy_short_form: Anatomy short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Transgene expression data
    """
    return _original_get_transgene_expression_here(anatomy_short_form=anatomy_short_form, return_dataframe=return_dataframe, limit=limit)

def get_components_of_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_components_of with SOLR caching.

    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Components of the specified anatomical structure
    """
    return _original_get_components_of(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_parts_of_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_parts_of with SOLR caching.

    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Parts of the specified anatomical structure
    """
    return _original_get_parts_of(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_subclasses_of_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_subclasses_of with SOLR caching.

    Args:
        short_form: Class short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Subclasses of the specified class
    """
    return _original_get_subclasses_of(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_neuron_classes_fasciculating_here_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_neuron_classes_fasciculating_here with SOLR caching.

    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Neuron classes fasciculating in the specified anatomical structure
    """
    return _original_get_neuron_classes_fasciculating_here(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_tracts_nerves_innervating_here_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_tracts_nerves_innervating_here with SOLR caching.

    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Tracts and nerves innervating the specified anatomical structure
    """
    return _original_get_tracts_nerves_innervating_here(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_lineage_clones_in_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_lineage_clones_in with SOLR caching.

    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Lineage clones in the specified anatomical structure
    """
    return _original_get_lineage_clones_in(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_images_neurons_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_images_neurons with SOLR caching.

    Args:
        short_form: Neuron short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Images of the specified neuron
    """
    return _original_get_images_neurons(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_images_that_develop_from_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_images_that_develop_from with SOLR caching.

    Args:
        short_form: Anatomical structure short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Images that develop from the specified anatomical structure
    """
    return _original_get_images_that_develop_from(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_expression_pattern_fragments_cached(short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_expression_pattern_fragments with SOLR caching.

    Args:
        short_form: Expression pattern short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Expression pattern fragments data
    """
    return _original_get_expression_pattern_fragments(short_form=short_form, return_dataframe=return_dataframe, limit=limit)

def get_terms_for_pub_cached(pub_short_form: str, return_dataframe=True, limit: int = -1, force_refresh: bool = False):
    """
    Enhanced get_terms_for_pub with SOLR caching.

    Args:
        pub_short_form: Publication short form
        return_dataframe: Whether to return DataFrame or list of dicts
        limit: Maximum number of results (-1 for all)

    Returns:
        Terms associated with the specified publication
    """
    return _original_get_terms_for_pub(pub_short_form=pub_short_form, return_dataframe=return_dataframe, limit=limit)

# Convenience function to replace original functions
def patch_vfbquery_with_caching():
    """
    Replace original VFBquery functions with cached versions.
    
    This allows existing code to benefit from caching without changes.
    """
    import vfbquery.vfb_queries as vfb_queries
    import vfbquery
    
    # Store original functions for fallback
    setattr(vfb_queries, '_original_get_term_info', vfb_queries.get_term_info)
    setattr(vfb_queries, '_original_get_instances', vfb_queries.get_instances)
    setattr(vfb_queries, '_original_get_templates', vfb_queries.get_templates)
    setattr(vfb_queries, '_original_get_related_anatomy', vfb_queries.get_related_anatomy)
    setattr(vfb_queries, '_original_get_similar_neurons', vfb_queries.get_similar_neurons)
    setattr(vfb_queries, '_original_get_individual_neuron_inputs', vfb_queries.get_individual_neuron_inputs)
    setattr(vfb_queries, '_original_get_expression_overlaps_here', vfb_queries.get_expression_overlaps_here)
    setattr(vfb_queries, '_original_get_neurons_with_part_in', vfb_queries.get_neurons_with_part_in)
    setattr(vfb_queries, '_original_get_neurons_with_synapses_in', vfb_queries.get_neurons_with_synapses_in)
    setattr(vfb_queries, '_original_get_neurons_with_presynaptic_terminals_in', vfb_queries.get_neurons_with_presynaptic_terminals_in)
    setattr(vfb_queries, '_original_get_neurons_with_postsynaptic_terminals_in', vfb_queries.get_neurons_with_postsynaptic_terminals_in)
    setattr(vfb_queries, '_original_get_components_of', vfb_queries.get_components_of)
    setattr(vfb_queries, '_original_get_parts_of', vfb_queries.get_parts_of)
    setattr(vfb_queries, '_original_get_subclasses_of', vfb_queries.get_subclasses_of)
    setattr(vfb_queries, '_original_get_neuron_classes_fasciculating_here', vfb_queries.get_neuron_classes_fasciculating_here)
    setattr(vfb_queries, '_original_get_tracts_nerves_innervating_here', vfb_queries.get_tracts_nerves_innervating_here)
    setattr(vfb_queries, '_original_get_lineage_clones_in', vfb_queries.get_lineage_clones_in)
    setattr(vfb_queries, '_original_get_neuron_neuron_connectivity', vfb_queries.get_neuron_neuron_connectivity)
    setattr(vfb_queries, '_original_get_neuron_region_connectivity', vfb_queries.get_neuron_region_connectivity)
    setattr(vfb_queries, '_original_get_images_neurons', vfb_queries.get_images_neurons)
    setattr(vfb_queries, '_original_get_images_that_develop_from', vfb_queries.get_images_that_develop_from)
    setattr(vfb_queries, '_original_get_expression_pattern_fragments', vfb_queries.get_expression_pattern_fragments)
    setattr(vfb_queries, '_original_get_anatomy_scrnaseq', vfb_queries.get_anatomy_scrnaseq)
    setattr(vfb_queries, '_original_get_cluster_expression', vfb_queries.get_cluster_expression)
    setattr(vfb_queries, '_original_get_expression_cluster', vfb_queries.get_expression_cluster)
    setattr(vfb_queries, '_original_get_scrnaseq_dataset_data', vfb_queries.get_scrnaseq_dataset_data)
    setattr(vfb_queries, '_original_get_similar_morphology', vfb_queries.get_similar_morphology)
    setattr(vfb_queries, '_original_get_similar_morphology_part_of', vfb_queries.get_similar_morphology_part_of)
    setattr(vfb_queries, '_original_get_similar_morphology_part_of_exp', vfb_queries.get_similar_morphology_part_of_exp)
    setattr(vfb_queries, '_original_get_similar_morphology_nb', vfb_queries.get_similar_morphology_nb)
    setattr(vfb_queries, '_original_get_similar_morphology_nb_exp', vfb_queries.get_similar_morphology_nb_exp)
    setattr(vfb_queries, '_original_get_similar_morphology_userdata', vfb_queries.get_similar_morphology_userdata)
    setattr(vfb_queries, '_original_get_painted_domains', vfb_queries.get_painted_domains)
    setattr(vfb_queries, '_original_get_dataset_images', vfb_queries.get_dataset_images)
    setattr(vfb_queries, '_original_get_all_aligned_images', vfb_queries.get_all_aligned_images)
    setattr(vfb_queries, '_original_get_aligned_datasets', vfb_queries.get_aligned_datasets)
    setattr(vfb_queries, '_original_get_all_datasets', vfb_queries.get_all_datasets)
    setattr(vfb_queries, '_original_get_terms_for_pub', vfb_queries.get_terms_for_pub)
    setattr(vfb_queries, '_original_get_transgene_expression_here', vfb_queries.get_transgene_expression_here)
    
    # Replace with cached versions in vfb_queries module
    vfb_queries.get_term_info = get_term_info_cached
    vfb_queries.get_instances = get_instances_cached
    vfb_queries.get_templates = get_templates_cached
    vfb_queries.get_related_anatomy = get_related_anatomy_cached
    vfb_queries.get_similar_neurons = get_similar_neurons_cached
    vfb_queries.get_individual_neuron_inputs = get_individual_neuron_inputs_cached
    vfb_queries.get_expression_overlaps_here = get_expression_overlaps_here_cached
    vfb_queries.get_neurons_with_part_in = get_neurons_with_part_in_cached
    vfb_queries.get_neurons_with_synapses_in = get_neurons_with_synapses_in_cached
    vfb_queries.get_neurons_with_presynaptic_terminals_in = get_neurons_with_presynaptic_terminals_in_cached
    vfb_queries.get_neurons_with_postsynaptic_terminals_in = get_neurons_with_postsynaptic_terminals_in_cached
    vfb_queries.get_components_of = get_components_of_cached
    vfb_queries.get_parts_of = get_parts_of_cached
    vfb_queries.get_subclasses_of = get_subclasses_of_cached
    vfb_queries.get_neuron_classes_fasciculating_here = get_neuron_classes_fasciculating_here_cached
    vfb_queries.get_tracts_nerves_innervating_here = get_tracts_nerves_innervating_here_cached
    vfb_queries.get_lineage_clones_in = get_lineage_clones_in_cached
    vfb_queries.get_neuron_neuron_connectivity = get_neuron_neuron_connectivity_cached
    vfb_queries.get_neuron_region_connectivity = get_neuron_region_connectivity_cached
    vfb_queries.get_images_neurons = get_images_neurons_cached
    vfb_queries.get_images_that_develop_from = get_images_that_develop_from_cached
    vfb_queries.get_expression_pattern_fragments = get_expression_pattern_fragments_cached
    vfb_queries.get_anatomy_scrnaseq = get_anatomy_scrnaseq_cached
    vfb_queries.get_cluster_expression = get_cluster_expression_cached
    vfb_queries.get_expression_cluster = get_expression_cluster_cached
    vfb_queries.get_scrnaseq_dataset_data = get_scrnaseq_dataset_data_cached
    vfb_queries.get_similar_morphology = get_similar_morphology_cached
    vfb_queries.get_similar_morphology_part_of = get_similar_morphology_part_of_cached
    vfb_queries.get_similar_morphology_part_of_exp = get_similar_morphology_part_of_exp_cached
    vfb_queries.get_similar_morphology_nb = get_similar_morphology_nb_cached
    vfb_queries.get_similar_morphology_nb_exp = get_similar_morphology_nb_exp_cached
    vfb_queries.get_similar_morphology_userdata = get_similar_morphology_userdata_cached
    vfb_queries.get_painted_domains = get_painted_domains_cached
    vfb_queries.get_dataset_images = get_dataset_images_cached
    vfb_queries.get_all_aligned_images = get_all_aligned_images_cached
    vfb_queries.get_aligned_datasets = get_aligned_datasets_cached
    vfb_queries.get_all_datasets = get_all_datasets_cached
    vfb_queries.get_terms_for_pub = get_terms_for_pub_cached
    vfb_queries.get_transgene_expression_here = get_transgene_expression_here_cached
    
    # Also replace in the main vfbquery module namespace (since functions were imported with 'from .vfb_queries import *')
    vfbquery.get_term_info = get_term_info_cached
    vfbquery.get_instances = get_instances_cached
    vfbquery.get_templates = get_templates_cached
    vfbquery.get_related_anatomy = get_related_anatomy_cached
    vfbquery.get_similar_neurons = get_similar_neurons_cached
    vfbquery.get_individual_neuron_inputs = get_individual_neuron_inputs_cached
    vfbquery.get_expression_overlaps_here = get_expression_overlaps_here_cached
    vfbquery.get_neurons_with_part_in = get_neurons_with_part_in_cached
    vfbquery.get_neurons_with_synapses_in = get_neurons_with_synapses_in_cached
    vfbquery.get_neurons_with_presynaptic_terminals_in = get_neurons_with_presynaptic_terminals_in_cached
    vfbquery.get_neurons_with_postsynaptic_terminals_in = get_neurons_with_postsynaptic_terminals_in_cached
    vfbquery.get_components_of = get_components_of_cached
    vfbquery.get_parts_of = get_parts_of_cached
    vfbquery.get_subclasses_of = get_subclasses_of_cached
    vfbquery.get_neuron_classes_fasciculating_here = get_neuron_classes_fasciculating_here_cached
    vfbquery.get_tracts_nerves_innervating_here = get_tracts_nerves_innervating_here_cached
    vfbquery.get_lineage_clones_in = get_lineage_clones_in_cached
    vfbquery.get_neuron_neuron_connectivity = get_neuron_neuron_connectivity_cached
    vfbquery.get_neuron_region_connectivity = get_neuron_region_connectivity_cached
    vfbquery.get_images_neurons = get_images_neurons_cached
    vfbquery.get_images_that_develop_from = get_images_that_develop_from_cached
    vfbquery.get_expression_pattern_fragments = get_expression_pattern_fragments_cached
    vfbquery.get_anatomy_scrnaseq = get_anatomy_scrnaseq_cached
    vfbquery.get_cluster_expression = get_cluster_expression_cached
    vfbquery.get_expression_cluster = get_expression_cluster_cached
    vfbquery.get_scrnaseq_dataset_data = get_scrnaseq_dataset_data_cached
    vfbquery.get_similar_morphology = get_similar_morphology_cached
    vfbquery.get_similar_morphology_part_of = get_similar_morphology_part_of_cached
    vfbquery.get_similar_morphology_part_of_exp = get_similar_morphology_part_of_exp_cached
    vfbquery.get_similar_morphology_nb = get_similar_morphology_nb_cached
    vfbquery.get_similar_morphology_nb_exp = get_similar_morphology_nb_exp_cached
    vfbquery.get_similar_morphology_userdata = get_similar_morphology_userdata_cached
    vfbquery.get_painted_domains = get_painted_domains_cached
    vfbquery.get_dataset_images = get_dataset_images_cached
    vfbquery.get_all_aligned_images = get_all_aligned_images_cached
    vfbquery.get_aligned_datasets = get_aligned_datasets_cached
    vfbquery.get_all_datasets = get_all_datasets_cached
    vfbquery.get_terms_for_pub = get_terms_for_pub_cached
    vfbquery.get_transgene_expression_here = get_transgene_expression_here_cached
    
    print("VFBquery functions patched with caching support")

def unpatch_vfbquery_caching():
    """Restore original VFBquery functions."""
    import vfbquery.vfb_queries as vfb_queries
    
    if hasattr(vfb_queries, '_original_get_term_info'):
        vfb_queries.get_term_info = getattr(vfb_queries, '_original_get_term_info')
    if hasattr(vfb_queries, '_original_get_instances'):
        vfb_queries.get_instances = getattr(vfb_queries, '_original_get_instances')
    if hasattr(vfb_queries, '_original_get_templates'):
        vfb_queries.get_templates = getattr(vfb_queries, '_original_get_templates')
    if hasattr(vfb_queries, '_original_get_related_anatomy'):
        vfb_queries.get_related_anatomy = getattr(vfb_queries, '_original_get_related_anatomy')
    if hasattr(vfb_queries, '_original_get_similar_neurons'):
        vfb_queries.get_similar_neurons = getattr(vfb_queries, '_original_get_similar_neurons')
    if hasattr(vfb_queries, '_original_get_individual_neuron_inputs'):
        vfb_queries.get_individual_neuron_inputs = getattr(vfb_queries, '_original_get_individual_neuron_inputs')
    if hasattr(vfb_queries, '_original_get_expression_overlaps_here'):
        vfb_queries.get_expression_overlaps_here = getattr(vfb_queries, '_original_get_expression_overlaps_here')
    if hasattr(vfb_queries, '_original_get_neurons_with_part_in'):
        vfb_queries.get_neurons_with_part_in = getattr(vfb_queries, '_original_get_neurons_with_part_in')
    if hasattr(vfb_queries, '_original_get_neurons_with_synapses_in'):
        vfb_queries.get_neurons_with_synapses_in = getattr(vfb_queries, '_original_get_neurons_with_synapses_in')
    if hasattr(vfb_queries, '_original_get_neurons_with_presynaptic_terminals_in'):
        vfb_queries.get_neurons_with_presynaptic_terminals_in = getattr(vfb_queries, '_original_get_neurons_with_presynaptic_terminals_in')
    if hasattr(vfb_queries, '_original_get_neurons_with_postsynaptic_terminals_in'):
        vfb_queries.get_neurons_with_postsynaptic_terminals_in = getattr(vfb_queries, '_original_get_neurons_with_postsynaptic_terminals_in')
    if hasattr(vfb_queries, '_original_get_components_of'):
        vfb_queries.get_components_of = getattr(vfb_queries, '_original_get_components_of')
    if hasattr(vfb_queries, '_original_get_parts_of'):
        vfb_queries.get_parts_of = getattr(vfb_queries, '_original_get_parts_of')
    if hasattr(vfb_queries, '_original_get_subclasses_of'):
        vfb_queries.get_subclasses_of = getattr(vfb_queries, '_original_get_subclasses_of')
    if hasattr(vfb_queries, '_original_get_neuron_classes_fasciculating_here'):
        vfb_queries.get_neuron_classes_fasciculating_here = getattr(vfb_queries, '_original_get_neuron_classes_fasciculating_here')
    if hasattr(vfb_queries, '_original_get_tracts_nerves_innervating_here'):
        vfb_queries.get_tracts_nerves_innervating_here = getattr(vfb_queries, '_original_get_tracts_nerves_innervating_here')
    if hasattr(vfb_queries, '_original_get_lineage_clones_in'):
        vfb_queries.get_lineage_clones_in = getattr(vfb_queries, '_original_get_lineage_clones_in')
    if hasattr(vfb_queries, '_original_get_neuron_neuron_connectivity'):
        vfb_queries.get_neuron_neuron_connectivity = getattr(vfb_queries, '_original_get_neuron_neuron_connectivity')
    if hasattr(vfb_queries, '_original_get_neuron_region_connectivity'):
        vfb_queries.get_neuron_region_connectivity = getattr(vfb_queries, '_original_get_neuron_region_connectivity')
    if hasattr(vfb_queries, '_original_get_images_neurons'):
        vfb_queries.get_images_neurons = getattr(vfb_queries, '_original_get_images_neurons')
    if hasattr(vfb_queries, '_original_get_images_that_develop_from'):
        vfb_queries.get_images_that_develop_from = getattr(vfb_queries, '_original_get_images_that_develop_from')
    if hasattr(vfb_queries, '_original_get_expression_pattern_fragments'):
        vfb_queries.get_expression_pattern_fragments = getattr(vfb_queries, '_original_get_expression_pattern_fragments')
    if hasattr(vfb_queries, '_original_get_anatomy_scrnaseq'):
        vfb_queries.get_anatomy_scrnaseq = getattr(vfb_queries, '_original_get_anatomy_scrnaseq')
    if hasattr(vfb_queries, '_original_get_cluster_expression'):
        vfb_queries.get_cluster_expression = getattr(vfb_queries, '_original_get_cluster_expression')
    if hasattr(vfb_queries, '_original_get_expression_cluster'):
        vfb_queries.get_expression_cluster = getattr(vfb_queries, '_original_get_expression_cluster')
    if hasattr(vfb_queries, '_original_get_scrnaseq_dataset_data'):
        vfb_queries.get_scrnaseq_dataset_data = getattr(vfb_queries, '_original_get_scrnaseq_dataset_data')
    if hasattr(vfb_queries, '_original_get_similar_morphology'):
        vfb_queries.get_similar_morphology = getattr(vfb_queries, '_original_get_similar_morphology')
    if hasattr(vfb_queries, '_original_get_similar_morphology_part_of'):
        vfb_queries.get_similar_morphology_part_of = getattr(vfb_queries, '_original_get_similar_morphology_part_of')
    if hasattr(vfb_queries, '_original_get_similar_morphology_part_of_exp'):
        vfb_queries.get_similar_morphology_part_of_exp = getattr(vfb_queries, '_original_get_similar_morphology_part_of_exp')
    if hasattr(vfb_queries, '_original_get_similar_morphology_nb'):
        vfb_queries.get_similar_morphology_nb = getattr(vfb_queries, '_original_get_similar_morphology_nb')
    if hasattr(vfb_queries, '_original_get_similar_morphology_nb_exp'):
        vfb_queries.get_similar_morphology_nb_exp = getattr(vfb_queries, '_original_get_similar_morphology_nb_exp')
    if hasattr(vfb_queries, '_original_get_similar_morphology_userdata'):
        vfb_queries.get_similar_morphology_userdata = getattr(vfb_queries, '_original_get_similar_morphology_userdata')
    if hasattr(vfb_queries, '_original_get_painted_domains'):
        vfb_queries.get_painted_domains = getattr(vfb_queries, '_original_get_painted_domains')
    if hasattr(vfb_queries, '_original_get_dataset_images'):
        vfb_queries.get_dataset_images = getattr(vfb_queries, '_original_get_dataset_images')
    if hasattr(vfb_queries, '_original_get_all_aligned_images'):
        vfb_queries.get_all_aligned_images = getattr(vfb_queries, '_original_get_all_aligned_images')
    if hasattr(vfb_queries, '_original_get_aligned_datasets'):
        vfb_queries.get_aligned_datasets = getattr(vfb_queries, '_original_get_aligned_datasets')
    if hasattr(vfb_queries, '_original_get_all_datasets'):
        vfb_queries.get_all_datasets = getattr(vfb_queries, '_original_get_all_datasets')
    if hasattr(vfb_queries, '_original_get_terms_for_pub'):
        vfb_queries.get_terms_for_pub = getattr(vfb_queries, '_original_get_terms_for_pub')
    if hasattr(vfb_queries, '_original_get_transgene_expression_here'):
        vfb_queries.get_transgene_expression_here = getattr(vfb_queries, '_original_get_transgene_expression_here')
    
    print("VFBquery functions restored to original (non-cached) versions")
