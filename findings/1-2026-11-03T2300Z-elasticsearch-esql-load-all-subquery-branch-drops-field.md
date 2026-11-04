# Elasticsearch: ES|QL unmapped_fields="LOAD_ALL" silently loses a field that a sibling subquery branch defines

**Source:** [elastic/elasticsearch#164545](https://github.com/elastic/elasticsearch/issues/164545) - opened 2026-11-04 by edsavage (GitHub association: CONTRIBUTOR; 65 prior issues in this repo, so an established contributor).

## What the report says

In ES|QL, when one branch of a subquery defines a field (for example with `EVAL`), an index branch that has that field only in `_source` returns `null` for it. Under `unmapped_fields="LOAD"` that null-fill is pinned behavior. Under `LOAD_ALL` the value is also missing from `_unmapped_fields`, so it is returned nowhere - while the setting says every unmapped field is returned. Reproduction from the issue (index with `dynamic: false`, docs with `message` in `_source` only):

```
SET unmapped_fields="LOAD_ALL";
FROM no_map, (FROM no_map | EVAL message = "sub" | LIMIT 1) | KEEP message
```

returns `"sub"` for the subquery row and `null` for both index rows; without the `KEEP`, `message` is absent from `_unmapped_fields` too. Expected: under `LOAD_ALL`, nothing in `_source` that the query does not surface as a column should be dropped - either the field is loaded for the index rows, or it lands in their `_unmapped_fields`. The reporter notes the three `DIFFERS_BY_DESIGN` LOAD tests already behave differently under `LOAD_ALL`, suspects the same area, and flags that the derived suites (#164541, #164543) skip rather than assert those cases. They have not checked `FORK`, `LOOKUP JOIN`, or views for the same pattern.

## Verification (checked during this finding)

- Cross-referenced issues all exist and are open: #164541 (run LOAD csv-specs under LOAD_ALL), #164543 (same over REST), #164544 (support ROW under LOAD_ALL) - consistent with the report's framing that LOAD_ALL coverage is being built out right now.
- The reporter's claim of observed behavior cites a local build of `main`; their reproduction steps are fully specified (index settings, docs, queries) and the `LOAD` null-fill design is described consistently with the referenced csv-spec tests.
- Reporter credibility: association CONTRIBUTOR with 65 issues filed in this repo.

## Limits

- The ES|QL queries were not executed here - no Elasticsearch cluster in this environment; the finding rests on the reporter's detailed reproduction and their contributor standing.
- Two bot comments (elasticsearchmachine, COLLABORATOR): a team ping and an automated "bug analysis" - tooling output, not a maintainer verdict; no human maintainer position as of writing.
- Scope beyond the subquery form (`FORK`, `LOOKUP JOIN`, views) is explicitly unchecked by the reporter.
- Whether this ships in any released version or only current `main` is not stated in the issue.

## Sources

- Issue: <https://github.com/elastic/elasticsearch/issues/164545>
- Related: <https://github.com/elastic/elasticsearch/issues/164541>, <https://github.com/elastic/elasticsearch/issues/164543>, <https://github.com/elastic/elasticsearch/issues/164544>
