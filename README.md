# VFBquery

to setup requirements:
```bash
pip install --upgrade vfbquery
```

## 🚀 Performance & Caching

VFBquery includes intelligent SOLR-based caching for optimal performance:

- **54,000x speedup** for repeated queries
- **NBLAST similarity queries**: 10+ seconds → <0.1 seconds (cached)
- **Zero configuration** - works automatically
- **Persistent cache** survives restarts
- **3-month TTL** matches VFB_connect behavior

```python
import vfbquery as vfb

# First query builds cache (~1-2 seconds)
result1 = vfb.get_term_info('FBbt_00003748')

# Subsequent queries served from cache (<0.1 seconds)
result2 = vfb.get_term_info('FBbt_00003748')  # 54,000x faster!

# Similarity queries also cached
similar = vfb.get_similar_neurons('VFB_jrchk00s')  # Fast after first run
```

To get term info for a term:
get_term_info(ID)

e.g.
```python
import vfbquery as vfb
```
Class example:
```python
vfb.get_term_info('FBbt_00003748', force_refresh=True)
```
```json
{
   "Name": "medulla",
   "Id": "FBbt_00003748",
   "SuperTypes": [
      "Entity",
      "Class",
      "Adult",
      "Anatomy",
      "Nervous_system",
      "Synaptic_neuropil",
      "Synaptic_neuropil_domain",
      "Visual_system"
   ],
   "Meta": {
      "Name": "[medulla](FBbt_00003748)",
      "Description": "The second optic neuropil, sandwiched between the lamina and the lobula complex. It is divided into 10 layers: 1-6 make up the outer (distal) medulla, the seventh (or serpentine) layer exhibits a distinct architecture and layers 8-10 make up the inner (proximal) medulla (Ito et al., 2014).",
      "Comment": "Nern et al. (2025) - doi:10.1038/s41586-025-08746-0 say distal is M1-5 and M6-7 is central medulla.",
      "Types": "[anterior ectoderm derivative](FBbt_00025991); [synaptic neuropil domain](FBbt_00040007)",
      "Relationships": "[develops from](RO_0002202): [medulla anlage](FBbt_00001935); [is part of](BFO_0000050): [adult optic lobe](FBbt_00003701)"
   },
   "Tags": [
      "Adult",
      "Nervous_system",
      "Synaptic_neuropil_domain",
      "Visual_system"
   ],
   "Queries": [
      {
         "query": "ListAllAvailableImages",
         "label": "List all available images of medulla",
         "function": "get_instances",
         "takes": {
            "short_form": {
               "$and": [
                  "Class",
                  "Anatomy"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Gross Types",
                  "type": "tags",
                  "order": 3
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            },
            "rows": [
               {
                  "id": "VFB_00102107",
                  "label": "[ME on JRC2018Unisex adult brain](VFB_00102107)",
                  "tags": "Nervous_system|Adult|Visual_system|Synaptic_neuropil_domain",
                  "thumbnail": "[![ME on JRC2018Unisex adult brain aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png \"ME on JRC2018Unisex adult brain aligned to JRC2018U\")](VFB_00101567,VFB_00102107)"
               },
               {
                  "id": "VFB_00101385",
                  "label": "[ME(R) on JRC_FlyEM_Hemibrain](VFB_00101385)",
                  "tags": "Nervous_system|Adult|Visual_system|Synaptic_neuropil_domain",
                  "thumbnail": "[![ME(R) on JRC_FlyEM_Hemibrain aligned to JRCFIB2018Fum](https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png \"ME(R) on JRC_FlyEM_Hemibrain aligned to JRCFIB2018Fum\")](VFB_00101384,VFB_00101385)"
               },
               {
                  "id": "VFB_00030810",
                  "label": "[medulla on adult brain template Ito2014](VFB_00030810)",
                  "tags": "Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain",
                  "thumbnail": "[![medulla on adult brain template Ito2014 aligned to adult brain template Ito2014](https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/thumbnail.png \"medulla on adult brain template Ito2014 aligned to adult brain template Ito2014\")](VFB_00030786,VFB_00030810)"
               },
               {
                  "id": "VFB_00030624",
                  "label": "[medulla on adult brain template JFRC2](VFB_00030624)",
                  "tags": "Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain",
                  "thumbnail": "[![medulla on adult brain template JFRC2 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/thumbnail.png \"medulla on adult brain template JFRC2 aligned to JFRC2\")](VFB_00017894,VFB_00030624)"
               }
            ]
         },
         "output_format": "table",
         "count": 4
      },
      {
         "query": "NeuronsPartHere",
         "label": "Neurons with some part in medulla",
         "function": "get_neurons_with_part_in",
         "takes": {
            "short_form": {
               "$and": [
                  "Class",
                  "Anatomy"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 2
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            },
            "rows": [
               {
                  "id": "FBbt_20011363",
                  "label": "[Cm10](FBbt_20011363)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940629671015 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/8027/VFB_00101567/thumbnail.png 'FlyWire:720575940629671015 aligned to JRC2018U')](FBbt_20011363)"
               },
               {
                  "id": "FBbt_20011364",
                  "label": "[Cm15](FBbt_20011364)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940611214802 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/4277/VFB_00101567/thumbnail.png 'FlyWire:720575940611214802 aligned to JRC2018U')](FBbt_20011364)"
               },
               {
                  "id": "FBbt_20011365",
                  "label": "[Cm16](FBbt_20011365)",
                  "tags": "Adult|Glutamatergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940631561002 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw09/9899/VFB_00101567/thumbnail.png 'FlyWire:720575940631561002 aligned to JRC2018U')](FBbt_20011365)"
               },
               {
                  "id": "FBbt_20011366",
                  "label": "[Cm17](FBbt_20011366)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940624043817 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/1609/VFB_00101567/thumbnail.png 'FlyWire:720575940624043817 aligned to JRC2018U')](FBbt_20011366)"
               },
               {
                  "id": "FBbt_20011362",
                  "label": "[Cm1](FBbt_20011362)",
                  "tags": "Adult|Cholinergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940621358986 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw08/9799/VFB_00101567/thumbnail.png 'FlyWire:720575940621358986 aligned to JRC2018U')](FBbt_20011362)"
               }
            ]
         },
         "output_format": "table",
         "count": 472
      },
      {
         "query": "NeuronsSynaptic",
         "label": "Neurons with synaptic terminals in medulla",
         "function": "get_neurons_with_synapses_in",
         "takes": {
            "short_form": {
               "$and": [
                  "Class",
                  "Anatomy"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 2
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            },
            "rows": [
               {
                  "id": "FBbt_20011363",
                  "label": "[Cm10](FBbt_20011363)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940629671015 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/8027/VFB_00101567/thumbnail.png 'FlyWire:720575940629671015 aligned to JRC2018U')](FBbt_20011363)"
               },
               {
                  "id": "FBbt_20011364",
                  "label": "[Cm15](FBbt_20011364)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940611214802 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/4277/VFB_00101567/thumbnail.png 'FlyWire:720575940611214802 aligned to JRC2018U')](FBbt_20011364)"
               },
               {
                  "id": "FBbt_20011365",
                  "label": "[Cm16](FBbt_20011365)",
                  "tags": "Adult|Glutamatergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940631561002 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw09/9899/VFB_00101567/thumbnail.png 'FlyWire:720575940631561002 aligned to JRC2018U')](FBbt_20011365)"
               },
               {
                  "id": "FBbt_20011366",
                  "label": "[Cm17](FBbt_20011366)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940624043817 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/1609/VFB_00101567/thumbnail.png 'FlyWire:720575940624043817 aligned to JRC2018U')](FBbt_20011366)"
               },
               {
                  "id": "FBbt_20011362",
                  "label": "[Cm1](FBbt_20011362)",
                  "tags": "Adult|Cholinergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940621358986 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw08/9799/VFB_00101567/thumbnail.png 'FlyWire:720575940621358986 aligned to JRC2018U')](FBbt_20011362)"
               }
            ]
         },
         "output_format": "table",
         "count": 465
      },
      {
         "query": "NeuronsPresynapticHere",
         "label": "Neurons with presynaptic terminals in medulla",
         "function": "get_neurons_with_presynaptic_terminals_in",
         "takes": {
            "short_form": {
               "$and": [
                  "Class",
                  "Anatomy"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 2
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            },
            "rows": [
               {
                  "id": "FBbt_20011363",
                  "label": "[Cm10](FBbt_20011363)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940629671015 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/8027/VFB_00101567/thumbnail.png 'FlyWire:720575940629671015 aligned to JRC2018U')](FBbt_20011363)"
               },
               {
                  "id": "FBbt_20011364",
                  "label": "[Cm15](FBbt_20011364)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940611214802 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/4277/VFB_00101567/thumbnail.png 'FlyWire:720575940611214802 aligned to JRC2018U')](FBbt_20011364)"
               },
               {
                  "id": "FBbt_20011365",
                  "label": "[Cm16](FBbt_20011365)",
                  "tags": "Adult|Glutamatergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940631561002 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw09/9899/VFB_00101567/thumbnail.png 'FlyWire:720575940631561002 aligned to JRC2018U')](FBbt_20011365)"
               },
               {
                  "id": "FBbt_20011366",
                  "label": "[Cm17](FBbt_20011366)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940624043817 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/1609/VFB_00101567/thumbnail.png 'FlyWire:720575940624043817 aligned to JRC2018U')](FBbt_20011366)"
               },
               {
                  "id": "FBbt_20011362",
                  "label": "[Cm1](FBbt_20011362)",
                  "tags": "Adult|Cholinergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940621358986 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw08/9799/VFB_00101567/thumbnail.png 'FlyWire:720575940621358986 aligned to JRC2018U')](FBbt_20011362)"
               }
            ]
         },
         "output_format": "table",
         "count": 253
      },
      {
         "query": "NeuronsPostsynapticHere",
         "label": "Neurons with postsynaptic terminals in medulla",
         "function": "get_neurons_with_postsynaptic_terminals_in",
         "takes": {
            "short_form": {
               "$and": [
                  "Class",
                  "Anatomy"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 2
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            },
            "rows": [
               {
                  "id": "FBbt_20011363",
                  "label": "[Cm10](FBbt_20011363)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940629671015 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/8027/VFB_00101567/thumbnail.png 'FlyWire:720575940629671015 aligned to JRC2018U')](FBbt_20011363)"
               },
               {
                  "id": "FBbt_20011364",
                  "label": "[Cm15](FBbt_20011364)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940611214802 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/4277/VFB_00101567/thumbnail.png 'FlyWire:720575940611214802 aligned to JRC2018U')](FBbt_20011364)"
               },
               {
                  "id": "FBbt_20011365",
                  "label": "[Cm16](FBbt_20011365)",
                  "tags": "Adult|Glutamatergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940631561002 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw09/9899/VFB_00101567/thumbnail.png 'FlyWire:720575940631561002 aligned to JRC2018U')](FBbt_20011365)"
               },
               {
                  "id": "FBbt_20011366",
                  "label": "[Cm17](FBbt_20011366)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940624043817 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/1609/VFB_00101567/thumbnail.png 'FlyWire:720575940624043817 aligned to JRC2018U')](FBbt_20011366)"
               },
               {
                  "id": "FBbt_20011362",
                  "label": "[Cm1](FBbt_20011362)",
                  "tags": "Adult|Cholinergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940621358986 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw08/9799/VFB_00101567/thumbnail.png 'FlyWire:720575940621358986 aligned to JRC2018U')](FBbt_20011362)"
               }
            ]
         },
         "output_format": "table",
         "count": 331
      },
      {
         "query": "PartsOf",
         "label": "Parts of medulla",
         "function": "get_parts_of",
         "takes": {
            "short_form": {
               "$and": [
                  "Class"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 2
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            },
            "rows": [
               {
                  "id": "FBbt_00003750",
                  "label": "[medulla layer M1](FBbt_00003750)",
                  "tags": "Adult|Nervous_system|Synaptic_neuropil_subdomain|Visual_system",
                  "thumbnail": ""
               },
               {
                  "id": "FBbt_00003753",
                  "label": "[medulla layer M4](FBbt_00003753)",
                  "tags": "Adult|Nervous_system|Synaptic_neuropil_subdomain|Visual_system",
                  "thumbnail": ""
               },
               {
                  "id": "FBbt_00003754",
                  "label": "[medulla layer M5](FBbt_00003754)",
                  "tags": "Adult|Nervous_system|Synaptic_neuropil_subdomain|Visual_system",
                  "thumbnail": ""
               },
               {
                  "id": "FBbt_00003758",
                  "label": "[medulla layer M8](FBbt_00003758)",
                  "tags": "Adult|Nervous_system|Synaptic_neuropil_subdomain|Visual_system",
                  "thumbnail": ""
               },
               {
                  "id": "FBbt_00003759",
                  "label": "[medulla layer M9](FBbt_00003759)",
                  "tags": "Adult|Nervous_system|Synaptic_neuropil_subdomain|Visual_system",
                  "thumbnail": ""
               }
            ]
         },
         "output_format": "table",
         "count": 28
      },
      {
         "query": "SubclassesOf",
         "label": "Subclasses of medulla",
         "function": "get_subclasses_of",
         "takes": {
            "short_form": {
               "$and": [
                  "Class"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 2
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            }
         },
         "output_format": "table",
         "count": 0
      },
      {
         "query": "TractsNervesInnervatingHere",
         "label": "Tracts/nerves innervating medulla",
         "function": "get_tracts_nerves_innervating_here",
         "takes": {
            "short_form": {
               "$or": [
                  {
                     "$and": [
                        "Class",
                        "Synaptic_neuropil"
                     ]
                  },
                  {
                     "$and": [
                        "Class",
                        "Synaptic_neuropil_domain"
                     ]
                  }
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 2
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            },
            "rows": [
               {
                  "id": "FBbt_00005810",
                  "label": "[first optic chiasma](FBbt_00005810)",
                  "tags": "Adult|Nervous_system|Neuron_projection_bundle|Visual_system",
                  "thumbnail": ""
               },
               {
                  "id": "FBbt_00007427",
                  "label": "[posterior optic commissure](FBbt_00007427)",
                  "tags": "Adult|Nervous_system|Neuron_projection_bundle",
                  "thumbnail": "[![posterior optic commissure on adult brain template Ito2014 aligned to adult brain template Ito2014](https://www.virtualflybrain.org/data/VFB/i/0003/0828/VFB_00030786/thumbnail.png 'posterior optic commissure on adult brain template Ito2014 aligned to adult brain template Ito2014')](FBbt_00007427)"
               },
               {
                  "id": "FBbt_00003922",
                  "label": "[second optic chiasma](FBbt_00003922)",
                  "tags": "Adult|Nervous_system|Neuron_projection_bundle|Visual_system",
                  "thumbnail": ""
               }
            ]
         },
         "output_format": "table",
         "count": 3
      },
      {
         "query": "LineageClonesIn",
         "label": "Lineage clones found in medulla",
         "function": "get_lineage_clones_in",
         "takes": {
            "short_form": {
               "$and": [
                  "Class",
                  "Synaptic_neuropil"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 2
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            },
            "rows": [
               {
                  "id": "FBbt_00050019",
                  "label": "[adult DM1 lineage clone](FBbt_00050019)",
                  "tags": "Adult|Clone|lineage_DPMm1",
                  "thumbnail": "[![DM1 clone of Yu 2013 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0002/0006/VFB_00017894/thumbnail.png 'DM1 clone of Yu 2013 aligned to JFRC2')](FBbt_00050019)"
               },
               {
                  "id": "FBbt_00050143",
                  "label": "[adult DM6 lineage clone](FBbt_00050143)",
                  "tags": "Adult|Clone|lineage_CM3",
                  "thumbnail": "[![DM6 clone of Ito 2013 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0002/0204/VFB_00101567/thumbnail.png 'DM6 clone of Ito 2013 aligned to JRC2018U')](FBbt_00050143)"
               },
               {
                  "id": "FBbt_00050167",
                  "label": "[adult LALv1 lineage clone](FBbt_00050167)",
                  "tags": "Adult|Clone|lineage_BAmv1",
                  "thumbnail": "[![LALv1 clone of Yu 2013 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0002/0056/VFB_00101567/thumbnail.png 'LALv1 clone of Yu 2013 aligned to JRC2018U')](FBbt_00050167)"
               },
               {
                  "id": "FBbt_00050051",
                  "label": "[adult VESa2 lineage clone](FBbt_00050051)",
                  "tags": "Adult|Clone|lineage_BAlp1",
                  "thumbnail": "[![PSa1 clone of Ito 2013 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0002/0206/VFB_00101567/thumbnail.png 'PSa1 clone of Ito 2013 aligned to JRC2018U')](FBbt_00050051)"
               },
               {
                  "id": "FBbt_00050013",
                  "label": "[adult VPNl&d1 lineage clone](FBbt_00050013)",
                  "tags": "Adult|Clone",
                  "thumbnail": "[![VPNl&d1 clone of Ito 2013 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0002/0253/VFB_00101567/thumbnail.png 'VPNl&d1 clone of Ito 2013 aligned to JRC2018U')](FBbt_00050013)"
               }
            ]
         },
         "output_format": "table",
         "count": 7
      },
      {
         "query": "ImagesNeurons",
         "label": "Images of neurons with some part in medulla",
         "function": "get_images_neurons",
         "takes": {
            "short_form": {
               "$or": [
                  {
                     "$and": [
                        "Class",
                        "Synaptic_neuropil"
                     ]
                  },
                  {
                     "$and": [
                        "Class",
                        "Synaptic_neuropil_domain"
                     ]
                  }
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "label",
            "tags",
            "thumbnail"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "Add",
                  "type": "selection_id",
                  "order": -1
               },
               "label": {
                  "title": "Name",
                  "type": "markdown",
                  "order": 0,
                  "sort": {
                     "0": "Asc"
                  }
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 2
               },
               "thumbnail": {
                  "title": "Thumbnail",
                  "type": "markdown",
                  "order": 9
               }
            },
            "rows": [
               {
                  "id": "VFB_fw113160",
                  "label": "[FlyWire:720575940614228963](VFB_fw113160)",
                  "tags": [
                     "Adult",
                     "Cholinergic",
                     "Glutamatergic",
                     "Nervous_system",
                     "Visual_system",
                     "secondary_neuron"
                  ],
                  "thumbnail": "[![ME.38893 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/3160/VFB_00101567/thumbnail.png 'ME.38893 aligned to JRC2018U')](VFB_00101567,VFB_fw113160)"
               },
               {
                  "id": "VFB_fw113163",
                  "label": "[FlyWire:720575940617552345](VFB_fw113163)",
                  "tags": [
                     "Adult",
                     "Glutamatergic",
                     "Nervous_system",
                     "Visual_system"
                  ],
                  "thumbnail": "[![ME.22510 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/3163/VFB_00101567/thumbnail.png 'ME.22510 aligned to JRC2018U')](VFB_00101567,VFB_fw113163)"
               },
               {
                  "id": "VFB_fw113161",
                  "label": "[FlyWire:720575940620899019](VFB_fw113161)",
                  "tags": [
                     "Adult",
                     "Cholinergic",
                     "Nervous_system",
                     "Visual_system"
                  ],
                  "thumbnail": "[![ME.19455 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/3161/VFB_00101567/thumbnail.png 'ME.19455 aligned to JRC2018U')](VFB_00101567,VFB_fw113161)"
               },
               {
                  "id": "VFB_fw113162",
                  "label": "[FlyWire:720575940627258493](VFB_fw113162)",
                  "tags": [
                     "Adult",
                     "Cholinergic",
                     "Nervous_system",
                     "Visual_system"
                  ],
                  "thumbnail": "[![ME.23829 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/3162/VFB_00101567/thumbnail.png 'ME.23829 aligned to JRC2018U')](VFB_00101567,VFB_fw113162)"
               },
               {
                  "id": "VFB_fw113167",
                  "label": "[FlyWire:720575940628422216](VFB_fw113167)",
                  "tags": [
                     "Adult",
                     "Glutamatergic",
                     "Nervous_system",
                     "Visual_system"
                  ],
                  "thumbnail": "[![ME.11974 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw11/3167/VFB_00101567/thumbnail.png 'ME.11974 aligned to JRC2018U')](VFB_00101567,VFB_fw113167)"
               }
            ]
         },
         "output_format": "table",
         "count": 119989
      },
      {
         "query": "ExpressionOverlapsHere",
         "label": "Expression patterns overlapping medulla",
         "function": "get_expression_overlaps_here",
         "takes": {
            "short_form": {
               "$and": [
                  "Class",
                  "Anatomy"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "name",
            "tags",
            "pubs"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "ID",
                  "type": "selection_id",
                  "order": -1
               },
               "name": {
                  "title": "Expression Pattern",
                  "type": "markdown",
                  "order": 0
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 1
               },
               "pubs": {
                  "title": "Publications",
                  "type": "metadata",
                  "order": 2
               }
            },
            "rows": [
               {
                  "id": "VFBexp_FBti0182065",
                  "name": "[Mi{GT-GAL4}DIP-\u03b2[MI01971-GAL4] expression pattern](VFBexp_FBti0182065)",
                  "tags": "Expression_pattern",
                  "pubs": [
                     {
                        "core": {
                           "iri": "http://flybase.org/reports/FBrf0230454",
                           "symbol": "",
                           "types": [
                              "Entity",
                              "Individual",
                              "pub"
                           ],
                           "short_form": "FBrf0230454",
                           "label": "Carrillo et al., 2015, Cell 163(7): 1770--1782"
                        },
                        "FlyBase": "FBrf0230454",
                        "PubMed": "26687361",
                        "DOI": "10.1016/j.cell.2015.11.022"
                     }
                  ]
               },
               {
                  "id": "VFBexp_FBti0145260",
                  "name": "[Mi{MIC}dpr10[MI03557] expression pattern](VFBexp_FBti0145260)",
                  "tags": "Expression_pattern",
                  "pubs": [
                     {
                        "core": {
                           "iri": "http://flybase.org/reports/FBrf0230454",
                           "symbol": "",
                           "types": [
                              "Entity",
                              "Individual",
                              "pub"
                           ],
                           "short_form": "FBrf0230454",
                           "label": "Carrillo et al., 2015, Cell 163(7): 1770--1782"
                        },
                        "FlyBase": "FBrf0230454",
                        "PubMed": "26687361",
                        "DOI": "10.1016/j.cell.2015.11.022"
                     }
                  ]
               },
               {
                  "id": "VFBexp_FBti0143547",
                  "name": "[PBac{544.SVS-1}Fer2LCH[CPTI100064] expression pattern](VFBexp_FBti0143547)",
                  "tags": "Expression_pattern",
                  "pubs": [
                     {
                        "core": {
                           "iri": "http://flybase.org/reports/FBrf0215202",
                           "symbol": "",
                           "types": [
                              "Entity",
                              "Individual",
                              "pub"
                           ],
                           "short_form": "FBrf0215202",
                           "label": "Knowles-Barley, 2011.8.24, BrainTrap expression curation."
                        },
                        "FlyBase": "FBrf0215202",
                        "PubMed": "",
                        "DOI": ""
                     }
                  ]
               },
               {
                  "id": "VFBexp_FBti0143533",
                  "name": "[PBac{544.SVS-1}B4[CPTI100035] expression pattern](VFBexp_FBti0143533)",
                  "tags": "Expression_pattern",
                  "pubs": [
                     {
                        "core": {
                           "iri": "http://flybase.org/reports/FBrf0215202",
                           "symbol": "",
                           "types": [
                              "Entity",
                              "Individual",
                              "pub"
                           ],
                           "short_form": "FBrf0215202",
                           "label": "Knowles-Barley, 2011.8.24, BrainTrap expression curation."
                        },
                        "FlyBase": "FBrf0215202",
                        "PubMed": "",
                        "DOI": ""
                     }
                  ]
               },
               {
                  "id": "VFBexp_FBti0143524",
                  "name": "[PBac{566.P.SVS-1}IA-2[CPTI100013] expression pattern](VFBexp_FBti0143524)",
                  "tags": "Expression_pattern",
                  "pubs": [
                     {
                        "core": {
                           "iri": "http://flybase.org/reports/FBrf0215202",
                           "symbol": "",
                           "types": [
                              "Entity",
                              "Individual",
                              "pub"
                           ],
                           "short_form": "FBrf0215202",
                           "label": "Knowles-Barley, 2011.8.24, BrainTrap expression curation."
                        },
                        "FlyBase": "FBrf0215202",
                        "PubMed": "",
                        "DOI": ""
                     }
                  ]
               }
            ]
         },
         "output_format": "table",
         "count": 2339
      },
      {
         "query": "TransgeneExpressionHere",
         "label": "Transgene expression in medulla",
         "function": "get_transgene_expression_here",
         "takes": {
            "short_form": {
               "$and": [
                  "Class",
                  "Nervous_system",
                  "Anatomy"
               ]
            },
            "default": {
               "short_form": "FBbt_00003748"
            }
         },
         "preview": 5,
         "preview_columns": [
            "id",
            "name",
            "tags"
         ],
         "preview_results": {
            "headers": {
               "id": {
                  "title": "ID",
                  "type": "selection_id",
                  "order": -1
               },
               "name": {
                  "title": "Expression Pattern",
                  "type": "markdown",
                  "order": 0
               },
               "tags": {
                  "title": "Tags",
                  "type": "tags",
                  "order": 1
               }
            },
            "rows": [
               {
                  "id": "VFBexp_FBti0182065",
                  "name": "[Mi{GT-GAL4}DIP-\u03b2[MI01971-GAL4] expression pattern](VFBexp_FBti0182065)",
                  "tags": "Expression_pattern"
               },
               {
                  "id": "VFBexp_FBti0145260",
                  "name": "[Mi{MIC}dpr10[MI03557] expression pattern](VFBexp_FBti0145260)",
                  "tags": "Expression_pattern"
               },
               {
                  "id": "VFBexp_FBti0143547",
                  "name": "[PBac{544.SVS-1}Fer2LCH[CPTI100064] expression pattern](VFBexp_FBti0143547)",
                  "tags": "Expression_pattern"
               },
               {
                  "id": "VFBexp_FBti0143533",
                  "name": "[PBac{544.SVS-1}B4[CPTI100035] expression pattern](VFBexp_FBti0143533)",
                  "tags": "Expression_pattern"
               },
               {
                  "id": "VFBexp_FBti0143524",
                  "name": "[PBac{566.P.SVS-1}IA-2[CPTI100013] expression pattern](VFBexp_FBti0143524)",
                  "tags": "Expression_pattern"
               }
            ]
         },
         "output_format": "table",
         "count": 2339
      }
   ],
   "IsIndividual": False,
   "IsClass": True,
   "Examples": {
      "VFB_00101384": [
         {
            "id": "VFB_00101385",
            "label": "ME(R) on JRC_FlyEM_Hemibrain",
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png",
            "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnailT.png",
            "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.nrrd",
            "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.wlz",
            "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume_man.obj"
         }
      ],
      "VFB_00101567": [
         {
            "id": "VFB_00102107",
            "label": "ME on JRC2018Unisex adult brain",
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
            "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
            "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.nrrd",
            "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.wlz",
            "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume_man.obj"
         }
      ],
      "VFB_00017894": [
         {
            "id": "VFB_00030624",
            "label": "medulla on adult brain template JFRC2",
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/thumbnail.png",
            "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/thumbnailT.png",
            "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/volume.nrrd",
            "wlz": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/volume.wlz",
            "obj": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/volume_man.obj"
         }
      ],
      "VFB_00030786": [
         {
            "id": "VFB_00030810",
            "label": "medulla on adult brain template Ito2014",
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/thumbnail.png",
            "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/thumbnailT.png",
            "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/volume.nrrd",
            "wlz": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/volume.wlz",
            "obj": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/volume_man.obj"
         }
      ]
   },
   "IsTemplate": False,
   "Synonyms": [
      {
         "label": "ME",
         "scope": "has_exact_synonym",
         "type": "",
         "publication": "[Ito et al., 2014](FBrf0224194)"
      },
      {
         "label": "Med",
         "scope": "has_exact_synonym",
         "type": "",
         "publication": "[Chiang et al., 2011](FBrf0212704)"
      },
      {
         "label": "optic medulla",
         "scope": "has_exact_synonym",
         "type": "",
         "publication": "[Venkatesh and Shyamala, 2010](FBrf0212889)"
      },
      {
         "label": "m",
         "scope": "has_related_synonym",
         "type": "",
         "publication": ""
      }
   ]
}
```

