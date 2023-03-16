# VFBquery

to setup requirements:
```bash
pip install --upgrade vfbquery
```

To get term info for a term:
get_term_info(ID)

e.g.
```python
import vfbquery as vfb
```
Class example:
```
vfb.get_term_info('FBbt_00003748')
```
```python
{
   "Meta":{
      "Name":"[medulla](FBbt_00003748)",
      "Description":"The second optic neuropil, sandwiched between the lamina and the lobula complex. It is divided into 10 layers: 1-6 make up the outer (distal) medulla, the seventh (or serpentine) layer exhibits a distinct architecture and layers 8-10 make up the inner (proximal) medulla (Ito et al., 2014).",
      "Comment":""
   },
   "Id":"FBbt_00003748",
   "Name":"medulla",
   "SuperTypes":[
      "Entity",
      "Adult",
      "Anatomy",
      "Class",
      "Nervous_system",
      "Synaptic_neuropil",
      "Synaptic_neuropil_domain",
      "Visual_system"
   ],
   "IsClass":true,
   "Tags":[
      "Adult",
      "Nervous_system",
      "Synaptic_neuropil_domain",
      "Visual_system"
   ],
   "Examples":{
      "VFB_00030786":[
         {
            "id":"VFB_00030810",
            "label":"medulla on adult brain template Ito2014",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnailT.png",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.nrrd",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume_man.obj",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.wlz"
         }
      ],
      "VFB_00101567":[
         {
            "id":"VFB_00102107",
            "label":"ME on JRC2018Unisex adult brain",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.nrrd",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume_man.obj",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.wlz"
         }
      ],
      "VFB_00017894":[
         {
            "id":"VFB_00030624",
            "label":"medulla on adult brain template JFRC2",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnailT.png",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.nrrd",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume_man.obj",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.wlz"
         }
      ],
      "VFB_00101384":[
         {
            "id":"VFB_00101385",
            "label":"ME(R) on JRC_FlyEM_Hemibrain",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnailT.png",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.nrrd",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume_man.obj",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.wlz"
         }
      ]
   },
   "Queries":[
      {
         "query":"ListAllAvailableImages",
         "label":"List all available images of medulla",
         "function":"get_instances",
         "takes":{
            "short_form":{
               "$and":[
                  "Class",
                  "Anatomy"
               ]
            },
            "default":"FBbt_00003748"
         }
      }
   ]
}{
   "Examples":{
      "VFB_00030786":[
         {
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume_man.obj",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnail.png",
            "id":"VFB_00030810",
            "label":"medulla on adult brain template Ito2014",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.wlz",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.nrrd"
         }
      ],
      "VFB_00101567":[
         {
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume_man.obj",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
            "id":"VFB_00102107",
            "label":"ME on JRC2018Unisex adult brain",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.wlz",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.nrrd"
         }
      ],
      "VFB_00017894":[
         {
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume_man.obj",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnail.png",
            "id":"VFB_00030624",
            "label":"medulla on adult brain template JFRC2",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.wlz",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.nrrd"
         }
      ],
      "VFB_00101384":[
         {
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume_man.obj",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png",
            "id":"VFB_00101385",
            "label":"ME(R) on JRC_FlyEM_Hemibrain",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.wlz",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.nrrd"
         }
      ]
   },
   "IsIndividual":false,
   "Queries":[
      {
         "query":"ListAllAvailableImages",
         "label":"List all available images of medulla",
         "function":"get_instances",
         "takes":{
            "short_form":{
               "$and":[
                  "Class",
                  "Anatomy"
               ]
            },
            "default":"FBbt_00003748"
         }
      }
   ],
   "SuperTypes":[
      "Entity",
      "Adult",
      "Anatomy",
      "Class",
      "Nervous_system",
      "Synaptic_neuropil",
      "Synaptic_neuropil_domain",
      "Visual_system"
   ],
   "IsClass":true,
   "IsTemplate":false,
   "Name":"medulla",
   "Id":"FBbt_00003748",
   "Meta":{
      "Name":"[medulla](FBbt_00003748)",
      "Description":"The second optic neuropil, sandwiched between the lamina and the lobula complex. It is divided into 10 layers: 1-6 make up the outer (distal) medulla, the seventh (or serpentine) layer exhibits a distinct architecture and layers 8-10 make up the inner (proximal) medulla (Ito et al., 2014).",
      "Comment":""
   },
   "Tags":[
      "Adult",
      "Nervous_system",
      "Synaptic_neuropil_domain",
      "Visual_system"
   ]
}
```
Individual example:
```python
vfb.get_term_info('VFB_00000001')
```

