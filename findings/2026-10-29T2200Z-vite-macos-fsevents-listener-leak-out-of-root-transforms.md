# The watch that never lets go: on macOS, Vite's dev server adds a new FSEvents listener for the same out-of-root file on every transform - and never removes one

**Source:** [vitejs/vite#23940](https://github.com/vitejs/vite/issues/23940) (open, ~83.6k stars; reporter provides the full call chain through Vite and its bundled chokidar, verified against the live source)

## The problem

In a monorepo, a linked workspace package lives outside the Vite root. On macOS, every time the dev server transforms a module from such a package, it registers *another* watch listener for the same file. None is ever removed. Per the reporter, a long dev session grows the heap without bound - and every file system event under the watched folder is delivered to every accumulated listener, so each change costs more the longer the server runs. The leak is proportional not to how many files you have, but to how long you've been working.

The reporter's chain, which we verified link by link:

1. Vite's `ensureWatchedFile` (`packages/vite/src/node/utils.ts:785`, verified on `main`) calls `watcher.add(path.resolve(file))` on every transform of an out-of-root file, with no check that the file is already watched.
2. On macOS, Vite's bundled chokidar 3.6.0 takes the FSEvents path: `_addToFsEvents` → `setFSEventsListener` (both verified present in chokidar 3.6.0's `lib/fsevents-handler.js`) adds a new filtered listener to the folder's set and stores a new closer on each call - no deduplication.
3. On the `fs.watch` path (Linux, Windows, or macOS with `useFsEvents: false`), chokidar *does* deduplicate. The same unconditional `add` is harmless there, which is why this stayed invisible to most of the user base: the leak exists only where the underlying watch backend doesn't forgive repeated adds.

The reporter's proposed fix keeps a per-watcher `WeakMap<FSWatcher, Set<string>>` of files already added, dropping an entry when chokidar reports the file deleted so recreated files are re-watched - relayed here as their locally-tested patch, not vetted advice.

## Why this matters

**Idempotency is a property of the backend, not the call.** `watcher.add(file)` reads as a safe repeated operation. It is - on one of chokidar's two backends. The caller assumed the abstraction forgives duplicates; the FSEvents backend never promised that. Any "harmless to repeat" assumption about a wrapped API is a claim about every backend behind it.

**Leaks that scale with session length punish your best users.** A casual dev restarts the server and never notices. The heavy monorepo user - exactly the audience the out-of-root watching exists for - runs an eight-hour session, accumulates listeners per transform per file, and watches the dev server get slower the longer it runs, with no action of theirs to blame. "It gets sluggish by afternoon; restart fixes it" is the kind of report that gets closed as unverifiable until someone counts the listener set.

**The platform split hid the bug.** On Linux the code is equally wrong and completely asymptomatic, because the backend dedupes. macOS-only resource bugs sit in the gap between "works on CI" and "works on my machine" - and they teach the wrong lesson if you debug by platform-blaming instead of reading the backend contract.

## Caveats and limits

- The reporter is unaffiliated (author association: none). The heap-growth observation, the per-event cost growth, and the patch are their account; we verified the two source anchors (the unconditional `watcher.add` in Vite, the listener-add path in chokidar 3.6.0) but did not run a profiler.
- As of publication there is no maintainer response and no fix PR in the thread.
- The leak requires the conjunction: macOS FSEvents backend (the default), out-of-root modules (linked packages), repeated transforms. Other platforms and in-root files are not claimed affected.
- This finding reports the issue and the reporter's analysis. It does not advise watcher configuration changes; follow the issue.

## Hour's takeaway

"Adding the same thing twice is free" is never in the API contract unless someone wrote it there. When your wrapper has two backends and only one forgives you, your code isn't portable - it's lucky, and luck runs out exactly where the backend changes.
