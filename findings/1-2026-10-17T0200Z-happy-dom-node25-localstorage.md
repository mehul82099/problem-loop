# happy-dom on Node 25+: `localStorage` breaks because Node now ships its own

- Source: https://github.com/capricorn86/happy-dom/issues/1950 (open, label `bug`, opened 2025-11-12, last activity 2026-10-17)
- Checked through the GitHub API on 2026-10-17:
  - Node PR 57666 "unflag --experimental-webstorage by default": merged 2025-09-25 (https://github.com/nodejs/node/pull/57666)
  - Node issue 60303 on `localStorage` with no or invalid `--localstorage-file`: closed (https://github.com/nodejs/node/issues/60303)
  - Node PR 60351 "throw from localStorage getter on missing storage path": merged 2025-10-31 (https://github.com/nodejs/node/pull/60351)
  - Vitest issue 8757 "Node v25 breaks tests with Web Storage API": closed (https://github.com/vitest-dev/vitest/issues/8757)
  - Vitest PR 10293 "don't emit localStorage warnings on Node 26, fail gracefully when worker fails to start": merged 2026-07-01 (https://github.com/vitest-dev/vitest/pull/10293)
  - Vitest release v5.0.0, published 2026-09-03

## The problem
The reporter (dodomorandi) says that on Node 25, tests using happy-dom as the environment see `localStorage` as an empty object or missing, and happy-dom's own test run throws an assertion. Node 24 works.

Commenter brianhelba traced it to a Node change: Web Storage is enabled by default from Node 25, and it needs a `--localstorage-file` path. Node's own `localStorage` global then takes precedence over happy-dom's polyfill. A warning appears first: "`--localstorage-file` was provided without a valid path". After Node 25.2, he reports that any access throws `SecurityError: Cannot initialize local storage without a --localstorage-file path`. The patch he links (Node PR 60351) is the getter change listed above. He suggests happy-dom could detect when Node's version is unusable and fall back to its own implementation. Whether happy-dom did that is not stated in the thread.

## Workarounds reported by commenters (not run here)
- Pass a storage file path to Node through Vitest `execArgv`: `--localstorage-file <tmp path>` (brianhelba).
- Turn the feature off on Node 25 and later: `execArgv: ['--no-experimental-webstorage']` (r-thomson).

## Latest word, with a caveat
On 2026-10-17 TrevorBurnham wrote that the problem was fixed in Vitest 5.0.0 through vitest-dev/vitest#10293, was not backported to v4, and that the issue can probably be closed. I confirmed that PR 10293 exists, is merged, and that v5.0.0 was released later (2026-09-03). I did **not** confirm that the PR is in the v5.0.0 tag, and its title speaks of Node 26 warnings and graceful worker failure, which is not obviously the same as restoring happy-dom's `localStorage` on Node 25. Earlier commenters (TheJaredWilcurt, February 2026) saw this with Vitest 4.0.18 and happy-dom 20.6.0. The latest happy-dom release the API shows is v21.0.3 (2026-10-15).

So: the root cause is well documented. Whether upgrading Vitest alone is a full cure is one commenter's claim.

## Honest limits
- I ran no tests and installed no Node versions. All behaviour comes from the thread.
- Quoted Node errors and version behaviour are brianhelba's reports. Only the existence, state and dates of the linked PRs and issues were checked.
- I did not check what happy-dom itself changed in its releases, and the issue is still open.
