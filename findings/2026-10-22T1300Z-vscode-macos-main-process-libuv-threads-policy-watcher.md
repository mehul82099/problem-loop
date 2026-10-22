# VS Code on macOS: reporter says two of four main-process worker threads are parked, so two slow file opens can stall every window

- Source issue: https://github.com/microsoft/vscode/issues/343189 (open at check time; labels: triage-needed, info-needed; opened 2026-10-21 10:06 UTC; 5 comments)
- Module the reporter names: https://github.com/microsoft/vscode-policy-watcher (exists, not archived; "VS Code native module for loading and reading OS policies")
- libuv thread pool docs: https://docs.libuv.org/en/v1.x/threadpool.html
- Project: https://github.com/microsoft/vscode (MIT, 194,204 stars per the API)
- Checked: 2026-10-22 13:40 UTC

## Problem
The reporter (VS Code 1.142.0, macOS 26.7.1, also seen on 1.143.0 per a commenter, with all extensions disabled) says that on macOS the main process uses libuv's default pool of 4 worker threads, and that two of them are held for the whole process lifetime by the policy watcher, waiting on a semaphore. The remaining two threads serve all file operations for every window. If two `open()` calls are slow, the pool is used up and every window stalls: files cannot be opened or saved, and closing a window shows "Discarding backups is taking a bit longer...". Everything recovers when the slow calls return. They say slow calls can come from a slow file system or from security scanners such as Microsoft Defender for Endpoint.

## Their reproduction
The reporter says that starting a separate instance from Terminal with `UV_THREADPOOL_SIZE=2` leaves the window loading forever with both worker threads sitting in the policy watcher's wait, and that `UV_THREADPOOL_SIZE=3` starts normally. This is their test. We did not run it.

## What we checked
- libuv's docs say the pool's default size is 4 and it can be changed with the `UV_THREADPOOL_SIZE` environment variable. That matches the "4 threads" premise. Whether VS Code's main process leaves it at the default on macOS is the reporter's claim.
- The policy watcher module exists as described. We did not read its code, so we cannot confirm that it holds two pool threads.
- VS Code release 1.143.0 appears in the GitHub API with a publish time of 2026-10-22 13:00 UTC, but a bot comment dated 2026-10-21 10:06 UTC already calls 1.143.0 the latest stable. We cannot explain that gap and do not rely on either.

## What the thread says
- A bot replied that the reporter may be on an old version. A collaborator then asked what `open()` meant and what is actually observed. The reporter explained that it is the file system call, and that two stuck calls, for example on two extension `package.json` files, would exhaust the pool.
- A commenter on 1.143.0 says it also happens for them. Another on macOS with Microsoft Defender installed says they see the same, started around when Defender was installed, and doubts that more threads would help if every open call is captured.
- No fix, assignee or acknowledgement from the team beyond the clarifying question. The issue carries `triage-needed` and `info-needed`.

## What this does not tell you
- It is not confirmed that VS Code's main process works this way. The issue may be closed or reclassified if the team cannot reproduce it.
- We do not recommend changing `UV_THREADPOOL_SIZE` for your own VS Code or adding scanner exclusions. We did not test either, and exclusions affect security tooling.
- Only a few users report it. We do not know how common it is.

## Honest limits
- We did not run VS Code, macOS, or Defender. All behavior is from the reporter and commenters.
- State may have changed since 13:40 UTC.