Individual example:
```python
vfb.get_term_info('VFB_00000001')
```
```json
{
  "Name": "fru-M-200266",
  "Id": "VFB_00000001",
  "SuperTypes": [
    "Entity",
    "Individual",
    "VFB",
    "Neuron",
    "Adult",
    "Anatomy",
    "Cell",
    "Expression_pattern_fragment",
    "Nervous_system",
    "has_image",
    "lineage_CM3",
    "lineage_DM6",
    "FlyCircuit",
    "NBLAST"
  ],
  "Meta": {
    "Name": "[fru-M-200266](VFB_00000001)",
    "Description": "",
    "Comment": "OutAge: Adult 5~15 days",
    "Types": "[adult DM6 lineage neuron](FBbt_00050144); [expression pattern fragment](VFBext_0000004)",
    "Relationships": "[expresses](RO_0002292): [Scer\\GAL4%5Bfru.P1.D%5D](FBal0276838); [is part of](BFO_0000050): [Scer\\GAL4%5Bfru.P1.D%5D expression pattern](VFBexp_FBal0276838), [adult brain](FBbt_00003624), [male organism](FBbt_00007004); [overlaps](RO_0002131): [adult antennal lobe](FBbt_00007401), [adult crepine](FBbt_00045037), [adult lateral accessory lobe](FBbt_00003681), [superior posterior slope](FBbt_00045040), [vest](FBbt_00040041)"
  },
  "Tags": [
    "Adult",
    "Expression_pattern_fragment",
    "Neuron",
    "lineage_CM3"
  ],
  "Queries": [
    {
      "query": "SimilarMorphologyTo",
      "label": "Find similar neurons to fru-M-200266",
      "function": "get_similar_neurons",
      "takes": {
        "short_form": {
          "$and": [
            "Individual",
            "Neuron"
          ]
        },
        "default": {
          "neuron": "VFB_00000001",
          "similarity_score": "NBLAST_score"
        }
      },
      "preview": 5,
      "preview_columns": [
        "id",
        "score",
        "name",
        "tags",
        "thumbnail"
      ],
      "preview_results": {
        "headers": {
          "id": {
            "title": "Add",
            "type": "selection_id",
            "order": -1
          },
          "score": {
            "title": "Score",
            "type": "numeric",
            "order": 1,
            "sort": {
              "0": "Desc"
            }
          },
          "name": {
            "title": "Name",
            "type": "markdown",
            "order": 1,
            "sort": {
              "1": "Asc"
            }
          },
          "tags": {
            "title": "Tags",
            "type": "tags",
            "order": 2
          },
          "thumbnail": {
            "title": "Thumbnail",
            "type": "markdown",
            "order": 9
          }
        },
        "rows": [
          {
            "id": "VFB_00000333",
            "score": "0.61",
            "name": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00017894/thumbnail.png \"fru-M-000204 aligned to JFRC2\")](VFB_00017894,VFB_00000333)"
          },
          {
            "id": "VFB_00000333",
            "score": "0.61",
            "name": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00101567/thumbnail.png \"fru-M-000204 aligned to JRC2018U\")](VFB_00101567,VFB_00000333)"
          },
          {
            "id": "VFB_00002439",
            "score": "0.6",
            "name": "[fru-M-900020](VFB_00002439)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-900020 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00101567/thumbnail.png \"fru-M-900020 aligned to JRC2018U\")](VFB_00101567,VFB_00002439)"
          },
          {
            "id": "VFB_00002439",
            "score": "0.6",
            "name": "[fru-M-900020](VFB_00002439)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-900020 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00017894/thumbnail.png \"fru-M-900020 aligned to JFRC2\")](VFB_00017894,VFB_00002439)"
          },
          {
            "id": "VFB_00000845",
            "score": "0.59",
            "name": "[fru-M-100191](VFB_00000845)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-100191 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0845/VFB_00101567/thumbnail.png \"fru-M-100191 aligned to JRC2018U\")](VFB_00101567,VFB_00000845)"
          }
        ]
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
        "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/thumbnail.png",
        "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/thumbnailT.png",
        "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/volume.nrrd",
        "wlz": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/volume.wlz",
        "obj": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/volume.obj",
        "swc": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/volume.swc"
      }
    ],
    "VFB_00101567": [
      {
        "id": "VFB_00000001",
        "label": "fru-M-200266",
        "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/thumbnail.png",
        "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/thumbnailT.png",
        "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.nrrd",
        "wlz": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.wlz",
        "obj": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.obj",
        "swc": "https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.swc"
      }
    ]
  },
  "IsClass": false,
  "Examples": {},
  "IsTemplate": false,
  "Domains": {},
  "Licenses": {
    "0": {
      "iri": "http://virtualflybrain.org/reports/VFBlicense_FlyCircuit_License",
      "short_form": "VFBlicense_FlyCircuit_License",
      "label": "FlyCircuit License",
      "icon": "",
      "source": "FlyCircuit 1.0 - single neurons (Chiang2010)",
      "source_iri": "http://virtualflybrain.org/reports/Chiang2010"
    }
  },
  "Publications": [],
  "Synonyms": []
}
```

