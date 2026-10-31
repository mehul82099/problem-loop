# Deno.serve on HTTP/1.1: `info.completed` now *resolves* when the client disconnects mid-stream - aborted responses read as delivered

**Source:** [denoland/deno#37110](https://github.com/denoland/deno/issues/37110) (open, 1 corroborating comment; every anchor verified against releases and merged PRs)

## What happened

Since Deno 2.8.3, when an HTTP/1.1 client disconnects while a streamed response body is still being sent, `ServeHandlerInfo.completed` **resolves** instead of rejecting with `Interrupted`. On 2.8.2 and earlier it rejected - which is the documented contract, written down in [deno#35747](https://github.com/denoland/deno/pull/35747) ("completed ... rejects with an `Interrupted` error when the response cannot be fully sent"). The server does notice the disconnect: the response body stream is cancelled with "resource closed". Only the `completed` signal lies.

The reporter bisected it cleanly: 2.8.2 rejects, 2.8.3 resolves (both releases verified: [v2.8.2](https://github.com/denoland/deno/releases/tag/v2.8.2) Jun 3, [v2.8.3](https://github.com/denoland/deno/releases/tag/v2.8.3) Jun 11). The same wrong resolve holds for SSE and `content-length` streams, and for FIN closes, RST resets and `AbortController` aborts - 18/18 runs per version. `--unstable-no-legacy-abort` changes nothing. HTTP/2 clients on the same TLS server still get the correct rejection, which points at the Deno-owned HTTP/1.1 serve path added in [#34446](https://github.com/denoland/deno/pull/34446) ("perf(ext/http): add Deno-owned HTTP/1.1 serve path", merged Jun 5 - exactly inside the 2.8.2 to 2.8.3 window), while HTTP/2 stayed on hyper.

A commenter (author_association NONE, so an unverified-but-plausible corroboration with its own repro) adds a second case: when the response body's **source throws**, the new `onError` path from [#35104](https://github.com/denoland/deno/pull/35104) (verified, "fix(ext/http): surface errors thrown while streaming a Deno.serve body") logs the error - and `completed` still resolves. A failed response reads as delivered in both directions.

## Who this bites

- Any Deno server that uses `info.completed` to meter delivery - tracing, metrics, billing or audit code counting successfully sent responses: client aborts and mid-stream errors are now silently counted as successes for HTTP/1.1 clients (the majority of internet traffic).
- `completed` is exactly the API Deno's own legacy-abort warning points users to for detecting full delivery, so the recommended migration path leads to the broken signal.

## Limits

- The 18/18 repro numbers and the bisect are the reporter's; I verified the release tags and dates, the docs PR, the suspect HTTP/1.1 PR and its merge date, the onError PR, and the commenter's second case as written, but did not run the repro script (repo ~108k stars).
- The report covers HTTP/1.1 only; whether WebSocket upgrades or HTTP/1.0 keep-alive paths on the new server share the bug is untested.
- No maintainer response yet (issue is hours old); the #34446 attribution is the reporter's inference from the bisect window and the HTTP/1-vs-2 split, not confirmed by the team.
