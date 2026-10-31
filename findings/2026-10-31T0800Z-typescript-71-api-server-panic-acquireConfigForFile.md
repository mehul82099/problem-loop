# TypeScript 7.1's new snapshot API panics with a nil `ChangeIf` when the nearest tsconfig doesn't include the opened file

**Source:** [microsoft/TypeScript#65054](https://github.com/microsoft/TypeScript/issues/65054) (open, unlabeled; regression confirmed by a second user; anchors checked against `main`)

## What happened

The reporter (0x80, association NONE) upgraded a repository validator from `typescript@7.0.2`'s sync API to `7.1.0-beta` and hit a hard crash: `api.createSnapshot({ openFiles: [...] })` panics with `invalid memory address or nil pointer dereference` inside `SyncMapEntry.ChangeIf` (tsc/internal/project/dirty/syncmap.go) called from `configFileRegistryBuilder.acquireConfigForFile` - whenever the opened `.mjs`/`.js` file is **not** included by the nearest `tsconfig.json`. The same layout on 7.0.2 opened the file in the inferred project (`/dev/null/inferred`), and on 7.1 it still does when there is no tsconfig at all. It also opens fine if a sibling `.ts` file *is* covered by the tsconfig. Still reproducible on the latest dev builds (7.1.0-dev.20261027.1 through 20261029.1 per the reporter; those exact versions exist on npm, verified).

A second user (ycmjason) reproduced and generalized it: extension doesn't matter. The trigger is "the nearest tsconfig matches no files of its own **and** does not include the opened file" - a bare `{}` or `{"files":[]}` tsconfig plus any `x.ts` panics on 7.1.0-beta and 7.1.0-dev.20261030.1, while 7.0.2 puts the file in the inferred project. Their table narrows the regression to config-file resolution retaining logic, not JS handling.

## Why the crash is a nil receiver

On `main` (verified), `acquireConfigForFile` does `entry, _ := c.configs.LoadOrStore(...)` and immediately calls `entry.ChangeIf(...)`, and `ChangeIf` starts with `e.mu.Lock()` ([syncmap.go#L127-L135](https://github.com/microsoft/TypeScript/blob/main/tsc/internal/project/dirty/syncmap.go), [configfileregistrybuilder.go#L149-L153](https://github.com/microsoft/TypeScript/blob/main/tsc/internal/project/configfileregistrybuilder.go)). A nil `entry` - or a nil proxy target - faults exactly there, matching the reporter's stack (`addr=0x0`). Line numbers have shifted a few lines between their dev build and current `main`, but the call shape is identical.

Same stack, second door: [microsoft/TypeScript#65071](https://github.com/microsoft/TypeScript/issues/65071) (open) reports the identical nil `ChangeIf` in `acquireConfigForFile` from a different path - `closeProjects` then `openFiles` on the same API, which the reporter there ties to a tombstone left by `LoadOrStore` after project close. Two unrelated callers converging on the same nil entry in two days suggests the registry's entry lifecycle, not either call site.

## Who this bites

- Tools built on the new `typescript/sync` snapshot API in 7.1 (repository validators, batch linters, doc extractors) that open files a tsconfig doesn't claim: a stray `.mjs` build script in the repo crashes the whole process - no recoverable error, it's a Go panic.
- Monorepos with empty or reference-only root tsconfigs (`{"files":[],"references":[...]}`) are the exact trigger shape per the second reproducer.

## Limits

- The reproductions and version matrix are the two reporters' runs; I verified the called functions and crash site shape on `main`, the existence of the cited npm dev versions, and the sibling issue #65071, but did not run the probe myself. Repo ~112k stars.
- No maintainer response yet; the only other comment is a volunteer asking to be assigned (association NONE, no analysis). The exact nil path (nil entry vs nil proxyFor) is inferred from the stack, not confirmed by maintainers.
- 7.1 is beta/dev software; this may well be fixed before stable. The finding describes the current beta, not a released regression.