```python
{
   "Meta":{
      "Name":"[fru-M-200266](VFB_00000001)",
      "Description":"",
      "Comment":"OutAge: Adult 5~15 days"
   },
   "Id":"VFB_00000001",
   "Name":"fru-M-200266",
   "SuperTypes":[
      "Entity",
      "Adult",
      "Anatomy",
      "Cell",
      "Expression_pattern_fragment",
      "Individual",
      "Nervous_system",
      "Neuron",
      "VFB",
      "has_image",
      "FlyCircuit",
      "NBLAST"
   ],
   "IsIndividual":true,
   "Tags":[
      "Adult",
      "Expression_pattern_fragment",
      "Nervous_system",
      "Neuron"
   ],
   "Images":{
      "VFB_00101567":[
         {
            "id":"VFB_00000001",
            "label":"fru-M-200266",
            "thumbnail":"https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png",
            "thumbnail_transparent":"https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.nrrd",
            "obj":"https://virtualflybrain.org/reports/VFB_00000001/volume.obj",
            "wlz":"https://virtualflybrain.org/reports/VFB_00000001/volume.wlz",
            "swc":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.swc"
         }
      ],
      "VFB_00017894":[
         {
            "id":"VFB_00000001",
            "label":"fru-M-200266",
            "thumbnail":"https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png",
            "thumbnail_transparent":"https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.nrrd",
            "obj":"https://virtualflybrain.org/reports/VFB_00000001/volume.obj",
            "wlz":"https://virtualflybrain.org/reports/VFB_00000001/volume.wlz",
            "swc":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.swc"
         }
      ]
   },
   "Queries":[
      {
         "query":"SimilarMorphologyTo",
         "label":"Find similar neurons to fru-M-200266",
         "function":"get_similar_neurons",
         "takes":{
            "short_form":{
               "$and":[
                  "Individual",
                  "Neuron"
               ]
            },
            "default":"VFB_00000001"
         }
      }
   ]
}{
   "IsIndividual":true,
   "Queries":[
      {
         "query":"SimilarMorphologyTo",
         "label":"Find similar neurons to fru-M-200266",
         "function":"get_similar_neurons",
         "takes":{
            "short_form":{
               "$and":[
                  "Individual",
                  "Neuron"
               ]
            },
            "default":"VFB_00000001"
         }
      }
   ],
   "SuperTypes":[
      "Entity",
      "Adult",
      "Anatomy",
      "Cell",
      "Expression_pattern_fragment",
      "Individual",
      "Nervous_system",
      "Neuron",
      "VFB",
      "has_image",
      "FlyCircuit",
      "NBLAST"
   ],
   "Images":{
      "VFB_00101567":[
         {
            "obj":"https://virtualflybrain.org/reports/VFB_00000001/volume.obj",
            "swc":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.swc",
            "thumbnail":"https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png",
            "id":"VFB_00000001",
            "label":"fru-M-200266",
            "thumbnail_transparent":"https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png",
            "wlz":"https://virtualflybrain.org/reports/VFB_00000001/volume.wlz",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.nrrd"
         }
      ],
      "VFB_00017894":[
         {
            "obj":"https://virtualflybrain.org/reports/VFB_00000001/volume.obj",
            "swc":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.swc",
            "thumbnail":"https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png",
            "id":"VFB_00000001",
            "label":"fru-M-200266",
            "thumbnail_transparent":"https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png",
            "wlz":"https://virtualflybrain.org/reports/VFB_00000001/volume.wlz",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.nrrd"
         }
      ]
   },
   "IsClass":false,
   "IsTemplate":false,
   "Name":"fru-M-200266",
   "Id":"VFB_00000001",
   "Meta":{
      "Name":"[fru-M-200266](VFB_00000001)",
      "Description":"",
      "Comment":"OutAge: Adult 5~15 days"
   },
   "Tags":[
      "Adult",
      "Expression_pattern_fragment",
      "Nervous_system",
      "Neuron"
   ]
}
 ```
