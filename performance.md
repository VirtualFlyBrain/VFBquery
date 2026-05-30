# VFBquery Performance Test Results

**Test Date:** 2026-05-30 15:05:39 UTC
**Git Commit:** ce4f6dd707d2109fbd2b47d5b51e0d4a5a34dece
**Branch:** main
**Workflow Run:** [26687112125](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/26687112125)

## Test Overview

This performance test measures the execution time of all implemented VFB queries organized by functionality:

### 1. Term Information Queries

- **Term Info**: Comprehensive term information retrieval with preview data

### 2. Neuron Part & Synaptic Queries

- **NeuronsPartHere**: Neurons with parts overlapping anatomical regions
- **NeuronsSynaptic**: Neurons with synapses in a region
- **NeuronsPresynapticHere**: Neurons with presynaptic terminals in a region
- **NeuronsPostsynapticHere**: Neurons with postsynaptic terminals in a region

### 3. Anatomical Hierarchy Queries

- **ComponentsOf**: Anatomical components of a structure
- **PartsOf**: Parts of an anatomical structure
- **SubclassesOf**: Subclasses of anatomical terms (can be very slow for complex terms)

### 4. Tract/Nerve & Lineage Queries

- **NeuronClassesFasciculatingHere**: Neurons fasciculating with tracts
- **TractsNervesInnervatingHere**: Tracts/nerves innervating neuropils
- **LineageClonesIn**: Lineage clones in neuropils (complex OWL reasoning)

### 5. Image & Developmental Queries

- **ImagesNeurons**: Neuron images in anatomical regions
- **ImagesThatDevelopFrom**: Developmental lineage images
- **epFrag**: Expression pattern fragments
- **ListAllAvailableImages**: All available images for a term

### 6. Connectivity Queries

- **NeuronNeuronConnectivity**: Neuron-to-neuron connectivity
- **NeuronRegionConnectivity**: Neuron-to-region connectivity
- **NeuronInputsTo**: Individual neuron inputs

### 7. Similarity Queries (NBLAST & NeuronBridge)

- **SimilarMorphologyTo**: NBLAST morphological similarity
- **SimilarMorphologyToPartOf**: NBLAST to expression patterns (NBLASTexp)
- **SimilarMorphologyToPartOfexp**: Reverse NBLASTexp
- **SimilarMorphologyToNB**: NeuronBridge matches
- **SimilarMorphologyToNBexp**: NeuronBridge for expression patterns

### 8. Expression & Transcriptomics Queries

- **ExpressionOverlapsHere**: Expression patterns overlapping regions
- **anatScRNAseqQuery**: scRNAseq clusters in anatomy
- **clusterExpression**: Genes expressed in clusters
- **expressionCluster**: Clusters expressing genes
- **scRNAdatasetData**: Cluster data from scRNAseq datasets

### 9. Dataset & Template Queries

- **PaintedDomains**: Template painted anatomy domains
- **DatasetImages**: Images in datasets
- **AllAlignedImages**: Images aligned to templates
- **AlignedDatasets**: Datasets aligned to templates
- **AllDatasets**: All available datasets

### 10. Publication & Transgene Queries

- **TermsForPub**: Terms referencing publications
- **TransgeneExpressionHere**: Transgene expression patterns in regions

## Performance Thresholds

- **Fast queries**: < 1 second (SOLR lookups)
- **Medium queries**: < 3 seconds (Owlery + SOLR)
- **Slow queries**: < 10 seconds (Neo4j + complex processing)
- **Very Slow queries**: < 31 seconds (Complex OWL reasoning - over 30 seconds)

## Test Results

