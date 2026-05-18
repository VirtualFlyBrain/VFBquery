# VFBquery Performance Test Results

**Test Date:** 2026-05-18 06:06:49 UTC
**Git Commit:** 5ce1bdcd28211e71538c75862224aa4b65f0cbca
**Branch:** main
**Workflow Run:** [26016497007](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/26016497007)

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
test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance ... ok
test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries ... ok
test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries ... ok
test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":1},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_components_of_FBbt_00003748 to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_components_of_FBbt_00003748 to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3koa1.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

ok
test_05_tract_lineage_queries (src.test.test_query_performance.QueryPerformanceTest)
Test tract/nerve and lineage clone queries ... ok
test_05b_image_queries (src.test.test_query_performance.QueryPerformanceTest)
Test image and developmental lineage queries ... ok
test_06_instance_queries (src.test.test_query_performance.QueryPerformanceTest)
Test instance retrieval queries ... ok
test_07_connectivity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron connectivity queries ... ok
test_08_similarity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... ok
test_09_neuron_input_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron input/synapse queries ... ok
test_10_expression_queries (src.test.test_query_performance.QueryPerformanceTest)
Test expression pattern queries ... ok
test_11_transcriptomics_queries (src.test.test_query_performance.QueryPerformanceTest)
Test scRNAseq transcriptomics queries ... ok
test_12_nblast_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... ok
test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries ... FAIL
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... ok

======================================================================
FAIL: test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 660, in test_13_dataset_template_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "AllAlignedImages exceeded threshold")
AssertionError: 3.22556734085083 not less than 3.0 : AllAlignedImages exceeded threshold

----------------------------------------------------------------------
Ran 15 tests in 57.897s

FAILED (failures=1)
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 1.8613s ✅
get_term_info (individual): 1.5168s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 1.7461s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 1.5883s ✅
NeuronsPresynapticHere: 1.5423s ✅
NeuronsPostsynapticHere: 1.3503s ✅
NeuronNeuronConnectivity: 1.4088s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 2.2006s ✅
PartsOf: 1.2647s ✅
SubclassesOf: 1.3650s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 1.3487s ✅
TractsNervesInnervatingHere: 1.3687s ✅
LineageClonesIn: 1.2555s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 1.9445s ✅
ImagesThatDevelopFrom: 1.3309s ✅
epFrag: 1.1978s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 1.2294s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.2190s ✅
NeuronRegionConnectivityQuery: 1.3105s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 0.6869s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 3.1928s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 0.8021s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 0.5927s ✅
  └─ Found 57 total clusters, returned 10
clusterExpression: 1.8603s ✅
  └─ Found 4588 genes expressed, returned 10
expressionCluster: 0.6627s ✅
  └─ Found 9 clusters expressing gene
scRNAdatasetData: 0.6821s ✅
  └─ Found 13 clusters in dataset, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 0.7203s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.5889s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.6568s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.6891s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.6082s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.6105s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 0.5271s ✅
  └─ Found 46 images in dataset, returned 10
AllAlignedImages: 3.2256s ✅
  └─ Found 527179 aligned images, returned 10

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.5796s ✅
  └─ Found 2 terms for publication
TransgeneExpressionHere: 1.8124s ✅
  └─ Found 2340 transgene expressions, returned 10
✅ All publication/transgene queries completed

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 2.462s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.1871 seconds
VFB_00101567 query took: 1.2739 seconds
Total time for both queries: 2.4609 seconds
Performance Level: 🟡 Good (1.5-3 seconds)
==================================================
Performance test completed successfully!
```

## Summary

✅ **Test Status**: Performance tests completed


---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2026-05-18 06:06:49 UTC*
