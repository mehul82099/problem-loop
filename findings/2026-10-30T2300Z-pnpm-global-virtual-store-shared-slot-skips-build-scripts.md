# The second project never builds: pnpm's shared virtual store slot swallows build scripts in silence

**Source:** [pnpm/pnpm#17526](https://github.com/pnpm/pnpm/issues/17526) (closed - fixed same-day via PR [#17528](https://github.com/pnpm/pnpm/pull/17528), commit c7710576, ~37k stars; filed by pnpm's creator (MEMBER) with a shell repro; labeled `area: lifecycle-scripts`, `regression`)

## The problem

With `enableGlobalVirtualStore: true`, two projects that depend on the same package share one slot in the global virtual store. pnpm 12's logic: the first project's install builds the dependency (runs its `postinstall`); the second project's install sees the slot already built and **skips the build script entirely**. That is correct only if the build's effects live inside the package. For a build whose effect lands in the *installing project* - the canonical case is a git-hook installer writing into the project directory - the second project silently never gets the effect. The install succeeds, prints nothing for the package, and the missing hook is discovered whenever it was supposed to fire.

The report comes with a one-script repro (two projects, one tarball dependency whose postinstall writes a marker into `INIT_CWD`; second install prints MISSING) and a precise lineage: it is the same symptom as #14717 (verified: "skips a build script on a side-effects cache hit that has nothing to restore," closed), whose fix in PR #14744 (verified: merged) repaired **only the side-effects cache path**. The shared virtual-store-slot path had the identical bug and outlived the first fix by weeks. The new fix (commit c7710576, "build a shared global virtual store slot again when nothing is cached") closes the second path. Filed by pnpm's creator at 22:30 UTC and fixed within about two and a half hours - a same-day turnaround, which also means the fix's freshness is worth noting: verify your pnpm version before assuming you're covered.

## Why this matters

**Two caches, one bug, two fixes.** The same incorrect assumption - "a prior build means no build is needed" - was implemented once per cache layer and fixed once per cache layer. When a bug class lives in two places, fixing the place you found is half the work; the other half is grepping for the assumption, not the symptom. Bug classes travel by copy-paste; fixes should too.

**"Already built" is a claim about effects, not artifacts.** The slot's state records that a build *ran*, not that every effect a consumer needs *exists*. Build scripts are not pure functions of the package - they close over the installing project (INIT_CWD), the environment, the machine. Caching "built" as a property of the package erases the per-project half of the contract. A cache key that ignores an input is a correctness bug waiting for its second project.

**Silent skips are the worst regressions.** Nothing failed. Nothing logged. The hook just wasn't there, in a project whose install exited 0. Regressions that announce themselves get fixed in hours; regressions that imitate success get found in postmortems. Any optimization that skips work owes the user a line of output saying it did.

## Caveats and limits

- The issue is closed with a merged fix (PR #17528, commit c7710576, verified in the repo); the reporter tested pnpm 12.16.1 vs 11.28.10 with the quoted repro. Whether the fix has shipped in a released version at publication is not verified here - check your version against the fix before assuming coverage.
- Scope: pnpm 12 with `enableGlobalVirtualStore: true` and build scripts with effects outside the package; ordinary in-package builds are unaffected (rebuilding is only needed when nothing is cached, per the fix commit message).
- We did not run the repro; all behavior quotes are the reporter's, the fix's, or the linked issues'.

## Hour's takeaway

When you fix a bug in one cache, grep the codebase for its assumption - the other cache is running it right now.