Template example:
```python
vfb.get_term_info('VFB_00101567')
```
```json
{
  "Name": "JRC2018U",
  "Id": "VFB_00101567",
  "SuperTypes": [
    "Entity",
    "Individual",
    "VFB",
    "Adult",
    "Anatomy",
    "Nervous_system",
    "Template",
    "has_image"
  ],
  "Meta": {
    "Name": "[JRC2018Unisex](VFB_00101567)",
    "Symbol": "[JRC2018U](VFB_00101567)",
    "Description": "Janelia 2018 unisex, averaged adult brain template",
    "Comment": "",
    "Types": "[adult brain](FBbt_00003624)"
  },
  "Tags": [
    "Adult",
    "Nervous_system"
  ],
  "Queries": [
    {
      "query": "PaintedDomains",
      "label": "Painted domains for JRC2018U",
      "function": "get_painted_domains",
      "takes": {
        "short_form": {
          "$and": [
            "Template",
            "Individual"
          ]
        },
        "default": {
          "short_form": "VFB_00101567"
        }
      },
      "preview": 10,
      "preview_columns": [
        "id",
        "name",
        "type",
        "thumbnail"
      ],
      "preview_results": {
        "headers": {
          "id": {
            "title": "ID",
            "type": "selection_id",
            "order": -1
          },
          "name": {
            "title": "Domain",
            "type": "markdown",
            "order": 0
          },
          "type": {
            "title": "Type",
            "type": "text",
            "order": 1
          },
          "thumbnail": {
            "title": "Thumbnail",
            "type": "markdown",
            "order": 2
          }
        },
        "rows": [
          {
            "id": "VFB_00102274",
            "name": "[FLA on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102274)",
            "type": [
              "flange"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567//thumbnailT.png"
          },
          {
            "id": "VFB_00102218",
            "name": "[IPS on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102218)",
            "type": [
              "inferior posterior slope"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567//thumbnailT.png"
          },
          {
            "id": "VFB_00102214",
            "name": "[GOR on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102214)",
            "type": [
              "gorget"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567//thumbnailT.png"
          },
          {
            "id": "VFB_00102212",
            "name": "[VES on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102212)",
            "type": [
              "vest"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567//thumbnailT.png"
          },
          {
            "id": "VFB_00102201",
            "name": "[AL on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102201)",
            "type": [
              "adult antennal lobe"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567//thumbnailT.png"
          },
          {
            "id": "VFB_00102185",
            "name": "[IB on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102185)",
            "type": [
              "inferior bridge"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567//thumbnailT.png"
          },
          {
            "id": "VFB_00102176",
            "name": "[SCL on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102176)",
            "type": [
              "superior clamp"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567//thumbnailT.png"
          },
          {
            "id": "VFB_00102170",
            "name": "[SMP on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102170)",
            "type": [
              "superior medial protocerebrum"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567//thumbnailT.png"
          },
          {
            "id": "VFB_00102164",
            "name": "[SIP on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102164)",
            "type": [
              "superior intermediate protocerebrum"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567//thumbnailT.png"
          },
          {
            "id": "VFB_00102110",
            "name": "[LOP on JRC2018Unisex adult brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00102110)",
            "type": [
              "lobula plate"
            ],
            "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567//thumbnailT.png"
          }
        ]
      },
      "output_format": "table",
      "count": 46
    },
    {
      "query": "AllAlignedImages",
      "label": "All images aligned to JRC2018U",
      "function": "get_all_aligned_images",
      "takes": {
        "short_form": {
          "$and": [
            "Template",
            "Individual"
          ]
        },
        "default": {
          "short_form": "VFB_00101567"
        }
      },
      "preview": 10,
      "preview_columns": [
        "id",
        "name",
        "tags",
        "type"
      ],
      "preview_results": {
        "headers": {
          "id": {
            "title": "ID",
            "type": "selection_id",
            "order": -1
          },
          "name": {
            "title": "Image",
            "type": "markdown",
            "order": 0
          },
          "tags": {
            "title": "Tags",
            "type": "tags",
            "order": 1
          },
          "type": {
            "title": "Type",
            "type": "text",
            "order": 2
          }
        },
        "rows": [
          {
            "id": "VFB_fw137243",
            "name": "[FlyWire:720575940627896445](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_fw137243)",
            "tags": "secondary_neuron|Nervous_system|GABAergic|Adult|Visual_system|Cholinergic",
            "type": "transmedullary neuron Tm4"
          },
          {
            "id": "VFB_fw040027",
            "name": "[FlyWire:720575940620257750](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_fw040027)",
            "tags": "Nervous_system|Adult|Cholinergic",
            "type": "adult ascending neuron"
          },
          {
            "id": "VFB_fw040027",
            "name": "[FlyWire:720575940620257750](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_fw040027)",
            "tags": "Nervous_system|Adult|Cholinergic",
            "type": "adult cholinergic neuron"
          },
          {
            "id": "VFB_fw032724",
            "name": "[FlyWire:720575940622971283](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_fw032724)",
            "tags": "Adult|Cholinergic|lineage_CM4",
            "type": "adult crepine neuron 078"
          },
          {
            "id": "VFB_fw010978",
            "name": "[FlyWire:720575940626992202](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_fw010978)",
            "tags": "Nervous_system|Adult|Cholinergic",
            "type": "adult CB1903 neuron"
          },
          {
            "id": "VFB_001043rb",
            "name": "[Mi4_R (JRC_OpticLobe:68363)](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_001043rb)",
            "tags": "secondary_neuron|Nervous_system|Visual_system|GABAergic|Adult",
            "type": "medulla intrinsic neuron Mi4"
          },
          {
            "id": "VFB_00101vfi",
            "name": "[JRC_R41H08-GAL4_MCFO_Brain_20190212_63_F5_40x](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00101vfi)",
            "tags": "Expression_pattern_fragment|Nervous_system|Adult",
            "type": "expression pattern fragment"
          },
          {
            "id": "VFB_00101bzg",
            "name": "[VDRC_VT009650-GAL4_MCFO_Brain_20180427_64_E1_40x](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00101bzg)",
            "tags": "Expression_pattern_fragment|Nervous_system|Adult",
            "type": "expression pattern fragment"
          },
          {
            "id": "VFB_00043401",
            "name": "[VDRC_VT043925_LexAGAD_attP40_1](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00043401)",
            "tags": "Nervous_system|Adult|Expression_pattern",
            "type": "anatomical entity"
          },
          {
            "id": "VFB_00043401",
            "name": "[VDRC_VT043925_LexAGAD_attP40_1](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_00043401)",
            "tags": "Nervous_system|Adult|Expression_pattern",
            "type": "expression pattern"
          }
        ]
      },
      "output_format": "table",
      "count": 313780
    },
    {
      "query": "AlignedDatasets",
      "label": "Datasets aligned to JRC2018U",
      "function": "get_aligned_datasets",
      "takes": {
        "short_form": {
          "$and": [
            "Template",
            "Individual"
          ]
        },
        "default": {
          "short_form": "VFB_00101567"
        }
      },
      "preview": 10,
      "preview_columns": [
        "id",
        "name",
        "tags"
      ],
      "preview_results": {
        "headers": {
          "id": {
            "title": "ID",
            "type": "selection_id",
            "order": -1
          },
          "name": {
            "title": "Dataset",
            "type": "markdown",
            "order": 0
          },
          "tags": {
            "title": "Tags",
            "type": "tags",
            "order": 1
          }
        },
        "rows": [
          {
            "id": "TaiszGalili2022",
            "name": "[EM FAFB Taisz and Galili et al., 2022](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=TaiszGalili2022)",
            "tags": "DataSet"
          },
          {
            "id": "Sayin2019",
            "name": "[EM FAFB Sayin et al 2019](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Sayin2019)",
            "tags": "DataSet"
          },
          {
            "id": "Robie2017",
            "name": "[split-GAL4 lines for  EB neurons (Robie2017)](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Robie2017)",
            "tags": "DataSet"
          },
          {
            "id": "Otto2020",
            "name": "[EM FAFB Otto et al 2020](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Otto2020)",
            "tags": "DataSet"
          },
          {
            "id": "Kind2021",
            "name": "[EM FAFB Kind et al. 2021](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Kind2021)",
            "tags": "DataSet"
          },
          {
            "id": "FlyLight2019Wu2016",
            "name": "[split-GAL4 lines for LC VPNs (Wu2016)](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FlyLight2019Wu2016)",
            "tags": "DataSet"
          },
          {
            "id": "FlyLight2019Strother2017",
            "name": "[Splits targetting the visual motion pathway, Strother2017](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FlyLight2019Strother2017)",
            "tags": "DataSet"
          },
          {
            "id": "FlyLight2019LateralHorn2019",
            "name": "[FlyLight split-GAL4 lines for Lateral Horn](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FlyLight2019LateralHorn2019)",
            "tags": "DataSet"
          },
          {
            "id": "Engert2022",
            "name": "[EM FAFB Engert et al. 2022](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Engert2022)",
            "tags": "DataSet"
          },
          {
            "id": "Aso2014",
            "name": "[MBONs and split-GAL4 lines that target them (Aso2014)](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Aso2014)",
            "tags": "DataSet"
          }
        ]
      },
      "output_format": "table",
      "count": 71
    },
    {
      "query": "AllDatasets",
      "label": "All available datasets",
      "function": "get_all_datasets",
      "takes": {
        "short_form": {
          "$and": [
            "Template"
          ]
        },
        "default": {
          "short_form": "VFB_00101567"
        }
      },
      "preview": 10,
      "preview_columns": [
        "id",
        "name",
        "tags"
      ],
      "preview_results": {
        "headers": {
          "id": {
            "title": "ID",
            "type": "selection_id",
            "order": -1
          },
          "name": {
            "title": "Dataset",
            "type": "markdown",
            "order": 0
          },
          "tags": {
            "title": "Tags",
            "type": "tags",
            "order": 1
          }
        },
        "rows": [
          {
            "id": "Takemura2023",
            "name": "[Male Adult Nerve Cord (MANC) connectome neurons](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Takemura2023)",
            "tags": "DataSet"
          },
          {
            "id": "Takagi2017",
            "name": "[Larval wave neurons and circuit partners - EM  (Takagi2017)](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Takagi2017)",
            "tags": "DataSet"
          },
          {
            "id": "TaiszGalili2022",
            "name": "[EM FAFB Taisz and Galili et al., 2022](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=TaiszGalili2022)",
            "tags": "DataSet"
          },
          {
            "id": "Robie2017",
            "name": "[split-GAL4 lines for  EB neurons (Robie2017)](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Robie2017)",
            "tags": "DataSet"
          },
          {
            "id": "Otto2020",
            "name": "[EM FAFB Otto et al 2020](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Otto2020)",
            "tags": "DataSet"
          },
          {
            "id": "Kind2021",
            "name": "[EM FAFB Kind et al. 2021](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Kind2021)",
            "tags": "DataSet"
          },
          {
            "id": "Heckscher2015",
            "name": "[Eve+ neurons, sensorimotor circuit - EM (Heckscher2015)](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Heckscher2015)",
            "tags": "DataSet"
          },
          {
            "id": "FlyLight2019LateralHorn2019",
            "name": "[FlyLight split-GAL4 lines for Lateral Horn](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FlyLight2019LateralHorn2019)",
            "tags": "DataSet"
          },
          {
            "id": "Engert2022",
            "name": "[EM FAFB Engert et al. 2022](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=Engert2022)",
            "tags": "DataSet"
          },
          {
            "id": "BrainName_Ito_half_brain",
            "name": "[BrainName neuropils and tracts - Ito half-brain](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=BrainName_Ito_half_brain)",
            "tags": "DataSet"
          }
        ]
      },
      "output_format": "table",
      "count": 115
    }
  ],
  "IsIndividual": true,
  "Images": {
    "VFB_00101567": [
      {
        "id": "VFB_00101567",
        "label": "JRC2018Unisex",
        "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
        "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
        "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd",
        "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz",
        "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj",
        "index": 0,
        "center": {
          "X": 605.0,
          "Y": 283.0,
          "Z": 87.0
        },
        "extent": {
          "X": 1211.0,
          "Y": 567.0,
          "Z": 175.0
        },
        "voxel": {
          "X": 0.5189161,
          "Y": 0.5189161,
          "Z": 1.0
        },
        "orientation": "LPS"
      }
    ]
  },
  "IsClass": false,
  "Examples": {},
  "IsTemplate": true,
  "Domains": {
    "0": {
      "id": "VFB_00101567",
      "label": "JRC2018U",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj",
      "index": 0,
      "center": null,
      "type_label": "adult brain",
      "type_id": "FBbt_00003624"
    },
    "3": {
      "id": "VFB_00102107",
      "label": "ME on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume_man.obj",
      "index": 3,
      "center": null,
      "type_label": "medulla",
      "type_id": "FBbt_00003748"
    },
    "4": {
      "id": "VFB_00102108",
      "label": "AME on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/volume_man.obj",
      "index": 4,
      "center": null,
      "type_label": "accessory medulla",
      "type_id": "FBbt_00045003"
    },
    "5": {
      "id": "VFB_00102109",
      "label": "LO on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/volume_man.obj",
      "index": 5,
      "center": null,
      "type_label": "lobula",
      "type_id": "FBbt_00003852"
    },
    "6": {
      "id": "VFB_00102110",
      "label": "LOP on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/volume_man.obj",
      "index": 6,
      "center": null,
      "type_label": "lobula plate",
      "type_id": "FBbt_00003885"
    },
    "7": {
      "id": "VFB_00102114",
      "label": "CA on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/volume_man.obj",
      "index": 7,
      "center": null,
      "type_label": "calyx of adult mushroom body",
      "type_id": "FBbt_00007385"
    },
    "10": {
      "id": "VFB_00102118",
      "label": "PED on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/volume_man.obj",
      "index": 10,
      "center": null,
      "type_label": "pedunculus of adult mushroom body",
      "type_id": "FBbt_00007453"
    },
    "11": {
      "id": "VFB_00102119",
      "label": "aL on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/volume_man.obj",
      "index": 11,
      "center": null,
      "type_label": "adult mushroom body alpha-lobe",
      "type_id": "FBbt_00110657"
    },
    "12": {
      "id": "VFB_00102121",
      "label": "a\\'L on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/volume_man.obj",
      "index": 12,
      "center": null,
      "type_label": "adult mushroom body alpha'-lobe",
      "type_id": "FBbt_00013691"
    },
    "13": {
      "id": "VFB_00102123",
      "label": "bL on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/volume_man.obj",
      "index": 13,
      "center": null,
      "type_label": "adult mushroom body beta-lobe",
      "type_id": "FBbt_00110658"
    },
    "14": {
      "id": "VFB_00102124",
      "label": "b\\'L on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/volume_man.obj",
      "index": 14,
      "center": null,
      "type_label": "adult mushroom body beta'-lobe",
      "type_id": "FBbt_00013694"
    },
    "15": {
      "id": "VFB_00102133",
      "label": "gL on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/volume_man.obj",
      "index": 15,
      "center": null,
      "type_label": "adult mushroom body gamma-lobe",
      "type_id": "FBbt_00013695"
    },
    "16": {
      "id": "VFB_00102134",
      "label": "FB on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/volume_man.obj",
      "index": 16,
      "center": null,
      "type_label": "fan-shaped body",
      "type_id": "FBbt_00003679"
    },
    "18": {
      "id": "VFB_00102135",
      "label": "EB on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/volume_man.obj",
      "index": 18,
      "center": null,
      "type_label": "ellipsoid body",
      "type_id": "FBbt_00003678"
    },
    "19": {
      "id": "VFB_00102137",
      "label": "PB on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/volume_man.obj",
      "index": 19,
      "center": null,
      "type_label": "protocerebral bridge",
      "type_id": "FBbt_00003668"
    },
    "21": {
      "id": "VFB_00102139",
      "label": "BU on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/volume_man.obj",
      "index": 21,
      "center": null,
      "type_label": "bulb",
      "type_id": "FBbt_00003682"
    },
    "22": {
      "id": "VFB_00102140",
      "label": "LAL on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/volume_man.obj",
      "index": 22,
      "center": null,
      "type_label": "adult lateral accessory lobe",
      "type_id": "FBbt_00003681"
    },
    "23": {
      "id": "VFB_00102141",
      "label": "AOTU on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/volume_man.obj",
      "index": 23,
      "center": null,
      "type_label": "anterior optic tubercle",
      "type_id": "FBbt_00007059"
    },
    "24": {
      "id": "VFB_00102146",
      "label": "AVLP on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/volume_man.obj",
      "index": 24,
      "center": null,
      "type_label": "anterior ventrolateral protocerebrum",
      "type_id": "FBbt_00040043"
    },
    "25": {
      "id": "VFB_00102148",
      "label": "PVLP on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/volume_man.obj",
      "index": 25,
      "center": null,
      "type_label": "posterior ventrolateral protocerebrum",
      "type_id": "FBbt_00040042"
    },
    "26": {
      "id": "VFB_00102152",
      "label": "PLP on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/volume_man.obj",
      "index": 26,
      "center": null,
      "type_label": "posterior lateral protocerebrum",
      "type_id": "FBbt_00040044"
    },
    "27": {
      "id": "VFB_00102154",
      "label": "WED on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/volume_man.obj",
      "index": 27,
      "center": null,
      "type_label": "wedge",
      "type_id": "FBbt_00045027"
    },
    "28": {
      "id": "VFB_00102159",
      "label": "LH on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/volume_man.obj",
      "index": 28,
      "center": null,
      "type_label": "adult lateral horn",
      "type_id": "FBbt_00007053"
    },
    "29": {
      "id": "VFB_00102162",
      "label": "SLP on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/volume_man.obj",
      "index": 29,
      "center": null,
      "type_label": "superior lateral protocerebrum",
      "type_id": "FBbt_00007054"
    },
    "30": {
      "id": "VFB_00102164",
      "label": "SIP on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/volume_man.obj",
      "index": 30,
      "center": null,
      "type_label": "superior intermediate protocerebrum",
      "type_id": "FBbt_00045032"
    },
    "31": {
      "id": "VFB_00102170",
      "label": "SMP on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/volume_man.obj",
      "index": 31,
      "center": null,
      "type_label": "superior medial protocerebrum",
      "type_id": "FBbt_00007055"
    },
    "32": {
      "id": "VFB_00102171",
      "label": "CRE on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/volume_man.obj",
      "index": 32,
      "center": null,
      "type_label": "adult crepine",
      "type_id": "FBbt_00045037"
    },
    "33": {
      "id": "VFB_00102174",
      "label": "ROB on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/volume_man.obj",
      "index": 33,
      "center": null,
      "type_label": "adult round body",
      "type_id": "FBbt_00048509"
    },
    "34": {
      "id": "VFB_00102175",
      "label": "RUB on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/volume_man.obj",
      "index": 34,
      "center": null,
      "type_label": "rubus",
      "type_id": "FBbt_00040038"
    },
    "35": {
      "id": "VFB_00102176",
      "label": "SCL on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/volume_man.obj",
      "index": 35,
      "center": null,
      "type_label": "superior clamp",
      "type_id": "FBbt_00040048"
    },
    "36": {
      "id": "VFB_00102179",
      "label": "ICL on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/volume_man.obj",
      "index": 36,
      "center": null,
      "type_label": "inferior clamp",
      "type_id": "FBbt_00040049"
    },
    "37": {
      "id": "VFB_00102185",
      "label": "IB on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/volume_man.obj",
      "index": 37,
      "center": null,
      "type_label": "inferior bridge",
      "type_id": "FBbt_00040050"
    },
    "38": {
      "id": "VFB_00102190",
      "label": "ATL on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/volume_man.obj",
      "index": 38,
      "center": null,
      "type_label": "antler",
      "type_id": "FBbt_00045039"
    },
    "39": {
      "id": "VFB_00102201",
      "label": "AL on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/volume_man.obj",
      "index": 39,
      "center": null,
      "type_label": "adult antennal lobe",
      "type_id": "FBbt_00007401"
    },
    "40": {
      "id": "VFB_00102212",
      "label": "VES on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/volume_man.obj",
      "index": 40,
      "center": null,
      "type_label": "vest",
      "type_id": "FBbt_00040041"
    },
    "41": {
      "id": "VFB_00102213",
      "label": "EPA on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/volume_man.obj",
      "index": 41,
      "center": null,
      "type_label": "epaulette",
      "type_id": "FBbt_00040040"
    },
    "42": {
      "id": "VFB_00102214",
      "label": "GOR on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/volume_man.obj",
      "index": 42,
      "center": null,
      "type_label": "gorget",
      "type_id": "FBbt_00040039"
    },
    "43": {
      "id": "VFB_00102215",
      "label": "SPS on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/volume_man.obj",
      "index": 43,
      "center": null,
      "type_label": "superior posterior slope",
      "type_id": "FBbt_00045040"
    },
    "44": {
      "id": "VFB_00102218",
      "label": "IPS on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/volume_man.obj",
      "index": 44,
      "center": null,
      "type_label": "inferior posterior slope",
      "type_id": "FBbt_00045046"
    },
    "45": {
      "id": "VFB_00102271",
      "label": "SAD on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/volume_man.obj",
      "index": 45,
      "center": null,
      "type_label": "saddle",
      "type_id": "FBbt_00045048"
    },
    "46": {
      "id": "VFB_00102273",
      "label": "AMMC on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/volume_man.obj",
      "index": 46,
      "center": null,
      "type_label": "antennal mechanosensory and motor center",
      "type_id": "FBbt_00003982"
    },
    "47": {
      "id": "VFB_00102274",
      "label": "FLA on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/volume_man.obj",
      "index": 47,
      "center": null,
      "type_label": "flange",
      "type_id": "FBbt_00045050"
    },
    "48": {
      "id": "VFB_00102275",
      "label": "CAN on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/volume_man.obj",
      "index": 48,
      "center": null,
      "type_label": "cantle",
      "type_id": "FBbt_00045051"
    },
    "49": {
      "id": "VFB_00102276",
      "label": "PRW on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/volume_man.obj",
      "index": 49,
      "center": null,
      "type_label": "prow",
      "type_id": "FBbt_00040051"
    },
    "50": {
      "id": "VFB_00102280",
      "label": "GNG on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/volume_man.obj",
      "index": 50,
      "center": null,
      "type_label": "adult gnathal ganglion",
      "type_id": "FBbt_00014013"
    },
    "59": {
      "id": "VFB_00102281",
      "label": "GA on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/volume_man.obj",
      "index": 59,
      "center": null,
      "type_label": "gall",
      "type_id": "FBbt_00040060"
    },
    "94": {
      "id": "VFB_00102282",
      "label": "NO on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/volume_man.obj",
      "index": 94,
      "center": null,
      "type_label": "nodulus",
      "type_id": "FBbt_00003680"
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
  },
  "Publications": [],
  "Synonyms": []
}
```

