# VFB JSON Schema Documentation

This document describes the JSON schema structure for the Virtual Fly Brain (VFB) term information API.

## Table of Contents

- [Core Schema](#core-schema)
  - [Query previews and the -1 count](#query-previews-and-the--1-count)
- [Entity Types](#entity-types)
  - [Individual](#individual)
  - [Class](#class)
  - [Template](#template)
- [Common Objects](#common-objects)
  - [Coordinates](#coordinates)
  - [MinimalEntityInfo](#minimalentityinfo)
  - [MinimalEdgeInfo](#minimaledgeinfo)
  - [Pub](#pub)
  - [License](#license)
  - [Xref](#xref)
- [Query Types](#query-types)
- [Examples](#examples)

## Core Schema

The base schema returned by term info queries:

```json
{
  "Name": "String (term name)",
  "Id": "String (term ID/short form)",
  "SuperTypes": ["String (class hierarchies)"],
  "Meta": {
    "Name": "String (markdown link)",
    "Description": "String (description)",
    "Comment": "String (additional information)",
    "Types": "String (class information)",
    "Relationships": "String (relationships)",
    "Cross References": "String (external links)",
    "Synonyms": "String (alternative names)"
  },
  "Tags": ["String (tag names)"],
  "Technique": ["String (imaging techniques, Individual only)"],
  "Queries": [
    {
      "query": "String (query identifier)",
      "label": "String (human-readable query name)",
      "function": "String (backend function name)",
      "takes": {
        "short_form": {"$and": ["String (required type constraints)"]},
        "default": {"parameter_key": "parameter_value"}
      },
      "preview": "Integer (number of preview results, -1 for all)",
      "preview_columns": ["String (column identifiers)"],
      "preview_results": {
        "status": "String (pending|complete; optional — absent means complete)",
        "message": "String (present with status; explains a pending or uncounted preview)",
        "headers": {
          "column_id": {
            "title": "String (display name)",
            "type": "String (data type)",
            "order": "Integer (display order)",
            "sort": {"Integer (priority)": "String (direction)"}
          }
        },
        "rows": [
          {
            "id": "String (entity ID)",
            "column_name": "Value (column data)",
            // Additional columns...
          }
        ]
      },
      "output_format": "String (table/ribbon)",
      "count": "Integer (total result count; -1 = not counted, distinct from 0)"
    }
  ],
  "IsIndividual": "Boolean",
  "IsClass": "Boolean",
  "IsTemplate": "Boolean",
  "Publications": [
    {
      "title": "String (publication title)",
      "short_form": "String (publication ID)",
      "microref": "String (short citation)",
      "refs": ["String (URL to external reference)"]
    }
  ]
}
```

### Query previews and the -1 count

Each entry in `Queries` describes a query the caller can run against the term, and carries a small
preview of that query's results so a client can show something useful without running anything. A
preview is expensive, so it is not always available when the term itself is, and the schema has to be
able to say so.

`count` is that signal. A count of `0` means the query was run and matched nothing. A count of `-1`
means the query has **not been counted**, which is a different statement entirely: it says nothing
about whether results exist, only that finding out requires running the query. Treating `-1` as "no
results" is the single most common misreading of this schema. (Note the unrelated `-1` on the
`preview` field just above it, which means "preview every result" — the two are not related.)

A preview can be uncounted for four reasons. It has not been computed yet, because this was the first
request for the term and the full previews are being computed in the background; it timed out inside
its share of the response budget; it failed; or — the one case where `-1` does *not* mean unknown —
the rows are complete but the exact total exceeded the counting cap, so `-1` here means "many".

`preview_results.status` distinguishes those. It is `pending` when the rows are not the answer and
`complete` when they are, and `preview_results.message` accompanies it with a sentence saying which
case this is and what to do about it. Both keys are optional, and **absence means complete**: results
cached before these keys existed carry neither, and remain valid. So the rule for a consumer is:
trust `status` when it is present, and fall back to `count >= 0` when it is not.

A `pending` preview is transient, not an error. Requesting the same term again shortly will usually
return it filled in, since the first request schedules the computation; passing `force_refresh=true`
(or the `X-Force-Refresh: true` header, from a whitelisted caller) computes it synchronously instead.

## Entity Types

VFB entities fall into three main types, each with specific fields beyond the core schema:

### Individual

Individual instances (neurons, expression patterns, anatomical instances):

```json
"Technique": ["String (imaging techniques used)"],
"Images": {
  "template_id": [
    {
      "id": "String (image ID)",
      "label": "String (image label)",
      "thumbnail": "String (URL to thumbnail)",
      "thumbnail_transparent": "String (URL to transparent thumbnail)",
      "nrrd": "String (URL to NRRD volume)",
      "wlz": "String (URL to Woolz volume)",
      "obj": "String (URL to OBJ model)",
      "swc": "String (URL to SWC file)",
      "index": "Integer (sorting order)",
      "center": {"X": "Float", "Y": "Float", "Z": "Float"},
      "extent": {"X": "Float", "Y": "Float", "Z": "Float"},
      "voxel": {"X": "Float", "Y": "Float", "Z": "Float"},
      "orientation": "String (orientation code)",
      "type_label": "String (anatomical type)",
      "type_id": "String (anatomical type ID)"
    }
  ]
},
"Publications": [
  {
    "title": "String (publication title)",
    "short_form": "String (publication ID)",
    "microref": "String (short citation)",
    "refs": ["String (URL to external reference)"]
  }
],
"Licenses": {
  "index": {
    "iri": "String (license IRI)",
    "short_form": "String (license ID)",
    "label": "String (license name)",
    "icon": "String (URL to license icon)",
    "source": "String (dataset source)",
    "source_iri": "String (dataset source IRI)"
  }
}
```

### Class

Ontology classes (anatomical structures, neuron types):

```json
"Examples": {
  "template_id": [
    {
      // Same structure as Images objects
    }
  ]
},
"Publications": [
  {
    "title": "String (publication title)",
    "short_form": "String (publication ID)",
    "microref": "String (short citation)",
    "refs": ["String (URL to external reference)"]
  }
],
"Synonyms": [
  {
    "label": "String (synonym text)",
    "scope": "String (synonym scope)",
    "type": "String (synonym type)",
    "publication": "String (publication reference)"
  }
]
```

### Template

Template brains and reference images:

```json
"Images": {
  "template_id": [
    {
      // Same structure as individual images
    }
  ]
},
"Domains": {
  "index": {
    "id": "String (domain ID)",
    "label": "String (domain label)",
    "thumbnail": "String (URL to thumbnail)",
    "thumbnail_transparent": "String (URL to transparent thumbnail)",
    "index": "Integer (sorting order)",
    "center": {"X": "Float", "Y": "Float", "Z": "Float"} | null,
    "type_label": "String (anatomical type)",
    "type_id": "String (anatomical type ID)"
  }
},
"Licenses": {
  "index": {
    "iri": "String (license IRI)",
    "short_form": "String (license ID)",
    "label": "String (license name)",
    "icon": "String (URL to license icon)",
    "source": "String (dataset source)",
    "source_iri": "String (dataset source IRI)"
  }
}
```

## Common Objects

These objects appear in multiple places throughout the schema:

### Coordinates

Represents 3D coordinates in space:

```json
{
  "X": "Float",
  "Y": "Float",
  "Z": "Float"
}
```

### MinimalEntityInfo

Basic information about any entity:

```json
{
  "short_form": "String (entity ID)",
  "iri": "String (full IRI)",
  "label": "String (display name)",
  "types": ["String (entity types)"],
  "unique_facets": ["String (special classifications)"],
  "symbol": "String (alternate identifier)"
}
```

### MinimalEdgeInfo

Basic information about relationships:

```json
{
  "short_form": "String (relation ID)",
  "iri": "String (full IRI)",
  "label": "String (relation name)",
  "type": "String (relation type)"
}
```

### Pub

Publication information:

```json
{
  "core": {
    // MinimalEntityInfo
  },
  "microref": "String (short citation)",
  "PubMed": "String (PubMed ID)",
  "FlyBase": "String (FlyBase ID)",
  "DOI": "String (DOI)",
  "ISBN": "String (ISBN)"
}
```

### License

License information:

```json
{
  "core": {
    // MinimalEntityInfo
  },
  "link": "String (URL to license)",
  "icon": "String (URL to license icon)",
  "is_bespoke": "String (custom license flag)"
}
```

### Xref

Cross-reference to external resources:

```json
{
  "site": {
    // MinimalEntityInfo
  },
  "homepage": "String (site homepage)",
  "link_base": "String (base URL for links)",
  "link_postfix": "String (URL suffix)",
  "accession": "String (ID in external system)",
  "link_text": "String (display text)",
  "icon": "String (URL to site icon)"
}
```

## Query Types

The system supports several query types:

### ListAllAvailableImages

Returns all available images for a term.

```json
{
  "query": "ListAllAvailableImages",
  "label": "List all images for [term]",
  "function": "get_images",
  "takes": {
    "short_form": {"$and": ["has_image"]},
    "default": {"term": "TERM_ID"}
  }
}
```

### SimilarMorphologyTo

Finds neurons with similar morphology.

```json
{
  "query": "SimilarMorphologyTo",
  "label": "Find similar neurons to [neuron]",
  "function": "get_similar_neurons",
  "takes": {
    "short_form": {"$and": ["Individual", "Neuron"]},
    "default": {
      "neuron": "NEURON_ID",
      "similarity_score": "NBLAST_score"
    }
  }
}
```

### NeuronInputsTo

Finds neurons with synapses into the target.

```json
{
  "query": "NeuronInputsTo",
  "label": "Find neurons with inputs to [neuron]",
  "function": "get_individual_neuron_inputs",
  "takes": {
    "short_form": {"$and": ["Individual", "Neuron"]},
    "default": {
      "neuron_short_form": "NEURON_ID",
      "summary_mode": true
    }
  }
}
```

### ClassifiedAs

Finds instances classified as a specific type.

```json
{
  "query": "ClassifiedAs",
  "label": "Find instances of [class]",
  "function": "get_instances",
  "takes": {
    "short_form": {"$and": ["Class"]},
    "default": {"short_form": "CLASS_ID"}
  }
}
```

### RelatedIndividuals

Finds individuals related to a template.

```json
{
  "query": "RelatedIndividuals",
  "label": "Find instances in [template]",
  "function": "get_related_anatomy",
  "takes": {
    "short_form": {"$and": ["Template"]},
    "default": {"template_short_form": "TEMPLATE_ID"}
  }
}
```

## Examples

### Neuron Example

```json
{
  "Name": "fru-M-200266",
  "Id": "VFB_00000001",
  "SuperTypes": [
    "Entity", "Adult", "Anatomy", "Cell", "Expression_pattern_fragment",
    "Individual", "Nervous_system", "Neuron", "VFB", "has_image",
    "FlyCircuit", "NBLAST"
  ],
  "Meta": {
    "Name": "[fru-M-200266](VFB_00000001)",
    "Comment": "OutAge: Adult 5~15 days",
    "Types": "[adult DM6 lineage neuron](FBbt_00050144); [expression pattern fragment](VFBext_0000004)",
    "Relationships": "[expresses](RO_0002292): [Scer\\GAL4[fru.P1.D]](FBal0276838); [is part of](BFO_0000050): [Scer\\GAL4[fru.P1.D] expression pattern](VFBexp_FBal0276838), [adult brain](FBbt_00003624), [male organism](FBbt_00007004)",
    "Cross References": "[FlyCircuit 1.0](http://flycircuit.tw): [fru-M-200266](http://flycircuit.tw/modules.php?name=clearpage&op=detail_table&neuron=fru-M-200266)"
  },
  "Tags": ["Adult", "Expression_pattern_fragment", "Nervous_system", "Neuron"],
  "Queries": [
    {
      "query": "SimilarMorphologyTo",
      "label": "Find similar neurons to fru-M-200266",
      "function": "get_similar_neurons",
      "takes": {
        "short_form": {"$and": ["Individual", "Neuron"]},
        "default": {
          "neuron": "VFB_00000001",
          "similarity_score": "NBLAST_score"
        }
      },
      "preview": 5,
      "preview_columns": ["id", "score", "name", "tags", "thumbnail"],
      "preview_results": {
        "status": "complete",
        "headers": {
          "id": {"title": "Add", "type": "selection_id", "order": -1},
          "score": {"title": "Score", "type": "numeric", "order": 1, "sort": {"0": "Desc"}},
          "name": {"title": "Name", "type": "markdown", "order": 1, "sort": {"1": "Asc"}},
          "tags": {"title": "Tags", "type": "tags", "order": 2},
          "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
        },
        "rows": []
      },
      "output_format": "table",
      "count": 60
    }
  ],
  "IsIndividual": true,
  "Images": {
    "VFB_00017894": [
      {
        "id": "VFB_00000001",
        "label": "fru-M-200266",
        "thumbnail": "https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png",
        "thumbnail_transparent": "https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png",
        "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/volume.nrrd",
        "wlz": "https://virtualflybrain.org/reports/VFB_00000001/volume.wlz",
        "obj": "https://virtualflybrain.org/reports/VFB_00000001/volume.obj",
        "swc": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/volume.swc"
      }
    ]
  },
  "IsClass": false,
  "IsTemplate": false,
  "Licenses": {
    "0": {
      "iri": "http://virtualflybrain.org/reports/VFBlicense_FlyCircuit_License",
      "short_form": "VFBlicense_FlyCircuit_License",
      "label": "FlyCircuit License",
      "icon": "",
      "source": "FlyCircuit 1.0 - single neurons (Chiang2010)",
      "source_iri": "http://virtualflybrain.org/reports/Chiang2010"
    }
  }
}
```

### Template Example

```json
{
  "Name": "JRC2018Unisex",
  "Id": "VFB_00101567",
  "SuperTypes": [
    "Entity", "Adult", "Anatomy", "Individual",
    "Nervous_system", "Template", "has_image"
  ],
  "Meta": {
    "Name": "[JRC2018Unisex](VFB_00101567)",
    "Description": "Janelia 2018 unisex, averaged adult brain template",
    "Types": "[adult brain](FBbt_00003624)"
  },
  "Tags": ["Adult", "Nervous_system"],
  "Queries": [],
  "IsIndividual": true,
  "Images": {
    "VFBc_00101567": [{
      "id": "VFBc_00101567",
      "label": "JRC2018Unisex_c",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj",
      "index": 0,
      "center": {"X": 605.0, "Y": 283.0, "Z": 87.0},
      "extent": {"X": 1211.0, "Y": 567.0, "Z": 175.0},
      "voxel": {"X": 0.5189161, "Y": 0.5189161, "Z": 1.0},
      "orientation": "LPS"
    }]
  },
  "IsClass": false,
  "IsTemplate": true,
  "Domains": {
    "0": {
      "id": "VFB_00101567",
      "label": "JRC2018Unisex",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
      "index": 0,
      "type_label": "adult brain",
      "type_id": "FBbt_00003624"
    }
  },
  "Licenses": {
    "0": {
      "iri": "http://virtualflybrain.org/reports/VFBlicense_CC_BY_NC_SA_4_0",
      "short_form": "VFBlicense_CC_BY_NC_SA_4_0",
      "label": "CC-BY-NC-SA_4.0",
      "icon": "http://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png",
      "source": "JRC 2018 templates & ROIs",
      "source_iri": "http://virtualflybrain.org/reports/JRC2018"
    }
  }
}
```

### Class Example

```json
{
  "Name": "adult antennal lobe projection neuron",
  "Id": "FBbt_00007354",
  "SuperTypes": [
    "Entity", "Adult", "Anatomy", "Class", "Nervous_system", "Neuron"
  ],
  "Meta": {
    "Name": "[adult antennal lobe projection neuron](FBbt_00007354)",
    "Description": "Any adult secondary olfactory neuron that has branched terminals in the antennal lobe and elsewhere (generally the protocerebrum).",
    "Relationships": "[is a](is_a): [adult antennal lobe neuron](FBbt_00007363), [adult projection neuron](FBbt_00007353); [synonyms](has_exact_synonym): olfactory projection neuron, antennal lobe projection neuron, AL projection neuron, secondary olfactory neuron, ALPN",
    "Classification": "[adult neuron](FBbt_00005106) > [adult intrinsic neuron](FBbt_00005116) > [adult central nervous system neuron](FBbt_00005125) > [adult cerebrum neuron](FBbt_00047698) > [adult antennal lobe neuron](FBbt_00007363) > adult antennal lobe projection neuron",
    "Types": "[adult antennal lobe neuron](FBbt_00007363); [adult projection neuron](FBbt_00007353)"
  },
  "Tags": ["Adult", "Nervous_system", "Neuron"],
  "Queries": [
    {
      "query": "ClassifiedAs",
      "label": "Find instances of adult antennal lobe projection neuron",
      "function": "get_instances",
      "takes": {
        "short_form": {"$and": ["Class"]},
        "default": {"short_form": "FBbt_00007354"}
      },
      "preview": 5,
      "preview_columns": ["id", "name", "driver", "thumbnail"],
      "preview_results": {
        "status": "complete",
        "headers": {
          "id": {"title": "Add", "type": "selection_id", "order": -1},
          "name": {"title": "Name", "type": "markdown", "order": 1, "sort": {"0": "Asc"}},
          "driver": {"title": "Driver", "type": "markdown", "order": 2},
          "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
        },
        "rows": []
      },
      "output_format": "table",
      "count": 387
    }
  ],
  "IsIndividual": false,
  "IsClass": true,
  "Examples": {
    "VFB_00017894": [
      {
        "id": "VFB_jrchc2b",
        "label": "PN v-L-Ad3",
        "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/00jc/hc2b/VFB_jrchc2b/thumbnail.png",
        "type_label": "adult antennal lobe projection neuron",
        "type_id": "FBbt_00007354"
      }
    ]
  },
  "Synonyms": [
    {
      "label": "olfactory projection neuron",
      "scope": "exact",
      "type": "synonym"
    },
    {
      "label": "antennal lobe projection neuron",
      "scope": "exact",
      "type": "synonym"
    },
    {
      "label": "AL projection neuron",
      "scope": "exact",
      "type": "synonym"
    },
    {
      "label": "secondary olfactory neuron",
      "scope": "exact", 
      "type": "synonym"
    },
    {
      "label": "ALPN",
      "scope": "exact",
      "type": "synonym"
    }
  ]
}
```

### Publication Example

```json
{
  "Name": "Chiang et al., 2011",
  "Id": "FBrf0213510",
  "SuperTypes": ["Entity", "Publication"],
  "Meta": {
    "Name": "[Chiang et al., 2011](FBrf0213510)",
    "Description": "Chiang AS, Lin CY, Chuang CC, Chang HM, Hsieh CH, Yeh CW, Shih CT, Wu JJ, Wang GT, Chen YC et al. 2011. Three-dimensional reconstruction of brain-wide wiring networks in Drosophila at single-cell resolution. Curr. Biol. 21(1):1--11.",
    "Cross References": "[PubMed](https://www.ncbi.nlm.nih.gov/pubmed/): [21129968](http://www.ncbi.nlm.nih.gov/pubmed/?term=21129968); [FlyBase](http://flybase.org/): [FBrf0213510](http://flybase.org/reports/FBrf0213510); [DOI](https://doi.org/): [10.1016/j.cub.2010.11.056](https://doi.org/10.1016/j.cub.2010.11.056)"
  },
  "IsIndividual": true,
  "IsClass": false,
  "IsTemplate": false,
  "Publications": [
    {
      "title": "Three-dimensional reconstruction of brain-wide wiring networks in Drosophila at single-cell resolution",
      "short_form": "FBrf0213510",
      "microref": "Chiang et al., 2011",
      "refs": [
        "http://www.ncbi.nlm.nih.gov/pubmed/?term=21129968",
        "http://flybase.org/reports/FBrf0213510",
        "https://doi.org/10.1016/j.cub.2010.11.056"
      ]
    }
  ]
}
```
