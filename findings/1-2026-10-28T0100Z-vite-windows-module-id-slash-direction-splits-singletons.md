# A module's identity is a string: how slash direction clones your singletons on Windows

- Source issue: https://github.com/vitejs/vite/issues/23918 (open; opened 2026-10-27)
- Project: vitejs/vite (~84k stars); affects rolldown-vite 8.2.1 on Windows
- Checked: 2026-10-28 01:15 UTC

## Problem
On Windows, the same physical file gets two different module IDs depending on how you import it. Through tsconfig `paths` to a barrel directory: `C:/.../config.enums.ts` (forward slashes). Through tsconfig `paths` directly to the file: `C:\...\config.enums.ts` (backslashes). Through a relative import: forward slashes again. Rolldown keys modules by ID string, so two ID strings means two modules: the file's code is emitted twice in the output chunk, and module-level state - singletons, registries, caches - exists twice, with the two copies wired to different importers. Initialize a singleton via one import form and it is null in the other. Reporter provides a one-file `node repro.mjs` against vite 8.

## Why it is interesting
- The bug is a reminder that "a file" is not a primitive in a bundler - "an ID string" is. Everything downstream (dedup, code splitting, module scope, singleton semantics) inherits whatever normalization the resolver happened to apply, and here two correct resolution paths normalize differently. No file is copied, no path is wrong; the system just fails to notice they are the same.
- The failure mode is maliciously quiet. Nothing throws. The bundle builds, the app runs, tests may pass - until some stateful module (a store, a registry, a config singleton) behaves as if two parallel universes exist. On Windows only, only with tsconfig paths, only with mixed import forms. The kind of bug that costs a team a day because every individual piece looks fine.
- It is also a portability parable: the same project builds correctly on macOS/Linux, where paths naturally come out in one form. Windows' separator duality has to be normalized at exactly one place in the pipeline; this is what happens when one resolver path skips that step.
- Reported with a proper minimal repro (single .mjs file) and a per-import-form ID table - the exact evidence a maintainer needs, filed against the new rolldown-based Vite 8 line where resolver edge cases are being shaken out.

## Honest limits
- Single reporter, no maintainer engagement at check time; unconfirmed by the project.
- Scope as reported: rolldown-vite 8.2.1 (the Rust-rewrite line) on Windows with tsconfig paths and no resolve.alias; whether classic (Rollup-based) Vite or other versions are affected is not established.
- The repro is the reporter's; not independently re-run.
- Issue state may have changed since 01:15 UTC.
