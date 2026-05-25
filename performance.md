# VFBquery Performance Test Results

**Test Date:** 2026-05-25 06:46:00 UTC
**Git Commit:** c6fa8f2e223928d26a055963818c0d45cc3dd00a
**Branch:** main
**Workflow Run:** [26386445191](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/26386445191)

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
Test synaptic terminal queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":258},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_neurons_synaptic_FBbt_00007401_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_neurons_synaptic_FBbt_00007401_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3koa1.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":172},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_neurons_presynaptic_FBbt_00007401_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_neurons_presynaptic_FBbt_00007401_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3koa1.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

ok
test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":257},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_neurons_postsynaptic_FBbt_00007401_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_neurons_postsynaptic_FBbt_00007401_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3koa1.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":0},
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
test_07b_downstream_class_connectivity (src.test.test_query_performance.QueryPerformanceTest)
Test DownstreamClassConnectivity query (multi-step aggregation) ... ok
test_07b_upstream_class_connectivity (src.test.test_query_performance.QueryPerformanceTest)
Test UpstreamClassConnectivity query (multi-step aggregation) ... ok
test_07c_cross_dataset_connectivity (src.test.test_query_performance.QueryPerformanceTest)
Test cross-dataset query_connectivity (live, both-end filtered) ... ok
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
    "QTime":263},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_similar_neurons_VFB_jrchk00s_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_similar_neurons_VFB_jrchk00s_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3koa1.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

ok
test_12_nblast_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... ok
test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries ... ok
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... ok

----------------------------------------------------------------------
Ran 18 tests in 144.969s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 1.9618s ✅
get_term_info (individual): 1.4609s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 3.4613s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 9.5884s ✅
NeuronsPresynapticHere: 2.2804s ✅
NeuronsPostsynapticHere: 3.2414s ✅
NeuronNeuronConnectivity: 1.3997s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 2.0500s ✅
PartsOf: 1.3868s ✅
SubclassesOf: 1.4358s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 1.3813s ✅
TractsNervesInnervatingHere: 1.2571s ✅
LineageClonesIn: 1.1679s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 2.0292s ✅
ImagesThatDevelopFrom: 1.3512s ✅
epFrag: 1.3034s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 1.1613s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.1752s ✅
NeuronRegionConnectivityQuery: 1.2544s ✅

================================================================================
DOWNSTREAM CLASS CONNECTIVITY (multi-step aggregation)
================================================================================
DownstreamClassConnectivity: 2.2487s ✅

================================================================================
UPSTREAM CLASS CONNECTIVITY (multi-step aggregation)
================================================================================
UpstreamClassConnectivity: 1.2739s ✅

================================================================================
CROSS-DATASET CONNECTIVITY (live, slow)
================================================================================
QueryConnectivity: 1.6077s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 22.1189s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 3.0878s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 0.8439s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 0.5937s ✅
  └─ Found 57 total clusters, returned 10
clusterExpression: 48.6247s ✅
  └─ Found 4588 genes expressed, returned 10
clusterExpression: Skipped (test data may not exist): 48.62468385696411 not less than 15.0 : clusterExpression exceeded threshold
expressionCluster: 0.7341s ✅
  └─ Found 9 clusters expressing gene
scRNAdatasetData: 0.6389s ✅
  └─ Found 13 clusters in dataset, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 0.8477s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.5745s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.5672s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.5120s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.7246s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.5910s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 0.6042s ✅
  └─ Found 46 images in dataset, returned 10
AllAlignedImages: 2.9315s ✅
  └─ Found 527179 aligned images, returned 10
AlignedDatasets: 0.5952s ✅
  └─ Found 86 aligned datasets, returned 10
AllDatasets: 1.3130s ✅
  └─ Found 130 total datasets, returned 20
✅ All dataset/template queries completed

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.5774s ✅
  └─ Found 2 terms for publication
TransgeneExpressionHere: 2.1445s ✅
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
Ran 1 test in 2.471s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.1850 seconds
VFB_00101567 query took: 1.2853 seconds
Total time for both queries: 2.4703 seconds
Performance Level: 🟡 Good (1.5-3 seconds)
==================================================
Performance test completed successfully!
============================= test session starts ==============================
platform linux -- Python 3.10.20, pytest-9.0.3, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.20/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
collecting ... collected 55 items

src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results PASSED [  1%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys PASSED [  3%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present PASSED [  5%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected PASSED [  7%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream PASSED [  9%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream PASSED [ 10%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe PASSED [ 12%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns PASSED [ 14%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected PASSED [ 16%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation PASSED [ 18%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results PASSED [ 20%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys PASSED [ 21%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present PASSED [ 23%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected PASSED [ 25%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe PASSED [ 27%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns PASSED [ 29%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected PASSED [ 30%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation PASSED [ 32%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results PASSED [ 34%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys PASSED [ 36%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present PASSED [ 38%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected PASSED [ 40%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero PASSED [ 41%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe PASSED [ 43%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns PASSED [ 45%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected PASSED [ 47%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe PASSED [ 49%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts PASSED [ 50%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows PASSED [ 52%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root PASSED [ 54%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation PASSED [ 56%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results PASSED [ 58%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys PASSED [ 60%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present PASSED [ 61%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected PASSED [ 63%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero PASSED [ 65%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe PASSED [ 67%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns PASSED [ 69%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected PASSED [ 70%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe PASSED [ 72%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts PASSED [ 74%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows PASSED [ 76%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root PASSED [ 78%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation PASSED [ 80%]
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets PASSED [ 81%]
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol PASSED [ 83%]
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present PASSED [ 85%]
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol PASSED [ 87%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types PASSED [ 89%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone PASSED [ 90%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class PASSED [ 92%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results PASSED [ 94%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results PASSED [ 96%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning PASSED [ 98%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error PASSED [100%]

=============================== warnings summary ===============================
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(default=default, dump_default=dump_default, **kwargs)

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

src/vfbquery/vfb_queries.py:137
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:137: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    output_format = fields.String(required=False, missing='table')

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

src/vfbquery/vfb_queries.py:307
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:307: ChangedInMarshmallow4Warning: `Field` should not be instantiated. Use `fields.Raw` or  another field subclass instead.
    Publications = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False)

src/vfbquery/vfb_queries.py:308
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:308: ChangedInMarshmallow4Warning: `Field` should not be instantiated. Use `fields.Raw` or  another field subclass instead.
    Synonyms = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False, allow_none=True)

src/test/test_neuron_neuron_connectivity.py:22
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:22: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:31
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:31: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:41
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:41: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:51
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:51: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:59
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:59: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:70
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:70: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:85
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:85: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:93
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:93: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:101
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:101: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:23
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:23: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:32
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:32: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:42
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:42: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:52
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:52: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:64
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:64: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:72
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:72: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:80
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:80: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:25
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:25: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:34
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:34: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:47
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:47: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:55
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:55: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:64
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:64: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:76
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:76: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:84
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:84: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:95
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:95: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:102
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:102: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:124
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:124: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:168
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:168: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:181
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:181: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:25
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:25: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:34
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:34: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:47
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:47: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:55
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:55: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:64
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:64: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:76
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:76: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:84
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:84: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:95
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:95: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:102
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:102: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:123
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:123: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:171
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:171: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:185
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:185: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:16
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:16: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:21
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:21: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:28
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:28: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:34
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:34: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:47
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:47: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:56
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:56: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:71
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:71: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:85
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:85: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:101
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:101: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:114
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:114: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 55 passed, 64 warnings in 1456.63s (0:24:16) =================
```

## Summary

✅ **Test Status**: Performance tests completed


---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2026-05-25 06:46:00 UTC*
