# Your folder name is a glob pattern: how `[ws]` on disk gives you phantom type errors

- Source issue: https://github.com/microsoft/TypeScript/issues/64987 (open; opened 2026-10-27)
- Verified: sibling typescript-go#3733 and its fix PR typescript-go#4529 (same symptom, different cause; fix present, this bug still reproduces)
- Project: microsoft/TypeScript (~112k stars); affects the Go-native compiler/language server (tsgo 7.1.0-dev)
- Checked: 2026-10-28 03:12 UTC

## Problem
Put your monorepo in a folder named `[ws]` (or `{ws}`) and the new Go-based TypeScript language server mis-files every newly created file. A fresh `new.ts` inside `apps/web` gets assigned to the parent project (lib: ES2015) instead of the nearest tsconfig (lib: ESNext), producing false diagnostics - `TS2550: findLast does not exist...` plus a cascading contextual-type error - that persist until the server is restarted. Same result when the path is plain but the tsconfig `include` case differs from disk on a case-insensitive filesystem (`include: ["App"]` vs folder `app`). Existing files are fine; only files created during the session are misassigned. The reporter ties it to project matching (PossiblyMatchesFileName/WildcardDirectoryGlobs territory): somewhere, a filesystem path is being matched as a glob, so `[ws]` is read as a character class, not a folder.

## Why it is interesting
- Two classic path-handling bugs in one report. First: paths are not patterns - any code that routes files through glob matching must escape metacharacters, and `[`/`{` in real folder names (common in monorepo conventions like `[apps]`) is exactly the input that exposes a missing escape. Second: case handling at the wrong layer - on a case-insensitive filesystem, "does this include match" and "which project owns this file" disagree when one side folds case and the other doesn't.
- The consequence is trust damage, not inconvenience. Language-server diagnostics are the ground truth developers act on. Phantom errors that survive edits and only vanish on restart teach people to either chase ghosts ("fix" code that is correct) or start ignoring red squiggles - both expensive.
- It isolates the event edge: existing files at startup are correctly assigned; the bug only bites on the file-created notification path, where the server decides project membership incrementally instead of from a full scan. Incremental paths are where matching shortcuts live.
- Careful prior-art work by the reporter: a sibling issue with the same symptom (typescript-go#3733) was fixed earlier (PR #4529) from a different cause; they verified that fix is present and this still reproduces. "Same symptom, still broken after the known fix" is exactly what keeps a bug report from being closed as a duplicate.

## Honest limits
- Affects the in-development Go-native tsgo (7.1.0-dev build at commit 4163ca172f), not the stable TypeScript 5.x language server; reporter could not test prior versions.
- Root cause (glob-vs-path matching, case folding layer) is inferred from symptoms and component names; not confirmed by the team at check time.
- No maintainer response yet; repro is the reporter's, not independently re-run.
- Issue state may have changed since 03:12 UTC.