Template example:
```python
vfb.get_term_info('VFB_00101567')
```

```python
{
   "Meta":{
      "Name":"[JRC2018Unisex](VFB_00101567)",
      "Description":"Janelia 2018 unisex, averaged adult brain template",
      "Comment":""
   },
   "Id":"VFB_00101567",
   "Name":"JRC2018Unisex",
   "SuperTypes":[
      "Entity",
      "Adult",
      "Anatomy",
      "Individual",
      "Nervous_system",
      "Template",
      "has_image"
   ],
   "IsIndividual":true,
   "Tags":[
      "Adult",
      "Nervous_system"
   ],
   "IsTemplate":true,
   "Images":{
      "VFBc_00101567":[
         {
            "id":"VFBc_00101567",
            "label":"JRC2018Unisex_c",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz",
            "center":Coordinates(X=605,
            Y=283,
            Z=87),
            "extent":Coordinates(X=1211,
            Y=567,
            Z=175),
            "voxel":Coordinates(X=0.5189161,
            Y=0.5189161,
            Z=1.0),
            "orientation":""
         }
      ]
   },
   "Domains":{
      "6":{
         "id":"VFB_00102110",
         "label":"LOP on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003885",
         "type_label":"lobula plate",
         "index":6,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "22":{
         "id":"VFB_00102140",
         "label":"LAL on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003681",
         "type_label":"adult lateral accessory lobe",
         "index":22,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "28":{
         "id":"VFB_00102159",
         "label":"LH on JRC2018Unisex adult brain",
         "type_id":"FBbt_00007053",
         "type_label":"adult lateral horn",
         "index":28,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "10":{
         "id":"VFB_00102118",
         "label":"PED on JRC2018Unisex adult brain",
         "type_id":"FBbt_00007453",
         "type_label":"pedunculus of adult mushroom body",
         "index":10,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "34":{
         "id":"VFB_00102175",
         "label":"RUB on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040038",
         "type_label":"rubus",
         "index":34,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "23":{
         "id":"VFB_00102141",
         "label":"AOTU on JRC2018Unisex adult brain",
         "type_id":"FBbt_00007059",
         "type_label":"anterior optic tubercle",
         "index":23,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "39":{
         "id":"VFB_00102201",
         "label":"AL on JRC2018Unisex adult brain",
         "type_id":"FBbt_00007401",
         "type_label":"adult antennal lobe",
         "index":39,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "46":{
         "id":"VFB_00102273",
         "label":"AMMC on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003982",
         "type_label":"antennal mechanosensory and motor center",
         "index":46,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "26":{
         "id":"VFB_00102152",
         "label":"PLP on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040044",
         "type_label":"posterior lateral protocerebrum",
         "index":26,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "37":{
         "id":"VFB_00102185",
         "label":"IB on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040050",
         "type_label":"inferior bridge",
         "index":37,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "59":{
         "id":"VFB_00102281",
         "label":"GA on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040060",
         "type_label":"gall",
         "index":59,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "7":{
         "id":"VFB_00102114",
         "label":"CA on JRC2018Unisex adult brain",
         "type_id":"FBbt_00007385",
         "type_label":"calyx of adult mushroom body",
         "index":7,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "40":{
         "id":"VFB_00102212",
         "label":"VES on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040041",
         "type_label":"vest",
         "index":40,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "49":{
         "id":"VFB_00102276",
         "label":"PRW on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040051",
         "type_label":"prow",
         "index":49,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "16":{
         "id":"VFB_00102134",
         "label":"FB on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003679",
         "type_label":"fan-shaped body",
         "index":16,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "94":{
         "id":"VFB_00102282",
         "label":"NO on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003680",
         "type_label":"nodulus",
         "index":94,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "44":{
         "id":"VFB_00102218",
         "label":"IPS on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045046",
         "type_label":"inferior posterior slope",
         "index":44,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "32":{
         "id":"VFB_00102171",
         "label":"CRE on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045037",
         "type_label":"adult crepine",
         "index":32,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "35":{
         "id":"VFB_00102176",
         "label":"SCL on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040048",
         "type_label":"superior clamp",
         "index":35,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "42":{
         "id":"VFB_00102214",
         "label":"GOR on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040039",
         "type_label":"gorget",
         "index":42,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "21":{
         "id":"VFB_00102139",
         "label":"BU on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003682",
         "type_label":"bulb",
         "index":21,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "19":{
         "id":"VFB_00102137",
         "label":"PB on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003668",
         "type_label":"protocerebral bridge",
         "index":19,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "38":{
         "id":"VFB_00102190",
         "label":"ATL on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045039",
         "type_label":"antler",
         "index":38,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "14":{
         "id":"VFB_00102124",
         "label":"b\\'L on JRC2018Unisex adult brain",
         "type_id":"FBbt_00013694",
         "type_label":"adult mushroom body beta'-lobe",
         "index":14,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "11":{
         "id":"VFB_00102119",
         "label":"aL on JRC2018Unisex adult brain",
         "type_id":"FBbt_00110657",
         "type_label":"adult mushroom body alpha-lobe",
         "index":11,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "30":{
         "id":"VFB_00102164",
         "label":"SIP on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045032",
         "type_label":"superior intermediate protocerebrum",
         "index":30,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "36":{
         "id":"VFB_00102179",
         "label":"ICL on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040049",
         "type_label":"inferior clamp",
         "index":36,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "3":{
         "id":"VFB_00102107",
         "label":"ME on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003748",
         "type_label":"medulla",
         "index":3,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "15":{
         "id":"VFB_00102133",
         "label":"gL on JRC2018Unisex adult brain",
         "type_id":"FBbt_00013695",
         "type_label":"adult mushroom body gamma-lobe",
         "index":15,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "5":{
         "id":"VFB_00102109",
         "label":"LO on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003852",
         "type_label":"lobula",
         "index":5,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "18":{
         "id":"VFB_00102135",
         "label":"EB on JRC2018Unisex adult brain",
         "type_id":"FBbt_00003678",
         "type_label":"ellipsoid body",
         "index":18,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "33":{
         "id":"VFB_00102174",
         "label":"ROB on JRC2018Unisex adult brain",
         "type_id":"FBbt_00048509",
         "type_label":"adult round body",
         "index":33,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "50":{
         "id":"VFB_00102280",
         "label":"GNG on JRC2018Unisex adult brain",
         "type_id":"FBbt_00014013",
         "type_label":"adult gnathal ganglion",
         "index":50,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "13":{
         "id":"VFB_00102123",
         "label":"bL on JRC2018Unisex adult brain",
         "type_id":"FBbt_00110658",
         "type_label":"adult mushroom body beta-lobe",
         "index":13,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "47":{
         "id":"VFB_00102274",
         "label":"FLA on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045050",
         "type_label":"flange",
         "index":47,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "29":{
         "id":"VFB_00102162",
         "label":"SLP on JRC2018Unisex adult brain",
         "type_id":"FBbt_00007054",
         "type_label":"superior lateral protocerebrum",
         "index":29,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "48":{
         "id":"VFB_00102275",
         "label":"CAN on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045051",
         "type_label":"cantle",
         "index":48,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "4":{
         "id":"VFB_00102108",
         "label":"AME on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045003",
         "type_label":"accessory medulla",
         "index":4,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "12":{
         "id":"VFB_00102121",
         "label":"a\\'L on JRC2018Unisex adult brain",
         "type_id":"FBbt_00013691",
         "type_label":"adult mushroom body alpha'-lobe",
         "index":12,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "25":{
         "id":"VFB_00102148",
         "label":"PVLP on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040042",
         "type_label":"posterior ventrolateral protocerebrum",
         "index":25,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "45":{
         "id":"VFB_00102271",
         "label":"SAD on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045048",
         "type_label":"saddle",
         "index":45,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "31":{
         "id":"VFB_00102170",
         "label":"SMP on JRC2018Unisex adult brain",
         "type_id":"FBbt_00007055",
         "type_label":"superior medial protocerebrum",
         "index":31,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "41":{
         "id":"VFB_00102213",
         "label":"EPA on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040040",
         "type_label":"epaulette",
         "index":41,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "43":{
         "id":"VFB_00102215",
         "label":"SPS on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045040",
         "type_label":"superior posterior slope",
         "index":43,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "27":{
         "id":"VFB_00102154",
         "label":"WED on JRC2018Unisex adult brain",
         "type_id":"FBbt_00045027",
         "type_label":"wedge",
         "index":27,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "24":{
         "id":"VFB_00102146",
         "label":"AVLP on JRC2018Unisex adult brain",
         "type_id":"FBbt_00040043",
         "type_label":"anterior ventrolateral protocerebrum",
         "index":24,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnailT.png",
         "center":"None"
      },
      "0":{
         "id":"VFB_00101567",
         "label":"JRC2018Unisex",
         "type_id":"FBbt_00003624",
         "type_label":"adult brain",
         "index":0,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
         "center":"None"
      }
   },
   "Queries":[
      
   ]
}{
   "IsIndividual":true,
   "Queries":[
      
   ],
   "SuperTypes":[
      "Entity",
      "Adult",
      "Anatomy",
      "Individual",
      "Nervous_system",
      "Template",
      "has_image"
   ],
   "Images":{
      "VFBc_00101567":[
         {
            "extent":{
               "X":1211,
               "Y":567,
               "Z":175
            },
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj",
            "voxel":{
               "X":0.5189161,
               "Y":0.5189161,
               "Z":1.0
            },
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
            "id":"VFBc_00101567",
            "orientation":"",
            "label":"JRC2018Unisex_c",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd",
            "center":{
               "X":605,
               "Y":283,
               "Z":87
            }
         }
      ]
   },
   "IsClass":false,
   "IsTemplate":true,
   "Name":"JRC2018Unisex",
   "Domains":{
      "6":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnail.png",
         "id":"VFB_00102110",
         "type_label":"lobula plate",
         "label":"LOP on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnailT.png",
         "index":6,
         "center":"None",
         "type_id":"FBbt_00003885"
      },
      "22":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnail.png",
         "id":"VFB_00102140",
         "type_label":"adult lateral accessory lobe",
         "label":"LAL on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnailT.png",
         "index":22,
         "center":"None",
         "type_id":"FBbt_00003681"
      },
      "28":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnail.png",
         "id":"VFB_00102159",
         "type_label":"adult lateral horn",
         "label":"LH on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnailT.png",
         "index":28,
         "center":"None",
         "type_id":"FBbt_00007053"
      },
      "10":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnail.png",
         "id":"VFB_00102118",
         "type_label":"pedunculus of adult mushroom body",
         "label":"PED on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnailT.png",
         "index":10,
         "center":"None",
         "type_id":"FBbt_00007453"
      },
      "34":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnail.png",
         "id":"VFB_00102175",
         "type_label":"rubus",
         "label":"RUB on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnailT.png",
         "index":34,
         "center":"None",
         "type_id":"FBbt_00040038"
      },
      "23":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnail.png",
         "id":"VFB_00102141",
         "type_label":"anterior optic tubercle",
         "label":"AOTU on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnailT.png",
         "index":23,
         "center":"None",
         "type_id":"FBbt_00007059"
      },
      "39":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnail.png",
         "id":"VFB_00102201",
         "type_label":"adult antennal lobe",
         "label":"AL on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnailT.png",
         "index":39,
         "center":"None",
         "type_id":"FBbt_00007401"
      },
      "46":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnail.png",
         "id":"VFB_00102273",
         "type_label":"antennal mechanosensory and motor center",
         "label":"AMMC on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnailT.png",
         "index":46,
         "center":"None",
         "type_id":"FBbt_00003982"
      },
      "26":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnail.png",
         "id":"VFB_00102152",
         "type_label":"posterior lateral protocerebrum",
         "label":"PLP on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnailT.png",
         "index":26,
         "center":"None",
         "type_id":"FBbt_00040044"
      },
      "37":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnail.png",
         "id":"VFB_00102185",
         "type_label":"inferior bridge",
         "label":"IB on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnailT.png",
         "index":37,
         "center":"None",
         "type_id":"FBbt_00040050"
      },
      "59":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnail.png",
         "id":"VFB_00102281",
         "type_label":"gall",
         "label":"GA on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnailT.png",
         "index":59,
         "center":"None",
         "type_id":"FBbt_00040060"
      },
      "7":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnail.png",
         "id":"VFB_00102114",
         "type_label":"calyx of adult mushroom body",
         "label":"CA on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnailT.png",
         "index":7,
         "center":"None",
         "type_id":"FBbt_00007385"
      },
      "40":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnail.png",
         "id":"VFB_00102212",
         "type_label":"vest",
         "label":"VES on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnailT.png",
         "index":40,
         "center":"None",
         "type_id":"FBbt_00040041"
      },
      "49":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnail.png",
         "id":"VFB_00102276",
         "type_label":"prow",
         "label":"PRW on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnailT.png",
         "index":49,
         "center":"None",
         "type_id":"FBbt_00040051"
      },
      "16":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnail.png",
         "id":"VFB_00102134",
         "type_label":"fan-shaped body",
         "label":"FB on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnailT.png",
         "index":16,
         "center":"None",
         "type_id":"FBbt_00003679"
      },
      "94":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnail.png",
         "id":"VFB_00102282",
         "type_label":"nodulus",
         "label":"NO on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnailT.png",
         "index":94,
         "center":"None",
         "type_id":"FBbt_00003680"
      },
      "44":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnail.png",
         "id":"VFB_00102218",
         "type_label":"inferior posterior slope",
         "label":"IPS on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnailT.png",
         "index":44,
         "center":"None",
         "type_id":"FBbt_00045046"
      },
      "32":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnail.png",
         "id":"VFB_00102171",
         "type_label":"adult crepine",
         "label":"CRE on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnailT.png",
         "index":32,
         "center":"None",
         "type_id":"FBbt_00045037"
      },
      "35":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnail.png",
         "id":"VFB_00102176",
         "type_label":"superior clamp",
         "label":"SCL on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnailT.png",
         "index":35,
         "center":"None",
         "type_id":"FBbt_00040048"
      },
      "42":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnail.png",
         "id":"VFB_00102214",
         "type_label":"gorget",
         "label":"GOR on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnailT.png",
         "index":42,
         "center":"None",
         "type_id":"FBbt_00040039"
      },
      "21":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnail.png",
         "id":"VFB_00102139",
         "type_label":"bulb",
         "label":"BU on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnailT.png",
         "index":21,
         "center":"None",
         "type_id":"FBbt_00003682"
      },
      "19":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnail.png",
         "id":"VFB_00102137",
         "type_label":"protocerebral bridge",
         "label":"PB on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnailT.png",
         "index":19,
         "center":"None",
         "type_id":"FBbt_00003668"
      },
      "38":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnail.png",
         "id":"VFB_00102190",
         "type_label":"antler",
         "label":"ATL on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnailT.png",
         "index":38,
         "center":"None",
         "type_id":"FBbt_00045039"
      },
      "14":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnail.png",
         "id":"VFB_00102124",
         "type_label":"adult mushroom body beta'-lobe",
         "label":"b\\'L on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnailT.png",
         "index":14,
         "center":"None",
         "type_id":"FBbt_00013694"
      },
      "11":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnail.png",
         "id":"VFB_00102119",
         "type_label":"adult mushroom body alpha-lobe",
         "label":"aL on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnailT.png",
         "index":11,
         "center":"None",
         "type_id":"FBbt_00110657"
      },
      "30":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnail.png",
         "id":"VFB_00102164",
         "type_label":"superior intermediate protocerebrum",
         "label":"SIP on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnailT.png",
         "index":30,
         "center":"None",
         "type_id":"FBbt_00045032"
      },
      "36":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnail.png",
         "id":"VFB_00102179",
         "type_label":"inferior clamp",
         "label":"ICL on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnailT.png",
         "index":36,
         "center":"None",
         "type_id":"FBbt_00040049"
      },
      "3":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
         "id":"VFB_00102107",
         "type_label":"medulla",
         "label":"ME on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
         "index":3,
         "center":"None",
         "type_id":"FBbt_00003748"
      },
      "15":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnail.png",
         "id":"VFB_00102133",
         "type_label":"adult mushroom body gamma-lobe",
         "label":"gL on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnailT.png",
         "index":15,
         "center":"None",
         "type_id":"FBbt_00013695"
      },
      "5":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnail.png",
         "id":"VFB_00102109",
         "type_label":"lobula",
         "label":"LO on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnailT.png",
         "index":5,
         "center":"None",
         "type_id":"FBbt_00003852"
      },
      "18":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnail.png",
         "id":"VFB_00102135",
         "type_label":"ellipsoid body",
         "label":"EB on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnailT.png",
         "index":18,
         "center":"None",
         "type_id":"FBbt_00003678"
      },
      "33":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnail.png",
         "id":"VFB_00102174",
         "type_label":"adult round body",
         "label":"ROB on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnailT.png",
         "index":33,
         "center":"None",
         "type_id":"FBbt_00048509"
      },
      "50":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnail.png",
         "id":"VFB_00102280",
         "type_label":"adult gnathal ganglion",
         "label":"GNG on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnailT.png",
         "index":50,
         "center":"None",
         "type_id":"FBbt_00014013"
      },
      "13":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnail.png",
         "id":"VFB_00102123",
         "type_label":"adult mushroom body beta-lobe",
         "label":"bL on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnailT.png",
         "index":13,
         "center":"None",
         "type_id":"FBbt_00110658"
      },
      "47":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnail.png",
         "id":"VFB_00102274",
         "type_label":"flange",
         "label":"FLA on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnailT.png",
         "index":47,
         "center":"None",
         "type_id":"FBbt_00045050"
      },
      "29":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnail.png",
         "id":"VFB_00102162",
         "type_label":"superior lateral protocerebrum",
         "label":"SLP on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnailT.png",
         "index":29,
         "center":"None",
         "type_id":"FBbt_00007054"
      },
      "48":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnail.png",
         "id":"VFB_00102275",
         "type_label":"cantle",
         "label":"CAN on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnailT.png",
         "index":48,
         "center":"None",
         "type_id":"FBbt_00045051"
      },
      "4":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnail.png",
         "id":"VFB_00102108",
         "type_label":"accessory medulla",
         "label":"AME on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnailT.png",
         "index":4,
         "center":"None",
         "type_id":"FBbt_00045003"
      },
      "12":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnail.png",
         "id":"VFB_00102121",
         "type_label":"adult mushroom body alpha'-lobe",
         "label":"a\\'L on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnailT.png",
         "index":12,
         "center":"None",
         "type_id":"FBbt_00013691"
      },
      "25":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnail.png",
         "id":"VFB_00102148",
         "type_label":"posterior ventrolateral protocerebrum",
         "label":"PVLP on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnailT.png",
         "index":25,
         "center":"None",
         "type_id":"FBbt_00040042"
      },
      "45":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnail.png",
         "id":"VFB_00102271",
         "type_label":"saddle",
         "label":"SAD on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnailT.png",
         "index":45,
         "center":"None",
         "type_id":"FBbt_00045048"
      },
      "31":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnail.png",
         "id":"VFB_00102170",
         "type_label":"superior medial protocerebrum",
         "label":"SMP on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnailT.png",
         "index":31,
         "center":"None",
         "type_id":"FBbt_00007055"
      },
      "41":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnail.png",
         "id":"VFB_00102213",
         "type_label":"epaulette",
         "label":"EPA on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnailT.png",
         "index":41,
         "center":"None",
         "type_id":"FBbt_00040040"
      },
      "43":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnail.png",
         "id":"VFB_00102215",
         "type_label":"superior posterior slope",
         "label":"SPS on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnailT.png",
         "index":43,
         "center":"None",
         "type_id":"FBbt_00045040"
      },
      "27":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnail.png",
         "id":"VFB_00102154",
         "type_label":"wedge",
         "label":"WED on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnailT.png",
         "index":27,
         "center":"None",
         "type_id":"FBbt_00045027"
      },
      "24":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnail.png",
         "id":"VFB_00102146",
         "type_label":"anterior ventrolateral protocerebrum",
         "label":"AVLP on JRC2018Unisex adult brain",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnailT.png",
         "index":24,
         "center":"None",
         "type_id":"FBbt_00040043"
      },
      "0":{
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
         "id":"VFB_00101567",
         "type_label":"adult brain",
         "label":"JRC2018Unisex",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
         "index":0,
         "center":"None",
         "type_id":"FBbt_00003624"
      }
   },
   "Id":"VFB_00101567",
   "Meta":{
      "Name":"[JRC2018Unisex](VFB_00101567)",
      "Description":"Janelia 2018 unisex, averaged adult brain template",
      "Comment":""
   },
   "Tags":[
      "Adult",
      "Nervous_system"
   ]
}
```

