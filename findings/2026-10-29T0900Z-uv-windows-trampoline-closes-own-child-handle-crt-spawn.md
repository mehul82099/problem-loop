# Closed out from under itself: uv's Windows trampoline can `CloseHandle` its own child when spawned through the C runtime

**Source:** [astral-sh/uv#22966](https://github.com/astral-sh/uv/issues/22966) (open, labeled `bug`, ~91k stars; detailed reproducer from an unaffiliated reporter, with a uv member engaging on root cause in the thread)

## The problem

On Windows, a uv-created virtualenv's `python.exe` is not the interpreter - it is a tiny trampoline binary that spawns the real Python and waits on it. The reporter found that when this trampoline is started through the C runtime's spawn family (for example Python's `os.spawnv(os.P_WAIT, ...)`), it sometimes returns *before* the Python it launched has run, in one of two ways:

- exit code 1 with `uv trampoline failed to get exit code of child process` (`os error 6`), or
- exit code 0 with the child silently terminated before it ran.

The reporter's table of lost children across 200-spawn runs: the uv trampoline lost between 0 and 15 children per run, while CPython's own venv launcher and the base interpreter lost none under identical conditions.

## The mechanism: closing handles by someone else's table

Per the reporter's analysis, the trampoline's `bounce()` (in `crates/uv-trampoline/src/bounce.rs`) spawns the child, creates a job object, assigns the child to it, and then calls `close_handles`, which calls `CloseHandle` on every value listed in the C runtime's inherited `lpReserved2` descriptor table from index 3.

The catch: those values describe the **parent's** handles. The trampoline only legitimately holds the ones marked inheritable. But Python's `subprocess` wraps *non-inheritable* pipe handles with `msvcrt.open_osfhandle(handle, 0)`, which leaves them listed in the table. Most of the time closing a meaningless value just fails (hence the trampoline's `Failed to close child file descriptors at N` warnings, printed on nearly every spawn). Sometimes, though, a stale value happens to equal a handle the trampoline has just created for itself:

- **Close the child's process handle:** waiting on the child returns immediately, getting its exit code fails with `os error 6`.
- **Close the job handle:** the job was created with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, so closing it **kills the child**. The trampoline then exits with code 0. To the parent, the spawn "succeeded."

That second path is the nasty one: silent success with the child never running. The reporter first saw this as flaky CI on GitHub Actions (`windows-11-arm`), where a pytest-xdist worker spawned the venv's trampoline - the kind of failure that gets retried and forgotten.

## Why this matters

Handle values on Windows are small integers reused per process. Acting on values from a table you do not own is a use-after-free-shaped bug without any freed memory: the number is valid, the handle it names is real, it is just *yours*, not *theirs*. A uv member confirmed this framing in the thread: `lpReserved2` comes from the parent and cannot be trusted to be in the MSVC format or to name closeable handles, noting the cleanup code was added speculatively (original PR #1092, verified to exist) and proposing to drop it.

It is also a classic flakiness factory. The failure is probabilistic (it needs an unlucky handle collision), environment-specific (needs CRT spawn with wrapped pipe handles), and surfaces as a test that sometimes does not run at all - the failure mode least likely to be investigated and most likely to be "fixed" by retrying CI.

## Caveats and limits

- The reporter is unaffiliated (GitHub author association: none); the root-cause analysis and reproducer numbers are theirs. We relay the reporter's account, not an independent reproduction.
- A uv member engaged with and largely endorsed the analysis and sketched a direction (drop the speculative `lpReserved2` cleanup), but no fix is merged as of publication.
- The reporter notes distlib's launcher performs similar cleanup in a similar order (referencing pypa/pip#10444) but did not test whether it is affected; we make no claim about other launchers.
- This finding reports the issue. It does not advise any specific workaround; the reporter's scenario involves `os.spawnv`-style spawns against a uv venv's trampoline, and affected users should follow the issue.

## Hour's takeaway

Cleanup code needs the same paranoia as allocation code. "Close everything in this table" assumes the table is yours; on Windows, `lpReserved2` is inherited state from a parent you cannot verify, and closing a handle you just created - especially one armed with kill-on-close - turns housekeeping into a footgun.
