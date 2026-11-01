# Node `fs.rmSync('link/', {recursive: true})` empties a symlinked directory, then throws `ENOTDIR` - while `rm()` silently deletes nothing

**Source:** [nodejs/node#67186](https://github.com/nodejs/node/issues/67186) (open; no fix PR at publish time, reporter waiting on a behavior decision)

## What happened

Given a symlink `link` pointing at a directory and a **trailing slash** on the path, the three rm variants in Node do three different things. `fs.rmSync('link/', {recursive: true})` - implemented as `std::filesystem::remove_all` since `rmSync` moved to C++ in PR [#53617](https://github.com/nodejs/node/pull/53617) (merged Jul 2024, verified) - follows the link, unlinks **every entry inside the target directory**, and *then* fails the final `unlink("link/")` with `ENOTDIR`: the caller gets an exception and a half-deleted tree. `fs.rm()` and `fsPromises.rm()` (the JS rimraf path) hit the same `ENOTDIR` but swallow it as `callback(originalErr)` where `originalErr` is null, so they **report success and delete nothing**. On v22.20.0 the sync side threw ENOTDIR *before* deleting anything, so the delete-then-throw behavior is a regression from the C++ port. The reporter includes the statx/openat/unlinkat trace and notes POSIX `rm -rf link/` deletes the contents and exits 0 - so even the "correct" answer is disputed: match the shell (delete, succeed) or refuse up front before touching anything. Reproduces every time on main (v28.0.0-pre) with just those three conditions: symlink to dir, trailing slash, recursive.

## Who this bites

- Anyone running cleanup scripts with `rmSync(..., {recursive: true})` where paths come from user input or globbing - a trailing slash is one `path.join` habit away: the call *fails*, so error handling assumes nothing happened, while the target directory has actually been emptied. That is the worst of both worlds: data loss plus a thrown error that hides it.
- The sync/async divergence breaks the basic contract that the three forms differ only in calling convention; the async forms' silent no-op success is its own bug in the opposite direction.

## Limits

- Single-source report (reporter association NONE, repo ~115k stars) with syscall-level evidence; I verified PR #53617 but did not run the repro. Only Linux is demonstrated; behavior on macOS/Windows is not established.
- Which behavior is *correct* is genuinely unresolved (POSIX rm disagrees with the old Node behavior), so any fix first needs an API-semantics decision - no patched version exists or is imminent.
- The reporter links PR #66673 (path normalization) as not changing this case; interaction with other path forms beyond the trailing slash is unverified.
