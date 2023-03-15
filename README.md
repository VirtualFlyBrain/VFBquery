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
{'meta': {'Name': '[medulla](FBbt_00003748)',
  'SuperTypes': ['Entity',
   'Adult',
   'Anatomy',
   'Class',
   'Nervous_system',
   'Synaptic_neuropil',
   'Synaptic_neuropil_domain',
   'Visual_system'],
  'Tags': ['Adult',
   'Nervous_system',
   'Synaptic_neuropil_domain',
   'Visual_system'],
  'Description': 'The second optic neuropil, sandwiched between the lamina and the lobula complex. It is divided into 10 layers: 1-6 make up the outer (distal) medulla, the seventh (or serpentine) layer exhibits a distinct architecture and layers 8-10 make up the inner (proximal) medulla (Ito et al., 2014).',
  'Comment': ''},
 'Examples': {'VFB_00030786': [{'id': 'VFB_00030810',
    'label': 'medulla on adult brain template Ito2014',
    'thumbnail': 'https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnail.png',
    'thumbnail_transparent': 'https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnailT.png',
    'nrrd': 'https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.nrrd',
    'obj': 'https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume_man.obj',
    'wlz': 'https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.wlz'}],
  'VFB_00101567': [{'id': 'VFB_00102107',
    'label': 'ME on JRC2018Unisex adult brain',
    'thumbnail': 'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png',
    'thumbnail_transparent': 'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png',
    'nrrd': 'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.nrrd',
    'obj': 'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume_man.obj',
    'wlz': 'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.wlz'}],
  'VFB_00017894': [{'id': 'VFB_00030624',
    'label': 'medulla on adult brain template JFRC2',
    'thumbnail': 'https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnail.png',
    'thumbnail_transparent': 'https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnailT.png',
    'nrrd': 'https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.nrrd',
    'obj': 'https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume_man.obj',
    'wlz': 'https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.wlz'}],
  'VFB_00101384': [{'id': 'VFB_00101385',
    'label': 'ME(R) on JRC_FlyEM_Hemibrain',
    'thumbnail': 'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png',
    'thumbnail_transparent': 'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnailT.png',
    'nrrd': 'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.nrrd',
    'obj': 'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume_man.obj',
    'wlz': 'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.wlz'}]},
 'Queries': [{'query': 'ListAllAvailableImages',
   'ME(R) on JRC_FlyEM_Hemibrain': 'List all available images of medulla',
   'function': 'get_instances',
   'takes': [{'short_form': {'&&': ['Class', 'Anatomy']},
     'default': 'FBbt_00003748'}]}]}
