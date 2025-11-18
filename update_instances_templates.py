import ast

# Read the current test_results.py
with open('test_results.py', 'r') as f:
    content = f.read()

# Parse the results list
tree = ast.parse(content)
results_assign = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'results':
        results_assign = node
        break

if not results_assign:
    raise ValueError("Could not find results assignment")

# Get the current results list
current_results = ast.literal_eval(ast.unparse(results_assign.value))

# New instances data (from the diff test output for example #4)
new_instances = {
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

# New templates data (from the diff test output for example #5)
new_templates = {
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
         "order": 5,
         "name": "[L1 larval CNS ssTEM - Cardona/Janelia](VFB_00050000)",
         "tags": "Nervous_system|Larva",
         "thumbnail": "[![L1 larval CNS ssTEM - Cardona/Janelia](http://www.virtualflybrain.org/data/VFB/i/0005/0000/VFB_00050000/thumbnail.png 'L1 larval CNS ssTEM - Cardona/Janelia')](VFB_00050000)",
         "dataset": "[larval hugin neurons - EM (Schlegel2016)](Schlegel2016), [Neurons involved in larval fast escape response - EM (Ohyama2016)](Ohyama2015)",
         "license": "[CC_BY](VFBlicense_CC_BY_4_0), [CC_BY_SA](VFBlicense_CC_BY_SA_4_0)"
      },
      {
         "id": "VFB_00049000",
         "order": 6,
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
         "thumbnail": "[![JFRC2](http://www.virtualflybrain.org/data/VFB/i/0001/7894/VFB_00017894/thumbnail.png 'JFRC2')](VFB_00017894)",
         "dataset": "[FlyLight - GMR GAL4 collection (Jenett2012)](Jenett2012)",
         "license": "[CC-BY-NC-SA](VFBlicense_CC_BY_NC_SA_4_0)"
      }
   ],
   "count": 10
}

# Update the results
current_results[3] = new_instances
current_results[4] = new_templates

# Write back to file
import pprint
with open('test_results.py', 'w') as f:
    f.write('results = ')
    f.write(pprint.pformat(current_results, width=120))
    f.write('\n')

print("Updated test_results.py with new instances and templates data.")