Queries:
```python
vfb.get_instances('FBbt_00003748')
```
```python
{
   "headers":{
      "label":{
         "title":"Name",
         "type":"markdown",
         "order":0,
         "sort":{
            "0":"Asc"
         }
      },
      "parent":{
         "title":"Parent Type",
         "type":"markdown",
         "order":1
      },
      "template":{
         "title":"Template",
         "type":"markdown",
         "order":4
      },
      "tags":{
         "title":"Gross Types",
         "type":"tags",
         "order":3
      },
      "source":{
         "title":"Data Source",
         "type":"markdown",
         "order":5
      },
      "source_id":{
         "title":"Data Source",
         "type":"markdown",
         "order":6
      }
   },
   "rows":[
      {
         "label":"[medulla on adult brain template Ito2014](VFB_00030810)",
         "tags":"Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain",
         "parent":"[medulla](FBbt_00003748)",
         "source":"",
         "source_id":"",
         "template":"[adult brain template Ito2014](VFB_00030786)",
         "dataset":"[BrainName neuropils and tracts - Ito half-brain](BrainName_Ito_half_brain)",
         "license":"[CC-BY-SA_4.0](VFBlicense_CC_BY_SA_4_0)"
      },
      {
         "label":"[ME on JRC2018Unisex adult brain](VFB_00102107)",
         "tags":"Nervous_system|Adult|Visual_system|Synaptic_neuropil_domain",
         "parent":"[medulla](FBbt_00003748)",
         "source":"",
         "source_id":"",
         "template":"[JRC2018Unisex](VFB_00101567)",
         "dataset":"[JRC 2018 templates & ROIs](JRC2018)",
         "license":"[CC-BY-NC-SA_4.0](VFBlicense_CC_BY_NC_SA_4_0)"
      },
      {
         "label":"[medulla on adult brain template JFRC2](VFB_00030624)",
         "tags":"Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain",
         "parent":"[medulla](FBbt_00003748)",
         "source":"",
         "source_id":"",
         "template":"[adult brain template JFRC2](VFB_00017894)",
         "dataset":"[BrainName neuropils on adult brain JFRC2 (Jenett, Shinomya)](JenettShinomya_BrainName)",
         "license":"[CC-BY-SA_4.0](VFBlicense_CC_BY_SA_4_0)"
      },
      {
         "label":"[ME(R) on JRC_FlyEM_Hemibrain](VFB_00101385)",
         "tags":"Nervous_system|Adult|Visual_system|Synaptic_neuropil_domain",
         "parent":"[medulla](FBbt_00003748)",
         "source":"",
         "source_id":"",
         "template":"[JRC_FlyEM_Hemibrain](VFB_00101384)",
         "dataset":"[JRC_FlyEM_Hemibrain painted domains](Xu2020roi)",
         "license":"[CC-BY_4.0](VFBlicense_CC_BY_4_0)"
      }
   ]
}
```