Queries:
```python
vfb.get_instances('FBbt_00003748', return_dataframe=False)
```
```json
{
  "headers": {
    "id": {
      "title": "Add",
      "type": "selection_id",
      "order": -1
    },
    "label": {
      "title": "Name",
      "type": "markdown",
      "order": 0,
      "sort": {
        "0": "Asc"
      }
    },
    "parent": {
      "title": "Parent Type",
      "type": "markdown",
      "order": 1
    },
    "template": {
      "title": "Template",
      "type": "markdown",
      "order": 4
    },
    "tags": {
      "title": "Gross Types",
      "type": "tags",
      "order": 3
    },
    "source": {
      "title": "Data Source",
      "type": "markdown",
      "order": 5
    },
    "source_id": {
      "title": "Data Source",
      "type": "markdown",
      "order": 6
    },
    "dataset": {
      "title": "Dataset",
      "type": "markdown",
      "order": 7
    },
    "license": {
      "title": "License",
      "type": "markdown",
      "order": 8
    },
    "thumbnail": {
      "title": "Thumbnail",
      "type": "markdown",
      "order": 9
    }
  },
  "rows": [
    {
      "id": "VFB_00102107",
      "label": "[ME on JRC2018Unisex adult brain](VFB_00102107)",
      "tags": "Nervous_system|Adult|Visual_system|Synaptic_neuropil_domain",
      "parent": "[medulla](FBbt_00003748)",
      "source": "",
      "source_id": "",
      "template": "[JRC2018U](VFB_00101567)",
      "dataset": "[JRC 2018 templates & ROIs](JRC2018)",
      "license": "",
      "thumbnail": "[![ME on JRC2018Unisex adult brain aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png \"ME on JRC2018Unisex adult brain aligned to JRC2018U\")](VFB_00101567,VFB_00102107)"
    },
    {
      "id": "VFB_00101385",
      "label": "[ME(R) on JRC_FlyEM_Hemibrain](VFB_00101385)",
      "tags": "Nervous_system|Adult|Visual_system|Synaptic_neuropil_domain",
      "parent": "[medulla](FBbt_00003748)",
      "source": "",
      "source_id": "",
      "template": "[JRCFIB2018Fum](VFB_00101384)",
      "dataset": "[JRC_FlyEM_Hemibrain painted domains](Xu2020roi)",
      "license": "",
      "thumbnail": "[![ME(R) on JRC_FlyEM_Hemibrain aligned to JRCFIB2018Fum](https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png \"ME(R) on JRC_FlyEM_Hemibrain aligned to JRCFIB2018Fum\")](VFB_00101384,VFB_00101385)"
    },
    {
      "id": "VFB_00030810",
      "label": "[medulla on adult brain template Ito2014](VFB_00030810)",
      "tags": "Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain",
      "parent": "[medulla](FBbt_00003748)",
      "source": "",
      "source_id": "",
      "template": "[adult brain template Ito2014](VFB_00030786)",
      "dataset": "[BrainName neuropils and tracts - Ito half-brain](BrainName_Ito_half_brain)",
      "license": "",
      "thumbnail": "[![medulla on adult brain template Ito2014 aligned to adult brain template Ito2014](https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/thumbnail.png \"medulla on adult brain template Ito2014 aligned to adult brain template Ito2014\")](VFB_00030786,VFB_00030810)"
    },
    {
      "id": "VFB_00030624",
      "label": "[medulla on adult brain template JFRC2](VFB_00030624)",
      "tags": "Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain",
      "parent": "[medulla](FBbt_00003748)",
      "source": "",
      "source_id": "",
      "template": "[JFRC2](VFB_00017894)",
      "dataset": "[BrainName neuropils on adult brain JFRC2 (Jenett, Shinomya)](JenettShinomya_BrainName)",
      "license": "",
      "thumbnail": "[![medulla on adult brain template JFRC2 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/thumbnail.png \"medulla on adult brain template JFRC2 aligned to JFRC2\")](VFB_00017894,VFB_00030624)"
    }
  ],
  "count": 4
}
```

