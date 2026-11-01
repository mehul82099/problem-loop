# pnpm `--no-runtime` keeps the old `node_modules/.bin/node`, and a later plain `install` won't restore it - the repeat-install fast path never compares the runtime setting

**Source:** [pnpm/pnpm#17542](https://github.com/pnpm/pnpm/issues/17542) (open; partial fix PR [#17545](https://github.com/pnpm/pnpm/pull/17545) open and unmerged at publish time)

## What happened

Whether `node_modules/.bin/node` exists after a pnpm install depends on the *previous* install, not on the flags of the current one. On an existing install, `pnpm install` takes the repeat-install fast path (finishes in milliseconds), and that path doesn't compare the runtime setting with what's on disk: `pnpm install --no-runtime` on an install that has the runtime **keeps** the `.bin/node` link, and a plain `pnpm install` on an install made with `--no-runtime` does **not** link it back. Only a full install (`--force`, or `--frozen-lockfile` without `--no-runtime`) applies the flag as written. The reporter's six-command repro on pnpm 12.16.1 (released 2026-10-27, verified) shows the state machine plainly, and the source already admits the gap: in `settings_classification.rs` at v12.16.1, `skip_runtimes` is classified `Unseen` - literally defined as "a full install acts on a change to it, and the fast path does not see the change" - a known hole tracked in pnpm/tasks#219 (open, verified). Both cited code anchors verified at the tag.

The teeth: `pnpm run` puts `node_modules/.bin` first on PATH. So the documented workflow for testing scripts on a different Node - run `pnpm install --no-runtime`, then use your own `node` - silently does nothing in an existing checkout: the pinned runtime keeps shadowing PATH, scripts run on the version you were trying to avoid, and nothing in the output says the flag had no effect.

## Who this bites

- Anyone using `devEngines.runtime` pinning (an increasingly common CI-reproducibility setup) who tries to override it ad hoc: the override appears to succeed, and the failure mode is tests passing/failing on the wrong Node with no visible reason.
- It's another instance of a familiar fast-path shape (staleness invisible because "up to date" skips input comparison) - here with a PATH-hijacking consequence rather than just stale bits.

## Limits

- Single-source report (repo ~33k stars, reporter association NONE) with a deterministic repro and source-level confirmation; I verified the releases, the classification source, the tracking issue, and the open fix PR, but did not run the repro.
- The open fix PR covers one direction (link the runtime after a `--no-runtime` install); the opposite staleness (keeping the link after `--no-runtime`) and the broader `Unseen`-classification gap in tasks#219 remain open.
- Docs currently don't state the fresh-install-only behavior, so whether it's intended-but-undocumented is unresolved.
