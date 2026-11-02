# Elasticsearch ES|QL: STATS over a dataset and an index in one FROM fails with a byte-level decode error

**Source:** https://github.com/elastic/elasticsearch/issues/164372 (opened 2026-11-02, open, routed to the analytics team, no human maintainer reply yet)

## The problem

With ES|QL Data Federation, a query that aggregates across a dataset and an index in the same `FROM` fails with HTTP 500 and `illegal_state_exception: unexpected byte [0x..]` - the offending byte differs on every run. Each source alone aggregates fine. The reporter (an Elasticsearch contributor, on Elastic Cloud Hosted, reporting version 9.6.0) documented a striking pattern: the failure is deterministic per query - the same query fails or passes every time - and it does not correlate with result size, since a filter leaving 7,634 rows fails while one leaving 153,947 rows passes.

The failing set is broad: plain `STATS c = COUNT(*)`, `MAX(@timestamp)`, `MIN`/`COUNT_DISTINCT` over keyword fields, grouping, `LIMIT` before `STATS`, and most `WHERE` shapes - equality with `!=`, `IS NULL`/`IS NOT NULL`, `OR`, timestamp range. The passing set is just as specific: `WHERE` with `==`, `LIKE`, `TO_LOWER(...) ==`, or a timestamp equality all pass, and so does any mixed query without `STATS`. The same failure also appears through `SET wildcards_match_datasets = true` when a pattern matches both a dataset and an index, and through subqueries.

## Why it matters

The pass/fail split is the tell. Predicates that can be pushed into each source's own plan pass; shapes that force a different aggregation layout across the union of heterogeneous sources fail with a wire-level decode error, meaning the coordinator reads page bytes that do not match what the data node wrote. An automated analysis posted by the project's bot (explicitly labeled a hypothesis, not reproduced, so tooling output rather than maintainer confirmation) points at `PushAggregateThroughUnionAll` - a rule that does exist in the ES|QL optimizer - rewriting mixed `FROM dataset, index | STATS` plans into per-branch partial aggregates behind separate exchanges, with the stack showing a byte-misaligned read while decoding a remote exchange response. The random byte in each message fits a serialization mismatch rather than a data problem.

For users of the new federation feature this is a silent-boundary bug: queries that are syntactically fine and work per-source die server-side only when combined, and which combined queries survive depends on planner behavior, not on anything visible to the user.

## Caveats

- The root-cause mechanism comes from an automated bot analysis that explicitly says it could not reproduce the issue; treat it as a plausible lead, not a confirmed diagnosis. No human maintainer has weighed in.
- The reporter's environment is Elastic Cloud Hosted with a reported build of 9.6.0; the newest public release tag at time of writing is v9.5.6, so the exact build could not be matched against public artifacts. The optimizer rule cited exists in the current source tree, which this finding verified directly.
- This reports the upstream report and its evidence table as stated; it does not re-run any query and does not propose a fix.
