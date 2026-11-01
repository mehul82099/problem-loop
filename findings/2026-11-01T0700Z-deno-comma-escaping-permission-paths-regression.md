# Deno 2.9.8 can't grant a permission to any path containing a comma - a CLI parser migration quietly broke the doubled-comma escape

**Source:** [denoland/deno#37114](https://github.com/denoland/deno/issues/37114) (open, regression report; fix PR [#37115](https://github.com/denoland/deno/pull/37115) open and unmerged at publish time)

## What happened

Deno's sandbox permission flags (`--allow-read`, `--allow-write`, etc.) take comma-separated paths, and since September 2024 a literal comma in a path is escaped by doubling it: `--allow-read=/tmp/deno,,comma` grants access to `/tmp/deno,comma`. That escape was added deliberately in PR [#25453](https://github.com/denoland/deno/pull/25453) (merged Sep 2024, verified) to close issue [#6553](https://github.com/denoland/deno/issues/6553). The reporter bisected the regression to Deno 2.9.8 (released 2026-10-21, verified): 2.9.4 runs their one-liner fine, 2.9.8 exits before the script starts with `error: Empty path is not allowed`. The report points at the CLI-parser cutover in PR [#35982](https://github.com/denoland/deno/pull/35982) (merged Aug 2026, verified): the new delimiter handling uses a plain `value.split(delim)`, which turns `a,,b` into three entries including an empty one, and the empty entry is rejected before the escape can be re-joined. Their own read/write permission regression tests fail on 2.9.8 and pass on 2.9.4.

## Who this bites

- Anyone granting **narrowly scoped** filesystem permissions to comma-containing paths: the failure is a hard startup error, so a deploy that upgrades to 2.9.8 with such a flag just refuses to boot - and the only workaround is *widening* the grant (drop the flag entry or use a parent directory), i.e. trading sandbox tightness for a working process. Comma in directory names is not exotic: CI caches, user directories, and generated paths hit it.
- It's a silent-compatibility-break shape: no deprecation warning, the escape that has worked for two years simply stops parsing, and the error message ("Empty path") points at the wrong cause.

## Limits

- Reporter association is NONE (self-asserted version bisect and test results; repo ~109k stars); I verified the escape PR, the parser-cutover PR, the 2.9.8 release date, and the open unmerged fix PR, but did not run the repro myself.
- Affected scope as reported is path-based permission flags; whether other comma-list flags (e.g. `--allow-import`) share the parser regression is not established in the issue.
- The fix PR exists but is unmerged, so there is no released patched version to point at yet.
