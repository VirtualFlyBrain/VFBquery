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
   'Name':'medulla',
   'Meta':{
      'Name':'[medulla](FBbt_00003748)',
      'Description':'The second optic neuropil, sandwiched between the lamina and the lobula complex. It is divided into 10 layers: 1-6 make up the outer (distal) medulla, the seventh (or serpentine) layer exhibits a distinct architecture and layers 8-10 make up the inner (proximal) medulla (Ito et al., 2014).',
      'Comment':'',
      'Types':'[synaptic neuropil domain](FBbt_00040007)',
      'Relationships':'[develops from](RO_0002202): [medulla anlage](FBbt_00001935); [is part of](BFO_0000050): [adult optic lobe](FBbt_00003701)',
      'Cross References':'![Insect Brain DB](https://insectbraindb.org/app/assets/images/Megalopta_frontal.png) [Insect Brain DB](https://insectbraindb.org/): [38](https://insectbraindb.org/app/structures/38)'
   },
   'Id':'FBbt_00003748',
   'Tags':[
      'Adult',
      'Nervous_system',
      'Synaptic_neuropil_domain',
      'Visual_system'
   ],
   'IsClass':True,
   'Queries':[
      {
         'query':'ListAllAvailableImages',
         'label':'List all available images of medulla',
         'function':'get_instances',
         'takes':{
            'short_form':{
               '$and':[
                  'Class',
                  'Anatomy'
               ]
            },
            'default':{
               'short_form':'FBbt_00003748'
            }
         },
         'preview':0,
         'preview_columns':[
            'id',
            'label',
            'tags',
            'thumbnail'
         ],
         'preview_results':{
            'headers':{
               'id':{
                  'title':'Add',
                  'type':'selection_id',
                  'order':-1
               },
               'label':{
                  'title':'Name',
                  'type':'markdown',
                  'order':0,
                  'sort':{
                     0:'Asc'
                  }
               },
               'tags':{
                  'title':'Gross Types',
                  'type':'tags',
                  'order':3
               },
               'thumbnail':{
                  'title':'Thumbnail',
                  'type':'markdown',
                  'order':9
               }
            },
            'rows':[
               
            ]
         },
         'count':4
      }
   ],
   'IsTemplate':False,
   'IsIndividual':False,
   'SuperTypes':[
      'Entity',
      'Adult',
      'Anatomy',
      'Class',
      'Nervous_system',
      'Synaptic_neuropil',
      'Synaptic_neuropil_domain',
      'Visual_system'
   ],
   'Examples':{
      'VFB_00030786':[
         {
            'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnailT.png',
            'obj':'https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume_man.obj',
            'wlz':'https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.wlz',
            'label':'medulla on adult brain template Ito2014',
            'id':'VFB_00030810',
            'nrrd':'https://www.virtualflybrain.org/data/VFB/i/0003/0810/volume.nrrd',
            'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnail.png'
         }
      ],
      'VFB_00101567':[
         {
            'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png',
            'obj':'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume_man.obj',
            'wlz':'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.wlz',
            'label':'ME on JRC2018Unisex adult brain',
            'id':'VFB_00102107',
            'nrrd':'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/volume.nrrd',
            'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png'
         }
      ],
      'VFB_00017894':[
         {
            'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnailT.png',
            'obj':'https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume_man.obj',
            'wlz':'https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.wlz',
            'label':'medulla on adult brain template JFRC2',
            'id':'VFB_00030624',
            'nrrd':'https://www.virtualflybrain.org/data/VFB/i/0003/0624/volume.nrrd',
            'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnail.png'
         }
      ],
      'VFB_00101384':[
         {
            'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnailT.png',
            'obj':'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume_man.obj',
            'wlz':'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.wlz',
            'label':'ME(R) on JRC_FlyEM_Hemibrain',
            'id':'VFB_00101385',
            'nrrd':'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/volume.nrrd',
            'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png'
         }
      ]
   }
}
```
Individual example:
```python
vfb.get_term_info('VFB_00000001')
```

```json
{
   'Name':'fru-M-200266',
   'IsTemplate':False,
   'IsClass':False,
   'Queries':[
      {
         'query':'SimilarMorphologyTo',
         'label':'Find similar neurons to fru-M-200266',
         'function':'get_similar_neurons',
         'takes':{
            'short_form':{
               '$and':[
                  'Individual',
                  'Neuron'
               ]
            },
            'default':{
               'neuron':'VFB_00000001',
               'similarity_score':'NBLAST_score'
            }
         },
         'preview':5,
         'preview_columns':[
            'id',
            'score',
            'name',
            'tags',
            'thumbnail'
         ],
         'preview_results':{
            'headers':{
               'id':{
                  'title':'Add',
                  'type':'selection_id',
                  'order':-1
               },
               'score':{
                  'title':'Score',
                  'type':'numeric',
                  'order':1,
                  'sort':{
                     0:'Desc'
                  }
               },
               'name':{
                  'title':'Name',
                  'type':'markdown',
                  'order':1,
                  'sort':{
                     1:'Asc'
                  }
               },
               'tags':{
                  'title':'Tags',
                  'type':'tags',
                  'order':2
               },
               'thumbnail':{
                  'title':'Thumbnail',
                  'type':'markdown',
                  'order':9
               }
            },
            'rows':[
               {
                  'id':'VFB_00000333',
                  'score':0.61,
                  'name':'[fru-M-000204](VFB_00000333)',
                  'tags':'Nervous_system|Expression_pattern_fragment|Neuron|Adult',
                  'thumbnail':"[![fru-M-000204 aligned to adult brain template JFRC2](http://virtualflybrain.org/reports/VFB_00000333/thumbnail.png 'fru-M-000204 aligned to adult brain template JFRC2')](VFB_00017894,VFB_00000333)"
               },
               {
                  'id':'VFB_00000333',
                  'score':0.61,
                  'name':'[fru-M-000204](VFB_00000333)',
                  'tags':'Nervous_system|Expression_pattern_fragment|Neuron|Adult',
                  'thumbnail':"[![fru-M-000204 aligned to JRC2018Unisex](http://virtualflybrain.org/reports/VFB_00000333/thumbnail.png 'fru-M-000204 aligned to JRC2018Unisex')](VFB_00101567,VFB_00000333)"
               },
               {
                  'id':'VFB_00002439',
                  'score':0.6,
                  'name':'[fru-M-900020](VFB_00002439)',
                  'tags':'Expression_pattern_fragment|Nervous_system|Neuron|Adult',
                  'thumbnail':"[![fru-M-900020 aligned to adult brain template JFRC2](http://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00017894/thumbnail.png 'fru-M-900020 aligned to adult brain template JFRC2')](VFB_00017894,VFB_00002439)"
               },
               {
                  'id':'VFB_00002439',
                  'score':0.6,
                  'name':'[fru-M-900020](VFB_00002439)',
                  'tags':'Expression_pattern_fragment|Nervous_system|Neuron|Adult',
                  'thumbnail':"[![fru-M-900020 aligned to JRC2018Unisex](http://www.virtualflybrain.org/data/VFB/i/0000/2439/VFB_00101567/thumbnail.png 'fru-M-900020 aligned to JRC2018Unisex')](VFB_00101567,VFB_00002439)"
               },
               {
                  'id':'VFB_00001880',
                  'score':0.59,
                  'name':'[fru-M-100041](VFB_00001880)',
                  'tags':'Nervous_system|Expression_pattern_fragment|Neuron|Adult',
                  'thumbnail':"[![fru-M-100041 aligned to JRC2018Unisex](http://www.virtualflybrain.org/data/VFB/i/0000/1880/VFB_00101567/thumbnail.png 'fru-M-100041 aligned to JRC2018Unisex')](VFB_00101567,VFB_00001880)"
               }
            ]
         },
         'count':60
      }
   ],
   'Id':'VFB_00000001',
   'SuperTypes':[
      'Entity',
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
      'NBLAST'
   ],
   'Images':{
      'VFB_00101567':[
         {
            'wlz':'https://virtualflybrain.org/reports/VFB_00000001/volume.wlz',
            'id':'VFB_00000001',
            'swc':'https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.swc',
            'label':'fru-M-200266',
            'thumbnail':'https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png',
            'obj':'https://virtualflybrain.org/reports/VFB_00000001/volume.obj',
            'nrrd':'https://www.virtualflybrain.org/data/VFB/i/0000/0001/VFB_00101567/volume.nrrd',
            'thumbnail_transparent':'https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png'
         }
      ],
      'VFB_00017894':[
         {
            'wlz':'https://virtualflybrain.org/reports/VFB_00000001/volume.wlz',
            'id':'VFB_00000001',
            'swc':'https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.swc',
            'label':'fru-M-200266',
            'thumbnail':'https://virtualflybrain.org/reports/VFB_00000001/thumbnail.png',
            'obj':'https://virtualflybrain.org/reports/VFB_00000001/volume.obj',
            'nrrd':'https://www.virtualflybrain.org/data/VFB/i/0000/0001/volume.nrrd',
            'thumbnail_transparent':'https://virtualflybrain.org/reports/VFB_00000001/thumbnailT.png'
         }
      ]
   },
   'IsIndividual':True,
   'Meta':{
      'Name':'[fru-M-200266](VFB_00000001)',
      'Description':'',
      'Comment':'OutAge: Adult 5~15 days',
      'Types':'[adult DM6 lineage neuron](FBbt_00050144); [expression pattern fragment](VFBext_0000004)',
      'Relationships':'[expresses](RO_0002292): [Scer\\GAL4[fru.P1.D]](FBal0276838); [is part of](BFO_0000050): [Scer\\GAL4[fru.P1.D] expression pattern](VFBexp_FBal0276838), [adult brain](FBbt_00003624), [male organism](FBbt_00007004); [overlaps](RO_0002131): [adult antennal lobe](FBbt_00007401), [adult crepine](FBbt_00045037), [adult lateral accessory lobe](FBbt_00003681), [superior posterior slope](FBbt_00045040), [vest](FBbt_00040041)',
      'Cross References':'[FlyCircuit 1.0](http://flycircuit.tw): [fru-M-200266](http://flycircuit.tw/modules.php?name=clearpage&op=detail_table&neuron=fru-M-200266)'
   },
   'Tags':[
      'Adult',
      'Expression_pattern_fragment',
      'Nervous_system',
      'Neuron'
   ]
}
```
Template example:
```python
vfb.get_term_info('VFB_00101567')
```

```json
{
   'Name':'JRC2018Unisex',
   'Domains':{
      0:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003624',
         'label':'JRC2018Unisex',
         'id':'VFB_00101567',
         'index':0,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult brain'
      },
      3:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003748',
         'label':'ME on JRC2018Unisex adult brain',
         'id':'VFB_00102107',
         'index':3,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'medulla'
      },
      4:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045003',
         'label':'AME on JRC2018Unisex adult brain',
         'id':'VFB_00102108',
         'index':4,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2108/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'accessory medulla'
      },
      5:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003852',
         'label':'LO on JRC2018Unisex adult brain',
         'id':'VFB_00102109',
         'index':5,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2109/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'lobula'
      },
      6:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003885',
         'label':'LOP on JRC2018Unisex adult brain',
         'id':'VFB_00102110',
         'index':6,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2110/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'lobula plate'
      },
      7:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00007385',
         'label':'CA on JRC2018Unisex adult brain',
         'id':'VFB_00102114',
         'index':7,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2114/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'calyx of adult mushroom body'
      },
      10:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00007453',
         'label':'PED on JRC2018Unisex adult brain',
         'id':'VFB_00102118',
         'index':10,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2118/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'pedunculus of adult mushroom body'
      },
      11:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00110657',
         'label':'aL on JRC2018Unisex adult brain',
         'id':'VFB_00102119',
         'index':11,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2119/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult mushroom body alpha-lobe'
      },
      12:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00013691',
         'label':"a\\'L on JRC2018Unisex adult brain",
         'id':'VFB_00102121',
         'index':12,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2121/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':"adult mushroom body alpha'-lobe"
      },
      13:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00110658',
         'label':'bL on JRC2018Unisex adult brain',
         'id':'VFB_00102123',
         'index':13,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2123/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult mushroom body beta-lobe'
      },
      14:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00013694',
         'label':"b\\'L on JRC2018Unisex adult brain",
         'id':'VFB_00102124',
         'index':14,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2124/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':"adult mushroom body beta'-lobe"
      },
      15:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00013695',
         'label':'gL on JRC2018Unisex adult brain',
         'id':'VFB_00102133',
         'index':15,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2133/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult mushroom body gamma-lobe'
      },
      16:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003679',
         'label':'FB on JRC2018Unisex adult brain',
         'id':'VFB_00102134',
         'index':16,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2134/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'fan-shaped body'
      },
      18:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003678',
         'label':'EB on JRC2018Unisex adult brain',
         'id':'VFB_00102135',
         'index':18,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2135/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'ellipsoid body'
      },
      19:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003668',
         'label':'PB on JRC2018Unisex adult brain',
         'id':'VFB_00102137',
         'index':19,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2137/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'protocerebral bridge'
      },
      21:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003682',
         'label':'BU on JRC2018Unisex adult brain',
         'id':'VFB_00102139',
         'index':21,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2139/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'bulb'
      },
      22:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003681',
         'label':'LAL on JRC2018Unisex adult brain',
         'id':'VFB_00102140',
         'index':22,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2140/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult lateral accessory lobe'
      },
      23:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00007059',
         'label':'AOTU on JRC2018Unisex adult brain',
         'id':'VFB_00102141',
         'index':23,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2141/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'anterior optic tubercle'
      },
      24:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040043',
         'label':'AVLP on JRC2018Unisex adult brain',
         'id':'VFB_00102146',
         'index':24,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2146/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'anterior ventrolateral protocerebrum'
      },
      25:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040042',
         'label':'PVLP on JRC2018Unisex adult brain',
         'id':'VFB_00102148',
         'index':25,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2148/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'posterior ventrolateral protocerebrum'
      },
      26:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040044',
         'label':'PLP on JRC2018Unisex adult brain',
         'id':'VFB_00102152',
         'index':26,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2152/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'posterior lateral protocerebrum'
      },
      27:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045027',
         'label':'WED on JRC2018Unisex adult brain',
         'id':'VFB_00102154',
         'index':27,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2154/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'wedge'
      },
      28:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00007053',
         'label':'LH on JRC2018Unisex adult brain',
         'id':'VFB_00102159',
         'index':28,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2159/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult lateral horn'
      },
      29:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00007054',
         'label':'SLP on JRC2018Unisex adult brain',
         'id':'VFB_00102162',
         'index':29,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2162/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'superior lateral protocerebrum'
      },
      30:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045032',
         'label':'SIP on JRC2018Unisex adult brain',
         'id':'VFB_00102164',
         'index':30,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2164/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'superior intermediate protocerebrum'
      },
      31:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00007055',
         'label':'SMP on JRC2018Unisex adult brain',
         'id':'VFB_00102170',
         'index':31,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2170/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'superior medial protocerebrum'
      },
      32:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045037',
         'label':'CRE on JRC2018Unisex adult brain',
         'id':'VFB_00102171',
         'index':32,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2171/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult crepine'
      },
      33:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00048509',
         'label':'ROB on JRC2018Unisex adult brain',
         'id':'VFB_00102174',
         'index':33,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2174/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult round body'
      },
      34:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040038',
         'label':'RUB on JRC2018Unisex adult brain',
         'id':'VFB_00102175',
         'index':34,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2175/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'rubus'
      },
      35:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040048',
         'label':'SCL on JRC2018Unisex adult brain',
         'id':'VFB_00102176',
         'index':35,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2176/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'superior clamp'
      },
      36:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040049',
         'label':'ICL on JRC2018Unisex adult brain',
         'id':'VFB_00102179',
         'index':36,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2179/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'inferior clamp'
      },
      37:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040050',
         'label':'IB on JRC2018Unisex adult brain',
         'id':'VFB_00102185',
         'index':37,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2185/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'inferior bridge'
      },
      38:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045039',
         'label':'ATL on JRC2018Unisex adult brain',
         'id':'VFB_00102190',
         'index':38,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2190/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'antler'
      },
      39:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00007401',
         'label':'AL on JRC2018Unisex adult brain',
         'id':'VFB_00102201',
         'index':39,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2201/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult antennal lobe'
      },
      40:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040041',
         'label':'VES on JRC2018Unisex adult brain',
         'id':'VFB_00102212',
         'index':40,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2212/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'vest'
      },
      41:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040040',
         'label':'EPA on JRC2018Unisex adult brain',
         'id':'VFB_00102213',
         'index':41,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2213/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'epaulette'
      },
      42:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040039',
         'label':'GOR on JRC2018Unisex adult brain',
         'id':'VFB_00102214',
         'index':42,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2214/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'gorget'
      },
      43:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045040',
         'label':'SPS on JRC2018Unisex adult brain',
         'id':'VFB_00102215',
         'index':43,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2215/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'superior posterior slope'
      },
      44:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045046',
         'label':'IPS on JRC2018Unisex adult brain',
         'id':'VFB_00102218',
         'index':44,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2218/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'inferior posterior slope'
      },
      45:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045048',
         'label':'SAD on JRC2018Unisex adult brain',
         'id':'VFB_00102271',
         'index':45,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2271/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'saddle'
      },
      46:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003982',
         'label':'AMMC on JRC2018Unisex adult brain',
         'id':'VFB_00102273',
         'index':46,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2273/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'antennal mechanosensory and motor center'
      },
      47:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045050',
         'label':'FLA on JRC2018Unisex adult brain',
         'id':'VFB_00102274',
         'index':47,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2274/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'flange'
      },
      48:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00045051',
         'label':'CAN on JRC2018Unisex adult brain',
         'id':'VFB_00102275',
         'index':48,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2275/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'cantle'
      },
      49:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040051',
         'label':'PRW on JRC2018Unisex adult brain',
         'id':'VFB_00102276',
         'index':49,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2276/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'prow'
      },
      50:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00014013',
         'label':'GNG on JRC2018Unisex adult brain',
         'id':'VFB_00102280',
         'index':50,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2280/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'adult gnathal ganglion'
      },
      59:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00040060',
         'label':'GA on JRC2018Unisex adult brain',
         'id':'VFB_00102281',
         'index':59,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2281/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'gall'
      },
      94:{
         'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnailT.png',
         'type_id':'FBbt_00003680',
         'label':'NO on JRC2018Unisex adult brain',
         'id':'VFB_00102282',
         'index':94,
         'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/2282/VFB_00101567/thumbnail.png',
         'center':None,
         'type_label':'nodulus'
      }
   },
   'Id':'VFB_00101567',
   'IsClass':False,
   'SuperTypes':[
      'Entity',
      'Adult',
      'Anatomy',
      'Individual',
      'Nervous_system',
      'Template',
      'has_image'
   ],
   'IsIndividual':True,
   'Images':{
      'VFBc_00101567':[
         {
            'thumbnail_transparent':'https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnailT.png',
            'wlz':'https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.wlz',
            'orientation':'',
            'extent':{
               'X':1211,
               'Y':567,
               'Z':175
            },
            'label':'JRC2018Unisex_c',
            'id':'VFBc_00101567',
            'voxel':{
               'X':0.5189161,
               'Y':0.5189161,
               'Z':1.0
            },
            'thumbnail':'https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/thumbnail.png',
            'nrrd':'https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume.nrrd',
            'center':{
               'X':605,
               'Y':283,
               'Z':87
            },
            'obj':'https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj'
         }
      ]
   },
   'IsTemplate':True,
   'Queries':[
      
   ],
   'Tags':[
      'Adult',
      'Nervous_system'
   ],
   'Meta':{
      'Name':'[JRC2018Unisex](VFB_00101567)',
      'Description':'Janelia 2018 unisex, averaged adult brain template',
      'Comment':'',
      'Types':'[adult brain](FBbt_00003624)'
   }
}
```

Queries:
```python
vfb.get_instances('FBbt_00003748', return_dataframe=False)
```
```json
{
   'headers':{
      'id':{
         'title':'Add',
         'type':'selection_id',
         'order':-1
      },
      'label':{
         'title':'Name',
         'type':'markdown',
         'order':0,
         'sort':{
            0:'Asc'
         }
      },
      'parent':{
         'title':'Parent Type',
         'type':'markdown',
         'order':1
      },
      'template':{
         'title':'Template',
         'type':'markdown',
         'order':4
      },
      'tags':{
         'title':'Gross Types',
         'type':'tags',
         'order':3
      },
      'source':{
         'title':'Data Source',
         'type':'markdown',
         'order':5
      },
      'source_id':{
         'title':'Data Source',
         'type':'markdown',
         'order':6
      },
      'dataset':{
         'title':'Dataset',
         'type':'markdown',
         'order':7
      },
      'license':{
         'title':'License',
         'type':'markdown',
         'order':8
      },
      'thumbnail':{
         'title':'Thumbnail',
         'type':'markdown',
         'order':9
      }
   },
   'rows':[
      {
         'id':'VFB_00102107',
         'label':'[ME on JRC2018Unisex adult brain](VFB_00102107)',
         'tags':'Nervous_system|Adult|Visual_system|Synaptic_neuropil_domain',
         'parent':'[medulla](FBbt_00003748)',
         'source':'',
         'source_id':'',
         'template':'[JRC2018Unisex](VFB_00101567)',
         'dataset':'[JRC 2018 templates & ROIs](JRC2018)',
         'license':'',
         'thumbnail':"[![ME on JRC2018Unisex adult brain aligned to JRC2018Unisex](http://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnail.png 'ME on JRC2018Unisex adult brain aligned to JRC2018Unisex')](VFB_00101567,VFB_00102107)"
      },
      {
         'id':'VFB_00101385',
         'label':'[ME(R) on JRC_FlyEM_Hemibrain](VFB_00101385)',
         'tags':'Nervous_system|Adult|Visual_system|Synaptic_neuropil_domain',
         'parent':'[medulla](FBbt_00003748)',
         'source':'',
         'source_id':'',
         'template':'[JRC_FlyEM_Hemibrain](VFB_00101384)',
         'dataset':'[JRC_FlyEM_Hemibrain painted domains](Xu2020roi)',
         'license':'',
         'thumbnail':"[![ME(R) on JRC_FlyEM_Hemibrain aligned to JRC_FlyEM_Hemibrain](http://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnail.png 'ME(R) on JRC_FlyEM_Hemibrain aligned to JRC_FlyEM_Hemibrain')](VFB_00101384,VFB_00101385)"
      },
      {
         'id':'VFB_00030810',
         'label':'[medulla on adult brain template Ito2014](VFB_00030810)',
         'tags':'Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain',
         'parent':'[medulla](FBbt_00003748)',
         'source':'',
         'source_id':'',
         'template':'[adult brain template Ito2014](VFB_00030786)',
         'dataset':'[BrainName neuropils and tracts - Ito half-brain](BrainName_Ito_half_brain)',
         'license':'',
         'thumbnail':"[![medulla on adult brain template Ito2014 aligned to adult brain template Ito2014](http://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnail.png 'medulla on adult brain template Ito2014 aligned to adult brain template Ito2014')](VFB_00030786,VFB_00030810)"
      },
      {
         'id':'VFB_00030624',
         'label':'[medulla on adult brain template JFRC2](VFB_00030624)',
         'tags':'Nervous_system|Visual_system|Adult|Synaptic_neuropil_domain',
         'parent':'[medulla](FBbt_00003748)',
         'source':'',
         'source_id':'',
         'template':'[adult brain template JFRC2](VFB_00017894)',
         'dataset':'[BrainName neuropils on adult brain JFRC2 (Jenett, Shinomya)](JenettShinomya_BrainName)',
         'license':'',
         'thumbnail':"[![medulla on adult brain template JFRC2 aligned to adult brain template JFRC2](http://www.virtualflybrain.org/data/VFB/i/0003/0624/VFB_00017894/thumbnail.png 'medulla on adult brain template JFRC2 aligned to adult brain template JFRC2')](VFB_00017894,VFB_00030624)"
      }
   ],
   'count':4
}
```