```python
vfb.get_templates(return_dataframe=False)
```
```json
{
  "headers": {
    "id": {
      "title": "Add",
      "type": "selection_id",
      "order": -1
    },
    "order": {
      "title": "Order",
      "type": "numeric",
      "order": 1,
      "sort": {
        "0": "Asc"
      }
    },
    "name": {
      "title": "Name",
      "type": "markdown",
      "order": 1,
      "sort": {
        "1": "Asc"
      }
    },
    "tags": {
      "title": "Tags",
      "type": "tags",
      "order": 2
    },
    "thumbnail": {
      "title": "Thumbnail",
      "type": "markdown",
      "order": 9
    },
    "dataset": {
      "title": "Dataset",
      "type": "metadata",
      "order": 3
    },
    "license": {
      "title": "License",
      "type": "metadata",
      "order": 4
    }
  },
  "rows": [
    {
      "id": "VFB_00200000",
      "order": 2,
      "name": "[JRCVNC2018U](VFB_00200000)",
      "tags": "Nervous_system|Adult|Ganglion",
      "thumbnail": "[![JRCVNC2018U](http://www.virtualflybrain.org/data/VFB/i/0020/0000/VFB_00200000/thumbnail.png 'JRCVNC2018U')](VFB_00200000)",
      "dataset": "[JRC 2018 templates & ROIs](JRC2018)",
      "license": "[CC-BY-NC-SA](VFBlicense_CC_BY_NC_SA_4_0)"
    },
    {
      "id": "VFB_00120000",
      "order": 10,
      "name": "[Adult T1 Leg (Kuan2020)](VFB_00120000)",
      "tags": "Adult|Anatomy",
      "thumbnail": "[![Adult T1 Leg (Kuan2020)](http://www.virtualflybrain.org/data/VFB/i/0012/0000/VFB_00120000/thumbnail.png 'Adult T1 Leg (Kuan2020)')](VFB_00120000)",
      "dataset": "[Millimeter-scale imaging of a Drosophila leg at single-neuron resolution](Kuan2020)",
      "license": "[CC_BY](VFBlicense_CC_BY_4_0)"
    },
    {
      "id": "VFB_00110000",
      "order": 9,
      "name": "[Adult Head (McKellar2020)](VFB_00110000)",
      "tags": "Adult|Anatomy",
      "thumbnail": "[![Adult Head (McKellar2020)](http://www.virtualflybrain.org/data/VFB/i/0011/0000/VFB_00110000/thumbnail.png 'Adult Head (McKellar2020)')](VFB_00110000)",
      "dataset": "[GAL4 lines from McKellar et al., 2020](McKellar2020)",
      "license": "[CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
    },
    {
      "id": "VFB_00101567",
      "order": 1,
      "name": "[JRC2018U](VFB_00101567)",
      "tags": "Nervous_system|Adult",
      "thumbnail": "[![JRC2018U](http://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png 'JRC2018U')](VFB_00101567)",
      "dataset": "[JRC 2018 templates & ROIs](JRC2018)",
      "license": "[CC-BY-NC-SA](VFBlicense_CC_BY_NC_SA_4_0)"
    },
    {
      "id": "VFB_00101384",
      "order": 4,
      "name": "[JRCFIB2018Fum](VFB_00101384)",
      "tags": "Nervous_system|Adult",
      "thumbnail": "[![JRCFIB2018Fum](http://www.virtualflybrain.org/data/VFB/i/0010/1384/VFB_00101384/thumbnail.png 'JRCFIB2018Fum')](VFB_00101384)",
      "dataset": "[JRC_FlyEM_Hemibrain painted domains](Xu2020roi)",
      "license": "[CC_BY](VFBlicense_CC_BY_4_0)"
    },
    {
      "id": "VFB_00100000",
      "order": 7,
      "name": "[COURT2018VNS](VFB_00100000)",
      "tags": "Nervous_system|Adult|Ganglion",
      "thumbnail": "[![COURT2018VNS](http://www.virtualflybrain.org/data/VFB/i/0010/0000/VFB_00100000/thumbnail.png 'COURT2018VNS')](VFB_00100000)",
      "dataset": "[Adult VNS neuropils (Court2017)](Court2017)",
      "license": "[CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
    },
    {
      "id": "VFB_00050000",
      "order": 5,
      "name": "[L1 larval CNS ssTEM - Cardona/Janelia](VFB_00050000)",
      "tags": "Nervous_system|Larva",
      "thumbnail": "[![L1 larval CNS ssTEM - Cardona/Janelia](http://www.virtualflybrain.org/data/VFB/i/0005/0000/VFB_00050000/thumbnail.png 'L1 larval CNS ssTEM - Cardona/Janelia')](VFB_00050000)",
      "dataset": "[larval hugin neurons - EM (Schlegel2016)](Schlegel2016), [Neurons involved in larval fast escape response - EM (Ohyama2016)](Ohyama2015)",
      "license": "[CC_BY](VFBlicense_CC_BY_4_0), [CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
    },
    {
      "id": "VFB_00049000",
      "order": 6,
      "name": "[L3 CNS template - Wood2018](VFB_00049000)",
      "tags": "Nervous_system|Larva",
      "thumbnail": "[![L3 CNS template - Wood2018](http://www.virtualflybrain.org/data/VFB/i/0004/9000/VFB_00049000/thumbnail.png 'L3 CNS template - Wood2018')](VFB_00049000)",
      "dataset": "[L3 Larval CNS Template (Truman2016)](Truman2016)",
      "license": "[CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
    },
    {
      "id": "VFB_00030786",
      "order": 8,
      "name": "[adult brain template Ito2014](VFB_00030786)",
      "tags": "Nervous_system|Adult",
      "thumbnail": "[![adult brain template Ito2014](http://www.virtualflybrain.org/data/VFB/i/0003/0786/VFB_00030786/thumbnail.png 'adult brain template Ito2014')](VFB_00030786)",
      "dataset": "[BrainName neuropils and tracts - Ito half-brain](BrainName_Ito_half_brain)",
      "license": "[CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
    },
    {
      "id": "VFB_00017894",
      "order": 3,
      "name": "[JFRC2](VFB_00017894)",
      "tags": "Nervous_system|Adult",
      "thumbnail": "[![JFRC2](http://www.virtualflybrain.org/data/VFB/i/0001/7894/VFB_00017894/thumbnail.png 'JFRC2')](VFB_00017894)",
      "dataset": "[FlyLight - GMR GAL4 collection (Jenett2012)](Jenett2012)",
      "license": "[CC-BY-NC-SA](VFBlicense_CC_BY_NC_SA_4_0)"
    }
  ],
  "count": 10
}
```
