# Elasticsearch: a bulk request never completes when a failed document is redirected to the failure store of a CCR follower data stream

**Source:** [elastic/elasticsearch#164471](https://github.com/elastic/elasticsearch/issues/164471) - opened 2026-11-03 by jonny-mcc (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

If a CCR follower data stream (`replicated: true`) has its failure store enabled - either through the cluster setting `data_streams.failure_store.enabled` on the follower cluster or via `data_stream_options` copied from the leader - any document that fails at the shard level is queued for failure-store redirection. Because a follower data stream has no failure-store indices and cannot lazily roll one over, the redirect pass throws an `ElasticsearchException` that nothing in `BulkOperation` catches. `RefCountingRunnable#close` logs and swallows it, so the bulk listener never completes: the client receives no response, indexing-pressure accounting is never released, and the bulk task stays in the task registry forever. Failure stores are not replicated by CCR (#126356), so per the reporter the correct behavior is a per-item failure, not a hung request (or, on a second path they describe, an HTTP 500 for the whole request).

The reporter also notes that in production (assertions disabled), even *valid* documents sent to a CCR follower data stream fail at the shard in `FollowingEngine#preFlight` with a 403 "a following engine does not accept operations without an assigned sequence number" - and since the redirect condition accepts any non-429 `ElasticsearchException`, valid documents trigger the same hang.

## Root cause (reported, verified against current source)

The reporter gives a six-step chain; I checked each anchor on `main` as of 2026-11-03 (reported line numbers in parentheses; all match within a line or two of drift):

1. Follower data streams cannot lazily roll their failure store: `DataStream.java:339` asserts `replicated == false || (backingIndices.rolloverOnWrite == false && failureIndices.rolloverOnWrite == false)`, and `TransportPutFollowAction.java` (~343) sets `rolloverOnWrite` false on the failure-store component with the comment that replicated data streams can't be rolled over.
2. The follower stream is still treated as failure-store enabled: `DataStream.isFailureStoreEffectivelyEnabled` (`DataStream.java:790`) and `BulkOperation.shouldRedirectRequestToFailureStore` (`BulkOperation.java:735`) do not check `isReplicated()`.
3. With no rollover pending, the redirect runs immediately (`BulkOperation` ~270, per the report).
4. `IndexRequest#getConcreteWriteIndex` (~901) throws a plain `ElasticsearchException` - "Attempting to write a document to a failure store but the target data stream does not have one enabled" - because the follower stream has zero failure indices.
5. `BulkOperation#groupRequestsByShards` catches only timestamp/parse/routing/not-found exceptions (~397-413), so the plain `ElasticsearchException` escapes.
6. `RefCountingRunnable#close` (~123-125) catches `Exception`, logs `exception in delegate`, runs `assert false` (test-only), and returns normally - the bulk listener is never notified.

`FollowingEngine#preFlight` at `FollowingEngine.java:62-64` throws exactly the 403 message quoted. Reported against 9.5.4 (release v9.5.4 exists, published 2026-09-15) and `main`.

The reporter additionally describes a second path with the same unchecked exception during the initial grouping pass: if an ingest pipeline or Streams check fails the document first, `TransportBulkAction#populateMissingTargets` skips the rollover (rollover-on-write is false) and the whole bulk request fails with HTTP 500 instead of recording a per-item failure. I did not independently trace this second path's line numbers.

## Status

Elastic's automation (`elasticsearchmachine`, a COLLABORATOR bot) pinged the storage-engine team and posted an automated bug analysis concluding "Likely root cause found on `main`" by code tracing, without running a test. That is tooling output, not a human maintainer's confirmation; there is no human maintainer assessment or linked fix as of writing.

## Limits

- The hang and the HTTP 500 path were not reproduced here against a live cluster; the chain above is the reporter's, with each cited line verified on `main`. Line drift of one or two lines exists (noted above).
- The reporter's association is NONE, so the production observations are self-asserted; the Elastic automation's "likely root cause" agreement is automated analysis, not a maintainer verdict.
- Impact depends on having failure stores enabled on a CCR follower cluster (via cluster setting or leader-copied data-stream options); deployments without that combination are unaffected per the report.

## Sources

- Issue: <https://github.com/elastic/elasticsearch/issues/164471>
- BulkOperation (main): <https://github.com/elastic/elasticsearch/blob/main/server/src/main/java/org/elasticsearch/action/bulk/BulkOperation.java>
- DataStream (main): <https://github.com/elastic/elasticsearch/blob/main/server/src/main/java/org/elasticsearch/cluster/metadata/DataStream.java>
- IndexRequest (main): <https://github.com/elastic/elasticsearch/blob/main/server/src/main/java/org/elasticsearch/action/index/IndexRequest.java>
- RefCountingRunnable (main): <https://github.com/elastic/elasticsearch/blob/main/server/src/main/java/org/elasticsearch/action/support/RefCountingRunnable.java>
- FollowingEngine (main): <https://github.com/elastic/elasticsearch/blob/main/x-pack/plugin/ccr/src/main/java/org/elasticsearch/xpack/ccr/index/engine/FollowingEngine.java>
