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
```python
vfb.get_term_info('FBbt_00003748')
```
```json
{
   "IsIndividual":false,
   "IsClass":true,
   "Id":"FBbt_00003748",
   "Meta":{
      "Name":"[medulla](FBbt_00003748)",
      "Description":"The second optic neuropil, sandwiched between the lamina and the lobula complex. It is divided into 10 layers: 1-6 make up the outer (distal) medulla, the seventh (or serpentine) layer exhibits a distinct architecture and layers 8-10 make up the inner (proximal) medulla (Ito et al., 2014).",
      "Comment":"",
      "Types":"[synaptic neuropil domain](FBbt_00040007)",
      "Relationships":"[develops from](RO_0002202): [medulla anlage](FBbt_00001935); [is part of](BFO_0000050): [adult optic lobe](FBbt_00003701)",
      "Cross References":"![Insect Brain DB](https://insectbraindb.org/app/assets/images/Megalopta_frontal.png) [Insect Brain DB](https://insectbraindb.org/): [38](https://insectbraindb.org/app/structures/38)"
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
   "Examples":{
      "VFB_00030786":[
         {
            "id":"VFB_00030810",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.nrrd",
            "label":"medulla on adult brain template Ito2014",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume_man.obj",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.wlz"
         }
      ],
      "VFB_00101567":[
         {
            "id":"VFB_00102107",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.nrrd",
            "label":"ME on JRC2018Unisex adult brain",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume_man.obj",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.wlz"
         }
      ],
      "VFB_00017894":[
         {
            "id":"VFB_00030624",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.nrrd",
            "label":"medulla on adult brain template JFRC2",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume_man.obj",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.wlz"
         }
      ],
      "VFB_00101384":[
         {
            "id":"VFB_00101385",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.nrrd",
            "label":"ME(R) on JRC_FlyEM_Hemibrain",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume_man.obj",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.wlz"
         }
      ]
   },
   "Name":"medulla",
   "IsTemplate":false,
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

```json
{
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
   "Id":"VFB_00000001",
   "Tags":[
      "Adult",
      "Expression_pattern_fragment",
      "Nervous_system",
      "Neuron"
   ],
   "Meta":{
      "Name":"[fru-M-200266](VFB_00000001)",
      "Description":"",
      "Comment":"OutAge: Adult 5~15 days",
      "Types":"[adult DM6 lineage neuron](FBbt_00050144); [expression pattern fragment](VFBext_0000004)",
      "Relationships":"[expresses](RO_0002292): [Scer\\GAL4[fru.P1.D]](FBal0276838); [is part of](BFO_0000050): [Scer\\GAL4[fru.P1.D] expression pattern](VFBexp_FBal0276838), [adult brain](FBbt_00003624), [male organism](FBbt_00007004); [overlaps](RO_0002131): [adult antennal lobe](FBbt_00007401), [adult crepine](FBbt_00045037), [adult lateral accessory lobe](FBbt_00003681), [superior posterior slope](FBbt_00045040), [vest](FBbt_00040041)",
      "Cross References":"[FlyCircuit 1.0](http://flycircuit.tw): [fru-M-200266](http://flycircuit.tw/modules.php?name=clearpage&op=detail_table&neuron=fru-M-200266)"
   },
   "IsClass":false,
   "IsTemplate":false,
   "Name":"fru-M-200266",
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
   "Images":{
      "VFB_00101567":[
         {
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.nrrd",
            "wlz":"https://virtualflybrain.org/reports/VFB_00000001/volume.wlz",
            "thumbnail_transparent":"https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png",
            "thumbnail":"https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png",
            "swc":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.swc",
            "label":"fru-M-200266",
            "id":"VFB_00000001",
            "obj":"https://virtualflybrain.org/reports/VFB_00000001/volume.obj"
         }
      ],
      "VFB_00017894":[
         {
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.nrrd",
            "wlz":"https://virtualflybrain.org/reports/VFB_00000001/volume.wlz",
            "thumbnail_transparent":"https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png",
            "thumbnail":"https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png",
            "swc":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.swc",
            "label":"fru-M-200266",
            "id":"VFB_00000001",
            "obj":"https://virtualflybrain.org/reports/VFB_00000001/volume.obj"
         }
      ]
   }
}
```
Template example:
```python
vfb.get_term_info('VFB_00101567')
```

```json
{
   "Meta":{
      "Name":"[JRC2018Unisex](VFB_00101567)",
      "Description":"Janelia 2018 unisex, averaged adult brain template",
      "Comment":"",
      "Types":"[adult brain](FBbt_00003624)"
   },
   "Tags":[
      "Adult",
      "Nervous_system"
   ],
   "Queries":[
      
   ],
   "Id":"VFB_00101567",
   "SuperTypes":[
      "Entity",
      "Adult",
      "Anatomy",
      "Individual",
      "Nervous_system",
      "Template",
      "has_image"
   ],
   "Domains":{
      "0":{
         "type_id":"FBbt_00003624",
         "id":"VFB_00101567",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
         "type_label":"adult brain",
         "index":0,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
         "label":"JRC2018Unisex",
         "center":"None"
      },
      "3":{
         "type_id":"FBbt_00003748",
         "id":"VFB_00102107",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
         "type_label":"medulla",
         "index":3,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
         "label":"ME on JRC2018Unisex adult brain",
         "center":"None"
      },
      "4":{
         "type_id":"FBbt_00045003",
         "id":"VFB_00102108",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnailT.png",
         "type_label":"accessory medulla",
         "index":4,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnail.png",
         "label":"AME on JRC2018Unisex adult brain",
         "center":"None"
      },
      "5":{
         "type_id":"FBbt_00003852",
         "id":"VFB_00102109",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnailT.png",
         "type_label":"lobula",
         "index":5,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnail.png",
         "label":"LO on JRC2018Unisex adult brain",
         "center":"None"
      },
      "6":{
         "type_id":"FBbt_00003885",
         "id":"VFB_00102110",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnailT.png",
         "type_label":"lobula plate",
         "index":6,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnail.png",
         "label":"LOP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "7":{
         "type_id":"FBbt_00007385",
         "id":"VFB_00102114",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnailT.png",
         "type_label":"calyx of adult mushroom body",
         "index":7,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnail.png",
         "label":"CA on JRC2018Unisex adult brain",
         "center":"None"
      },
      "10":{
         "type_id":"FBbt_00007453",
         "id":"VFB_00102118",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnailT.png",
         "type_label":"pedunculus of adult mushroom body",
         "index":10,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnail.png",
         "label":"PED on JRC2018Unisex adult brain",
         "center":"None"
      },
      "11":{
         "type_id":"FBbt_00110657",
         "id":"VFB_00102119",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnailT.png",
         "type_label":"adult mushroom body alpha-lobe",
         "index":11,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnail.png",
         "label":"aL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "12":{
         "type_id":"FBbt_00013691",
         "id":"VFB_00102121",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnailT.png",
         "type_label":"adult mushroom body alpha'-lobe",
         "index":12,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnail.png",
         "label":"a\\'L on JRC2018Unisex adult brain",
         "center":"None"
      },
      "13":{
         "type_id":"FBbt_00110658",
         "id":"VFB_00102123",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnailT.png",
         "type_label":"adult mushroom body beta-lobe",
         "index":13,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnail.png",
         "label":"bL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "14":{
         "type_id":"FBbt_00013694",
         "id":"VFB_00102124",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnailT.png",
         "type_label":"adult mushroom body beta'-lobe",
         "index":14,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnail.png",
         "label":"b\\'L on JRC2018Unisex adult brain",
         "center":"None"
      },
      "15":{
         "type_id":"FBbt_00013695",
         "id":"VFB_00102133",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnailT.png",
         "type_label":"adult mushroom body gamma-lobe",
         "index":15,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnail.png",
         "label":"gL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "16":{
         "type_id":"FBbt_00003679",
         "id":"VFB_00102134",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnailT.png",
         "type_label":"fan-shaped body",
         "index":16,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnail.png",
         "label":"FB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "18":{
         "type_id":"FBbt_00003678",
         "id":"VFB_00102135",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnailT.png",
         "type_label":"ellipsoid body",
         "index":18,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnail.png",
         "label":"EB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "19":{
         "type_id":"FBbt_00003668",
         "id":"VFB_00102137",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnailT.png",
         "type_label":"protocerebral bridge",
         "index":19,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnail.png",
         "label":"PB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "21":{
         "type_id":"FBbt_00003682",
         "id":"VFB_00102139",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnailT.png",
         "type_label":"bulb",
         "index":21,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnail.png",
         "label":"BU on JRC2018Unisex adult brain",
         "center":"None"
      },
      "22":{
         "type_id":"FBbt_00003681",
         "id":"VFB_00102140",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnailT.png",
         "type_label":"adult lateral accessory lobe",
         "index":22,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnail.png",
         "label":"LAL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "23":{
         "type_id":"FBbt_00007059",
         "id":"VFB_00102141",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnailT.png",
         "type_label":"anterior optic tubercle",
         "index":23,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnail.png",
         "label":"AOTU on JRC2018Unisex adult brain",
         "center":"None"
      },
      "24":{
         "type_id":"FBbt_00040043",
         "id":"VFB_00102146",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnailT.png",
         "type_label":"anterior ventrolateral protocerebrum",
         "index":24,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnail.png",
         "label":"AVLP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "25":{
         "type_id":"FBbt_00040042",
         "id":"VFB_00102148",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnailT.png",
         "type_label":"posterior ventrolateral protocerebrum",
         "index":25,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnail.png",
         "label":"PVLP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "26":{
         "type_id":"FBbt_00040044",
         "id":"VFB_00102152",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnailT.png",
         "type_label":"posterior lateral protocerebrum",
         "index":26,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnail.png",
         "label":"PLP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "27":{
         "type_id":"FBbt_00045027",
         "id":"VFB_00102154",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnailT.png",
         "type_label":"wedge",
         "index":27,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnail.png",
         "label":"WED on JRC2018Unisex adult brain",
         "center":"None"
      },
      "28":{
         "type_id":"FBbt_00007053",
         "id":"VFB_00102159",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnailT.png",
         "type_label":"adult lateral horn",
         "index":28,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnail.png",
         "label":"LH on JRC2018Unisex adult brain",
         "center":"None"
      },
      "29":{
         "type_id":"FBbt_00007054",
         "id":"VFB_00102162",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnailT.png",
         "type_label":"superior lateral protocerebrum",
         "index":29,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnail.png",
         "label":"SLP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "30":{
         "type_id":"FBbt_00045032",
         "id":"VFB_00102164",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnailT.png",
         "type_label":"superior intermediate protocerebrum",
         "index":30,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnail.png",
         "label":"SIP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "31":{
         "type_id":"FBbt_00007055",
         "id":"VFB_00102170",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnailT.png",
         "type_label":"superior medial protocerebrum",
         "index":31,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnail.png",
         "label":"SMP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "32":{
         "type_id":"FBbt_00045037",
         "id":"VFB_00102171",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnailT.png",
         "type_label":"adult crepine",
         "index":32,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnail.png",
         "label":"CRE on JRC2018Unisex adult brain",
         "center":"None"
      },
      "33":{
         "type_id":"FBbt_00048509",
         "id":"VFB_00102174",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnailT.png",
         "type_label":"adult round body",
         "index":33,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnail.png",
         "label":"ROB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "34":{
         "type_id":"FBbt_00040038",
         "id":"VFB_00102175",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnailT.png",
         "type_label":"rubus",
         "index":34,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnail.png",
         "label":"RUB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "35":{
         "type_id":"FBbt_00040048",
         "id":"VFB_00102176",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnailT.png",
         "type_label":"superior clamp",
         "index":35,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnail.png",
         "label":"SCL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "36":{
         "type_id":"FBbt_00040049",
         "id":"VFB_00102179",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnailT.png",
         "type_label":"inferior clamp",
         "index":36,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnail.png",
         "label":"ICL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "37":{
         "type_id":"FBbt_00040050",
         "id":"VFB_00102185",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnailT.png",
         "type_label":"inferior bridge",
         "index":37,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnail.png",
         "label":"IB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "38":{
         "type_id":"FBbt_00045039",
         "id":"VFB_00102190",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnailT.png",
         "type_label":"antler",
         "index":38,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnail.png",
         "label":"ATL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "39":{
         "type_id":"FBbt_00007401",
         "id":"VFB_00102201",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnailT.png",
         "type_label":"adult antennal lobe",
         "index":39,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnail.png",
         "label":"AL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "40":{
         "type_id":"FBbt_00040041",
         "id":"VFB_00102212",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnailT.png",
         "type_label":"vest",
         "index":40,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnail.png",
         "label":"VES on JRC2018Unisex adult brain",
         "center":"None"
      },
      "41":{
         "type_id":"FBbt_00040040",
         "id":"VFB_00102213",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnailT.png",
         "type_label":"epaulette",
         "index":41,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnail.png",
         "label":"EPA on JRC2018Unisex adult brain",
         "center":"None"
      },
      "42":{
         "type_id":"FBbt_00040039",
         "id":"VFB_00102214",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnailT.png",
         "type_label":"gorget",
         "index":42,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnail.png",
         "label":"GOR on JRC2018Unisex adult brain",
         "center":"None"
      },
      "43":{
         "type_id":"FBbt_00045040",
         "id":"VFB_00102215",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnailT.png",
         "type_label":"superior posterior slope",
         "index":43,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnail.png",
         "label":"SPS on JRC2018Unisex adult brain",
         "center":"None"
      },
      "44":{
         "type_id":"FBbt_00045046",
         "id":"VFB_00102218",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnailT.png",
         "type_label":"inferior posterior slope",
         "index":44,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnail.png",
         "label":"IPS on JRC2018Unisex adult brain",
         "center":"None"
      },
      "45":{
         "type_id":"FBbt_00045048",
         "id":"VFB_00102271",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnailT.png",
         "type_label":"saddle",
         "index":45,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnail.png",
         "label":"SAD on JRC2018Unisex adult brain",
         "center":"None"
      },
      "46":{
         "type_id":"FBbt_00003982",
         "id":"VFB_00102273",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnailT.png",
         "type_label":"antennal mechanosensory and motor center",
         "index":46,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnail.png",
         "label":"AMMC on JRC2018Unisex adult brain",
         "center":"None"
      },
      "47":{
         "type_id":"FBbt_00045050",
         "id":"VFB_00102274",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnailT.png",
         "type_label":"flange",
         "index":47,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnail.png",
         "label":"FLA on JRC2018Unisex adult brain",
         "center":"None"
      },
      "48":{
         "type_id":"FBbt_00045051",
         "id":"VFB_00102275",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnailT.png",
         "type_label":"cantle",
         "index":48,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnail.png",
         "label":"CAN on JRC2018Unisex adult brain",
         "center":"None"
      },
      "49":{
         "type_id":"FBbt_00040051",
         "id":"VFB_00102276",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnailT.png",
         "type_label":"prow",
         "index":49,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnail.png",
         "label":"PRW on JRC2018Unisex adult brain",
         "center":"None"
      },
      "50":{
         "type_id":"FBbt_00014013",
         "id":"VFB_00102280",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnailT.png",
         "type_label":"adult gnathal ganglion",
         "index":50,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnail.png",
         "label":"GNG on JRC2018Unisex adult brain",
         "center":"None"
      },
      "59":{
         "type_id":"FBbt_00040060",
         "id":"VFB_00102281",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnailT.png",
         "type_label":"gall",
         "index":59,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnail.png",
         "label":"GA on JRC2018Unisex adult brain",
         "center":"None"
      },
      "94":{
         "type_id":"FBbt_00003680",
         "id":"VFB_00102282",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnailT.png",
         "type_label":"nodulus",
         "index":94,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnail.png",
         "label":"NO on JRC2018Unisex adult brain",
         "center":"None"
      }
   },
   "Images":{
      "VFBc_00101567":[
         {
            "voxel":{
               "X":0.5189161,
               "Y":0.5189161,
               "Z":1.0
            },
            "id":"VFBc_00101567",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
            "orientation":"",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
            "extent":{
               "X":1211,
               "Y":567,
               "Z":175
            },
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd",
            "label":"JRC2018Unisex_c",
            "center":{
               "X":605,
               "Y":283,
               "Z":87
            },
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj"
         }
      ]
   },
   "IsClass":false,
   "Name":"JRC2018Unisex",
   "IsTemplate":true,
   "IsIndividual":true
}
```

Queries:
```python
vfb.get_instances('FBbt_00003748')
```
```json
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
