# VFB Queries - Comprehensive Reference

**Last Updated**: November 4, 2025  
**Purpose**: Track all VFB queries from the XMI specification and their conversion status in VFBquery Python implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Query Information Sources](#query-information-sources)
3. [Query Matching Criteria System](#query-matching-criteria-system)
4. [All VFB Queries - Complete List](#all-vfb-queries---complete-list)
5. [Conversion Status Summary](#conversion-status-summary)
6. [Implementation Patterns](#implementation-patterns)
7. [Next Steps](#next-steps)

---

## Overview

VFB queries are defined in the XMI specification and expose various ways to query the Virtual Fly Brain knowledge base. Each query:

- Has a unique identifier (e.g., `NeuronsPartHere`, `ComponentsOf`)
- Targets specific entity types via matching criteria
- Chains through data sources: Owlery (OWL reasoning) → Neo4j → SOLR
- Returns structured results with preview capability

---

## Query Information Sources

### 1. XMI Specification
**Location**: `https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi`

**What it contains**:
- Complete query definitions (SimpleQuery, CompoundQuery, CompoundRefQuery)
- Query chains (Owlery → Neo4j → SOLR processing)
- Matching criteria (which entity types each query applies to)
- Cypher queries for Neo4j
- OWL queries for Owlery reasoning

### 2. Python Implementation
**Location**: `src/vfbquery/vfb_queries.py`

**What it contains**:
- Query schema functions (e.g., `NeuronsPartHere_to_schema()`)
- Query execution functions (e.g., `get_neurons_with_part_in()`)
- Result processing and formatting
- SOLR caching integration

### 3. Schema Documentation
**Location**: `schema.md`

**What it contains**:
- JSON schema structure for term info
- Query result format specifications
- Preview column definitions
- Example outputs

### 4. Test Suite
**Location**: `src/test/test_neurons_part_here.py` (example)

**What it contains**:
- Query functionality tests
- Expected result validation
- Preview result verification
- Performance benchmarks

---

## Query Matching Criteria System

Queries are conditionally applied based on entity type. The XMI uses a library reference system:

### Entity Type References (from XMI)
```
//@libraries.3/@types.0  = Individual (base)
//@libraries.3/@types.1  = Class (base)
//@libraries.3/@types.2  = Neuron (Individual)
//@libraries.3/@types.3  = Tract_or_nerve
//@libraries.3/@types.4  = Clone
//@libraries.3/@types.5  = Synaptic_neuropil
//@libraries.3/@types.16 = pub (Publication)
//@libraries.3/@types.20 = Template
//@libraries.3/@types.22 = Cluster
//@libraries.3/@types.23 = Synaptic_neuropil_domain
//@libraries.3/@types.24 = DataSet
//@libraries.3/@types.25 = NBLAST
//@libraries.3/@types.26 = Visual_system (Anatomy)
//@libraries.3/@types.27 = Expression_pattern
//@libraries.3/@types.28 = Nervous_system (Anatomy)
//@libraries.3/@types.30 = License
//@libraries.3/@types.36 = Term_reference
//@libraries.3/@types.37 = Intersectional_expression_pattern
//@libraries.3/@types.41 = Dataset (Individual)
//@libraries.3/@types.42 = Connected_neuron
//@libraries.3/@types.43 = Region_connectivity
//@libraries.3/@types.44 = NBLAST_exp
//@libraries.3/@types.45 = NeuronBridge
//@libraries.3/@types.46 = Expression_pattern_fragment
//@libraries.3/@types.47 = scRNAseq
//@libraries.3/@types.48 = Gene
//@libraries.3/@types.49 = User_upload (NBLAST)
//@libraries.3/@types.50 = Neuroblast
```

### Matching Criteria Examples

**NeuronsPartHere**:
```xml
<matchingCriteria type="//@libraries.3/@types.1 //@libraries.3/@types.5"/>
<matchingCriteria type="//@libraries.3/@types.1 //@libraries.3/@types.26"/>
<matchingCriteria type="//@libraries.3/@types.1 //@libraries.3/@types.23"/>
```
Applies to: Class + Synaptic_neuropil, Class + Visual_system, Class + Synaptic_neuropil_domain

---

## All VFB Queries - Complete List

### ✅ CONVERTED - Queries with Python Implementation

---

### ✅ FULLY CONVERTED - Complete Implementation

#### 1. **NeuronsPartHere** ✅
- **ID**: `NeuronsPartHere`
- **Name**: "Neuron Classes with some part in a region"
- **Description**: "Neuron classes with some part overlapping $NAME"
- **Matching Criteria**: 
  - Class + Synaptic_neuropil
  - Class + Anatomy (broader match)
- **Query Chain**: Owlery subclass query → Process → SOLR
- **OWL Query**: `'Neuron' that 'overlaps' some '{short_form}'`
- **Python Function**: `get_neurons_with_part_in()`
- **Schema Function**: `NeuronsPartHere_to_schema()`
- **Cache Key**: `'neurons_part_here'`
- **Preview**: 10 results with images (id, label, tags, thumbnail, source)
- **Status**: ✅ **FULLY IMPLEMENTED** with tests

#### 2. **NeuronsSynaptic** ✅
- **ID**: `NeuronsSynaptic`
- **Name**: "Neurons with synaptic terminals in region"
- **Description**: "Neuron classes with synaptic terminals in $NAME"
- **Matching Criteria**:
  - Class + Synaptic_neuropil
  - Class + Visual_system
  - Class + Synaptic_neuropil_domain
- **Query Chain**: Owlery subclass query → Process → SOLR
- **OWL Query**: `'Neuron' that 'has synaptic terminals in' some '{short_form}'`
- **Python Function**: `get_neurons_with_synapses_in()`
- **Schema Function**: `NeuronsSynaptic_to_schema()`
- **Cache Key**: `'neurons_synaptic'`
- **Preview**: 10 results (id, label, tags, thumbnail)
- **Status**: ✅ **FULLY IMPLEMENTED** with term_info integration

#### 3. **NeuronsPresynapticHere** ✅
- **ID**: `NeuronsPresynapticHere`
- **Name**: "Neurons with presynaptic terminals in region"
- **Description**: "Neuron classes with presynaptic terminals in $NAME"
- **Matching Criteria**:
  - Class + Synaptic_neuropil
  - Class + Visual_system
  - Class + Synaptic_neuropil_domain
- **Query Chain**: Owlery subclass query → Process → SOLR
- **OWL Query**: `'Neuron' that 'has presynaptic terminal in' some '{short_form}'`
- **Python Function**: `get_neurons_with_presynaptic_terminals_in()`
- **Schema Function**: `NeuronsPresynapticHere_to_schema()`
- **Cache Key**: `'neurons_presynaptic'`
- **Preview**: 10 results (id, label, tags, thumbnail)
- **Status**: ✅ **FULLY IMPLEMENTED** with term_info integration

#### 4. **NeuronsPostsynapticHere** ✅
- **ID**: `NeuronsPostsynapticHere`
- **Name**: "Neurons with postsynaptic terminals in region"
- **Description**: "Neuron classes with postsynaptic terminals in $NAME"
- **Matching Criteria**:
  - Class + Synaptic_neuropil
  - Class + Visual_system
  - Class + Synaptic_neuropil_domain
- **Query Chain**: Owlery subclass query → Process → SOLR
- **OWL Query**: `'Neuron' that 'has postsynaptic terminal in' some '{short_form}'`
- **Python Function**: `get_neurons_with_postsynaptic_terminals_in()`
- **Schema Function**: `NeuronsPostsynapticHere_to_schema()`
- **Cache Key**: `'neurons_postsynaptic'`
- **Preview**: 10 results (id, label, tags, thumbnail)
- **Status**: ✅ **FULLY IMPLEMENTED** with term_info integration

#### 5. **ComponentsOf** ✅
- **ID**: `ComponentsOf`
- **Name**: "Components of"
- **Description**: "Components of $NAME"
- **Matching Criteria**: Class + Clone
- **Query Chain**: Owlery Part of → Process → SOLR
- **OWL Query**: `'part of' some '{short_form}'`
- **Python Function**: `get_components_of()`
- **Schema Function**: `ComponentsOf_to_schema()`
- **Cache Key**: `'components_of'`
- **Preview**: 10 results (id, label, tags, thumbnail)
- **Status**: ✅ **FULLY IMPLEMENTED** with term_info integration

#### 6. **PartsOf** ✅
- **ID**: `PartsOf`
- **Name**: "Parts of"
- **Description**: "Parts of $NAME"
- **Matching Criteria**: Class (any)
- **Query Chain**: Owlery Part of → Process → SOLR
- **OWL Query**: `'part of' some '{short_form}'`
- **Python Function**: `get_parts_of()`
- **Schema Function**: `PartsOf_to_schema()`
- **Cache Key**: `'parts_of'`
- **Preview**: 10 results (id, label, tags, thumbnail)
- **Status**: ✅ **FULLY IMPLEMENTED** with term_info integration

#### 7. **SubclassesOf** ✅
- **ID**: `SubclassesOf`
- **Name**: "Subclasses of"
- **Description**: "Subclasses of $NAME"
- **Matching Criteria**: Class (any)
- **Query Chain**: Owlery subclasses query → Process → SOLR
- **OWL Query**: `'{short_form}'` (direct class query)
- **Python Function**: `get_subclasses_of()`
- **Schema Function**: `SubclassesOf_to_schema()`
- **Cache Key**: `'subclasses_of'`
- **Preview**: 10 results (id, label, tags, thumbnail)
- **Status**: ✅ **FULLY IMPLEMENTED** with term_info integration

#### 8. **ListAllAvailableImages** ✅
- **ID**: `ListAllAvailableImages`
- **Name**: "List all available images for class with examples"
- **Description**: "List all available images of $NAME"
- **Matching Criteria**: Class + Anatomy
- **Query Chain**: Neo4j → Process Images → SOLR
- **Python Function**: `get_instances()`
- **Schema Function**: `ListAllAvailableImages_to_schema()`
- **Preview**: 5 results (id, label, tags, thumbnail)
- **Status**: ✅ **FULLY IMPLEMENTED**

#### 9. **SimilarMorphologyTo** ✅ (Partial)
- **ID**: `SimilarMorphologyTo` / `has_similar_morphology_to`
- **Name**: "NBLAST similarity neo Query"
- **Description**: "Neurons with similar morphology to $NAME [NBLAST mean score]"
- **Matching Criteria**: Individual + Neuron + NBLAST
- **Query Chain**: Neo4j NBLAST query → Process
- **Python Function**: `get_similar_neurons()` (exists but may need enhancement)
- **Schema Function**: `SimilarMorphologyTo_to_schema()`
- **Preview**: 5 results (id, score, name, tags, thumbnail)
- **Status**: ✅ **IMPLEMENTED** (may need preview enhancement)

#### 10. **NeuronInputsTo** ✅ (Partial)
- **ID**: `NeuronInputsTo`
- **Name**: "Neuron inputs query"
- **Description**: "Find neurons with synapses into $NAME"
- **Matching Criteria**: Individual + Neuron
- **Python Function**: `get_individual_neuron_inputs()`
- **Schema Function**: `NeuronInputsTo_to_schema()`
- **Preview**: -1 (all results, ribbon format)
- **Preview Columns**: Neurotransmitter, Weight
- **Status**: ✅ **IMPLEMENTED** (ribbon format)

---

### ❌ NOT CONVERTED - XMI Only

#### 11. **ExpressionOverlapsHere** ❌
- **ID**: `ExpressionOverlapsHere`
- **Name**: "Expression overlapping what anatomy"
- **Description**: "Anatomy $NAME is expressed in"
- **Matching Criteria**: 
  - Class + Expression_pattern
  - Class + Expression_pattern_fragment
- **Query Chain**: Neo4j ep_2_anat query → Process
- **Cypher Query**: Complex pattern matching for expression patterns
- **Status**: ❌ **NOT IMPLEMENTED**

#### 8. **TransgeneExpressionHere** ❌
- **ID**: `TransgeneExpressionHere`
- **Name**: "Expression overlapping selected anatomy"
- **Description**: "Reports of transgene expression in $NAME"
- **Matching Criteria**:
  - Class + Nervous_system + Anatomy
  - Class + Nervous_system + Neuron
- **Query Chain**: Multi-step Owlery and Neo4j queries
- **Status**: ❌ **NOT IMPLEMENTED**

#### 9. **NeuronClassesFasciculatingHere** ❌
- **ID**: `NeuronClassesFasciculatingHere` / `AberNeuronClassesFasciculatingHere`
- **Name**: "Neuron classes fasciculating here"
- **Description**: "Neurons fasciculating in $NAME"
- **Matching Criteria**: Class + Tract_or_nerve
- **Query Chain**: Owlery → Process → SOLR
- **OWL Query**: `object=<FBbt_00005106> and <RO_0002101> some <$ID>`
- **Status**: ❌ **NOT IMPLEMENTED**

#### 10. **ImagesNeurons** ❌
- **ID**: `ImagesNeurons`
- **Name**: "Images of neurons with some part here"
- **Description**: "Images of neurons with some part in $NAME"
- **Matching Criteria**:
  - Class + Synaptic_neuropil
  - Class + Synaptic_neuropil_domain
- **Query Chain**: Owlery instances → Process → SOLR
- **OWL Query**: `object=<FBbt_00005106> and <RO_0002131> some <$ID>` (instances, not classes)
- **Status**: ❌ **NOT IMPLEMENTED**

#### 12. **PaintedDomains** ❌
- **ID**: `PaintedDomains` / `domainsForTempId`
- **Name**: "Show all painted domains for template"
- **Description**: "List all painted anatomy available for $NAME"
- **Matching Criteria**: Template + Individual
- **Query Chain**: Neo4j domains query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 15. **DatasetImages** ❌
- **ID**: `DatasetImages` / `imagesForDataSet`
- **Name**: "Show all images for a dataset"
- **Description**: "List all images included in $NAME"
- **Matching Criteria**: DataSet + Individual
- **Query Chain**: Neo4j → Process → SOLR
- **Status**: ❌ **NOT IMPLEMENTED**

#### 16. **TractsNervesInnervatingHere** ❌
- **ID**: `TractsNervesInnervatingHere` / `innervatesX`
- **Name**: "Tracts/nerves innervating synaptic neuropil"
- **Description**: "Tracts/nerves innervating $NAME"
- **Matching Criteria**: 
  - Class + Synaptic_neuropil
  - Class + Synaptic_neuropil_domain
- **Query Chain**: Owlery → Process → SOLR
- **OWL Query**: `object=<FBbt_00005099> and <RO_0002134> some <$ID>`
- **Status**: ❌ **NOT IMPLEMENTED**

#### 17. **LineageClonesIn** ❌
- **ID**: `LineageClonesIn` / `lineageClones`
- **Name**: "Lineage clones found here"
- **Description**: "Lineage clones found in $NAME"
- **Matching Criteria**:
  - Class + Synaptic_neuropil
  - Class + Synaptic_neuropil_domain
- **Query Chain**: Owlery → Process → SOLR
- **OWL Query**: `object=<FBbt_00007683> and <RO_0002131> some <$ID>`
- **Status**: ❌ **NOT IMPLEMENTED**

#### 18. **AllAlignedImages** ❌
- **ID**: `AllAlignedImages` / `imagesForTempQuery`
- **Name**: "Show all images aligned to template"
- **Description**: "List all images aligned to $NAME"
- **Matching Criteria**: Template + Individual
- **Query Chain**: Neo4j → Neo4j Pass → SOLR
- **Status**: ❌ **NOT IMPLEMENTED**

#### 19. **AlignedDatasets** ❌
- **ID**: `AlignedDatasets` / `template_2_datasets_ids`
- **Name**: "Show all datasets aligned to template"
- **Description**: "List all datasets aligned to $NAME"
- **Matching Criteria**: Template + Individual
- **Query Chain**: Neo4j → Neo4j Pass → SOLR → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 21. **AllDatasets** ❌
- **ID**: `AllDatasets` / `all_datasets_ids`
- **Name**: "Show all datasets"
- **Description**: "List all datasets"
- **Matching Criteria**: Template
- **Query Chain**: Neo4j → Neo4j Pass → SOLR → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 22. **neuron_region_connectivity_query** ❌
- **ID**: `ref_neuron_region_connectivity_query` / `compound_neuron_region_connectivity_query`
- **Name**: "Show connectivity to regions from Neuron X"
- **Description**: "Show connectivity per region for $NAME"
- **Matching Criteria**: Region_connectivity
- **Query Chain**: Neo4j compound query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 23. **neuron_neuron_connectivity_query** ❌
- **ID**: `ref_neuron_neuron_connectivity_query` / `compound_neuron_neuron_connectivity_query`
- **Name**: "Show connectivity to neurons from Neuron X"
- **Description**: "Show neurons connected to $NAME"
- **Matching Criteria**: Connected_neuron
- **Query Chain**: Neo4j compound query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 24. **SimilarMorphologyToPartOf** ❌
- **ID**: `SimilarMorphologyToPartOf` / `has_similar_morphology_to_part_of`
- **Name**: "NBLASTexp similarity neo Query"
- **Description**: "Expression patterns with some similar morphology to $NAME [NBLAST mean score]"
- **Matching Criteria**: Individual + Neuron + NBLAST_exp
- **Query Chain**: Neo4j NBLAST exp query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 25. **TermsForPub** ❌
- **ID**: `TermsForPub` / `neoTermIdsRefPub`
- **Name**: "has_reference_to_pub"
- **Description**: "List all terms that reference $NAME"
- **Matching Criteria**: Individual + Publication
- **Query Chain**: Neo4j → Neo4j Pass → SOLR
- **Status**: ❌ **NOT IMPLEMENTED**

#### 26. **SimilarMorphologyToPartOfexp** ❌
- **ID**: `SimilarMorphologyToPartOfexp`
- **Name**: "has_similar_morphology_to_part_of_exp"
- **Description**: "Neurons with similar morphology to part of $NAME [NBLAST mean score]"
- **Matching Criteria**: 
  - Individual + Expression_pattern + NBLAST_exp
  - Individual + Expression_pattern_fragment + NBLAST_exp
- **Query Chain**: Neo4j NBLAST exp query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 27. **SimilarMorphologyToNB** ❌
- **ID**: `SimilarMorphologyToNB` / `has_similar_morphology_to_nb`
- **Name**: "NeuronBridge similarity neo Query"
- **Description**: "Neurons that overlap with $NAME [NeuronBridge]"
- **Matching Criteria**: NeuronBridge + Individual + Expression_pattern
- **Query Chain**: Neo4j NeuronBridge query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 28. **SimilarMorphologyToNBexp** ❌
- **ID**: `SimilarMorphologyToNBexp` / `has_similar_morphology_to_nb_exp`
- **Name**: "NeuronBridge similarity neo Query (expression)"
- **Description**: "Expression patterns that overlap with $NAME [NeuronBridge]"
- **Matching Criteria**: NeuronBridge + Individual + Neuron
- **Query Chain**: Neo4j NeuronBridge query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 29. **anatScRNAseqQuery** ❌
- **ID**: `anatScRNAseqQuery` / `anat_scRNAseq_query_compound`
- **Name**: "anat_scRNAseq_query"
- **Description**: "Single cell transcriptomics data for $NAME"
- **Matching Criteria**: Class + Nervous_system + scRNAseq
- **Query Chain**: Owlery → Owlery Pass → Neo4j scRNAseq query
- **Status**: ❌ **NOT IMPLEMENTED**

#### 30. **clusterExpression** ❌
- **ID**: `clusterExpression` / `cluster_expression_query_compound`
- **Name**: "cluster_expression"
- **Description**: "Genes expressed in $NAME"
- **Matching Criteria**: Individual + Cluster
- **Query Chain**: Neo4j cluster expression query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 31. **scRNAdatasetData** ❌
- **ID**: `scRNAdatasetData` / `dataset_scRNAseq_query_compound`
- **Name**: "Show all Clusters for a scRNAseq dataset"
- **Description**: "List all Clusters for $NAME"
- **Matching Criteria**: DataSet + scRNAseq
- **Query Chain**: Neo4j dataset scRNAseq query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 32. **expressionCluster** ❌
- **ID**: `expressionCluster` / `expression_cluster_query_compound`
- **Name**: "expression_cluster"
- **Description**: "scRNAseq clusters expressing $NAME"
- **Matching Criteria**: Class + Gene + scRNAseq
- **Query Chain**: Neo4j expression cluster query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 33. **SimilarMorphologyToUserData** ❌
- **ID**: `SimilarMorphologyToUserData` / `has_similar_morphology_to_userdata`
- **Name**: "User data NBLAST similarity"
- **Description**: "Neurons with similar morphology to your upload $NAME [NBLAST mean score]"
- **Matching Criteria**: User_upload + Individual
- **Query Chain**: SOLR cached user NBLAST query → Process
- **Status**: ❌ **NOT IMPLEMENTED**

#### 34. **ImagesThatDevelopFrom** ❌
- **ID**: `ImagesThatDevelopFrom` / `imagesDevelopsFromNeuroblast`
- **Name**: "Show all images that develops_from X"
- **Description**: "List images of neurons that develop from $NAME"
- **Matching Criteria**: Class + Neuroblast
- **Query Chain**: Owlery instances → Owlery Pass → SOLR
- **OWL Query**: `object=<FBbt_00005106> and <RO_0002202> some <$ID>`
- **Status**: ❌ **NOT IMPLEMENTED**

#### 35. **epFrag** ❌
- **ID**: `epFrag`
- **Name**: "Images of expression pattern fragments"
- **Description**: "Images of fragments of $NAME"
- **Matching Criteria**: Class + Expression_pattern
- **Query Chain**: Owlery individual parts → Process → SOLR
- **OWL Query**: `object=<BFO_0000050> some <$ID>` (instances)
- **Status**: ❌ **NOT IMPLEMENTED**

---

## Conversion Status Summary

### Statistics
- **Total VFB Queries**: 35
- **✅ Fully Implemented**: 10 (29%)
- **🔶 Partially Implemented**: 2 (6%)
- **❌ Not Implemented**: 23 (66%)

### Recently Implemented (This Session)
- ✅ **NeuronsSynaptic** - neurons with synaptic terminals in region
- ✅ **NeuronsPresynapticHere** - neurons with presynaptic terminals in region
- ✅ **NeuronsPostsynapticHere** - neurons with postsynaptic terminals in region
- ✅ **ComponentsOf** - components of anatomical structures
- ✅ **PartsOf** - parts of anatomical structures
- ✅ **SubclassesOf** - subclasses of a class

### Implementation Priority Categories

#### High Priority (Common Use Cases)
1. ✅ **NeuronsSynaptic** - synaptic terminal queries are very common (COMPLETED)
2. ✅ **NeuronsPresynapticHere** - presynaptic connectivity is essential (COMPLETED)
3. ✅ **NeuronsPostsynapticHere** - postsynaptic connectivity is essential (COMPLETED)
4. ❌ **ExpressionOverlapsHere** - expression pattern queries are frequent
5. ✅ **ComponentsOf** - anatomical hierarchy navigation (COMPLETED)
6. ✅ **PartsOf** - anatomical hierarchy navigation (COMPLETED)

#### Medium Priority (Specialized Queries)
7. ❌ **neuron_region_connectivity_query** - connectivity analysis
8. ❌ **neuron_neuron_connectivity_query** - circuit analysis
9. ✅ **SubclassesOf** - ontology navigation (COMPLETED)
10. ❌ **anatScRNAseqQuery** - transcriptomics integration
11. ❌ **clusterExpression** - gene expression analysis

#### Lower Priority (Advanced/Specialized)
- NeuronBridge queries (27, 28)
- User data NBLAST (33)
- Dataset-specific queries (14, 15, 20, 21, 31)
- Template-specific queries (14, 19, 20)
- Lineage queries (17, 34)

---

## Implementation Patterns

### Pattern 1: Owlery-Based Class Queries (Most Common)

**Example**: NeuronsPartHere (✅ implemented)

```python
def get_neurons_with_part_in(short_form: str, limit: int = None):
    """
    Query neurons that have some part overlapping with anatomical region.
    
    Steps:
    1. Owlery subclass query (OWL reasoning)
    2. Process IDs
    3. SOLR lookup for full details
    """
    # 1. Owlery query
    owlery_url = f"http://owl.virtualflybrain.org/kbs/vfb/subclasses"
    owl_query = f"object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/{short_form}>"
    
    # 2. Get class IDs from Owlery
    class_ids = owlery_request(owlery_url, owl_query)
    
    # 3. Lookup in SOLR
    results = solr_lookup(class_ids, limit=limit)
    
    return results
```

**Applies to**: NeuronsSynaptic, NeuronsPresynapticHere, NeuronsPostsynapticHere, ComponentsOf, PartsOf, SubclassesOf

### Pattern 2: Neo4j Complex Queries

**Example**: ExpressionOverlapsHere (❌ not implemented)

```python
def get_expression_overlaps(short_form: str):
    """
    Query expression patterns overlapping anatomy.
    
    Uses Neo4j Cypher query with complex pattern matching:
    - Match expression patterns
    - Follow relationships through anonymous individuals
    - Collect publication references
    - Retrieve example images
    """
    # Neo4j Cypher query (from XMI)
    cypher = """
    MATCH (ep:Expression_pattern:Class)<-[ar:overlaps|part_of]-(anoni:Individual)-[:INSTANCEOF]->(anat:Class)
    WHERE ep.short_form in [$id]
    WITH anoni, anat, ar
    OPTIONAL MATCH (p:pub {short_form: []+ar.pub[0]})
    ...
    """
    
    # Execute and process results
    results = neo4j_query(cypher, id=short_form)
    return process_results(results)
```

**Applies to**: ExpressionOverlapsHere, TransgeneExpressionHere, neuron_region_connectivity_query, neuron_neuron_connectivity_query

### Pattern 3: Owlery Instance Queries

**Example**: ImagesNeurons (❌ not implemented)

```python
def get_neuron_images_in(short_form: str):
    """
    Get individual neuron instances (not classes) with part in region.
    
    Uses Owlery instances endpoint instead of subclasses.
    """
    # Owlery instances query
    owlery_url = f"http://owl.virtualflybrain.org/kbs/vfb/instances"
    owl_query = f"object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/{short_form}>"
    
    # Rest is similar to Pattern 1
    ...
```

**Applies to**: ImagesNeurons, epFrag, ImagesThatDevelopFrom

### Pattern 4: SOLR Cached Queries

**Example**: anatScRNAseqQuery, clusterExpression (❌ not implemented)

```python
def get_cluster_expression(short_form: str):
    """
    Retrieve cached scRNAseq cluster data from SOLR.
    
    Uses pre-cached Neo4j query results stored in SOLR.
    """
    # Query SOLR for cached field
    results = vfb_solr.search(f'id:{short_form}', fl='cluster_expression_query')
    
    # Process cached JSON
    return process_cached_query(results.docs[0]['cluster_expression_query'])
```

**Applies to**: anatScRNAseqQuery, clusterExpression, scRNAdatasetData, expressionCluster, SimilarMorphologyToUserData

---

## Next Steps

### Immediate Next Query: **NeuronsSynaptic**

**Why this one?**
1. High-value query for neuroscience research
2. Uses same Pattern 1 (Owlery-based) as NeuronsPartHere ✅
3. We have a working template from NeuronsPartHere
4. Clear matching criteria and well-defined OWL query
5. Moderate complexity - good learning progression

**Implementation checklist**:
- [ ] Create `NeuronsSynaptic_to_schema()` function
- [ ] Create `get_neurons_with_synapses_in()` function
- [ ] Add query matching logic in `get_term_info()`
- [ ] Create comprehensive test suite
- [ ] Update documentation

### Recommended Query Order

**Phase 1: Owlery Pattern Queries** (Easiest, similar to NeuronsPartHere)
1. ✅ NeuronsPartHere (DONE)
2. **NeuronsSynaptic** (NEXT)
3. NeuronsPresynapticHere
4. NeuronsPostsynapticHere
5. ComponentsOf
6. PartsOf
7. SubclassesOf

**Phase 2: Neo4j Pattern Queries** (Medium difficulty)
8. ExpressionOverlapsHere
9. TransgeneExpressionHere
10. neuron_region_connectivity_query
11. neuron_neuron_connectivity_query

**Phase 3: Instance & Specialized Queries** (More complex)
12. ImagesNeurons
13. anatScRNAseqQuery
14. clusterExpression
15. ... (others as needed)

---

## Implementation Template

Use this template for each new query:

```python
# 1. Schema function
def QueryName_to_schema(name, take_default):
    """
    Schema for QueryName.
    [Description of what the query does]
    
    Matching criteria from XMI:
    - [List matching criteria]
    
    Query chain: [Describe data source chain]
    OWL/Cypher query: [Quote the actual query]
    """
    query = "QueryName"
    label = f"[Human readable description with {name}]"
    function = "function_name"
    takes = {
        "short_form": {"$and": ["Type1", "Type2"]},
        "default": take_default,
    }
    preview = 10  # or -1 for all
    preview_columns = ["id", "label", ...]  # columns to show
    
    return Query(query=query, label=label, function=function, 
                 takes=takes, preview=preview, preview_columns=preview_columns)

# 2. Execution function
@with_solr_cache('query_name')
def function_name(short_form: str, limit: int = None):
    """
    Execute the QueryName query.
    
    :param short_form: Term ID to query
    :param limit: Optional result limit
    :return: Query results as DataFrame or dict
    """
    # Implementation here
    pass

# 3. Add to term_info matching logic
# In get_term_info(), add conditional:
if is_type(vfbTerm, ["Type1", "Type2"]):
    q = QueryName_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
    termInfo["Queries"].append(q)

# 4. Create test file
# src/test/test_query_name.py with comprehensive tests
```

---

## Resources

- **XMI Spec**: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
- **Owlery API**: http://owl.virtualflybrain.org/kbs/vfb/
- **SOLR API**: https://solr.virtualflybrain.org/solr/vfb_json/select
- **Neo4j**: http://pdb.v4.virtualflybrain.org/db/neo4j/tx
- **VFB Ontology**: http://purl.obolibrary.org/obo/fbbt.owl

---

**Last Reviewed**: November 4, 2025  
**Maintainer**: VFBquery Development Team
