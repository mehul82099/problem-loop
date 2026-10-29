# "Already up to date" until you check: pnpm 12's repeat-install fast path skips a changed injected dependency, then the frozen install fails on the change it skipped

**Source:** [pnpm/pnpm#17476](https://github.com/pnpm/pnpm/issues/17476) (open, ~37k stars, labels `area: lockfile` + `area: monorepo`; filed by pnpm's lead maintainer, with an AI-assistance disclosure on the issue body)

## The problem

A monorepo with `injectWorkspacePackages: true` depends on a library through `workspace:../lib`, where `../lib` lies **outside** the workspace's `packages:` globs - a legal, supported shape. Edit `../lib/package.json` to add a dependency, run `pnpm install`, and pnpm 12 finishes in milliseconds without re-resolving: the lockfile snapshot keeps the old dependency set. Run `pnpm install --frozen-lockfile` right after, and it fails:

```
ERR_PNPM_OUTDATED_LOCKFILE
  Failure reason:
  local dependency "lib" at "../lib" is outdated
```

The same tool, back to back: the fast install says nothing changed; the frozen install says the lockfile is stale. pnpm 11 re-resolves after the same edit (last working version 11.28.9 per the report, reproduced on 12.16.1 and `main`).

## The mechanism: a cheap staleness check that answers a different question

Per the reporter's analysis, pnpm 12's repeat-install fast path decides whether an injected dependency *can* have changed by comparing project manifests it already knows about. With a shared lockfile it assumes every injected package is a workspace project whose manifest it tracks. That holds for `workspace:*` references by name - and fails for `workspace:../dir` or `file:../dir` pointing outside the workspace patterns: the edited manifest is nobody's tracked manifest, so the fast path sees "no change" and skips the resolution that would have noticed one. The report notes the same assumption bit the frozen-lockfile check in pnpm/pnpm#17473, and that with `sharedWorkspaceLockfile: false` the fast path yields for any injected dependency, which is why the bug hides in the default monorepo layout.

## Why this matters

**A fast path is a bet that a cheap check implies an expensive one.** Here the cheap check ("did any manifest I track change?") is narrower than the expensive one ("did anything that feeds the lockfile change?"), and the gap is exactly the supported-but-unusual configuration. The result is the worst failure shape for a package manager: not an error, but a stale lockfile written with confidence.

**The two commands contradicting each other is the tell.** `install` succeeding instantly and `--frozen-lockfile` then failing looks like user error or lockfile corruption and invites the destructive "fix" of deleting the lockfile. The paradox is the signal: when the optimistic path and the verifying path disagree, the optimistic path is the suspect.

**The report models the standard.** The issue comes with a five-line shell reproducer, the last-working version, the exact assumption that broke, the sibling issue it also explains, and the maintainer's own pointer to where the fix is landing (a PR for pnpm/tasks#228, which we verified exists). The body carries an explicit "Written by an agent" disclosure - worth noting because it did not change what makes the report good: the reproducer is checkable either way.

## Caveats and limits

- The root-cause analysis and the pnpm 11 comparison are the reporter's account, not independently re-run here; the reporter is the project's lead maintainer (GitHub author association: MEMBER), and the issue body discloses AI assistance in its drafting.
- As of publication no fix is merged for this issue specifically; the referenced fix belongs to a PR against another pnpm repository.
- The bug requires the conjunction: pnpm 12, shared workspace lockfile, injected dependency outside the workspace patterns, edited manifest. Other layouts are not claimed to be affected.
- This finding reports the issue. It does not advise downgrades, lockfile surgery, or disabling the fast path; follow the issue for the sanctioned resolution.

## Hour's takeaway

Every fast path should be able to state, in one sentence, the exact set of inputs its cheap check covers - and treat everything outside that set as "changed." pnpm 12's check silently redrew that set to "manifests I track," and the uncovered region turned into a stale-lockfile generator.
