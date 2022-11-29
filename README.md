# VFB_queries

To get term info for a term:
get_term_info(ID)

e.g.
```python
from src.vfb_queries import get_term_info

get_term_info('FBbt_00003748')

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
 'Examples': {'VFB_00101567': [{'id': 'VFB_00102107',
    'label': 'ME on JRC2018Unisex adult brain',
    'thumbnail': 'http://www.virtualflybrain.org/data/VFB/i/0010/2107/VFB_00101567/thumbnailT.png'}],
  'VFB_00017894': [{'id': 'VFB_00030624',
    'label': 'medulla on adult brain template JFRC2',
    'thumbnail': 'http://www.virtualflybrain.org/data/VFB/i/0003/0624/thumbnailT.png'}],
  'VFB_00101384': [{'id': 'VFB_00101385',
    'label': 'ME(R) on JRC_FlyEM_Hemibrain',
    'thumbnail': 'http://www.virtualflybrain.org/data/VFB/i/0010/1385/VFB_00101384/thumbnailT.png'}],
  'VFB_00030786': [{'id': 'VFB_00030810',
    'label': 'medulla on adult brain template Ito2014',
    'thumbnail': 'http://www.virtualflybrain.org/data/VFB/i/0003/0810/thumbnailT.png'}]},
 'Queries': [{'query': 'ListAllAvailableImages',
   'function': 'get_instances',
   'takes': [{'short_form': {'&&': ['Class', 'Anatomy']}}]}]}
```

Queries:
```python
get_instances('FBbt_00003686')
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