```
Individual example:
```python
vfb.get_term_info('VFB_00000001')
```

```python
{'meta': {'Name': '[fru-M-200266](VFB_00000001)',
  'SuperTypes': ['Entity',
   'Adult',
   'Anatomy',
   'Cell',
   'Expression_pattern_fragment',
   'Individual',
   'Nervous_system',
   'Neuron',
   'VFB',
   'has_image',
   'FlyCircuit',
   'NBLAST'],
  'Tags': ['Adult', 'Expression_pattern_fragment', 'Nervous_system', 'Neuron'],
  'Description': '',
  'Comment': 'OutAge: Adult 5~15 days'},
 'Thumbnails': {'VFB_00101567': [{'id': 'VFB_00000001',
    'label': 'fru-M-200266',
    'thumbnail': 'https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png',
    'thumbnail_transparent': 'https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png',
    'nrrd': 'https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.nrrd',
    'obj': 'https://virtualflybrain.org/reports/VFB_00000001/volume.obj',
    'wlz': 'https://virtualflybrain.org/reports/VFB_00000001/volume.wlz',
    'swc': 'https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.swc'}],
  'VFB_00017894': [{'id': 'VFB_00000001',
    'label': 'fru-M-200266',
    'thumbnail': 'https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png',
    'thumbnail_transparent': 'https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png',
    'nrrd': 'https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.nrrd',
    'obj': 'https://virtualflybrain.org/reports/VFB_00000001/volume.obj',
    'wlz': 'https://virtualflybrain.org/reports/VFB_00000001/volume.wlz',
    'swc': 'https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.swc'}]},
 'Queries': []}
 ```
Template example:
```python
vfb.get_term_info('VFB_00101567')
```

```python
{
   "Name":"JRC2018Unisex",
   "IsIndividual":true,
   "Domains":{
      "6":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003885",
         "index":6,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnail.png",
         "type_label":"lobula plate",
         "id":"VFB_00102110",
         "label":"LOP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "22":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003681",
         "index":22,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnail.png",
         "type_label":"adult lateral accessory lobe",
         "id":"VFB_00102140",
         "label":"LAL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "28":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00007053",
         "index":28,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnail.png",
         "type_label":"adult lateral horn",
         "id":"VFB_00102159",
         "label":"LH on JRC2018Unisex adult brain",
         "center":"None"
      },
      "10":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00007453",
         "index":10,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnail.png",
         "type_label":"pedunculus of adult mushroom body",
         "id":"VFB_00102118",
         "label":"PED on JRC2018Unisex adult brain",
         "center":"None"
      },
      "34":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040038",
         "index":34,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnail.png",
         "type_label":"rubus",
         "id":"VFB_00102175",
         "label":"RUB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "23":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00007059",
         "index":23,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnail.png",
         "type_label":"anterior optic tubercle",
         "id":"VFB_00102141",
         "label":"AOTU on JRC2018Unisex adult brain",
         "center":"None"
      },
      "39":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00007401",
         "index":39,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnail.png",
         "type_label":"adult antennal lobe",
         "id":"VFB_00102201",
         "label":"AL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "46":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003982",
         "index":46,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnail.png",
         "type_label":"antennal mechanosensory and motor center",
         "id":"VFB_00102273",
         "label":"AMMC on JRC2018Unisex adult brain",
         "center":"None"
      },
      "26":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040044",
         "index":26,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnail.png",
         "type_label":"posterior lateral protocerebrum",
         "id":"VFB_00102152",
         "label":"PLP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "37":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040050",
         "index":37,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnail.png",
         "type_label":"inferior bridge",
         "id":"VFB_00102185",
         "label":"IB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "59":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040060",
         "index":59,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnail.png",
         "type_label":"gall",
         "id":"VFB_00102281",
         "label":"GA on JRC2018Unisex adult brain",
         "center":"None"
      },
      "7":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00007385",
         "index":7,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnail.png",
         "type_label":"calyx of adult mushroom body",
         "id":"VFB_00102114",
         "label":"CA on JRC2018Unisex adult brain",
         "center":"None"
      },
      "40":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040041",
         "index":40,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnail.png",
         "type_label":"vest",
         "id":"VFB_00102212",
         "label":"VES on JRC2018Unisex adult brain",
         "center":"None"
      },
      "49":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040051",
         "index":49,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnail.png",
         "type_label":"prow",
         "id":"VFB_00102276",
         "label":"PRW on JRC2018Unisex adult brain",
         "center":"None"
      },
      "16":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003679",
         "index":16,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnail.png",
         "type_label":"fan-shaped body",
         "id":"VFB_00102134",
         "label":"FB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "94":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003680",
         "index":94,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnail.png",
         "type_label":"nodulus",
         "id":"VFB_00102282",
         "label":"NO on JRC2018Unisex adult brain",
         "center":"None"
      },
      "44":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045046",
         "index":44,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnail.png",
         "type_label":"inferior posterior slope",
         "id":"VFB_00102218",
         "label":"IPS on JRC2018Unisex adult brain",
         "center":"None"
      },
      "32":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045037",
         "index":32,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnail.png",
         "type_label":"adult crepine",
         "id":"VFB_00102171",
         "label":"CRE on JRC2018Unisex adult brain",
         "center":"None"
      },
      "35":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040048",
         "index":35,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnail.png",
         "type_label":"superior clamp",
         "id":"VFB_00102176",
         "label":"SCL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "42":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040039",
         "index":42,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnail.png",
         "type_label":"gorget",
         "id":"VFB_00102214",
         "label":"GOR on JRC2018Unisex adult brain",
         "center":"None"
      },
      "21":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003682",
         "index":21,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnail.png",
         "type_label":"bulb",
         "id":"VFB_00102139",
         "label":"BU on JRC2018Unisex adult brain",
         "center":"None"
      },
      "19":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003668",
         "index":19,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnail.png",
         "type_label":"protocerebral bridge",
         "id":"VFB_00102137",
         "label":"PB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "38":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045039",
         "index":38,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnail.png",
         "type_label":"antler",
         "id":"VFB_00102190",
         "label":"ATL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "14":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00013694",
         "index":14,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnail.png",
         "type_label":"adult mushroom body beta'-lobe",
         "id":"VFB_00102124",
         "label":"b\\'L on JRC2018Unisex adult brain",
         "center":"None"
      },
      "11":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00110657",
         "index":11,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnail.png",
         "type_label":"adult mushroom body alpha-lobe",
         "id":"VFB_00102119",
         "label":"aL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "30":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045032",
         "index":30,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnail.png",
         "type_label":"superior intermediate protocerebrum",
         "id":"VFB_00102164",
         "label":"SIP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "36":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040049",
         "index":36,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnail.png",
         "type_label":"inferior clamp",
         "id":"VFB_00102179",
         "label":"ICL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "3":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003748",
         "index":3,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png",
         "type_label":"medulla",
         "id":"VFB_00102107",
         "label":"ME on JRC2018Unisex adult brain",
         "center":"None"
      },
      "15":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00013695",
         "index":15,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnail.png",
         "type_label":"adult mushroom body gamma-lobe",
         "id":"VFB_00102133",
         "label":"gL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "5":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003852",
         "index":5,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnail.png",
         "type_label":"lobula",
         "id":"VFB_00102109",
         "label":"LO on JRC2018Unisex adult brain",
         "center":"None"
      },
      "18":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003678",
         "index":18,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnail.png",
         "type_label":"ellipsoid body",
         "id":"VFB_00102135",
         "label":"EB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "33":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00048509",
         "index":33,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnail.png",
         "type_label":"adult round body",
         "id":"VFB_00102174",
         "label":"ROB on JRC2018Unisex adult brain",
         "center":"None"
      },
      "50":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00014013",
         "index":50,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnail.png",
         "type_label":"adult gnathal ganglion",
         "id":"VFB_00102280",
         "label":"GNG on JRC2018Unisex adult brain",
         "center":"None"
      },
      "13":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00110658",
         "index":13,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnail.png",
         "type_label":"adult mushroom body beta-lobe",
         "id":"VFB_00102123",
         "label":"bL on JRC2018Unisex adult brain",
         "center":"None"
      },
      "47":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045050",
         "index":47,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnail.png",
         "type_label":"flange",
         "id":"VFB_00102274",
         "label":"FLA on JRC2018Unisex adult brain",
         "center":"None"
      },
      "29":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00007054",
         "index":29,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnail.png",
         "type_label":"superior lateral protocerebrum",
         "id":"VFB_00102162",
         "label":"SLP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "48":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045051",
         "index":48,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnail.png",
         "type_label":"cantle",
         "id":"VFB_00102275",
         "label":"CAN on JRC2018Unisex adult brain",
         "center":"None"
      },
      "4":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045003",
         "index":4,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnail.png",
         "type_label":"accessory medulla",
         "id":"VFB_00102108",
         "label":"AME on JRC2018Unisex adult brain",
         "center":"None"
      },
      "12":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00013691",
         "index":12,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnail.png",
         "type_label":"adult mushroom body alpha'-lobe",
         "id":"VFB_00102121",
         "label":"a\\'L on JRC2018Unisex adult brain",
         "center":"None"
      },
      "25":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040042",
         "index":25,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnail.png",
         "type_label":"posterior ventrolateral protocerebrum",
         "id":"VFB_00102148",
         "label":"PVLP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "45":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045048",
         "index":45,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnail.png",
         "type_label":"saddle",
         "id":"VFB_00102271",
         "label":"SAD on JRC2018Unisex adult brain",
         "center":"None"
      },
      "31":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00007055",
         "index":31,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnail.png",
         "type_label":"superior medial protocerebrum",
         "id":"VFB_00102170",
         "label":"SMP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "41":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040040",
         "index":41,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnail.png",
         "type_label":"epaulette",
         "id":"VFB_00102213",
         "label":"EPA on JRC2018Unisex adult brain",
         "center":"None"
      },
      "43":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045040",
         "index":43,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnail.png",
         "type_label":"superior posterior slope",
         "id":"VFB_00102215",
         "label":"SPS on JRC2018Unisex adult brain",
         "center":"None"
      },
      "27":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00045027",
         "index":27,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnail.png",
         "type_label":"wedge",
         "id":"VFB_00102154",
         "label":"WED on JRC2018Unisex adult brain",
         "center":"None"
      },
      "24":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00040043",
         "index":24,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnail.png",
         "type_label":"anterior ventrolateral protocerebrum",
         "id":"VFB_00102146",
         "label":"AVLP on JRC2018Unisex adult brain",
         "center":"None"
      },
      "0":{
         "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
         "type_id":"FBbt_00003624",
         "index":0,
         "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
         "type_label":"adult brain",
         "id":"VFB_00101567",
         "label":"JRC2018Unisex",
         "center":"None"
      }
   },
   "IsTemplate":true,
   "Tags":[
      "Adult",
      "Nervous_system"
   ],
   "Images":{
      "VFBc_00101567":[
         {
            "thumbnail_transparent":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png",
            "wlz":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz",
            "voxel":{
               "X":0.5189161,
               "Y":0.5189161,
               "Z":1.0
            },
            "nrrd":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd",
            "extent":{
               "X":1211,
               "Y":567,
               "Z":175
            },
            "thumbnail":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png",
            "orientation":"",
            "obj":"https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj",
            "id":"VFBc_00101567",
            "label":"JRC2018Unisex_c",
            "center":{
               "X":605,
               "Y":283,
               "Z":87
            }
         }
      ]
   },
   "SuperTypes":[
      "Entity",
      "Adult",
      "Anatomy",
      "Individual",
      "Nervous_system",
      "Template",
      "has_image"
   ],
   "Meta":{
      "Name":"[JRC2018Unisex](VFB_00101567)",
      "Description":"Janelia 2018 unisex, averaged adult brain template",
      "Comment":""
   },
   "Queries":[
      
   ],
   "IsClass":false,
   "Id":"VFB_00101567"
}
```

Queries:
```python
vfb.get_instances('FBbt_00003686')
```
```python
{'headers': {'label': {'title': 'Name',
   'type': 'markdown',
   'order': 0,
   'sort': {0: 'Asc'}},
  'parent': {'title': 'Parent Type', 'type': 'markdown', 'order': 1},
  'template': {'title': 'Template', 'type': 'string', 'order': 4},
  'tags': {'title': 'Gross Types', 'type': 'tags', 'order': 3}},
 'rows': [{'label': '[KC (L1EM:16438190)](VFB_00100462)',
   'parent': '[Kenyon cell](FBbt_00003686)',
   'template': 'L1 larval CNS ssTEM - Cardona/Janelia',
   'tags': ['Entity',
    'Anatomy',
    'Cell',
    'Individual',
    'Nervous_system',
    'Neuron',
    'has_image',
    'has_neuron_connectivity',
    'L1EM',
    'NBLAST']},
  {'label': '[KC (L1EM:16627950)](VFB_00100485)',
   'parent': '[Kenyon cell](FBbt_00003686)',
   'template': 'L1 larval CNS ssTEM - Cardona/Janelia',
   'tags': ['Entity',
    'Anatomy',
    'Cell',
    'Individual',
    'Nervous_system',
    'Neuron',
    'has_image',
    'has_neuron_connectivity',
    'L1EM',
    'NBLAST']},
...
```
