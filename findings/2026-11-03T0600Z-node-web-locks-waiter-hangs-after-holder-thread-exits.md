# Node.js: a Web Locks request stays pending forever after the worker thread holding the lock exits

**Source:** https://github.com/nodejs/node/issues/67216 (opened 2026-11-03 UTC, open, no maintainer reply yet)

## The problem

With `navigator.locks` on worker threads, if the thread holding a lock exits - `process.exit()` or an uncaught exception - a request waiting for that lock is never granted. It stays pending until any thread makes any unrelated lock request, which flushes the queue as a side effect. The reporter's repro prints `still waiting`, then `granted` only after an unrelated `ifAvailable` request on a different lock name. Reproduces always on v26.13.0 and v24.22.2 (both tags verified), including when the waiter is in another worker thread; `worker.terminate()` takes a different path and does not trigger it.

The reporter pinpoints the cause, and the code confirms it verbatim on main: `LockManager::CleanupEnvironment` in `src/node_locks.cc` removes the dead environment's held locks and its own pending requests, then erases the environment - but never processes the pending queue. The normal release path, `ReleaseLockAndProcessQueue`, does exactly what its name says; the cleanup path frees the lock and walks away, leaving everyone else's waiters queued behind a lock nobody holds.

## Why it matters

The Web Locks API is the coordination primitive for exactly the pattern that makes this bite: multiple threads sharing a database or resource handle. The reporter found it running Evolu, a local-first sync platform, on Node worker threads - a thread waiting on a database lock hangs forever when the holder crashes, and the application looks idle rather than broken. Browsers grant the waiter when a worker holding a lock ends, so this is also a spec-behavior divergence that only shows up in Node's multithreaded deployments.

## Caveats

- Open with no maintainer response; reporter association NONE. The repro is self-contained and the named cleanup function was verified directly in current source; the browser-behavior comparison is the reporter's claim.
- This finding does not propose a fix, though the report's framing - process the pending queue during environment cleanup - identifies the gap precisely.
