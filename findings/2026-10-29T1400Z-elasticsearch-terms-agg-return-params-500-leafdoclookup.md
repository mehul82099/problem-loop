# A script returning `params` shouldn't be a server fault: Elasticsearch terms aggregation dies with a 500 `UnsupportedOperationException` in `LeafDocLookup.isEmpty`

**Source:** [elastic/elasticsearch#163977](https://github.com/elastic/elasticsearch/issues/163977) (open, ~78k stars, labeled `>bug` / `Team:Analytics`; filed by a contributor against `main` / 9.7.0 with a three-request reproducer and full stack trace)

## The problem

Give a `terms` aggregation a Painless script that returns `params` - the script's parameter map, which in this context also carries the `doc`/`_fields` lookup objects:

```
POST test/_search?size=0
{
  "aggs": {
    "t": {
      "terms": {
        "script": { "lang": "painless", "source": "return params" }
      }
    }
  }
}
```

Per the reporter, the search does not reject the script as invalid. It runs, and then fails with HTTP 500: an `UnsupportedOperationException` thrown from `LeafDocLookup.isEmpty`, surfacing as `QueryPhaseExecutionException: Query Failed`. The stack trace shows the failure flowing through the shard-level request cache's `computeIfAbsent` as well - the query was far enough along to be interacting with caching machinery when it blew up.

Returning `params` from a terms script is nonsense input - a terms agg needs a scalar or a list of scalars to bucket on. The bug is not that it fails. The bug is *how* it fails.

## Why this matters

**A 500 is a promise that the server broke.** HTTP status codes are an operational contract: 4xx wakes the user, 5xx wakes the on-call. A script the engine cannot honor is user error, and should come back as a 400-class rejection naming the script. Instead the misuse travels deep into the collection machinery before something throws a Java-internal `UnsupportedOperationException` - an exception type that says "this object doesn't implement that method," naming nobody's mistake. Every monitoring rule that pages on 5xx now treats a bad query as an outage.

**The failure point reveals a missing validation boundary.** The agg machinery expected script results to be plain values; `params` smuggled in a live `LeafDocLookup` - a per-document view object, not data - and nothing checked the shape of what the script returned until `isEmpty()` turned out not to exist. Inputs crossing a boundary (script sandbox to aggregation engine) need their contract enforced at the boundary, not discovered mid-flight.

**Mid-pipeline failures cost real work.** This did not fail at parse time. The query was planned, executed against documents, and touching the shard request cache when it died. Cheap validation up front is not just nicer errors - it is work not done, cache slots not touched, and partial results not computed before the inevitable throw.

## Caveats and limits

- The reporter is an external contributor (author association: CONTRIBUTOR); the reproduction is against `main` (9.7.0), and we relay their account and stack trace without re-running the cluster.
- As of publication the only thread activity is the project's automated team ping; no maintainer has confirmed the diagnosis or accepted a classification change.
- The report shows one failure shape (terms agg + `return params`); whether sibling aggregations or other script contexts share the unguarded path is unverified.
- This finding reports the issue. It does not advise on Painless script authoring beyond what the issue itself states; follow the issue for maintainer guidance.

## Hour's takeaway

Status codes and exception types are user interface, not implementation detail. When misuse can reach your internals before your validators, the exception you throw - and the status code it maps to - becomes the error message, and "UnsupportedOperationException at LeafDocLookup.isEmpty" is an error message that answers no one's question.
