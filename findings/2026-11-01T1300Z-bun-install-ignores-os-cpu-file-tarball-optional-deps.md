# `bun install` ignores `os`/`cpu` for `file:` tarball optionalDependencies - every platform's binary lands on disk

**Source:** [oven-sh/bun#47640](https://github.com/oven-sh/bun/issues/47640) (open; no fix PR at publish time)

## What happened

Bun filters optional dependencies by `os`/`cpu` correctly when they resolve from a registry (that was fixed back in #1205, verified closed), but the filter silently doesn't apply when the optional dependency is a local `file:` tarball: `bun install` installs *all* of them - linux-x64, linux-arm64, darwin-x64, darwin-arm64, win32-x64 - with exit code 0 and no warning. npm filters the exact same `file:` layout correctly. The reporter's repro is network-free (five tarballs built with `bun pm pack`, a package.json pointing each at `file:`), reproduces on Bun 1.4.4 and 1.4.3 (both releases verified), on linux-x64 locally and in CI on all five platforms, and also hits the wrapper-package layout that esbuild/swc-style tools use when their per-platform binary packages are carried as local tarballs - the standard shape for **offline or air-gapped installs**.

## Who this bites

- Exactly the people who use `file:` tarballs for platform packages: offline/air-gapped environments and restricted CI, where a registry isn't reachable and binaries are carried in. The install "succeeds" but every platform's binary lands on disk - multiplying install size, and breaking any tooling that asserts exactly one platform package got installed (or that scans/audits installed binaries per platform).
- The silent-success shape is the hazard: nothing in the output says the wrong-arch packages were installed, so a linux-x64 deploy can quietly ship darwin and windows binaries into production images.

## Limits

- Single-source report (repo ~85k stars, reporter association NONE) with a clean network-free repro; I verified the Bun releases and the earlier registry-side fix, but did not run the reproduction.
- Scope as reported is `file:` tarballs (including nested inside a wrapper tarball); other local specifiers (`link:`, `workspace:`) are not established in the issue.
- No maintainer response or fix yet, so no patched version to point at.
