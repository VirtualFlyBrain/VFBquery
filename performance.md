# VFBquery Performance Test Results

**Test Date:** 2026-05-05 05:19:46 UTC
**Git Commit:** d3baefab2ade89d8c366e4e343ea0634585ed5f9
**Branch:** main
**Workflow Run:** [25358565868](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/25358565868)

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
Test term info query performance ... Failed to cache result: HTTP 503 - <html><body><h1>503 Service Unavailable</h1>
No server is available to handle this request.
</body></html>

Failed to cache result: HTTP 503 - <html><body><h1>503 Service Unavailable</h1>
No server is available to handle this request.
</body></html>

FAIL
test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries ... ok
test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries ... Failed to cache result: HTTP 503 - <html><body><h1>503 Service Unavailable</h1>
No server is available to handle this request.
</body></html>

WARNING: Owlery unavailable for query '<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002113> some <http://purl.obolibrary.org/obo/FBbt_00007401>': ConnectionError
FAIL
test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries ... ok
test_05_tract_lineage_queries (src.test.test_query_performance.QueryPerformanceTest)
Test tract/nerve and lineage clone queries ... WARNING: Owlery unavailable for query '<http://purl.obolibrary.org/obo/FBbt_00005099> and <http://purl.obolibrary.org/obo/RO_0002134> some <http://purl.obolibrary.org/obo/FBbt_00007401>': ConnectionError
Query returned error result for tracts_nerves_innervating_here(FBbt_00007401), clearing cache entry
Failed to clear cache entry: HTTP 500
FAIL
test_05b_image_queries (src.test.test_query_performance.QueryPerformanceTest)
Test image and developmental lineage queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":1223},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_images_neurons_FBbt_00007401_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_images_neurons_FBbt_00007401_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

FAIL
test_06_instance_queries (src.test.test_query_performance.QueryPerformanceTest)
Test instance retrieval queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":1},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_instances_FBbt_00003982_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_instances_FBbt_00003982_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

ok
test_07_connectivity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron connectivity queries ... Failed to cache result: HTTP 503 - <html><body><h1>503 Service Unavailable</h1>
No server is available to handle this request.
</body></html>

FAIL
test_08_similarity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... ok
test_09_neuron_input_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron input/synapse queries ... ok
test_10_expression_queries (src.test.test_query_performance.QueryPerformanceTest)
Test expression pattern queries ... ok
test_11_transcriptomics_queries (src.test.test_query_performance.QueryPerformanceTest)
Test scRNAseq transcriptomics queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":297},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_anatomy_scrnaseq_FBbt_00058230_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_anatomy_scrnaseq_FBbt_00058230_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

ok
test_12_nblast_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... ok
test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":0},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_painted_domains_VFB_00101567_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_painted_domains_VFB_00101567_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

FAIL
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":145},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_painted_domains_VFB_00101567_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_painted_domains_VFB_00101567_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

ok

======================================================================
FAIL: test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 123, in test_01_term_info_queries
    self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "term_info query exceeded threshold")
AssertionError: 56.63698387145996 not less than 31.0 : term_info query exceeded threshold

======================================================================
FAIL: test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 167, in test_03_synaptic_queries
    self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "NeuronsPresynapticHere exceeded threshold")
AssertionError: 832.9208195209503 not less than 31.0 : NeuronsPresynapticHere exceeded threshold

======================================================================
FAIL: test_05_tract_lineage_queries (src.test.test_query_performance.QueryPerformanceTest)
Test tract/nerve and lineage clone queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 255, in test_05_tract_lineage_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "TractsNervesInnervatingHere exceeded threshold")
AssertionError: 296.6967034339905 not less than 15.0 : TractsNervesInnervatingHere exceeded threshold

======================================================================
FAIL: test_05b_image_queries (src.test.test_query_performance.QueryPerformanceTest)
Test image and developmental lineage queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 284, in test_05b_image_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "ImagesNeurons exceeded threshold")
AssertionError: 19.595817804336548 not less than 15.0 : ImagesNeurons exceeded threshold

======================================================================
FAIL: test_07_connectivity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron connectivity queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 350, in test_07_connectivity_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronRegionConnectivityQuery exceeded threshold")
AssertionError: 38.34907150268555 not less than 15.0 : NeuronRegionConnectivityQuery exceeded threshold

======================================================================
FAIL: test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 632, in test_13_dataset_template_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "PaintedDomains exceeded threshold")
AssertionError: 12.052563667297363 not less than 3.0 : PaintedDomains exceeded threshold

----------------------------------------------------------------------
Ran 15 tests in 1452.466s

FAILED (failures=6)
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 6.6012s ✅
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
get_term_info (individual): 56.6370s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 15.6295s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 6.0934s ✅
NeuronsPresynapticHere: 832.9208s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 4.3376s ✅
PartsOf: 4.0472s ✅
SubclassesOf: 2.3160s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 3.7765s ✅
TractsNervesInnervatingHere: 296.6967s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 19.5958s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 9.0422s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 8.2777s ✅
NeuronRegionConnectivityQuery: 38.3491s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 6.5532s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
NeuronInputsTo: 9.3567s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 8.5723s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
[31mConnection Error:[0m 503 (Service Unavailable)
anatScRNAseqQuery: 1.1858s ✅
  └─ Found 57 total clusters, returned 10
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
clusterExpression: 0.6084s ✅
  └─ Found 0 genes expressed
expressionCluster: 25.6153s ✅
  └─ Found 9 clusters expressing gene
expressionCluster: Skipped (test data may not exist): 25.61532688140869 not less than 15.0 : expressionCluster exceeded threshold
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
scRNAdatasetData: 0.7604s ✅
  └─ Found 0 clusters in dataset

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
SimilarMorphologyTo: 4.1683s ✅
  └─ Found 0 NBLAST matches
SimilarMorphologyToPartOf: 2.9795s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.7569s ✅
  └─ Found 0 reverse NBLASTexp matches
[31mConnection Error:[0m 503 (Service Unavailable)
SimilarMorphologyToNB: 0.7920s ✅
  └─ Found 15 NeuronBridge matches, returned 10
[31mConnection Error:[0m 503 (Service Unavailable)
SimilarMorphologyToNBexp: 4.2741s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
PaintedDomains: 12.0526s ✅
  └─ Found 46 painted domains, returned 10

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
TermsForPub: 2.8090s ✅
  └─ Found 2 terms for publication
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
[31mConnection Error:[0m 503 (Service Unavailable)
TransgeneExpressionHere: 6.4369s ✅
  └─ Found 0 transgene expressions
✅ All publication/transgene queries completed

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... FAIL

======================================================================
FAIL: test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/term_info_queries_test.py", line 594, in test_term_info_performance
    self.assertLess(duration_1 + duration_2, max_total_time,
AssertionError: 10.199373483657837 not less than 10.0 : Total query time 10.1994s exceeds 10.0s threshold

----------------------------------------------------------------------
Ran 1 test in 10.200s

FAILED (failures=1)
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 3.7507 seconds
VFB_00101567 query took: 6.4486 seconds
Total time for both queries: 10.1994 seconds
Performance Level: 🔴 Slow (> 6 seconds)
==================================================
```

## Summary

✅ **Test Status**: Performance tests completed


---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2026-05-05 05:19:46 UTC*
