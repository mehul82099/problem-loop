# sass-embedded: the synchronous API fails with "Invalid protobuf" on Node 24.22 for large CSS output, and a contributor found a likely cause

- Source issue: https://github.com/sass/embedded-host-node/issues/451 (open at check time; no labels; opened 2026-10-22 08:16 UTC; 4 comments)
- Pull request with a one-file fix: https://github.com/sass/sync-child-process/pull/38 ("Fix buffer corruption", open, not merged, created 2026-10-23 01:47 UTC)
- Code the contributor points at: https://github.com/sass-contrib/sync-child-process (the same logic is in the `main` branch of https://github.com/sass/sync-child-process, `lib/index.ts`)
- Node docs line quoted in the thread: https://nodejs.org/api/buffer.html (section on `buf.buffer`)
- Node releases per nodejs.org: v24.22.1 (2026-10-20), v24.22.0 (2026-10-14), v24.21.0 (2026-09-07)
- Project: https://github.com/sass/embedded-host-node (MIT, 229 stars per the API)
- Earlier finding on a different Sass bug: `2026-10-21T0800Z-dart-sass-1-106-0-empty-attribute-selector-crash.md`
- Checked: 2026-10-23 01:55 UTC

## Problem
The reporter says that since Node 24.22.0, `initCompiler().compile()` (the synchronous API) on Linux x64 with glibc fails with `Compiler caused error: Invalid protobuf: ... illegal tag: field no 13 wire type 6` when the compiled CSS is large. They say the async API works on the same input and Node 24.21.0 and earlier work with both. Their table, from generated files, shows the sync API succeeding 5 of 5 times at about 500 KB of output, 1 of 5 at about 1 MB to 1.5 MB, and 0 of 5 at about 2.5 MB. They give a short reproduction using a Docker image of Node 24.22.0 and `sass-embedded` 1.106.1. We did not run it.

## What the thread says
- A contributor reproduced something different at first: on Linux (glibc and musl) but not macOS, both sync and async calls failed with "exited unexpectedly" or "Dispatcher closed". Later they found their small VM had run out of memory (the kernel killed the Sass process when compiling a 9.7 MB input), and said that is a separate problem from the protobuf error. We read this as two different failures that look alike.
- Later the same contributor reproduced the original protobuf error, and posted a cause: a helper package copies a received chunk with `Buffer.from(message.data.buffer)`. They say that copy is sometimes not equal to the original data, while `Buffer.from(message.data)` always is, and that a debug comparison they added showed this. They add that Node's docs warn the underlying array buffer "is not guaranteed to correspond exactly to the original Buffer". They opened a one-file fix, pull request #38, with the issue as its target.

## What we checked
- The Node docs say that sentence, in the section on `buf.buffer`. Per Node's docs, a `Buffer` can be a view into a larger shared memory block, so its underlying array buffer can hold more than the buffer's own bytes. That fits the contributor's reading but does not prove their finding for this bug.
- The sync-child-process code on its `main` branch still uses `Buffer.from(message.data.buffer)` in two places (stdout and stderr), lines 107 and 112 in our read.
- The pull request exists, is open, and changes one file. We did not read the diff.
- Node 24.22.0 came out on 2026-10-14, which matches the report that the problem started with it. We do not know what changed in Node that exposes the problem, and the thread does not say.

## What this does not tell you
- The fix is not merged or released. We did not test the pull request or the cause.
- Node 24.22.0 and later is not shown to be at fault. The contributor's explanation points at the helper's own code, and says Node's behavior is documented.
- We do not recommend downgrading Node. Node 24.22.1 is a newer release and some projects need current security releases. The safer step is to use the async API, which the reporter says works, if your build allows it. That is the reporter's observation, not tested by us.

## Honest limits
- We did not run Sass, Node or Docker. We read the issue, source on `main`, the Node docs and release data.
- State may have changed since 01:55 UTC.
