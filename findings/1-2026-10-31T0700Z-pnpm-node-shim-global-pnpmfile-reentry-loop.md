# pnpm's node shim re-enters itself forever when a global pnpmfile meets an uncached pinned runtime

**Source:** [pnpm/pnpm#17530](https://github.com/pnpm/pnpm/issues/17530) (open, no labels yet; cause confirmed in source by a contributor; code anchors verified against `main`)

## What happened

On Linux with Node installed globally through pnpm, `~/.local/share/pnpm/bin/node` is a hard link of the pnpm binary running in shim mode. The reporter (tebb, association NONE) found that with a `globalPnpmfile` configured, any project pinning a Node version pnpm has not downloaded yet makes **both** `node -v` and `pnpm install` hang silently, spawning a new orphaned `node --input-type commonjs -e <pnpmfile loader>` process every ~5 seconds, all stuck in `futex_wait`, none cleaned up when pnpm is killed. On 12.16.1 a 30s run ends with `pnpmfile hook 'updateConfig' timed out after 30 seconds`; 12.17.0 behaves the same.

The matrix is crisp: cached pin works (244ms), no global pnpmfile works, a **local** `.pnpmfile.mjs` with the same uncached pin works, `PNPM_SHIM_BYPASS=1` works. `.node-version` with an uncached version hangs too. So the trigger is exactly `globalPnpmfile` x uncached pin.

## Why it happens

The reporter inferred the loop from process evidence; a contributor (aron-intframe, CONTRIBUTOR) then confirmed it in the source on `main` at `c771057`:

1. The shim provisions the uncached pin through `materialize_runtime` / `install_runtime` in `pnpm/crates/cli/src/shim_dispatch/runtime_env.rs` (verified on `main`: `trusted_runtime_config` line 61, `materialize_runtime` line 129, `install_runtime` line 258).
2. `trusted_runtime_config` anchors the install in the state dir, so a project pnpmfile is never found - but `globalPnpmfile` still comes from `config.yaml`. That is why only the global one triggers it.
3. The hook worker is spawned by `NodeWorker::spawn` as a bare `Command::new("node")` (verified: `pnpm/crates/hooks/src/worker.rs:159` on `main`). PATH resolves `node` back to the shim, which is also unprovisioned, so it loads config and spawns another worker. Loop.

The contributor tested a one-line fix in `hardened_install_config` (rc=1 30.1s and 7 orphans becomes rc=0 2.7s, 0 orphans; 43 shim_dispatch unit tests pass) but flagged two cautions: forcing `PNPM_SHIM_BYPASS=1` on the worker moves every pinned project's hooks onto the global Node, and a slow first provision can still exceed the hook's 30s timer, failing `pnpm install` cleanly instead of hanging. Their improved one-off workaround: `PNPM_CONFIG_IGNORE_PNPMFILE=true node -v` inside the project, once per new pin. Their analysis is disclosed as agent-written (Claude Code); no PR is open yet, and pnpm's bot has asked the reporter whether they plan one.

## Who this bites

- Linux users who install Node via pnpm's global shims **and** set `globalPnpmfile` (a documented but discouraged setting) **and** use `devEngines.runtime` or `.node-version` pins: the first command in any project with a fresh pin hangs with no output and leaves orphaned processes behind.
- CI images that preinstall Node this way hit it on the first uncached pin, and the orphan chain can outlive the job.

## Limits

- The reproduction numbers (orphan cadence, timing table) are the reporter's and the contributor's local runs on 12.16.1/12.17.0 and `main` at c771057; I verified the source anchors on `main` but did not run the reproduction (no Linux pnpm-shim setup here). Repo ~37k stars.
- The fix is proposed and locally tested by one contributor, not reviewed or merged; the behavioral trade-off (hooks moving to the global Node under bypass) is unresolved design territory.
- `globalPnpmfile` is explicitly discouraged in pnpm's docs, which may affect how maintainers prioritize this; the reporter argues a silent hang with unbounded process spawning deserves a guard regardless.
