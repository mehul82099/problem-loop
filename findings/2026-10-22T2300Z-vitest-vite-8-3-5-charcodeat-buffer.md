# Vitest with Vite 8.3.5: "code.charCodeAt is not a function" because a file is read as bytes instead of text

- Source issue: https://github.com/vitest-dev/vitest/issues/11682 (open at check time; labels: p2-edge-case, approved; opened 2026-10-21 09:24 UTC; 4 comments)
- Vite change blamed in the thread: https://github.com/vitejs/vite/pull/23775 ("perf(ssr): extract inline source maps without a regexp", merged 2026-10-21 06:18 UTC)
- Vite releases per the API: v8.3.5 (2026-10-21 06:35 UTC) and v8.3.4 (2026-10-08)
- Vitest release used in the reports: v5.0.5 (2026-10-15)
- A downstream project that pinned the older Vite in its own tests: https://github.com/DataDog/dd-trace-js/pull/10864 (closed; "test(vitest): pin Vite 8.3.4 for core integration tests")
- Project: https://github.com/vitest-dev/vitest (MIT, 17,273 stars per the API)
- Checked: 2026-10-22 23:50 UTC

## Problem
With Vitest 5.0.5 and Vite 8.3.5, the reporter says that formatting an error thrown by a custom reporter crashes with `TypeError: code.charCodeAt is not a function`, hiding the original error. Their steps use a small project with one passing test and a reporter that throws on run end. A commenter on Linux with Node 24 confirms it. Another says the same error stops a whole run with "No test files found" when a global setup file imports a large cloud library, so no tests run at all.

## Cause as described in the thread
The reporter says Vitest's module runner reads a temporary file with `readFile(result.tmp)`, which returns a byte buffer, where Vite expects source text. A commenter says this only started to break when Vite's change above began calling `charCodeAt` on the fetched module, and that other places in Vitest that read the same kind of file already pass a text encoding. We checked the source: in both the `v5.0.5` tag and the `main` branch, `packages/vitest/src/node/environments/serverRunner.ts` has `const code = await readFile(result.tmp)` at line 40, without an encoding. We also confirmed that the Vite pull request was merged about 17 minutes before the 8.3.5 release. We did not run any of it.

## Status
- The issue is labeled `approved`, which, per a bot message posted on 2026-10-22 at 23:43 UTC, means the team accepts a pull request for it, one per issue. No fix pull request was visible to us at check time.
- Both the reporter and a commenter say that adding the text encoding fixes their case. A commenter says Vite 8.3.4 avoids the crash. These are their reports. The DataDog pull request above shows another project chose to pin Vite 8.3.4 in its tests, which matches the claim but does not prove it.

## What this does not tell you
- We do not tell anyone which versions to install. Pinning an older Vite also skips whatever else changed in 8.3.5.
- We do not know how many setups are affected. The reports involve source-map handling of modules loaded through a temporary file path, for example global setup files or error formatting, so ordinary test files may not hit it.
- The fix is not released. We do not know which release will carry it.

## Honest limits
- We read the issue, its comments, the two source files and release lists. We did not run Vitest or Vite.
- State may have changed since 23:50 UTC.
