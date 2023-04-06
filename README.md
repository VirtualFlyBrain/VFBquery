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
   "Images":{
      "VFB_00101567":[
         {
            "id":"VFB_00000001",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.nrrd",
            "label":"fru-M-200266",
            "obj":"https://virtualflybrain.org/reports/VFB_00000001/volume.obj",
            "thumbnail":"https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png",
            "thumbnail_transparent":"https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png",
            "wlz":"https://virtualflybrain.org/reports/VFB_00000001/volume.wlz",
            "swc":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.swc"
         }
      ],
      "VFB_00017894":[
         {
            "id":"VFB_00000001",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.nrrd",
            "label":"fru-M-200266",
            "obj":"https://virtualflybrain.org/reports/VFB_00000001/volume.obj",
            "thumbnail":"https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png",
            "thumbnail_transparent":"https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png",
            "wlz":"https://virtualflybrain.org/reports/VFB_00000001/volume.wlz",
            "swc":"https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.swc"
         }
      ]
   },
   "IsIndividual":true,
   "IsClass":false,
   "Id":"VFB_00000001",
   "Meta":{
      "Name":"[fru-M-200266](VFB_00000001)",
      "Description":"",
      "Comment":"OutAge: Adult 5~15 days",
      "Types":"[expression pattern fragment](VFBext_0000004); [adult DM6 lineage neuron](FBbt_00050144)",
      "Relationships":"[expresses](RO_0002292): [Scer\\GAL4[fru.P1.D]](FBal0276838); [overlaps](RO_0002131): [adult crepine](FBbt_00045037), [vest](FBbt_00040041), [superior posterior slope](FBbt_00045040), [adult antennal lobe](FBbt_00007401), [adult lateral accessory lobe](FBbt_00003681); [is part of](BFO_0000050): [Scer\\GAL4[fru.P1.D] expression pattern](VFBexp_FBal0276838), [adult brain](FBbt_00003624), [male organism](FBbt_00007004)",
      "Cross References":"[FlyCircuit 1.0](http://flycircuit.tw): [fru-M-200266](http://flycircuit.tw/modules.php?name=clearpage&op=detail_table&neuron=fru-M-200266)"
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
   "Name":"fru-M-200266",
   "IsTemplate":false,
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

```json
{
   "IsTemplate":true,
   "Meta":{
      "Name":"[JRC2018Unisex](VFB_00101567)",
      "Description":"Janelia 2018 unisex, averaged adult brain template",
      "Comment":"",
      "Types":"[adult brain](FBbt_00003624)"
   },
   "Images":{
      "VFBc_00101567":[
         {
            "id":"VFBc_00101567",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz",
            "voxel":{
               "X":0.5189161,
               "Y":0.5189161,
               "Z":1.0
            },
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd",
            "extent":{
               "X":1211,
               "Y":567,
               "Z":175
            },
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
            "label":"JRC2018Unisex_c",
            "center":{
               "X":605,
               "Y":283,
               "Z":87
            },
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
            "orientation":""
         }
      ]
   },
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
   "IsClass":false,
   "Queries":[
      
   ],
   "Id":"VFB_00101567",
   "Tags":[
      "Adult",
      "Nervous_system"
   ],
   "IsIndividual":true,
   "Domains":{
      "6":{
         "id":"VFB_00102110",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnailT.png",
         "label":"LOP on JRC2018Unisex adult brain",
         "center":"None",
         "index":6,
         "type_id":"FBbt_00003885",
         "type_label":"lobula plate",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnail.png"
      },
      "22":{
         "id":"VFB_00102140",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnailT.png",
         "label":"LAL on JRC2018Unisex adult brain",
         "center":"None",
         "index":22,
         "type_id":"FBbt_00003681",
         "type_label":"adult lateral accessory lobe",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnail.png"
      },
      "28":{
         "id":"VFB_00102159",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnailT.png",
         "label":"LH on JRC2018Unisex adult brain",
         "center":"None",
         "index":28,
         "type_id":"FBbt_00007053",
         "type_label":"adult lateral horn",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnail.png"
      },
      "10":{
         "id":"VFB_00102118",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnailT.png",
         "label":"PED on JRC2018Unisex adult brain",
         "center":"None",
         "index":10,
         "type_id":"FBbt_00007453",
         "type_label":"pedunculus of adult mushroom body",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnail.png"
      },
      "34":{
         "id":"VFB_00102175",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnailT.png",
         "label":"RUB on JRC2018Unisex adult brain",
         "center":"None",
         "index":34,
         "type_id":"FBbt_00040038",
         "type_label":"rubus",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnail.png"
      },
      "23":{
         "id":"VFB_00102141",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnailT.png",
         "label":"AOTU on JRC2018Unisex adult brain",
         "center":"None",
         "index":23,
         "type_id":"FBbt_00007059",
         "type_label":"anterior optic tubercle",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnail.png"
      },
      "39":{
         "id":"VFB_00102201",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnailT.png",
         "label":"AL on JRC2018Unisex adult brain",
         "center":"None",
         "index":39,
         "type_id":"FBbt_00007401",
         "type_label":"adult antennal lobe",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnail.png"
      },
      "46":{
         "id":"VFB_00102273",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnailT.png",
         "label":"AMMC on JRC2018Unisex adult brain",
         "center":"None",
         "index":46,
         "type_id":"FBbt_00003982",
         "type_label":"antennal mechanosensory and motor center",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnail.png"
      },
      "26":{
         "id":"VFB_00102152",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnailT.png",
         "label":"PLP on JRC2018Unisex adult brain",
         "center":"None",
         "index":26,
         "type_id":"FBbt_00040044",
         "type_label":"posterior lateral protocerebrum",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnail.png"
      },
      "37":{
         "id":"VFB_00102185",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnailT.png",
         "label":"IB on JRC2018Unisex adult brain",
         "center":"None",
         "index":37,
         "type_id":"FBbt_00040050",
         "type_label":"inferior bridge",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnail.png"
      },
      "59":{
         "id":"VFB_00102281",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnailT.png",
         "label":"GA on JRC2018Unisex adult brain",
         "center":"None",
         "index":59,
         "type_id":"FBbt_00040060",
         "type_label":"gall",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnail.png"
      },
      "7":{
         "id":"VFB_00102114",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnailT.png",
         "label":"CA on JRC2018Unisex adult brain",
         "center":"None",
         "index":7,
         "type_id":"FBbt_00007385",
         "type_label":"calyx of adult mushroom body",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnail.png"
      },
      "40":{
         "id":"VFB_00102212",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnailT.png",
         "label":"VES on JRC2018Unisex adult brain",
         "center":"None",
         "index":40,
         "type_id":"FBbt_00040041",
         "type_label":"vest",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnail.png"
      },
      "49":{
         "id":"VFB_00102276",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnailT.png",
         "label":"PRW on JRC2018Unisex adult brain",
         "center":"None",
         "index":49,
         "type_id":"FBbt_00040051",
         "type_label":"prow",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnail.png"
      },
      "16":{
         "id":"VFB_00102134",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnailT.png",
         "label":"FB on JRC2018Unisex adult brain",
         "center":"None",
         "index":16,
         "type_id":"FBbt_00003679",
         "type_label":"fan-shaped body",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnail.png"
      },
      "94":{
         "id":"VFB_00102282",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnailT.png",
         "label":"NO on JRC2018Unisex adult brain",
         "center":"None",
         "index":94,
         "type_id":"FBbt_00003680",
         "type_label":"nodulus",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnail.png"
      },
      "44":{
         "id":"VFB_00102218",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnailT.png",
         "label":"IPS on JRC2018Unisex adult brain",
         "center":"None",
         "index":44,
         "type_id":"FBbt_00045046",
         "type_label":"inferior posterior slope",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnail.png"
      },
      "32":{
         "id":"VFB_00102171",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnailT.png",
         "label":"CRE on JRC2018Unisex adult brain",
         "center":"None",
         "index":32,
         "type_id":"FBbt_00045037",
         "type_label":"adult crepine",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnail.png"
      },
      "35":{
         "id":"VFB_00102176",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnailT.png",
         "label":"SCL on JRC2018Unisex adult brain",
         "center":"None",
         "index":35,
         "type_id":"FBbt_00040048",
         "type_label":"superior clamp",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnail.png"
      },
      "42":{
         "id":"VFB_00102214",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnailT.png",
         "label":"GOR on JRC2018Unisex adult brain",
         "center":"None",
         "index":42,
         "type_id":"FBbt_00040039",
         "type_label":"gorget",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnail.png"
      },
      "21":{
         "id":"VFB_00102139",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnailT.png",
         "label":"BU on JRC2018Unisex adult brain",
         "center":"None",
         "index":21,
         "type_id":"FBbt_00003682",
         "type_label":"bulb",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnail.png"
      },
      "19":{
         "id":"VFB_00102137",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnailT.png",
         "label":"PB on JRC2018Unisex adult brain",
         "center":"None",
         "index":19,
         "type_id":"FBbt_00003668",
         "type_label":"protocerebral bridge",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnail.png"
      },
      "38":{
         "id":"VFB_00102190",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnailT.png",
         "label":"ATL on JRC2018Unisex adult brain",
         "center":"None",
         "index":38,
         "type_id":"FBbt_00045039",
         "type_label":"antler",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnail.png"
      },
      "14":{
         "id":"VFB_00102124",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnailT.png",
         "label":"b\\'L on JRC2018Unisex adult brain",
         "center":"None",
         "index":14,
         "type_id":"FBbt_00013694",
         "type_label":"adult mushroom body beta'-lobe",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnail.png"
      },
      "11":{
         "id":"VFB_00102119",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnailT.png",
         "label":"aL on JRC2018Unisex adult brain",
         "center":"None",
         "index":11,
         "type_id":"FBbt_00110657",
         "type_label":"adult mushroom body alpha-lobe",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnail.png"
      },
      "30":{
         "id":"VFB_00102164",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnailT.png",
         "label":"SIP on JRC2018Unisex adult brain",
         "center":"None",
         "index":30,
         "type_id":"FBbt_00045032",
         "type_label":"superior intermediate protocerebrum",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnail.png"
      },
      "36":{
         "id":"VFB_00102179",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnailT.png",
         "label":"ICL on JRC2018Unisex adult brain",
         "center":"None",
         "index":36,
         "type_id":"FBbt_00040049",
         "type_label":"inferior clamp",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnail.png"
      },
      "3":{
         "id":"VFB_00102107",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
         "label":"ME on JRC2018Unisex adult brain",
         "center":"None",
         "index":3,
         "type_id":"FBbt_00003748",
         "type_label":"medulla",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png"
      },
      "15":{
         "id":"VFB_00102133",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnailT.png",
         "label":"gL on JRC2018Unisex adult brain",
         "center":"None",
         "index":15,
         "type_id":"FBbt_00013695",
         "type_label":"adult mushroom body gamma-lobe",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnail.png"
      },
      "5":{
         "id":"VFB_00102109",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnailT.png",
         "label":"LO on JRC2018Unisex adult brain",
         "center":"None",
         "index":5,
         "type_id":"FBbt_00003852",
         "type_label":"lobula",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnail.png"
      },
      "18":{
         "id":"VFB_00102135",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnailT.png",
         "label":"EB on JRC2018Unisex adult brain",
         "center":"None",
         "index":18,
         "type_id":"FBbt_00003678",
         "type_label":"ellipsoid body",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnail.png"
      },
      "33":{
         "id":"VFB_00102174",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnailT.png",
         "label":"ROB on JRC2018Unisex adult brain",
         "center":"None",
         "index":33,
         "type_id":"FBbt_00048509",
         "type_label":"adult round body",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnail.png"
      },
      "50":{
         "id":"VFB_00102280",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnailT.png",
         "label":"GNG on JRC2018Unisex adult brain",
         "center":"None",
         "index":50,
         "type_id":"FBbt_00014013",
         "type_label":"adult gnathal ganglion",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnail.png"
      },
      "13":{
         "id":"VFB_00102123",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnailT.png",
         "label":"bL on JRC2018Unisex adult brain",
         "center":"None",
         "index":13,
         "type_id":"FBbt_00110658",
         "type_label":"adult mushroom body beta-lobe",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnail.png"
      },
      "47":{
         "id":"VFB_00102274",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnailT.png",
         "label":"FLA on JRC2018Unisex adult brain",
         "center":"None",
         "index":47,
         "type_id":"FBbt_00045050",
         "type_label":"flange",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnail.png"
      },
      "29":{
         "id":"VFB_00102162",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnailT.png",
         "label":"SLP on JRC2018Unisex adult brain",
         "center":"None",
         "index":29,
         "type_id":"FBbt_00007054",
         "type_label":"superior lateral protocerebrum",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnail.png"
      },
      "48":{
         "id":"VFB_00102275",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnailT.png",
         "label":"CAN on JRC2018Unisex adult brain",
         "center":"None",
         "index":48,
         "type_id":"FBbt_00045051",
         "type_label":"cantle",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnail.png"
      },
      "4":{
         "id":"VFB_00102108",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnailT.png",
         "label":"AME on JRC2018Unisex adult brain",
         "center":"None",
         "index":4,
         "type_id":"FBbt_00045003",
         "type_label":"accessory medulla",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnail.png"
      },
      "12":{
         "id":"VFB_00102121",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnailT.png",
         "label":"a\\'L on JRC2018Unisex adult brain",
         "center":"None",
         "index":12,
         "type_id":"FBbt_00013691",
         "type_label":"adult mushroom body alpha'-lobe",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnail.png"
      },
      "25":{
         "id":"VFB_00102148",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnailT.png",
         "label":"PVLP on JRC2018Unisex adult brain",
         "center":"None",
         "index":25,
         "type_id":"FBbt_00040042",
         "type_label":"posterior ventrolateral protocerebrum",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnail.png"
      },
      "45":{
         "id":"VFB_00102271",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnailT.png",
         "label":"SAD on JRC2018Unisex adult brain",
         "center":"None",
         "index":45,
         "type_id":"FBbt_00045048",
         "type_label":"saddle",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnail.png"
      },
      "31":{
         "id":"VFB_00102170",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnailT.png",
         "label":"SMP on JRC2018Unisex adult brain",
         "center":"None",
         "index":31,
         "type_id":"FBbt_00007055",
         "type_label":"superior medial protocerebrum",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnail.png"
      },
      "41":{
         "id":"VFB_00102213",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnailT.png",
         "label":"EPA on JRC2018Unisex adult brain",
         "center":"None",
         "index":41,
         "type_id":"FBbt_00040040",
         "type_label":"epaulette",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnail.png"
      },
      "43":{
         "id":"VFB_00102215",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnailT.png",
         "label":"SPS on JRC2018Unisex adult brain",
         "center":"None",
         "index":43,
         "type_id":"FBbt_00045040",
         "type_label":"superior posterior slope",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnail.png"
      },
      "27":{
         "id":"VFB_00102154",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnailT.png",
         "label":"WED on JRC2018Unisex adult brain",
         "center":"None",
         "index":27,
         "type_id":"FBbt_00045027",
         "type_label":"wedge",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnail.png"
      },
      "24":{
         "id":"VFB_00102146",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnailT.png",
         "label":"AVLP on JRC2018Unisex adult brain",
         "center":"None",
         "index":24,
         "type_id":"FBbt_00040043",
         "type_label":"anterior ventrolateral protocerebrum",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnail.png"
      },
      "0":{
         "id":"VFB_00101567",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
         "label":"JRC2018Unisex",
         "center":"None",
         "index":0,
         "type_id":"FBbt_00003624",
         "type_label":"adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png"
      }
   }
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
