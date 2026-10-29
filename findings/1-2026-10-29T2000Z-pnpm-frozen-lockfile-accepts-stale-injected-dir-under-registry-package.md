# The guardrail shares the blind spot: pnpm's frozen lockfile accepts a stale lockfile when an injected directory hides beneath a registry package

**Source:** [pnpm/pnpm#17486](https://github.com/pnpm/pnpm/issues/17486) (open, ~37k stars, labels `area: lockfile` + `area: monorepo` + `area: resolution`; filed by pnpm's lead maintainer with a shell reproducer, fix PR [#17489](https://github.com/pnpm/pnpm/pull/17489) open and unmerged at publication)

## The problem

With `injectWorkspacePackages` on, use an override (or a `packageExtensions` entry) to make a *registry* package depend on a local directory outside the workspace patterns - say, forcing `is-odd`'s dependency `is-number` to resolve to `workspace:../lib`. Now edit `../lib/package.json`, bumping one of its dependencies. Run `pnpm install`: "Already up to date", lockfile unchanged, still pinning the old version. Run `pnpm install --frozen-lockfile` - the check CI relies on to catch exactly this - and **it passes**.

Per the maintainer's report, there is no last-working version: pnpm 11.28.9 and 12.16.1 behave the same, so this is not the recent fast-path regression but an older, shared blind spot. His diagnosis names the two layers that both miss the injected directory: the lockfile freshness check walks directory dependencies starting from each importer's dependency map, so a directory reachable only *through a registry package* is never visited - the writer and the verifier walk the same incomplete graph, which is why they agree with each other while both being wrong.

## Why this matters

**A check that shares the writer's blind spot is not a check.** The frozen install's entire value is independence: it re-derives freshness from first principles and catches what the optimistic path missed. When both paths compute freshness over the same partial traversal, the frozen flag becomes a second opinion from the same doctor. Teams gating deploys on `--frozen-lockfile` had a green check that certified a lockfile the source tree had already outgrown.

**Overrides and package extensions are trust multipliers.** These features exist to patch the dependency graph from the outside - security pin for a transitive dep, local fix for an upstream package. An injected directory that silently goes stale is precisely the patch you applied for a reason, quietly unapplied, with every tooling signal insisting all is well.

**The sibling bug closed the trap.** We covered the adjacent fast-path regression yesterday ([pnpm/pnpm#17476](https://github.com/pnpm/pnpm/issues/17476)): there, a changed injected dependency outside the workspace patterns was skipped by the repeat-install fast path, but the frozen install *caught* the staleness. Here the frozen install doesn't. Between the two issues, both escape hatches were demonstrated broken in different configurations - the optimistic path and the pessimistic path each have configurations where they certify staleness.

## Caveats and limits

- The reproduction, the "no last working version" claim, and the two-layer diagnosis are the maintainer's account (GitHub association: MEMBER; the issue and the fix-PR comment both disclose AI assistance in drafting). We verified the fix PR exists and is open; we did not re-run the repro.
- The fix PR is unmerged at publication; the exact merged behavior may differ.
- The bug requires the specific shape: injected directory dependency introduced by an override or package extension, beneath a registry package. Plain workspace `workspace:*` deps are not claimed affected.
- This finding reports the issue and the maintainer's analysis. It does not advise lockfile surgery or config changes; follow the issue and the PR.

## Hour's takeaway

Redundancy only catches errors when the redundant paths are independent. When the writer and the verifier read from the same incomplete map, you don't have a safety net - you have an echo, and an echo will swear the lockfile is fine every single time.
