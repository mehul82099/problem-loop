# An optional cache that hard-fails everything: Vitest's `fsModuleCache` breaks every test in read-only project directories

**Source:** [vitest-dev/vitest#11777](https://github.com/vitest-dev/vitest/issues/11777) (open, ~17.3k stars, labeled `p3-minor-bug` and `approved`; filed by a user reporting a production education-platform breakage)

## The problem

Vitest 5.0.4 turned the `fsModuleCache` (a filesystem cache for transformed modules) on by default via merged PR [#11435](https://github.com/vitest-dev/vitest/pull/11435). A cache is, by definition, an optimization: it exists to make things faster and must never be required for correctness.

But when the project directory is not writable, every test file fails:

```
FAIL  sum.test.js [ sum.test.js ]
Error: ENOENT: no such file or directory, mkdir '/app/node_modules/.vitest-cache'
```

On a root-owned project used by a non-root user it is `EACCES: permission denied` instead. The reporter says the same setup passes on 5.0.3.

The cause is one unguarded line. In `packages/vitest/src/node/cache/fsModuleCache.ts` at tag `v5.0.5` (lines 299-301, verified against the tagged source):

```ts
if (!existsSync(cacheRoot)) {
  mkdirSync(cacheRoot, { recursive: true })
}
```

There is no `try/catch` and no fallback. A failed cache-directory creation throws, and the throw is attributed to the test file, so the entire suite reports failure. The optimization's failure mode is worse than its absence.

## Where it hits

Read-only setups are common, not exotic, and the reporter lists the environments that broke: containers running with a read-only root filesystem, sandboxes that mount the project read-only and run tests as a different user, and CI images with a pre-installed root-owned `node_modules`. The reporter's own case: an education platform running student exercises in locked-down containers, where every JavaScript exercise broke after upgrading to 5.0.5. Reporter-suggested workarounds (`--no-fsModuleCache` or setting `fsModuleCachePath`) exist but must be discovered per project; there is no environment variable to set once per image. We relay these only as claims from the issue, not as vetted advice.

## Why this matters

This is the "cache must fail open" principle violated in its purest form. A cache has exactly one acceptable failure behavior: notice it cannot cache, warn once, and run uncached at full correctness. Anything else converts an optional speedup into a correctness dependency. The bug is also a regression-by-default-flip: the feature worked the same before, but only users who opted in could hit it; making it default-on exported the fragility to every read-only environment overnight.

The diagnostic shape makes it worse. The error is reported per test file (`FAIL sum.test.js`), pointing at the test, not at the cache subsystem, so teams debugging it start by suspecting their own code or their container image, not a test-runner cache directory.

The reporter offered to send a PR that logs a single warning and continues with the cache disabled on `EACCES`/`EPERM`/`EROFS`/`ENOENT`. A bot comment on the issue states the team's `approved` label means a pull request is accepted for it - we attribute that approval signal to the project's triage automation and labels, not to a named maintainer's statement in the thread.

## Caveats and limits

- The version boundary (passes on 5.0.3, broken on 5.0.4/5.0.5) is the reporter's claim; we verified the default-flip PR is merged and the unguarded `mkdirSync` exists at `v5.0.5`, but did not independently re-run the reproduction.
- The issue author is an unaffiliated user (GitHub author association: none); the affected-environment list is self-reported.
- No fix is merged as of publication; maintainers have not posted their own diagnosis in the thread.
- This finding reports the issue and its stated impact. It does not advise any specific migration, downgrade, or workaround; teams on read-only filesystems should evaluate the reporter's suggested flags in their own environments.

## Hour's takeaway

Optional fast paths deserve paranoid failure handling precisely because they are optional. Every cache write should be wrapped as if the disk is read-only, because for some of your users, it is.
