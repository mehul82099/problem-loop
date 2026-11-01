# Node `http.Agent`: every idle keep-alive socket pins the last request's AsyncLocalStorage store - and runs idle-socket events inside it

**Source:** [nodejs/node#67181](https://github.com/nodejs/node/issues/67181) (open, 4 reactions within hours of filing; no fix PR at publish time)

## What happened

When `http.Agent` reuses a keep-alive socket, `asyncResetHandle` (`lib/internal/http/agent.js:702-710`, called from both reuse paths at lines 224 and 415) re-binds the socket's TCP handle to the *current request's* async context via `handle.asyncReset(...)`. Nothing unbinds it when the socket goes back to the free pool. So each idle socket retains the most recent request's entire `AsyncLocalStorage` store until the socket is reused or destroyed. The reporter demonstrates it with a core-only repro: 20 stores carrying 1 MB buffers each, and the number retained always equals the number of idle sockets - released only by `agent.destroy()`. A heap snapshot shows the retainer path `(GC roots) -> TCP -> AsyncContextFrame -> completed ALS store`. Verified the cited function, both call sites, and all three affected releases: v26.13.0 (2026-10-28), v24.22.1 (2026-10-21), v22.23.2 (2026-07-29).

There's a second half beyond memory: events on an *idle* pooled socket (e.g. the server closing the connection) fire with the stale, already-completed request's store still active, so logging/tracing/metrics code reading ALS in those handlers attributes socket lifecycle events to the wrong request. The `--isolated` control in the repro (initiating requests inside a module-scope `AsyncResource`) shows retention comes from the context active at reuse time, confirming the mechanism.

## Who this bites

- Any long-lived Node service using keep-alive agents (the default posture for outbound HTTP at scale) with per-request ALS stores - which is exactly how OpenTelemetry, CLS-based logging, and request-ID propagation work: every idle socket in every pool quietly pins one completed request's context, and context-heavy stores (trace baggage, user objects, buffers) inflate RSS in proportion to pool size, not traffic.
- The stale-context half is arguably worse than the bytes: idle-socket `close`/`error` events run under a completed request's identity, which corrupts exactly the observability data people use to debug connection churn.

## Limits

- Single-source report (reporter association NONE, repo ~115k stars) with an unusually thorough repro and heap-snapshot evidence; I verified code anchors and release dates but did not run the reproduction.
- Impact scales with idle pool size and store weight; one store per idle socket is bounded retention, not an unbounded leak.
- No maintainer comment or fix PR yet; whether the fix is an unbind-on-free or a doc change is unresolved.
