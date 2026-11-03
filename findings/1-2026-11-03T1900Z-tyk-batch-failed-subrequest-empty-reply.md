# Tyk Gateway: a failed /tyk/batch sub-request comes back as an empty reply (relative_url "" and code 0)

**Source:** [TykTechnologies/tyk#8876](https://github.com/TykTechnologies/tyk/issues/8876) - opened 2026-11-03 by pcbeingused333 (GitHub association: NONE, i.e. no affiliation badge; the issue body discloses it was drafted with AI assistance - "Drafted with the assistance of an AI tool (Claude)").

## What the report says

When a sub-request inside a `/tyk/batch` call fails at the HTTP layer - for example its target refuses the connection - the reply entry for that sub-request is `{"relative_url":"","code":0,"headers":null,"body":""}`. Two problems follow: the client sees a zero status instead of an error, and with parallel execution (replies arrive in completion order, where `relative_url` is the only field identifying which entry is which) the client cannot even tell which sub-request failed.

Reproduction from the issue: enable batch request support on an API, then POST to `/<listen_path>/tyk/batch/` with a sub-request whose target refuses connections, e.g. `{"requests":[{"method":"GET","relative_url":"http://127.0.0.1:1/x"}]}` through the manual/unsafe path, or any sub-request whose upstream call fails.

The reporter proposes returning the sub-request's `relative_url` and a non-zero status (suggesting 502 Bad Gateway) for the two failure paths, and offers a Go test with a closed port plus a PR.

## Verification (checked during this finding)

In `gateway/batch_requests.go` on `master`, `doRequest` does exactly what the report claims:

```go
resp, err := client.Do(req)
if err != nil {
    log.Error("Webhook request failed: ", err)
    return BatchReplyUnit{}      // line ~68
}
...
content, err := ioutil.ReadAll(resp.Body)
if err != nil {
    log.Warning("Body read failure! ", err)
    return BatchReplyUnit{}      // line ~75
}
```

A zero-value `BatchReplyUnit{}` is precisely `relative_url ""`, `code 0`, `headers null`, `body ""`; the success path just below returns the filled struct (`RelativeURL`, `Code`, `Headers`, `Body`). The parallel-execution path uses a `chan BatchReplyUnit` (line ~131), so replies indeed arrive in completion order with no index - consistent with the reporter's identification concern. The behavior was not executed against a live gateway here; it follows directly from the verified code.

## Limits

- The report (and this finding) covers the two transport-level failure paths in `doRequest`. Sub-requests that return an upstream error *status* (e.g. 500 from the target) already carry that status back; those are unaffected.
- The reporter's association is NONE, and the body is AI-drafted (disclosed); the claims were verified against source as noted. As of writing, the only reply is the repo's `probelabs[bot]` automation agreeing with the analysis - tooling output, not maintainer triage; no maintainer has weighed in on the proposed 502 mapping.
- Whether changing the failure shape (new status code, populated relative_url) would break existing batch clients that match on `code == 0` is a compatibility question the maintainers would need to answer.

## Sources

- Issue: <https://github.com/TykTechnologies/tyk/issues/8876>
- gateway/batch_requests.go (master): <https://github.com/TykTechnologies/tyk/blob/master/gateway/batch_requests.go>
