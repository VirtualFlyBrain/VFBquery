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
                  "thumbnail": "[![ME on JRC2018Unisex adult brain aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png 'ME on JRC2018Unisex adult brain aligned to JRC2018U')](VFB_00101567,VFB_00102107)"
               },
               {
                  "id": "VFB_00101385",
                  "label": "[ME(R) on JRC_FlyEM_Hemibrain](VFB_00101385)",
                  "tags": "Nervous_system|Adult|Visual_system|Synaptic_neuropil_domain",
                  "thumbnail": "[![ME(R) on JRC_FlyEM_Hemibrain aligned to JRCFIB2018Fum](https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png 'ME(R) on JRC_FlyEM_Hemibrain aligned to JRCFIB2018Fum')](VFB_00101384,VFB_00101385)"
               },
               {
                  "id": "VFB_00030810",
                  "label": "[medulla on adult brain template Ito2014](VFB_00030810)",
                  "tags": "Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain",
                  "thumbnail": "[![medulla on adult brain template Ito2014 aligned to adult brain template Ito2014](https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/thumbnail.png 'medulla on adult brain template Ito2014 aligned to adult brain template Ito2014')](VFB_00030786,VFB_00030810)"
               },
               {
                  "id": "VFB_00030624",
                  "label": "[medulla on adult brain template JFRC2](VFB_00030624)",
                  "tags": "Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain",
                  "thumbnail": "[![medulla on adult brain template JFRC2 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/thumbnail.png 'medulla on adult brain template JFRC2 aligned to JFRC2')](VFB_00017894,VFB_00030624)"
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
                  "id": "FBbt_20011362",
                  "label": "[Cm1](FBbt_20011362)",
                  "tags": "Adult|Cholinergic|Nervous_system|Visual_system",
                  "thumbnail": "[![FlyWire:720575940621358986 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw08/9799/VFB_00101567/thumbnail.png 'FlyWire:720575940621358986 aligned to JRC2018U')](FBbt_20011362)"
               },
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
                  "id": "FBbt_00053385",
                  "label": "[medulla intrinsic neuron](FBbt_00053385)",
                  "tags": "Adult|Nervous_system|Neuron|Visual_system",
                  "thumbnail": "[![ME.8543 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/0696/VFB_00101567/thumbnail.png 'ME.8543 aligned to JRC2018U')](FBbt_00053385)"
               },
               {
                  "id": "FBbt_00110033",
                  "label": "[medulla intrinsic neuron vGlutMinew1a](FBbt_00110033)",
                  "tags": "Adult|Glutamatergic|Nervous_system|Visual_system",
                  "thumbnail": ""
               },
               {
                  "id": "FBbt_00110142",
                  "label": "[OA-AL2i2](FBbt_00110142)",
                  "tags": "Adult|Nervous_system|Octopaminergic",
                  "thumbnail": "[![SPS.ME.7 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw04/2336/VFB_00101567/thumbnail.png 'SPS.ME.7 aligned to JRC2018U')](FBbt_00110142)"
               },
               {
                  "id": "FBbt_00110143",
                  "label": "[OA-AL2i3](FBbt_00110143)",
                  "tags": "Adult|Nervous_system|Octopaminergic|Visual_system",
                  "thumbnail": "[![ME.970 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw03/6562/VFB_00101567/thumbnail.png 'ME.970 aligned to JRC2018U')](FBbt_00110143)"
               },
               {
                  "id": "FBbt_00110144",
                  "label": "[OA-AL2i4](FBbt_00110144)",
                  "tags": "Adult|Nervous_system|Octopaminergic",
                  "thumbnail": "[![OA-AL2i4_R (JRC_OpticLobe:10677) aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0010/450b/VFB_00101567/thumbnail.png 'OA-AL2i4_R (JRC_OpticLobe:10677) aligned to JRC2018U')](FBbt_00110144)"
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
                  "id": "FBbt_02000003",
                  "label": "[yR8](FBbt_02000003)",
                  "tags": "Adult|Cholinergic|Histaminergic|Nervous_system|Sensory_neuron|Visual_system",
                  "thumbnail": "[![R8y_R (JRC_OpticLobe:203836) aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0010/48b9/VFB_00101567/thumbnail.png 'R8y_R (JRC_OpticLobe:203836) aligned to JRC2018U')](FBbt_02000003)"
               },
               {
                  "id": "FBbt_20007253",
                  "label": "[CB3838](FBbt_20007253)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![ME.38 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/2030/VFB_00101567/thumbnail.png 'ME.38 aligned to JRC2018U')](FBbt_20007253)"
               },
               {
                  "id": "FBbt_20007256",
                  "label": "[Cm31a](FBbt_20007256)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![ME.5 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/2043/VFB_00101567/thumbnail.png 'ME.5 aligned to JRC2018U')](FBbt_20007256)"
               },
               {
                  "id": "FBbt_20007257",
                  "label": "[Mi19](FBbt_20007257)",
                  "tags": "Adult|Nervous_system|Neuron|Visual_system",
                  "thumbnail": "[![ME.5256 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/1990/VFB_00101567/thumbnail.png 'ME.5256 aligned to JRC2018U')](FBbt_20007257)"
               },
               {
                  "id": "FBbt_20007258",
                  "label": "[Cm35](FBbt_20007258)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![ME.18 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/2034/VFB_00101567/thumbnail.png 'ME.18 aligned to JRC2018U')](FBbt_20007258)"
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
                  "id": "FBbt_20007253",
                  "label": "[CB3838](FBbt_20007253)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![ME.38 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/2030/VFB_00101567/thumbnail.png 'ME.38 aligned to JRC2018U')](FBbt_20007253)"
               },
               {
                  "id": "FBbt_20007256",
                  "label": "[Cm31a](FBbt_20007256)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![ME.5 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/2043/VFB_00101567/thumbnail.png 'ME.5 aligned to JRC2018U')](FBbt_20007256)"
               },
               {
                  "id": "FBbt_20007257",
                  "label": "[Mi19](FBbt_20007257)",
                  "tags": "Adult|Nervous_system|Neuron|Visual_system",
                  "thumbnail": "[![ME.5256 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/1990/VFB_00101567/thumbnail.png 'ME.5256 aligned to JRC2018U')](FBbt_20007257)"
               },
               {
                  "id": "FBbt_20007258",
                  "label": "[Cm35](FBbt_20007258)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![ME.18 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/2034/VFB_00101567/thumbnail.png 'ME.18 aligned to JRC2018U')](FBbt_20007258)"
               },
               {
                  "id": "FBbt_20007259",
                  "label": "[Cm32](FBbt_20007259)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system",
                  "thumbnail": "[![ME.278 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/fw06/1913/VFB_00101567/thumbnail.png 'ME.278 aligned to JRC2018U')](FBbt_20007259)"
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
                  "id": "FBbt_00003922",
                  "label": "[second optic chiasma](FBbt_00003922)",
                  "tags": "Adult|Nervous_system|Neuron_projection_bundle|Visual_system",
                  "thumbnail": ""
               },
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
                  "id": "FBbt_00050013",
                  "label": "[adult VPNl&d1 lineage clone](FBbt_00050013)",
                  "tags": "Adult|Clone",
                  "thumbnail": "[![VPNl&d1 clone of Ito 2013 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0002/0253/VFB_00101567/thumbnail.png 'VPNl&d1 clone of Ito 2013 aligned to JRC2018U')](FBbt_00050013)"
               },
               {
                  "id": "FBbt_00050019",
                  "label": "[adult DM1 lineage clone](FBbt_00050019)",
                  "tags": "Adult|Clone|lineage_DPMm1",
                  "thumbnail": "[![DM1 clone of Yu 2013 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0002/0006/VFB_00017894/thumbnail.png 'DM1 clone of Yu 2013 aligned to JFRC2')](FBbt_00050019)"
               },
               {
                  "id": "FBbt_00050051",
                  "label": "[adult VESa2 lineage clone](FBbt_00050051)",
                  "tags": "Adult|Clone|lineage_BAlp1",
                  "thumbnail": "[![PSa1 clone of Ito 2013 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0002/0206/VFB_00101567/thumbnail.png 'PSa1 clone of Ito 2013 aligned to JRC2018U')](FBbt_00050051)"
               },
               {
                  "id": "FBbt_00050167",
                  "label": "[adult LALv1 lineage clone](FBbt_00050167)",
                  "tags": "Adult|Clone|lineage_BAmv1",
                  "thumbnail": "[![LALv1 clone of Yu 2013 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0002/0056/VFB_00101567/thumbnail.png 'LALv1 clone of Yu 2013 aligned to JRC2018U')](FBbt_00050167)"
               },
               {
                  "id": "FBbt_00050229",
                  "label": "[adult SLPpl1 lineage clone](FBbt_00050229)",
                  "tags": "Adult|Clone|lineage_DPLl1",
                  "thumbnail": "[![SLPpl1 clone of Yu 2013 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0002/0077/VFB_00101567/thumbnail.png 'SLPpl1 clone of Yu 2013 aligned to JRC2018U')](FBbt_00050229)"
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
                  "id": "VFB_fw113167",
                  "label": "[ME.11974](VFB_fw113167)",
                  "tags": "Adult|Glutamatergic|Nervous_system|Visual_system",
                  "thumbnail": ""
               },
               {
                  "id": "VFB_fw113165",
                  "label": "[ME.17216](VFB_fw113165)",
                  "tags": "Adult|GABAergic|Nervous_system|Visual_system|secondary_neuron",
                  "thumbnail": ""
               },
               {
                  "id": "VFB_fw113168",
                  "label": "[ME.31287](VFB_fw113168)",
                  "tags": "Adult|Glutamatergic|Nervous_system|Visual_system",
                  "thumbnail": ""
               },
               {
                  "id": "VFB_fw113166",
                  "label": "[ME.4619](VFB_fw113166)",
                  "tags": "Adult|Cholinergic|Nervous_system|Visual_system|secondary_neuron",
                  "thumbnail": ""
               },
               {
                  "id": "VFB_fw113169",
                  "label": "[ME.26172](VFB_fw113169)",
                  "tags": "Adult|Cholinergic|Nervous_system|Visual_system|secondary_neuron",
                  "thumbnail": ""
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
                  "id": "VFBexp_FBti0143533",
                  "name": "[PBac{544.SVS-1}B4[CPTI100035] expression pattern](VFBexp_FBti0143533)",
                  "tags": "Expression_pattern"
               },
               {
                  "id": "VFBexp_FBti0143547",
                  "name": "[PBac{544.SVS-1}Fer2LCH[CPTI100064] expression pattern](VFBexp_FBti0143547)",
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
         "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnailT.png",
         "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/volume.nrrd",
         "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/volume.wlz",
         "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/volume_man.obj",
         "index": 49,
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
   }
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
         "thumbnail": "[![ME on JRC2018Unisex adult brain aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png 'ME on JRC2018Unisex adult brain aligned to JRC2018U')](VFB_00101567,VFB_00102107)"
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
         "thumbnail": "[![ME(R) on JRC_FlyEM_Hemibrain aligned to JRCFIB2018Fum](https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png 'ME(R) on JRC_FlyEM_Hemibrain aligned to JRCFIB2018Fum')](VFB_00101384,VFB_00101385)"
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
         "thumbnail": "[![medulla on adult brain template Ito2014 aligned to adult brain template Ito2014](https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/thumbnail.png 'medulla on adult brain template Ito2014 aligned to adult brain template Ito2014')](VFB_00030786,VFB_00030810)"
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
         "thumbnail": "[![medulla on adult brain template JFRC2 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/thumbnail.png 'medulla on adult brain template JFRC2 aligned to JFRC2')](VFB_00017894,VFB_00030624)"
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
         "thumbnail": "[![JRCVNC2018U](https://www.virtualflybrain.org/data/VFB/i/0020/0000/VFB_00200000/thumbnail.png 'JRCVNC2018U')](VFB_00200000)",
         "dataset": "[JRC 2018 templates & ROIs](JRC2018)",
         "license": "[CC-BY-NC-SA](VFBlicense_CC_BY_NC_SA_4_0)"
      },
      {
         "id": "VFB_00120000",
         "order": 10,
         "name": "[Adult T1 Leg (Kuan2020)](VFB_00120000)",
         "tags": "Adult|Anatomy",
         "thumbnail": "[![Adult T1 Leg (Kuan2020)](https://www.virtualflybrain.org/data/VFB/i/0012/0000/VFB_00120000/thumbnail.png 'Adult T1 Leg (Kuan2020)')](VFB_00120000)",
         "dataset": "[Millimeter-scale imaging of a Drosophila leg at single-neuron resolution](Kuan2020)",
         "license": "[CC_BY](VFBlicense_CC_BY_4_0)"
      },
      {
         "id": "VFB_00110000",
         "order": 9,
         "name": "[Adult Head (McKellar2020)](VFB_00110000)",
         "tags": "Adult|Anatomy",
         "thumbnail": "[![Adult Head (McKellar2020)](https://www.virtualflybrain.org/data/VFB/i/0011/0000/VFB_00110000/thumbnail.png 'Adult Head (McKellar2020)')](VFB_00110000)",
         "dataset": "[GAL4 lines from McKellar et al., 2020](McKellar2020)",
         "license": "[CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
      },
      {
         "id": "VFB_00101567",
         "order": 1,
         "name": "[JRC2018U](VFB_00101567)",
         "tags": "Nervous_system|Adult",
         "thumbnail": "[![JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png 'JRC2018U')](VFB_00101567)",
         "dataset": "[JRC 2018 templates & ROIs](JRC2018)",
         "license": "[CC-BY-NC-SA](VFBlicense_CC_BY_NC_SA_4_0)"
      },
      {
         "id": "VFB_00101384",
         "order": 4,
         "name": "[JRCFIB2018Fum](VFB_00101384)",
         "tags": "Nervous_system|Adult",
         "thumbnail": "[![JRCFIB2018Fum](https://www.virtualflybrain.org/data/VFB/i/0010/1384/VFB_00101384/thumbnail.png 'JRCFIB2018Fum')](VFB_00101384)",
         "dataset": "[JRC_FlyEM_Hemibrain painted domains](Xu2020roi)",
         "license": "[CC_BY](VFBlicense_CC_BY_4_0)"
      },
      {
         "id": "VFB_00100000",
         "order": 7,
         "name": "[COURT2018VNS](VFB_00100000)",
         "tags": "Nervous_system|Adult|Ganglion",
         "thumbnail": "[![COURT2018VNS](https://www.virtualflybrain.org/data/VFB/i/0010/0000/VFB_00100000/thumbnail.png 'COURT2018VNS')](VFB_00100000)",
         "dataset": "[Adult VNS neuropils (Court2017)](Court2017)",
         "license": "[CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
      },
      {
         "id": "VFB_00050000",
         "order": 5,
         "name": "[L1 larval CNS ssTEM - Cardona/Janelia](VFB_00050000)",
         "tags": "Nervous_system|Larva",
         "thumbnail": "[![L1 larval CNS ssTEM - Cardona/Janelia](https://www.virtualflybrain.org/data/VFB/i/0005/0000/VFB_00050000/thumbnail.png 'L1 larval CNS ssTEM - Cardona/Janelia')](VFB_00050000)",
         "dataset": "[larval hugin neurons - EM (Schlegel2016)](Schlegel2016), [Neurons involved in larval fast escape response - EM (Ohyama2016)](Ohyama2015)",
         "license": "[CC_BY](VFBlicense_CC_BY_4_0), [CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
      },
      {
         "id": "VFB_00049000",
         "order": 6,
         "name": "[L3 CNS template - Wood2018](VFB_00049000)",
         "tags": "Nervous_system|Larva",
         "thumbnail": "[![L3 CNS template - Wood2018](https://www.virtualflybrain.org/data/VFB/i/0004/9000/VFB_00049000/thumbnail.png 'L3 CNS template - Wood2018')](VFB_00049000)",
         "dataset": "[L3 Larval CNS Template (Truman2016)](Truman2016)",
         "license": "[CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
      },
      {
         "id": "VFB_00030786",
         "order": 8,
         "name": "[adult brain template Ito2014](VFB_00030786)",
         "tags": "Nervous_system|Adult",
         "thumbnail": "[![adult brain template Ito2014](https://www.virtualflybrain.org/data/VFB/i/0003/0786/VFB_00030786/thumbnail.png 'adult brain template Ito2014')](VFB_00030786)",
         "dataset": "[BrainName neuropils and tracts - Ito half-brain](BrainName_Ito_half_brain)",
         "license": "[CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
      },
      {
         "id": "VFB_00017894",
         "order": 3,
         "name": "[JFRC2](VFB_00017894)",
         "tags": "Nervous_system|Adult",
         "thumbnail": "[![JFRC2](https://www.virtualflybrain.org/data/VFB/i/0001/7894/VFB_00017894/thumbnail.png 'JFRC2')](VFB_00017894)",
         "dataset": "[FlyLight - GMR GAL4 collection (Jenett2012)](Jenett2012)",
         "license": "[CC-BY-NC-SA](VFBlicense_CC_BY_NC_SA_4_0)"
      }
   ],
   "count": 10
}
```
