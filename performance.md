# VFBquery Performance Test Results

**Test Date:** 2026-05-06 06:03:22 UTC
**Git Commit:** 493490932985c70ed046b749e5d88f008905b311
**Branch:** main
**Workflow Run:** [25417986900](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/25417986900)

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
Test anatomical hierarchy queries ... ok
test_05_tract_lineage_queries (src.test.test_query_performance.QueryPerformanceTest)
Test tract/nerve and lineage clone queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":0},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_neuron_classes_fasciculating_here_FBbt_00003987 to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_neuron_classes_fasciculating_here_FBbt_00003987 to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

FAIL
test_05b_image_queries (src.test.test_query_performance.QueryPerformanceTest)
Test image and developmental lineage queries ... Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 534, in _make_request
    response = conn.getresponse()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connection.py", line 571, in getresponse
    httplib_response = super().getresponse()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/http/client.py", line 1395, in getresponse
    response.begin()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/http/client.py", line 323, in begin
    version, status, reason = self._read_status()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/http/client.py", line 284, in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/socket.py", line 717, in readinto
    return self._sock.recv_into(b)
TimeoutError: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/adapters.py", line 645, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 841, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/util/retry.py", line 490, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 787, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 536, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 367, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/pysolr.py", line 334, in _send_request
    resp = requests_method(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 640, in post
    return self.request("POST", url, data=data, json=json, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 592, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 706, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/adapters.py", line 691, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 3590, in _owlery_query_to_results
    results = vfb_solr.search(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/pysolr.py", line 735, in search
    response = self._select(params, handler=search_handler)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/pysolr.py", line 413, in _select
    return self._send_request(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/pysolr.py", line 345, in _send_request
    raise SolrError(error_message % (url, err))
pysolr.SolrError: Connection to server 'http://solr.virtualflybrain.org/solr/vfb_json/select/' timed out: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)
Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":0},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_images_that_develop_from_FBbt_00001419_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_images_that_develop_from_FBbt_00001419_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

FAIL
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
Test scRNAseq transcriptomics queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":877},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_expression_overlaps_here_FBbt_00003982_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_expression_overlaps_here_FBbt_00003982_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":859},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_expression_overlaps_here_FBbt_00003982_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_expression_overlaps_here_FBbt_00003982_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":209},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_anatomy_scrnaseq_FBbt_00058230_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_anatomy_scrnaseq_FBbt_00058230_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

FAIL
test_12_nblast_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... Failed to cache result: HTTP 500 - {
  "responseHeader":{
    "status":500,
    "QTime":218},
  "error":{
    "metadata":[
      "error-class","org.apache.solr.common.SolrException",
      "root-error-class","java.nio.file.FileSystemException"],
    "msg":"Server error writing document id vfb_query_anatomy_scrnaseq_FBbt_00058230_dataframe_False to the index",
    "trace":"org.apache.solr.common.SolrException: Server error writing document id vfb_query_anatomy_scrnaseq_FBbt_00058230_dataframe_False to the index\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:246)\n\tat org.apache.solr.update.processor.RunUpdateProcessorFactory$RunUpdateProcessor.processAdd(RunUpdateProcessorFactory.java:73)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.NestedUpdateProcessorFactory$NestedUpdateProcessor.processAdd(NestedUpdateProcessorFactory.java:79)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doLocalAdd(DistributedUpdateProcessor.java:263)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.doVersionAdd(DistributedUpdateProcessor.java:502)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.lambda$versionAdd$0(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.VersionBucket.runWithLock(VersionBucket.java:50)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.versionAdd(DistributedUpdateProcessor.java:343)\n\tat org.apache.solr.update.processor.DistributedUpdateProcessor.processAdd(DistributedUpdateProcessor.java:229)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AddSchemaFieldsUpdateProcessorFactory$AddSchemaFieldsUpdateProcessor.processAdd(AddSchemaFieldsUpdateProcessorFactory.java:481)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldNameMutatingUpdateProcessorFactory$1.processAdd(FieldNameMutatingUpdateProcessorFactory.java:75)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:118)\n\tat org.apache.solr.update.processor.UpdateRequestProcessor.processAdd(UpdateRequestProcessor.java:55)\n\tat org.apache.solr.update.processor.AbstractDefaultValueUpdateProcessorFactory$DefaultValueUpdateProcessor.processAdd(AbstractDefaultValueUpdateProcessorFactory.java:92)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.handleAdds(JsonLoader.java:521)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.processUpdate(JsonLoader.java:180)\n\tat org.apache.solr.handler.loader.JsonLoader$SingleThreadedJsonLoader.load(JsonLoader.java:156)\n\tat org.apache.solr.handler.loader.JsonLoader.load(JsonLoader.java:84)\n\tat org.apache.solr.handler.UpdateRequestHandler$1.load(UpdateRequestHandler.java:97)\n\tat org.apache.solr.handler.ContentStreamHandlerBase.handleRequestBody(ContentStreamHandlerBase.java:82)\n\tat org.apache.solr.handler.RequestHandlerBase.handleRequest(RequestHandlerBase.java:216)\n\tat org.apache.solr.core.SolrCore.execute(SolrCore.java:2637)\n\tat org.apache.solr.servlet.HttpSolrCall.execute(HttpSolrCall.java:794)\n\tat org.apache.solr.servlet.HttpSolrCall.call(HttpSolrCall.java:560)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:437)\n\tat org.apache.solr.servlet.SolrDispatchFilter.doFilter(SolrDispatchFilter.java:367)\n\tat org.eclipse.jetty.servlet.FilterHolder.doFilter(FilterHolder.java:201)\n\tat org.eclipse.jetty.servlet.ServletHandler$Chain.doFilter(ServletHandler.java:1626)\n\tat org.eclipse.jetty.servlet.ServletHandler.doHandle(ServletHandler.java:552)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:143)\n\tat org.eclipse.jetty.security.SecurityHandler.handle(SecurityHandler.java:600)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:235)\n\tat org.eclipse.jetty.server.session.SessionHandler.doHandle(SessionHandler.java:1624)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextHandle(ScopedHandler.java:233)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doHandle(ContextHandler.java:1440)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:188)\n\tat org.eclipse.jetty.servlet.ServletHandler.doScope(ServletHandler.java:505)\n\tat org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1594)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.nextScope(ScopedHandler.java:186)\n\tat org.eclipse.jetty.server.handler.ContextHandler.doScope(ContextHandler.java:1355)\n\tat org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141)\n\tat org.eclipse.jetty.server.handler.ContextHandlerCollection.handle(ContextHandlerCollection.java:191)\n\tat org.eclipse.jetty.server.handler.InetAccessHandler.handle(InetAccessHandler.java:177)\n\tat org.eclipse.jetty.server.handler.HandlerCollection.handle(HandlerCollection.java:146)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.rewrite.handler.RewriteHandler.handle(RewriteHandler.java:322)\n\tat org.eclipse.jetty.server.handler.gzip.GzipHandler.handle(GzipHandler.java:772)\n\tat org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127)\n\tat org.eclipse.jetty.server.Server.handle(Server.java:516)\n\tat org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487)\n\tat org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732)\n\tat org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479)\n\tat org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277)\n\tat org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311)\n\tat org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105)\n\tat org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.runTask(EatWhatYouKill.java:338)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.doProduce(EatWhatYouKill.java:315)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.tryProduce(EatWhatYouKill.java:173)\n\tat org.eclipse.jetty.util.thread.strategy.EatWhatYouKill.run(EatWhatYouKill.java:131)\n\tat org.eclipse.jetty.util.thread.ReservedThreadExecutor$ReservedThread.run(ReservedThreadExecutor.java:409)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883)\n\tat org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034)\n\tat java.base/java.lang.Thread.run(Unknown Source)\nCaused by: org.apache.lucene.store.AlreadyClosedException: this IndexWriter is closed\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:877)\n\tat org.apache.lucene.index.IndexWriter.ensureOpen(IndexWriter.java:891)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1468)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1464)\n\tat org.apache.solr.update.DirectUpdateHandler2.updateDocOrDocValues(DirectUpdateHandler2.java:967)\n\tat org.apache.solr.update.DirectUpdateHandler2.doNormalUpdate(DirectUpdateHandler2.java:342)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc0(DirectUpdateHandler2.java:294)\n\tat org.apache.solr.update.DirectUpdateHandler2.addDoc(DirectUpdateHandler2.java:241)\n\t... 77 more\nCaused by: java.nio.file.FileSystemException: /var/solr/data/vfb_json/data/index/_3kkni.fdm: Input/output error\n\tat java.base/sun.nio.fs.UnixException.translateToIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixException.rethrowAsIOException(Unknown Source)\n\tat java.base/sun.nio.fs.UnixFileSystemProvider.newByteChannel(Unknown Source)\n\tat java.base/java.nio.file.spi.FileSystemProvider.newOutputStream(Unknown Source)\n\tat java.base/java.nio.file.Files.newOutputStream(Unknown Source)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:410)\n\tat org.apache.lucene.store.FSDirectory$FSIndexOutput.<init>(FSDirectory.java:406)\n\tat org.apache.lucene.store.FSDirectory.createOutput(FSDirectory.java:254)\n\tat org.apache.lucene.store.NRTCachingDirectory.createOutput(NRTCachingDirectory.java:146)\n\tat org.apache.lucene.store.LockValidatingDirectoryWrapper.createOutput(LockValidatingDirectoryWrapper.java:44)\n\tat org.apache.lucene.store.TrackingDirectoryWrapper.createOutput(TrackingDirectoryWrapper.java:43)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsWriter.<init>(CompressingStoredFieldsWriter.java:121)\n\tat org.apache.lucene.codecs.compressing.CompressingStoredFieldsFormat.fieldsWriter(CompressingStoredFieldsFormat.java:130)\n\tat org.apache.lucene.codecs.lucene87.Lucene87StoredFieldsFormat.fieldsWriter(Lucene87StoredFieldsFormat.java:141)\n\tat org.apache.lucene.index.StoredFieldsConsumer.initStoredFieldsWriter(StoredFieldsConsumer.java:48)\n\tat org.apache.lucene.index.StoredFieldsConsumer.startDocument(StoredFieldsConsumer.java:55)\n\tat org.apache.lucene.index.DefaultIndexingChain.startStoredFields(DefaultIndexingChain.java:452)\n\tat org.apache.lucene.index.DefaultIndexingChain.processDocument(DefaultIndexingChain.java:488)\n\tat org.apache.lucene.index.DocumentsWriterPerThread.updateDocuments(DocumentsWriterPerThread.java:208)\n\tat org.apache.lucene.index.DocumentsWriter.updateDocuments(DocumentsWriter.java:415)\n\tat org.apache.lucene.index.IndexWriter.updateDocuments(IndexWriter.java:1471)\n\t... 82 more\n",
    "code":500}}

FAIL
test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries ... FAIL
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... FAIL

======================================================================
FAIL: test_05_tract_lineage_queries (src.test.test_query_performance.QueryPerformanceTest)
Test tract/nerve and lineage clone queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 244, in test_05_tract_lineage_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronClassesFasciculatingHere exceeded threshold")
AssertionError: 898.6124591827393 not less than 15.0 : NeuronClassesFasciculatingHere exceeded threshold

======================================================================
FAIL: test_05b_image_queries (src.test.test_query_performance.QueryPerformanceTest)
Test image and developmental lineage queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 295, in test_05b_image_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "ImagesThatDevelopFrom exceeded threshold")
AssertionError: 1312.364571094513 not less than 15.0 : ImagesThatDevelopFrom exceeded threshold

======================================================================
FAIL: test_11_transcriptomics_queries (src.test.test_query_performance.QueryPerformanceTest)
Test scRNAseq transcriptomics queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 446, in test_11_transcriptomics_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "anatScRNAseqQuery exceeded threshold")
AssertionError: 23.125962257385254 not less than 15.0 : anatScRNAseqQuery exceeded threshold

