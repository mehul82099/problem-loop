# pnpm's `verifyDepsBeforeRun` forces a pre-run install when only the private root project's `version` changed

**Source:** [pnpm/pnpm#17560](https://github.com/pnpm/pnpm/issues/17560) (open; maintainer-labeled `area: lifecycle-scripts` + `area: lockfile`, no fix at publish time)

## What happened

With `verifyDepsBeforeRun: install` in `pnpm-workspace.yaml`, changing **only** the root manifest's `version` (1.0.0 -> 1.0.1) in a single private application makes every `pnpm dev` run a no-op install first - even in a project with zero dependencies, where the reporter byte-compared `pnpm-lock.yaml` before and after and found it identical. The minimal repro (empty dependency set, `install --offline --ignore-scripts`, bump version, run) takes only ~32 ms, but in a real application the reporter measured the pre-run no-op install at **36.1 seconds before Vite started**, and merging a version-bump-only branch triggers the same unnecessary install even though the dependency graph never changed. Reproduced on 12.3.4 and the current 12.16.1 (verified, released 2026-10-27) in an isolated temp directory. The report is careful about scope: workspace package versions legitimately affect resolution, so it asks either for verification to ignore root metadata that cannot affect installation or for a scoped option - not for blind skipping - and notes the current workaround (`verifyDepsBeforeRun: false`) also disables the useful checks. It distinguishes itself from [#16993](https://github.com/pnpm/pnpm/issues/16993) (verified open: repeated checks of *unchanged* lockfiles), which is a different failure. The `warn` policy mode reports "The workspace structure has changed since last install" for the same version-only diff.

## Who this bites

- Teams on the (recommended) `verifyDepsBeforeRun: install` setting with version-bump release flows: every merge that only bumps the app's own version silently taxes every subsequent `pnpm <script>` with a no-op install, and the only escape hatch disables staleness detection entirely.
- Monorepo CI and dev loops where the root version changes on every release: the cost scales with node_modules size, turning a metadata-only change into a recurring 30-second-plus stall with a misleading "workspace structure has changed" warning.

## Limits

- Single-source report (repo ~33k stars, reporter association NONE) with a clean minimal repro and honest scoping; the 36-second figure comes from the reporter's private app, not the published repro.
- Windows is the reporter's tested platform; the report was verified against the latest release but not bisected across versions.
- Maintainer triage (labels) exists but no comment or fix yet; whether ignoring root-version changes is safe in every workspace topology is exactly the open question the report raises.
