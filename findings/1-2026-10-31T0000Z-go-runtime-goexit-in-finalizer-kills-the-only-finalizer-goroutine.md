# One Goexit in a finalizer, and no finalizer in your process ever runs again

**Source:** [golang/go#82733](https://github.com/golang/go/issues/82733) (open, labeled `compiler/runtime`, ~139k stars; single-goroutine design verified against `master`; a runtime MEMBER is engaged)

## The problem

`runtime.Goexit` terminates the calling goroutine - and the goroutine that runs **all finalizers** is a single, process-wide singleton. `createfing` in `src/runtime/mfinal.go` says it in its own comment (verified on `master`, line 169): "start the finalizer goroutine exactly once." So if a finalizer calls `runtime.Goexit` - directly, or accidentally via `t.Fatal` in a test, since `FailNow` is `Goexit` - that one goroutine dies, `createfing` has already spent its one CAS, and **every finalizer registered afterward silently never runs**. No panic, no log, no error. The reporter's repro shows `finalizer 1 ran: true`, `finalizer 2 ran: false`, reproduced on go1.27.3, go1.26.10 and master.

The same exit corrupts two more systems. The cleanup queue (`runtime.AddCleanup`, the modern finalizer replacement) never decrements its goroutine count for the exited worker, so below 8 Ps no cleanup runs again either; with more Ps each Goexit permanently burns one of the `GOMAXPROCS/4` cleanup goroutines. And the runtime's own bookkeeping disagrees with itself: `gdestroy` re-classifies the dying goroutine as a *user* goroutine mid-finalizer, so `sched.ngsys` is left wrong and `runtime.NumGoroutine` undercounts by one per incident while `runtime.Stack` still shows the truth. The reporter mapped the full blast radius and even prototyped a partial fix (repairing only `ngsys` makes the goroutine *profile* overcount - the state has to be unwound atomically), then asked the runtime team which semantic is intended: restart the goroutine, or make Goexit-in-finalizer a fatal error. A runtime MEMBER has replied, asking for the real-world context. No fix chosen yet.

## Why this matters

**Singletons turn local mistakes into global outages.** One goroutine per process for all finalizers is a reasonable design - until one bad callback kills it, and the failure domain becomes "every finalizer in the program, forever." Shared execution contexts need either supervision (restart the worker) or containment (make the fault fatal loudly); silent death is the one option that converts a one-line bug into a system-wide, permanent, invisible one.

**The quietest API misuse is the one wrappers cause.** Nobody writes `runtime.Goexit` in a finalizer on purpose. They write `t.Fatal` - in a helper, three frames down, in a test that happens to exercise a finalizer. Dangerous primitives don't need to be common; they need to be reachable through one innocent wrapper. Auditing "who can reach Goexit" means auditing every assertion library, not every call site.

**Bookkeeping that disagrees with itself is a bug multiplier.** `NumGoroutine` saying 2 while `runtime.Stack` prints 4 isn't a cosmetic wart - it's the runtime losing track of what it owns, and every monitoring tool, leak detector and pprof consumer inherits the confusion. State that must change together (goroutine counts, cleanup-worker counts, running flags) needs one transaction or one owner; here it has neither.

## Caveats and limits

- The single-goroutine design and "exactly once" guard are verified on `master`; the repro output, the `gcCleanups.ng`/`sched.ngsys` accounting details, and the multi-version results are the reporter's analysis (CONTRIBUTOR), offered with a fix pending maintainer direction. We did not run the repro.
- Scope: finalizers/cleanups that call `runtime.Goexit` (including via `t.Fatal`); ordinary finalizers are unaffected. The `NumGoroutine` undercount persists per incident.
- This finding does not advise finalizer patterns - follow the issue.

## Hour's takeaway

If one callback can kill the only worker, the worker's liveness is part of your API contract - whether you documented it or not.
