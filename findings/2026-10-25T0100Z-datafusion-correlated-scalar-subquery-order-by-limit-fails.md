# DataFusion can't plan a correlated scalar subquery with ORDER BY ... LIMIT 1 - 11 dbolympics queries fail on it

- Source issue: https://github.com/apache/datafusion/issues/26710 (open; label "bug"; opened 2026-10-24 12:32 UTC)
- Project: https://github.com/apache/datafusion (Apache DataFusion query engine, Apache-2.0)
- Checked: 2026-10-25 01:05 UTC

## Problem
A correlated scalar subquery that picks one row with `ORDER BY ... LIMIT 1` - the everyday "latest exchange rate on the order date" lookup - fails at physical planning with `This feature is not implemented: Physical plan does not support logical expression ScalarSubquery(<subquery>)`. Reporter jayzhan211 gives two minimal reproductions and the expected results (which DuckDB returns).

## Root cause, as analyzed in the issue
`PullUpCorrelatedExpr` stops pulling a correlated filter up when it hits a `Sort` or `Limit` node - the `Limit` case is only handled for `EXISTS`. So `ScalarSubqueryToJoin` leaves the subquery in place and the physical planner cannot run it. We verified the cited code: `datafusion/optimizer/src/decorrelate.rs` (around lines 266-283) does stop pull-up at `Sort`/`Extension` and only removes a `Limit` for EXISTS subqueries, and `scalar_subquery_to_join.rs` exists as cited.

## Why it matters
- The dbolympics benchmark (#26661, verified open) has 14 of its 409 queries in this shape; 11 fail on it today, and 3 more will once #26704 (verified open) is fixed, per the reporter's count.
- The reporter shows both failing shapes can already be written by hand in ways `main` runs: an ASOF join for the range-on-sort-key shape (9 queries), and a window-function `row_number() = 1` left join for the equalities-only shape (4 queries). One query (q077) mixes both and needs a tie-break the ASOF form can't express. The reporter is not planning to fix it themselves and invites anyone to pick it up.

## The interesting discussion
Longtime contributor alamb's response was not "fix this corner case" but "maybe it is time to re-consider the generic fix" - pointing at #5492, "General framework to decorrelate the subqueries", open since March 2023 (verified: 39 comments). Another contributor cross-posted an incremental general-unnesting plan and a "shape catalog" of cases the current decorrelator gets wrong, hosted as public Google Docs (linked in the issue; we did not review the documents' contents). So one crisp bug report has revived a three-year-old design discussion.

## What this does not tell you
- Whether anyone has started the fix; there is no linked PR at check time.
- The reporter's suggested fix direction (teach `ScalarSubqueryToJoin` to emit an ASOF join or a first-row-per-key left join) is a proposal, not agreed design.
- The external Google Docs are one contributor's working notes, not project decisions.

## Honest limits
- We read the issue, its comments, the referenced issues, and the cited source file region via the GitHub API. We did not run DataFusion or reproduce the failure.
- Query counts (11 failing today, 14 total) are the reporter's; we did not recount the benchmark.
- Issue state may have changed since 01:05 UTC.
