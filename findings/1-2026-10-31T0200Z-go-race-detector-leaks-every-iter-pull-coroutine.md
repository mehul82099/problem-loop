# Every iter.Pull under -race leaks a goroutine's race state - 17KB you never get back

**Source:** [golang/go#82736](https://github.com/golang/go/issues/82736) (open, labeled `compiler/runtime`, ~139k stars; the asymmetric exit paths verified against `master`; no maintainer response yet)

## The problem

Build with `-race`, call `iter.Pull` in a loop, and watch memory climb forever: about 17KB per pull, never released. The reporter's measurements (go1.27.0, darwin/arm64, `/usr/bin/time -l`): 10,000 pulls peak at 202MB, 40,000 at 714MB, 160,000 at 2.7GB. The same program without `-race` at 160,000 pulls: 8MB. `vmmap` shows one 128KB "Sanitizer" mapping per pull, ~16KB resident - a per-goroutine shadow stack that is never freed. Plain goroutines started and finished under `-race` stay flat; only coroutines leak. In production terms: the reporter's compiler zips sequences with `iter.Pull` ~37,000 times per compile, and `go test -race` over a few dozen programs peaked at **124GB** and was killed by the OS.

The cause is an exit-path asymmetry, verified on `master`. A normal goroutine exits through `goexit1` in `src/runtime/proc.go` (line 4496), which calls `racegoend()` to free the race context:

```go
func goexit1() {
    if raceenabled {
        ...
        racegoend()
    }
```

An `iter.Pull` coroutine exits through `coroexit` in `src/runtime/coro.go` (line 80) - `gp.coroexit = true; mcall(coroswitch_m)` - and that file contains no call to `racegoend` at all. Two kinds of goroutine, two exit paths, one of them forgot to check out. Related history (surfaced by the repo's related-issues bot, tooling): #63276 ("-race leaks memory", closed) and #64651 (iter.Pull2 race-instrumentation false positives, closed) - the race detector and the coroutine machinery have met before, and it keeps not going well.

## Why this matters

**Every new control-flow path is a new place to forget a finally.** Go added coroutines as a second way for execution to end, and every piece of per-goroutine lifecycle bookkeeping - race contexts, profiling labels, defer chains - had to be re-hooked by hand. The race detector's hook landed in the old path only. When a language grows a new exit door, the audit question is not "does the new door work" but "what did the old door do that nobody wrote down?"

**Leaks that scale with *operations*, not *data*, hide in every profile.** 17KB per pull sounds small until you notice the counter is iterations, not input size: long-running tools, test suites, language servers, and compilers do millions of small pulls against constant-size data. Heap profiles stay clean (the leak lives in sanitizer mappings, not the Go heap), so the standard tooling story - "your heap is fine" - actively misdirects. The OS is the first observer that tells the truth, usually with a SIGKILL.

**`-race` is the safety net; holes in it hit the cautious.** Nobody runs `-race` in production for fun; they run it in CI, in fuzzing, in the test suites of people being careful. A leak that turns a careful team's CI job into a 124GB OOM isn't just wasted memory - it's a tax on the exact practice the tool exists to encourage.

## Caveats and limits

- The exit-path asymmetry (racegoend in goexit1; absent from the coroutine path) is verified on `master`. The memory numbers, the vmmap analysis, and the 124GB production incident are the reporter's measurements (association NONE; go1.27.0/1.27.3, darwin/arm64). We did not run the repro. No maintainer confirmation or fix at publication.
- Scope: programs using `iter.Pull`/`iter.Pull2` under the race detector; non-race builds and plain goroutines are unaffected per the report.
- This finding does not advise disabling the race detector or changing iterator patterns - follow the issue.

## Hour's takeaway

New control flow means new cleanup paths. grep for every old-path hook before you call the feature done.
