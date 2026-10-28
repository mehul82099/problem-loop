# Same bytes, different answer: Graal JIT warm-up makes the JDK manifest parser reject valid manifests

- Source issue: https://github.com/oracle/graal/issues/14797 (open; opened 2026-10-28)
- Related root cause: https://github.com/oracle/graal/issues/14395 (closed; fixed in 25.5.5.0.3, not backported to 25.0.x)
- Project: oracle/graal (~21.7k stars)
- Checked: 2026-10-28 17:15 UTC

## Problem
On Oracle GraalVM for JDK 25 with the default Graal JIT, the stock `java.util.jar.Manifest` starts rejecting byte-for-byte valid manifests after JIT warm-up: `java.io.IOException: invalid header field (line 1)` thrown on bytes that parse fine in a fresh JVM - and, as the reporter verified in one diagnosed JVM, on bytes identical to a fresh read in the *same* JVM. In production (Linux aarch64, AWS Graviton4) this surfaces as random `NoClassDefFoundError` / `ServiceConfigurationError: Provider not found` for classes that are present in the jar, because `BuiltinClassLoader.defineClass` reads the manifest first and `findClassOnClassPathOrNull` swallows the IOException. The reproducer is a tight self-check: it snapshots a signature of every jar's manifest on the classpath, then re-parses them in a loop until the JIT kicks in - `MINI_OK` expected, `MINI_BAD` typical. GraalVM CE and C2 are not affected. A Graal team member identified the root cause within hours as issue #14395 - `RemoveEmptyLoopsPhase` removing loops that contain loop-variant floating guards (a vectorization / counted-loop strip-mining interaction) - fixed in 25.5.5.0.3 but not yet backported to the 25.0.x series. Suggested workaround until then: disable `RemoveEmptyLoops`. Tracked internally as GR-80919.

## Why it is interesting
- This is the nightmare shape of a JIT miscompile: deterministic code that stops being deterministic after warm-up. The interpreter and early runs give the right answer, then the optimizer "learns" a wrong one, and byte-identical input flips outcomes inside a single JVM. Debugging intuitions trained on deterministic bugs are worse than useless here - they actively mislead.
- The blast radius is disguised by exception swallowing. Nobody deploys "manifest parsing"; they deploy class loading. The miscompile corrupts a parser deep inside `BuiltinClassLoader`, the IOException gets swallowed, and the observable symptom is "class not found" for classes that exist. Distance between cause and symptom is what makes production incidents like this take days instead of minutes.
- The root cause is a classic optimizer tension made concrete: removing an "empty" loop is only safe if nothing the loop guards can vary - and `RemoveEmptyLoopsPhase` deleted loops carrying loop-variant floating guards, so code that should have re-checked a condition per iteration stopped doing so. One wrong deletion, silently, inside vectorized/strip-mined counted loops.
- The un-backported fix is its own lesson. The bug is already understood and fixed - just not on the release line people are running (25.0.x). "Fixed upstream" and "fixed where you run" are different states, and this is the gap between them, with a named owner acknowledging the backport miss.

## Honest limits
- Root-cause attribution to #14395 comes from a Graal team member's read ("looks like this might be"), not yet a confirmed verification - verification is tracked internally (GR-80919).
- Reproduced by the reporter on Oracle GraalVM 25 / Linux aarch64; GraalVM CE and C2 unaffected per the report; other architectures unverified.
- Failure is timing-dependent (requires warm-up); exact reproduction rates vary per run.
- Fix availability in 25.5.5.0.3 is the team member's statement; the backport status to 25.0.x may change.