======================================================================
FAIL: test_12_nblast_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 535, in test_12_nblast_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "SimilarMorphologyTo exceeded threshold")
AssertionError: 24.45493507385254 not less than 15.0 : SimilarMorphologyTo exceeded threshold

======================================================================
FAIL: test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 646, in test_13_dataset_template_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "DatasetImages exceeded threshold")
AssertionError: 32.021164417266846 not less than 3.0 : DatasetImages exceeded threshold

======================================================================
FAIL: test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 731, in test_14_publication_transgene_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "TermsForPub exceeded threshold")
AssertionError: 10.38839054107666 not less than 3.0 : TermsForPub exceeded threshold

----------------------------------------------------------------------
Ran 15 tests in 2435.115s

FAILED (failures=6)
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 2.2280s ✅
get_term_info (individual): 2.0100s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 1.7453s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 1.6299s ✅
NeuronsPresynapticHere: 1.6569s ✅
NeuronsPostsynapticHere: 1.9341s ✅
NeuronNeuronConnectivity: 1.3946s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 1.6582s ✅
PartsOf: 1.4961s ✅
SubclassesOf: 1.4461s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 898.6125s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 2.9542s ✅
Error fetching SOLR data: Connection to server 'http://solr.virtualflybrain.org/solr/vfb_json/select/' timed out: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)
ImagesThatDevelopFrom: 1312.3646s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 1.9054s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 2.1564s ✅
NeuronRegionConnectivityQuery: 1.7328s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 0.8916s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 8.5465s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 2.9761s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 23.1260s ✅
  └─ Found 57 total clusters, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 24.4549s ✅
  └─ Found 215 NBLAST matches, returned 10

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.7004s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 32.0212s ✅
  └─ Found 46 images in dataset, returned 10

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 10.3884s ✅
  └─ Found 2 terms for publication

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 2.822s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.4123 seconds
VFB_00101567 query took: 1.4092 seconds
Total time for both queries: 2.8216 seconds
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
*Last updated: 2026-05-06 06:03:22 UTC*
