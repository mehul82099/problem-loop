# Repeated Vite `build()` calls in one process retain every per-build plugin closure after `closeBundle`

**Source:** [vitejs/vite#23968](https://github.com/vitejs/vite/issues/23968) (open; no maintainer reply at publish time)

## What happened

A reporter stress-testing Vite 8.3.5's programmatic API found that sequential `build()` calls in one process never release their per-build plugin state: 16 builds with a freshly created plugin each leave all 16 marker objects strongly reachable after repeated cross-event-loop GC turns, even though every build completed and its `closeBundle` hook ran, while a weak-only control object was collected as expected. The report (disclosed as AI-assisted, with the reporter's authorization) ships a standalone reproduction repo (verified: repo and pinned commit `402d220f` exist, created 2026-11-02) that generates 64 tiny modules, runs 16 builds holding only WeakRefs to per-build markers, and exits 1 when all survive. A heap snapshot shows the retaining path running from GC roots through `deferSyncScanData` -> `context.inputOptions` -> `onLog` -> `context.chunkMetadataMap` into old rendered-module metadata. The careful part: a direct-`rolldown()` control with the same harness has its markers collected, so the retention sits in Vite's build orchestration rather than the obvious candidate - but the report explicitly declines to claim which project must fix it, notes the Rolldown control uses a different callback shape, and lists what it checked against: [#23571](https://github.com/vitejs/vite/issues/23571) (server.restart environments, different path), [rolldown#10961](https://github.com/rolldown/rolldown/pull/10961) (callable-callback retention fix, shipped in Rolldown 1.2.16 and still not enough), and open [rolldown#11319](https://github.com/rolldown/rolldown/pull/11319) / [#11371](https://github.com/rolldown/rolldown/pull/11371) (classic-close lifetime, untested here). Versions verified: Vite 8.3.5 (2026-10-21), Rolldown 1.2.16 (2026-10-29), both current stable.

## Who this bites

- Long-lived processes that call Vite's `build()` repeatedly - test runners, watch-mode wrappers, static-site and library build orchestrators, CI workers processing many packages in one Node process: memory grows linearly with build count, with each dead build pinning its full plugin graph, module metadata and options.
- Vitest-adjacent tooling and monorepo build scripts are the natural habitat; the leak is invisible until the process is profiled, since nothing errors.

## Limits

- Single-source report (repo ~78k stars, reporter association NONE) on macOS arm64 / Node 24; no version bisect, no RSS/OOM claim - the assertion is reachability of discarded objects, which the report itself frames as a lifetime expectation, not a GC-timing guarantee.
- I did not run the reproduction; its logs are sanitized and the heap snapshot is not uploaded (local paths), so the retaining path is as-quoted.
- The report's AI-assistance disclosure is noted; no maintainer triage yet, so ownership between Vite and Rolldown is genuinely open.
