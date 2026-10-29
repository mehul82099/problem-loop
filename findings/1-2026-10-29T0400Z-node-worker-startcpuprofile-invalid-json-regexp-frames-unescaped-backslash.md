# The profiler that emits invalid JSON: RegExp frames break Node's startCpuProfile output

- Source issue: https://github.com/nodejs/node/issues/67097 (open; opened 2026-10-29)
- Project: nodejs/node (~123k stars)
- Checked: 2026-10-29 04:45 UTC

## Problem
`worker.startCpuProfile()` on Node v25.9.0 returns a profile string that `JSON.parse` rejects - `SyntaxError: Bad escaped character` - whenever the profiled code contains RegExp frames. The malformed field is `callFrame.functionName`: a frame named `RegExp: ^(\d{6})` has its backslash written into the JSON output unescaped, producing invalid JSON for any consumer. The repro is 15 lines: a worker spinning on `re.test()`, profile for under half a second, parse the result - throws. The control case is the interesting part: the same workload through the Inspector protocol's `Profiler.stop` returns a structured object that round-trips through `JSON.stringify`/`JSON.parse` cleanly. So the V8 profiler data is fine; the corruption happens in Node's own serialization layer for the `worker.startCpuProfile` convenience API, which appears to assemble JSON as a string rather than serialize an object.

## Why it is interesting
- The oldest serialization lesson in the book, alive in a flagship runtime: never build JSON by string concatenation. The moment a value contains a backslash, quote, or control character, hand-assembled output silently stops being JSON. RegExp names are exactly the kind of value nobody puts in a test fixture - "who profiles a regex?" - which is why this survived.
- Observability tooling has to be more correct than the code it observes. A profiler that emits corrupt output when pointed at real code is a debugging tool that fails precisely when you're debugging something exotic. Consumers don't lint profile JSON defensively; they parse it, and a syntax error in a profiling pipeline looks like the tool's fault, not the profiled code's.
- The API shape is the root issue: returning a string at all invites this class of bug. The Inspector path returns structured data and is immune; the convenience wrapper turned structure into a string and reintroduced escaping as a manual responsibility. "Return objects, serialize once, at the boundary" is the fix that prevents the whole category.
- Also notable: a volunteer picked it up within hours with the right plan (find the unescaped path, fix, add a regression test asserting valid JSON) - the open-source flywheel working on a fresh report.

## Honest limits
- Filed hours ago; the fix is a volunteer's stated intent, no PR at check time.
- Confirmed on v25.9.0 only in the report; other versions unverified (likely shared wherever the API exists).
- Trigger requires RegExp frames in the profiled stack; ordinary profiles without regex frames are unaffected per the report.
- No maintainer assessment yet; severity/scope classification is this finding's judgment.
