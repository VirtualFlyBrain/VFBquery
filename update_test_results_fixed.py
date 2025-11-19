import ast

with open('test_results.py', 'r') as f:
    content = f.read()

old_results = ast.literal_eval(content.split('results = ')[1])

# Update with new medulla
old_results[0] = {
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
        ],
        "count": 4
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
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/thumbnail.png 'fru-M-200266 aligned to JFRC2')](VFB_00017894,VFB_00000001)"
          },
          {
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/thumbnail.png 'fru-M-200266 aligned to JRC2018U')](VFB_00101567,VFB_00000001)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00017894/thumbnail.png 'fru-M-000204 aligned to JFRC2')](VFB_00017894,VFB_00000333)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00101567/thumbnail.png 'fru-M-000204 aligned to JRC2018U')](VFB_00101567,VFB_00000333)"
          },
          {
            "id": "VFB_00002439",
            "label": "[fru-M-900020](VFB_00002439)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-900020 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00101567/thumbnail.png 'fru-M-900020 aligned to JRC2018U')](VFB_00101567,VFB_00002439)"
          }
        ],
        "count": 60
      },
      "output_format": "table",
      "count": 60
    },
    {
      "query": "NeuronsSynaptic",
      "label": "Neurons with synapses in medulla",
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
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/thumbnail.png 'fru-M-200266 aligned to JFRC2')](VFB_00017894,VFB_00000001)"
          },
          {
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/thumbnail.png 'fru-M-200266 aligned to JRC2018U')](VFB_00101567,VFB_00000001)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00017894/thumbnail.png 'fru-M-000204 aligned to JFRC2')](VFB_00017894,VFB_00000333)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00101567/thumbnail.png 'fru-M-000204 aligned to JRC2018U')](VFB_00101567,VFB_00000333)"
          },
          {
            "id": "VFB_00002439",
            "label": "[fru-M-900020](VFB_00002439)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-900020 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00101567/thumbnail.png 'fru-M-900020 aligned to JRC2018U')](VFB_00101567,VFB_00002439)"
          }
        ],
        "count": 60
      },
      "output_format": "table",
      "count": 60
    },
    {
      "query": "NeuronsPresynaptic",
      "label": "Neurons with presynaptic sites in medulla",
      "function": "get_neurons_with_presynaptic_sites_in",
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
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/thumbnail.png 'fru-M-200266 aligned to JFRC2')](VFB_00017894,VFB_00000001)"
          },
          {
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/thumbnail.png 'fru-M-200266 aligned to JRC2018U')](VFB_00101567,VFB_00000001)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00017894/thumbnail.png 'fru-M-000204 aligned to JFRC2')](VFB_00017894,VFB_00000333)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00101567/thumbnail.png 'fru-M-000204 aligned to JRC2018U')](VFB_00101567,VFB_00000333)"
          },
          {
            "id": "VFB_00002439",
            "label": "[fru-M-900020](VFB_00002439)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-900020 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00101567/thumbnail.png 'fru-M-900020 aligned to JRC2018U')](VFB_00101567,VFB_00002439)"
          }
        ],
        "count": 60
      },
      "output_format": "table",
      "count": 60
    },
    {
      "query": "NeuronsPostsynaptic",
      "label": "Neurons with postsynaptic sites in medulla",
      "function": "get_neurons_with_postsynaptic_sites_in",
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
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/thumbnail.png 'fru-M-200266 aligned to JFRC2')](VFB_00017894,VFB_00000001)"
          },
          {
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/thumbnail.png 'fru-M-200266 aligned to JRC2018U')](VFB_00101567,VFB_00000001)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00017894/thumbnail.png 'fru-M-000204 aligned to JFRC2')](VFB_00017894,VFB_00000333)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00101567/thumbnail.png 'fru-M-000204 aligned to JRC2018U')](VFB_00101567,VFB_00000333)"
          },
          {
            "id": "VFB_00002439",
            "label": "[fru-M-900020](VFB_00002439)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-900020 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00101567/thumbnail.png 'fru-M-900020 aligned to JRC2018U')](VFB_00101567,VFB_00002439)"
          }
        ],
        "count": 60
      },
      "output_format": "table",
      "count": 60
    },
    {
      "query": "PartsOf",
      "label": "Parts of medulla",
      "function": "get_parts_of",
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
            "id": "FBbt_00007387",
            "label": "medulla layer M1",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M1](http://www.virtualflybrain.org/data/VFB/i/0000/7387/FBbt_00007387/thumbnail.png 'medulla layer M1')](FBbt_00007387)"
          },
          {
            "id": "FBbt_00007388",
            "label": "medulla layer M2",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M2](http://www.virtualflybrain.org/data/VFB/i/0000/7388/FBbt_00007388/thumbnail.png 'medulla layer M2')](FBbt_00007388)"
          },
          {
            "id": "FBbt_00007389",
            "label": "medulla layer M3",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M3](http://www.virtualflybrain.org/data/VFB/i/0000/7389/FBbt_00007389/thumbnail.png 'medulla layer M3')](FBbt_00007389)"
          },
          {
            "id": "FBbt_00007390",
            "label": "medulla layer M4",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M4](http://www.virtualflybrain.org/data/VFB/i/0000/7390/FBbt_00007390/thumbnail.png 'medulla layer M4')](FBbt_00007390)"
          },
          {
            "id": "FBbt_00007391",
            "label": "medulla layer M5",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M5](http://www.virtualflybrain.org/data/VFB/i/0000/7391/FBbt_00007391/thumbnail.png 'medulla layer M5')](FBbt_00007391)"
          }
        ],
        "count": 10
      },
      "output_format": "table",
      "count": 10
    },
    {
      "query": "SubclassesOf",
      "label": "Subclasses of medulla",
      "function": "get_subclasses_of",
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
            "id": "FBbt_00007387",
            "label": "medulla layer M1",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M1](http://www.virtualflybrain.org/data/VFB/i/0000/7387/FBbt_00007387/thumbnail.png 'medulla layer M1')](FBbt_00007387)"
          },
          {
            "id": "FBbt_00007388",
            "label": "medulla layer M2",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M2](http://www.virtualflybrain.org/data/VFB/i/0000/7388/FBbt_00007388/thumbnail.png 'medulla layer M2')](FBbt_00007388)"
          },
          {
            "id": "FBbt_00007389",
            "label": "medulla layer M3",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M3](http://www.virtualflybrain.org/data/VFB/i/0000/7389/FBbt_00007389/thumbnail.png 'medulla layer M3')](FBbt_00007389)"
          },
          {
            "id": "FBbt_00007390",
            "label": "medulla layer M4",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M4](http://www.virtualflybrain.org/data/VFB/i/0000/7390/FBbt_00007390/thumbnail.png 'medulla layer M4')](FBbt_00007390)"
          },
          {
            "id": "FBbt_00007391",
            "label": "medulla layer M5",
            "tags": "Nervous_system|Adult|Synaptic_neuropil_domain|Visual_system",
            "thumbnail": "[![medulla layer M5](http://www.virtualflybrain.org/data/VFB/i/0000/7391/FBbt_00007391/thumbnail.png 'medulla layer M5')](FBbt_00007391)"
          }
        ],
        "count": 10
      },
      "output_format": "table",
      "count": 10
    },
    {
      "query": "TractsNervesInnervatingHere",
      "label": "Tracts and nerves innervating medulla",
      "function": "get_tracts_nerves_innervating_here",
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
            "id": "FBbt_00003682",
            "label": "bulb",
            "tags": "Nervous_system|Adult",
            "thumbnail": "[![bulb](http://www.virtualflybrain.org/data/VFB/i/0000/3682/FBbt_00003682/thumbnail.png 'bulb')](FBbt_00003682)"
          },
          {
            "id": "FBbt_00003681",
            "label": "adult lateral accessory lobe",
            "tags": "Nervous_system|Adult",
            "thumbnail": "[![adult lateral accessory lobe](http://www.virtualflybrain.org/data/VFB/i/0000/3681/FBbt_00003681/thumbnail.png 'adult lateral accessory lobe')](FBbt_00003681)"
          },
          {
            "id": "FBbt_00003679",
            "label": "fan-shaped body",
            "tags": "Nervous_system|Adult",
            "thumbnail": "[![fan-shaped body](http://www.virtualflybrain.org/data/VFB/i/0000/3679/FBbt_00003679/thumbnail.png 'fan-shaped body')](FBbt_00003679)"
          },
          {
            "id": "FBbt_00003678",
            "label": "ellipsoid body",
            "tags": "Nervous_system|Adult",
            "thumbnail": "[![ellipsoid body](http://www.virtualflybrain.org/data/VFB/i/0000/3678/FBbt_00003678/thumbnail.png 'ellipsoid body')](FBbt_00003678)"
          },
          {
            "id": "FBbt_00003668",
            "label": "protocerebral bridge",
            "tags": "Nervous_system|Adult",
            "thumbnail": "[![protocerebral bridge](http://www.virtualflybrain.org/data/VFB/i/0000/3668/FBbt_00003668/thumbnail.png 'protocerebral bridge')](FBbt_00003668)"
          }
        ],
        "count": 5
      },
      "output_format": "table",
      "count": 5
    },
    {
      "query": "LineageClonesIn",
      "label": "Lineage clones in medulla",
      "function": "get_lineage_clones_in",
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
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/thumbnail.png 'fru-M-200266 aligned to JFRC2')](VFB_00017894,VFB_00000001)"
          },
          {
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/thumbnail.png 'fru-M-200266 aligned to JRC2018U')](VFB_00101567,VFB_00000001)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00017894/thumbnail.png 'fru-M-000204 aligned to JFRC2')](VFB_00017894,VFB_00000333)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00101567/thumbnail.png 'fru-M-000204 aligned to JRC2018U')](VFB_00101567,VFB_00000333)"
          },
          {
            "id": "VFB_00002439",
            "label": "[fru-M-900020](VFB_00002439)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-900020 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00101567/thumbnail.png 'fru-M-900020 aligned to JRC2018U')](VFB_00101567,VFB_00002439)"
          }
        ],
        "count": 60
      },
      "output_format": "table",
      "count": 60
    },
    {
      "query": "ImagesNeurons",
      "label": "Images of neurons in medulla",
      "function": "get_images_neurons",
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
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00017894/thumbnail.png 'fru-M-200266 aligned to JFRC2')](VFB_00017894,VFB_00000001)"
          },
          {
            "id": "VFB_00000001",
            "label": "[fru-M-200266](VFB_00000001)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-200266 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/thumbnail.png 'fru-M-200266 aligned to JRC2018U')](VFB_00101567,VFB_00000001)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JFRC2](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00017894/thumbnail.png 'fru-M-000204 aligned to JFRC2')](VFB_00017894,VFB_00000333)"
          },
          {
            "id": "VFB_00000333",
            "label": "[fru-M-000204](VFB_00000333)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-000204 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00101567/thumbnail.png 'fru-M-000204 aligned to JRC2018U')](VFB_00101567,VFB_00000333)"
          },
          {
            "id": "VFB_00002439",
            "label": "[fru-M-900020](VFB_00002439)",
            "tags": "Expression_pattern_fragment|Neuron|Adult|lineage_CM3",
            "thumbnail": "[![fru-M-900020 aligned to JRC2018U](https://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00101567/thumbnail.png 'fru-M-900020 aligned to JRC2018U')](VFB_00101567,VFB_00002439)"
          }
        ],
        "count": 60
      },
      "output_format": "table",
      "count": 60
    }
  ],
  "IsIndividual": False,
  "IsClass": True,
  "IsTemplate": False,
  "Domains": {
    "0": {
      "id": "VFB_00102107",
      "label": "ME on JRC2018Unisex adult brain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume_man.obj",
      "index": 3,
      "type_label": "medulla",
      "type_id": "FBbt_00003748"
    },
    "1": {
      "id": "VFB_00101385",
      "label": "ME(R) on JRC_FlyEM_Hemibrain",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume_man.obj",
      "index": 0,
      "type_label": "medulla",
      "type_id": "FBbt_00003748"
    },
    "2": {
      "id": "VFB_00030810",
      "label": "medulla on adult brain template Ito2014",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0003/0810/VFB_00030786/volume_man.obj",
      "index": 0,
      "type_label": "medulla",
      "type_id": "FBbt_00003748"
    },
    "3": {
      "id": "VFB_00030624",
      "label": "medulla on adult brain template JFRC2",
      "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/thumbnail.png",
      "thumbnail_transparent": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/thumbnailT.png",
      "nrrd": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/volume.nrrd",
      "wlz": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/volume.wlz",
      "obj": "https://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/volume_man.obj",
      "index": 0,
      "type_label": "medulla",
      "type_id": "FBbt_00003748"
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

# Update instances to dict
old_results[3] = {
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
  ],
  "count": 4
}

# Update templates
old_results.append({
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
      "order": 6,
      "name": "[L1 larval CNS ssTEM - Cardona/Janelia](VFB_00050000)",
      "tags": "Nervous_system|Larva",
      "thumbnail": "[![L1 larval CNS ssTEM - Cardona/Janelia](http://www.virtualflybrain.org/data/VFB/i/0005/0000/VFB_00050000/thumbnail.png 'L1 larval CNS ssTEM - Cardona/Janelia')](VFB_00050000)",
      "dataset": "[larval hugin neurons - EM (Schlegel2016)](Schlegel2016), [Neurons involved in larval fast escape response - EM (Ohyama2016)](Ohyama2015)",
      "license": "[CC_BY](VFBlicense_CC_BY_4_0), [CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
    },
    {
      "id": "VFB_00049000",
      "order": 5,
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
      "thumbnail": "[![JFRC2](http://www.virtualflybrain.org/data/VFB/i/0000/7894/VFB_00017894/thumbnail.png 'JFRC2')](VFB_00017894)",
      "dataset": "[FlyLight - GMR GAL4 collection (Jenett2012)](Jenett2012)",
      "license": "[CC-BY-NC-SA](VFBlicense_CC_BY_NC_SA_4_0)"
    }
  ],
  "count": 10
}

import json

new_content = 'from src.vfbquery.term_info_queries import *\nimport json\nresults = json.loads(''' + json.dumps(old_results) + ''')'

with open('test_results.py', 'w') as f:
    f.write(new_content)