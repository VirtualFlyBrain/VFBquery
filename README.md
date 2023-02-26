# VFB_queries

to setup requirements:
```bash
pip install vfb_queries
```

To get term info for a term:
get_term_info(ID)

e.g.
```python
import vfb_queries as vfb
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
