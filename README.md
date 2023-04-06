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
   "Domains":{
      "6":{
         "id":"VFB_00102110",
         "type_id":"FBbt_00003885",
         "label":"LOP on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"lobula plate",
         "index":6
      },
      "22":{
         "id":"VFB_00102140",
         "type_id":"FBbt_00003681",
         "label":"LAL on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult lateral accessory lobe",
         "index":22
      },
      "28":{
         "id":"VFB_00102159",
         "type_id":"FBbt_00007053",
         "label":"LH on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult lateral horn",
         "index":28
      },
      "10":{
         "id":"VFB_00102118",
         "type_id":"FBbt_00007453",
         "label":"PED on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"pedunculus of adult mushroom body",
         "index":10
      },
      "34":{
         "id":"VFB_00102175",
         "type_id":"FBbt_00040038",
         "label":"RUB on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"rubus",
         "index":34
      },
      "23":{
         "id":"VFB_00102141",
         "type_id":"FBbt_00007059",
         "label":"AOTU on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"anterior optic tubercle",
         "index":23
      },
      "39":{
         "id":"VFB_00102201",
         "type_id":"FBbt_00007401",
         "label":"AL on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult antennal lobe",
         "index":39
      },
      "46":{
         "id":"VFB_00102273",
         "type_id":"FBbt_00003982",
         "label":"AMMC on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"antennal mechanosensory and motor center",
         "index":46
      },
      "26":{
         "id":"VFB_00102152",
         "type_id":"FBbt_00040044",
         "label":"PLP on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"posterior lateral protocerebrum",
         "index":26
      },
      "37":{
         "id":"VFB_00102185",
         "type_id":"FBbt_00040050",
         "label":"IB on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"inferior bridge",
         "index":37
      },
      "59":{
         "id":"VFB_00102281",
         "type_id":"FBbt_00040060",
         "label":"GA on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"gall",
         "index":59
      },
      "7":{
         "id":"VFB_00102114",
         "type_id":"FBbt_00007385",
         "label":"CA on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"calyx of adult mushroom body",
         "index":7
      },
      "40":{
         "id":"VFB_00102212",
         "type_id":"FBbt_00040041",
         "label":"VES on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"vest",
         "index":40
      },
      "49":{
         "id":"VFB_00102276",
         "type_id":"FBbt_00040051",
         "label":"PRW on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"prow",
         "index":49
      },
      "16":{
         "id":"VFB_00102134",
         "type_id":"FBbt_00003679",
         "label":"FB on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"fan-shaped body",
         "index":16
      },
      "94":{
         "id":"VFB_00102282",
         "type_id":"FBbt_00003680",
         "label":"NO on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"nodulus",
         "index":94
      },
      "44":{
         "id":"VFB_00102218",
         "type_id":"FBbt_00045046",
         "label":"IPS on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"inferior posterior slope",
         "index":44
      },
      "32":{
         "id":"VFB_00102171",
         "type_id":"FBbt_00045037",
         "label":"CRE on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult crepine",
         "index":32
      },
      "35":{
         "id":"VFB_00102176",
         "type_id":"FBbt_00040048",
         "label":"SCL on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"superior clamp",
         "index":35
      },
      "42":{
         "id":"VFB_00102214",
         "type_id":"FBbt_00040039",
         "label":"GOR on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"gorget",
         "index":42
      },
      "21":{
         "id":"VFB_00102139",
         "type_id":"FBbt_00003682",
         "label":"BU on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"bulb",
         "index":21
      },
      "19":{
         "id":"VFB_00102137",
         "type_id":"FBbt_00003668",
         "label":"PB on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"protocerebral bridge",
         "index":19
      },
      "38":{
         "id":"VFB_00102190",
         "type_id":"FBbt_00045039",
         "label":"ATL on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"antler",
         "index":38
      },
      "14":{
         "id":"VFB_00102124",
         "type_id":"FBbt_00013694",
         "label":"b\\'L on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult mushroom body beta'-lobe",
         "index":14
      },
      "11":{
         "id":"VFB_00102119",
         "type_id":"FBbt_00110657",
         "label":"aL on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult mushroom body alpha-lobe",
         "index":11
      },
      "30":{
         "id":"VFB_00102164",
         "type_id":"FBbt_00045032",
         "label":"SIP on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"superior intermediate protocerebrum",
         "index":30
      },
      "36":{
         "id":"VFB_00102179",
         "type_id":"FBbt_00040049",
         "label":"ICL on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"inferior clamp",
         "index":36
      },
      "3":{
         "id":"VFB_00102107",
         "type_id":"FBbt_00003748",
         "label":"ME on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"medulla",
         "index":3
      },
      "15":{
         "id":"VFB_00102133",
         "type_id":"FBbt_00013695",
         "label":"gL on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult mushroom body gamma-lobe",
         "index":15
      },
      "5":{
         "id":"VFB_00102109",
         "type_id":"FBbt_00003852",
         "label":"LO on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"lobula",
         "index":5
      },
      "18":{
         "id":"VFB_00102135",
         "type_id":"FBbt_00003678",
         "label":"EB on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"ellipsoid body",
         "index":18
      },
      "33":{
         "id":"VFB_00102174",
         "type_id":"FBbt_00048509",
         "label":"ROB on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult round body",
         "index":33
      },
      "50":{
         "id":"VFB_00102280",
         "type_id":"FBbt_00014013",
         "label":"GNG on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult gnathal ganglion",
         "index":50
      },
      "13":{
         "id":"VFB_00102123",
         "type_id":"FBbt_00110658",
         "label":"bL on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult mushroom body beta-lobe",
         "index":13
      },
      "47":{
         "id":"VFB_00102274",
         "type_id":"FBbt_00045050",
         "label":"FLA on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"flange",
         "index":47
      },
      "29":{
         "id":"VFB_00102162",
         "type_id":"FBbt_00007054",
         "label":"SLP on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"superior lateral protocerebrum",
         "index":29
      },
      "48":{
         "id":"VFB_00102275",
         "type_id":"FBbt_00045051",
         "label":"CAN on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"cantle",
         "index":48
      },
      "4":{
         "id":"VFB_00102108",
         "type_id":"FBbt_00045003",
         "label":"AME on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"accessory medulla",
         "index":4
      },
      "12":{
         "id":"VFB_00102121",
         "type_id":"FBbt_00013691",
         "label":"a\\'L on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult mushroom body alpha'-lobe",
         "index":12
      },
      "25":{
         "id":"VFB_00102148",
         "type_id":"FBbt_00040042",
         "label":"PVLP on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"posterior ventrolateral protocerebrum",
         "index":25
      },
      "45":{
         "id":"VFB_00102271",
         "type_id":"FBbt_00045048",
         "label":"SAD on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"saddle",
         "index":45
      },
      "31":{
         "id":"VFB_00102170",
         "type_id":"FBbt_00007055",
         "label":"SMP on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"superior medial protocerebrum",
         "index":31
      },
      "41":{
         "id":"VFB_00102213",
         "type_id":"FBbt_00040040",
         "label":"EPA on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"epaulette",
         "index":41
      },
      "43":{
         "id":"VFB_00102215",
         "type_id":"FBbt_00045040",
         "label":"SPS on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"superior posterior slope",
         "index":43
      },
      "27":{
         "id":"VFB_00102154",
         "type_id":"FBbt_00045027",
         "label":"WED on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"wedge",
         "index":27
      },
      "24":{
         "id":"VFB_00102146",
         "type_id":"FBbt_00040043",
         "label":"AVLP on JRC2018Unisex adult brain",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"anterior ventrolateral protocerebrum",
         "index":24
      },
      "0":{
         "id":"VFB_00101567",
         "type_id":"FBbt_00003624",
         "label":"JRC2018Unisex",
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
         "center":"None",
         "type_label":"adult brain",
         "index":0
      }
   },
   "Images":{
      "VFBc_00101567":[
         {
            "id":"VFBc_00101567",
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd",
            "orientation":"",
            "label":"JRC2018Unisex_c",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj",
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
            "voxel":{
               "X":0.5189161,
               "Y":0.5189161,
               "Z":1.0
            },
            "center":{
               "X":605,
               "Y":283,
               "Z":87
            },
            "extent":{
               "X":1211,
               "Y":567,
               "Z":175
            },
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz"
         }
      ]
   },
   "IsIndividual":true,
   "IsClass":false,
   "Id":"VFB_00101567",
   "Meta":{
      "Name":"[JRC2018Unisex](VFB_00101567)",
      "Description":"Janelia 2018 unisex, averaged adult brain template",
      "Comment":"",
      "Types":"[adult brain](FBbt_00003624)"
   },
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
   "Name":"JRC2018Unisex",
   "IsTemplate":true,
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
