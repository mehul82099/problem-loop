# Italian public procurement data: is `importo_sal` cumulative or per-certificate? Summing it inflated totals about five times

- Source issue (written in Italian): https://github.com/dataciviclab/appalti-pubblici/issues/15 (open at check time; no labels; opened 2026-10-21; 6 comments)
- Proposed fix, open pull request: https://github.com/dataciviclab/appalti-pubblici/pull/18 (not merged; 10 files changed per the API)
- Related commit named in the thread: https://github.com/dataciviclab/appalti-pubblici/commit/3d2d9e5a (2026-10-22, "avoid row duplication from multiple CUP and acceptance records", touches `compose/anac-cross/sql/clean.sql`, its `dataset.yml` and one test)
- Earlier related fix (merged 2026-10-21): https://github.com/dataciviclab/appalti-pubblici/pull/14, which closed issue #6
- Project: https://github.com/dataciviclab/appalti-pubblici (MIT, 0 stars per the API). It builds analyses from open data of the Italian anti-corruption authority (ANAC).
- Checked: 2026-10-22 11:40 UTC

## Problem
The pipeline sums a field called `importo_sal` (the amount on a work progress certificate, "SAL") in three places. The reporter asks whether the field is the running total at each date (cumulative) or the amount of each single certificate. Summing only makes sense for the second case. The numbers in the thread suggest it is neither cleanly:
- For contracts with 3 to 6 certificates, the median of max/sum matches what a cumulative series with equal steps would give (0.50, 0.40, 0.33, 0.29) and not the incremental pattern (0.33, 0.25, 0.20, 0.17). So most series look cumulative.
- But a project member checked the published data and says the field is mixed: some contracts have equal incremental amounts, one has 1,419 monthly entries that are not monotonic, and one has a first value of about 1.1 billion followed by about 2.2 million, which they call a coding error.
- Per the reporter, a plain sum gives 1,185.7 billion euros, and treating the series as incremental would give 198.2 billion. The member says 24.5% of the deltas are negative.

All figures here are from the thread, computed on the project's 2026 clean table of 1,274,801 rows. We did not recompute them.

## What the thread says about the fix
- The proposed fix (#18) classifies each contract's certificate series as cumulative, incremental, ambiguous or single, and uses the maximum for cumulative and ambiguous series and the full amount for incremental ones. Duplicate rows (same date and amount) count once. The author reports that the total drops from 1,185.7 to 230.4 billion euros on the 2026 data, with about 35,000 ambiguous series (20.8 billion) treated as cumulative, which they call an underestimate.
- A later comment reports a second, independent inflation: joins to tables with several project codes (CUP) or acceptance records per contract duplicated rows, and fixing that, in the commit above, lowered a total from 253.2 to 230.4 billion (+9.9% before). We confirmed the commit exists and its files; we did not check which pull request carries it.
- The proposal in the original issue was to get the official field definition from ANAC before changing metrics. A member's later comment says they sent a formal certified-mail request. We saw no reply.
- A project member has not yet reviewed #18 as far as the thread shows.

## What this does not tell you
- The correct meaning of the field is not settled. Until ANAC publishes a definition, the classification in #18 is a heuristic, and its author says so.
- Any earlier published totals from this project that summed the field would be inflated by the same logic. We did not check what the project has published.
- This is about one project's pipeline, not about ANAC's data being wrong. The thread does suggest source records with apparent coding errors, but we did not verify that.

## Honest limits
- We did not run the pipeline or open the data, and do not read Italian procurement rules beyond what the thread explains.
- State may have changed since 11:40 UTC.
