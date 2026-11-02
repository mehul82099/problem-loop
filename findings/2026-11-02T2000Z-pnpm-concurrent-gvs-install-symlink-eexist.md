# pnpm: concurrent installs over a shared global virtual store race on bin symlinks and fail with ERR_PNPM_CMD_SHIM_SYMLINK_BIN (EEXIST)

**Source:** https://github.com/pnpm/pnpm/issues/17587 (opened 2026-11-02, open, no maintainer reply yet)

## The problem

With pnpm's global virtual store (GVS) enabled, running several installs concurrently against the same store intermittently fails with `ERR_PNPM_CMD_SHIM_SYMLINK_BIN` (EEXIST) while linking package executables. The reporter reproduced it on the native 12.17.0 standalone binary (released 2026-10-30) and on 12.16.1, with a fully self-contained script: two tiny synthetic packages and a loopback-only registry, a warm content store, a frozen lockfile, and four parallel offline installs. One package exposes 512 executable aliases for a single JS file purely to widen the scheduling window - no lifecycle scripts, cycles, hooks, or artificial delays. The controls isolate the race precisely: disabling GVS passes, disabling symlinked executables passes, and sequential installs pass. The first batch creates fresh GVS slots over the warm store; later batches reuse populated slots, so the race is in slot materialization, not registry I/O.

## The race, per the reporter

The bin-linking path already has a `symlink_already_points_at` helper in 12.17.0 (confirmed in `pnpm/crates/cmd-shim/src/link_bins/executable.rs`, with the error code defined in `link_bins.rs`), but an early check cannot close a check/unlink/create race: two installers can both observe a missing or stale link, one creates it, and the loser's create returns EEXIST. The reporter's suggested invariant is the useful part of the report: treat an existing symlink that already resolves to the intended target as a no-op (normalizing relative targets against the link's parent), and on EEXIST re-read the link and accept it when it points where it should - never unlink a correct link another process just created. The same rule should hold in the materialization and retry paths.

## Why it matters

GVS is pnpm's answer to cross-project store sharing, and CI fleets and monorepo tooling are exactly where parallel installs happen. A race that fails installs nondeterministically on a shared store pushes teams toward either serializing installs (slow) or disabling the feature (losing its dedup benefits) - and the EEXIST message points at bin shimming, not at the concurrency, so it is easy to misdiagnose as a corrupted store.

## Caveats

- Open with no maintainer response; the reporter's association is NONE. The race is intermittent by nature, so "reproduces" here means the reporter's harness fails in batches, with controls that pass - as described in the report.
- The code anchors named in the report (the error diagnostic and the `symlink_already_points_at` helper) exist in the v12.17.0 tree as cited; the fix direction is the reporter's proposal, not an agreed design.
- This finding does not re-run the reproduction and does not endorse a specific patch.