```
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/runpy.py", line 196, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/__main__.py", line 18, in <module>
    main(module=None)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/main.py", line 100, in __init__
    self.parseArgs(argv)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/main.py", line 147, in parseArgs
    self.createTests()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/main.py", line 158, in createTests
    self.test = self.testLoader.loadTestsFromNames(self.testNames,
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/loader.py", line 220, in loadTestsFromNames
    suites = [self.loadTestsFromName(name, module) for name in names]
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/loader.py", line 220, in <listcomp>
    suites = [self.loadTestsFromName(name, module) for name in names]
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/loader.py", line 154, in loadTestsFromName
    module = __import__(module_name)
  File "/home/runner/work/VFBquery/VFBquery/src/__init__.py", line 1, in <module>
    from vfbquery import *
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/__init__.py", line 1, in <module>
    from .vfb_queries import *
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 344, in <module>
    _RE_IMAGE_URL = re.compile(
NameError: name 're' is not defined
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/runpy.py", line 196, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/__main__.py", line 18, in <module>
    main(module=None)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/main.py", line 100, in __init__
    self.parseArgs(argv)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/main.py", line 147, in parseArgs
    self.createTests()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/main.py", line 158, in createTests
    self.test = self.testLoader.loadTestsFromNames(self.testNames,
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/loader.py", line 220, in loadTestsFromNames
    suites = [self.loadTestsFromName(name, module) for name in names]
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/loader.py", line 220, in <listcomp>
    suites = [self.loadTestsFromName(name, module) for name in names]
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/unittest/loader.py", line 154, in loadTestsFromName
    module = __import__(module_name)
  File "/home/runner/work/VFBquery/VFBquery/src/__init__.py", line 1, in <module>
    from vfbquery import *
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/__init__.py", line 1, in <module>
    from .vfb_queries import *
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 344, in <module>
    _RE_IMAGE_URL = re.compile(
NameError: name 're' is not defined
============================= test session starts ==============================
platform linux -- Python 3.10.20, pytest-9.0.3, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.20/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
collecting ... collected 0 items / 5 errors

==================================== ERRORS ====================================
_________ ERROR collecting src/test/test_neuron_neuron_connectivity.py _________
/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:1006: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:688: in _load_unlocked
    ???
<frozen importlib._bootstrap_external>:883: in exec_module
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
src/__init__.py:1: in <module>
    from vfbquery import *
src/vfbquery/__init__.py:1: in <module>
    from .vfb_queries import *
src/vfbquery/vfb_queries.py:344: in <module>
    _RE_IMAGE_URL = re.compile(
E   NameError: name 're' is not defined
_________ ERROR collecting src/test/test_neuron_region_connectivity.py _________
/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:1006: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:688: in _load_unlocked
    ???
<frozen importlib._bootstrap_external>:883: in exec_module
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
src/__init__.py:1: in <module>
    from vfbquery import *
src/vfbquery/__init__.py:1: in <module>
    from .vfb_queries import *
src/vfbquery/vfb_queries.py:344: in <module>
    _RE_IMAGE_URL = re.compile(
E   NameError: name 're' is not defined
________ ERROR collecting src/test/test_upstream_class_connectivity.py _________
/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:1006: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:688: in _load_unlocked
    ???
<frozen importlib._bootstrap_external>:883: in exec_module
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
src/__init__.py:1: in <module>
    from vfbquery import *
src/vfbquery/__init__.py:1: in <module>
    from .vfb_queries import *
src/vfbquery/vfb_queries.py:344: in <module>
    _RE_IMAGE_URL = re.compile(
E   NameError: name 're' is not defined
_______ ERROR collecting src/test/test_downstream_class_connectivity.py ________
/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:1006: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:688: in _load_unlocked
    ???
<frozen importlib._bootstrap_external>:883: in exec_module
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
src/__init__.py:1: in <module>
    from vfbquery import *
src/vfbquery/__init__.py:1: in <module>
    from .vfb_queries import *
src/vfbquery/vfb_queries.py:344: in <module>
    _RE_IMAGE_URL = re.compile(
E   NameError: name 're' is not defined
______________ ERROR collecting src/test/test_vfb_connectivity.py ______________
/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:992: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
<frozen importlib._bootstrap>:1050: in _gcd_import
    ???
<frozen importlib._bootstrap>:1027: in _find_and_load
    ???
<frozen importlib._bootstrap>:1006: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:688: in _load_unlocked
    ???
<frozen importlib._bootstrap_external>:883: in exec_module
    ???
<frozen importlib._bootstrap>:241: in _call_with_frames_removed
    ???
src/__init__.py:1: in <module>
    from vfbquery import *
src/vfbquery/__init__.py:1: in <module>
    from .vfb_queries import *
src/vfbquery/vfb_queries.py:344: in <module>
    _RE_IMAGE_URL = re.compile(
E   NameError: name 're' is not defined
=============================== warnings summary ===============================
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(default=default, dump_default=dump_default, **kwargs)

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986: 10 warnings
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776: 20 warnings
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

src/vfbquery/vfb_queries.py:137
src/vfbquery/vfb_queries.py:137
src/vfbquery/vfb_queries.py:137
src/vfbquery/vfb_queries.py:137
src/vfbquery/vfb_queries.py:137
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:137: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    output_format = fields.String(required=False, missing='table')

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218: 20 warnings
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

src/vfbquery/vfb_queries.py:307
src/vfbquery/vfb_queries.py:307
src/vfbquery/vfb_queries.py:307
src/vfbquery/vfb_queries.py:307
src/vfbquery/vfb_queries.py:307
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:307: ChangedInMarshmallow4Warning: `Field` should not be instantiated. Use `fields.Raw` or  another field subclass instead.
    Publications = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False)

src/vfbquery/vfb_queries.py:308
src/vfbquery/vfb_queries.py:308
src/vfbquery/vfb_queries.py:308
src/vfbquery/vfb_queries.py:308
src/vfbquery/vfb_queries.py:308
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:308: ChangedInMarshmallow4Warning: `Field` should not be instantiated. Use `fields.Raw` or  another field subclass instead.
    Synonyms = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False, allow_none=True)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR src/test/test_neuron_neuron_connectivity.py - NameError: name 're' is not defined
ERROR src/test/test_neuron_region_connectivity.py - NameError: name 're' is not defined
ERROR src/test/test_upstream_class_connectivity.py - NameError: name 're' is not defined
ERROR src/test/test_downstream_class_connectivity.py - NameError: name 're' is not defined
ERROR src/test/test_vfb_connectivity.py - NameError: name 're' is not defined
!!!!!!!!!!!!!!!!!!! Interrupted: 5 errors during collection !!!!!!!!!!!!!!!!!!!!
======================== 70 warnings, 5 errors in 1.24s ========================
```

## Summary

❌ **Test Status**: Performance tests failed to run properly

Please check the test output above for errors.

---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2026-05-30 15:05:39 UTC*
