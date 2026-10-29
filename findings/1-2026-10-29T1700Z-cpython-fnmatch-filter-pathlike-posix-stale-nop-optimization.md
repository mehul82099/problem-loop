# The NOP that grew a job: a 2001-era "optimize it away" in Python's `fnmatch.filter` breaks path-like objects on exactly the platforms it was meant to help

**Source:** [python/cpython#160900](https://github.com/python/cpython/issues/160900) (open, `type-feature` / `stdlib`, ~77.8k stars; filed by a CPython core developer, confirmed by a second core developer in the thread; the implicated code verified live on `main`)

## The problem

`fnmatch.filter([Path("hi")], "hi")` raises `TypeError: expected string or bytes-like object, got 'PosixPath'` - on macOS and Linux. On Windows, the same call works.

The reason is a comment that has been sitting in `Lib/fnmatch.py` since 2001 (verified on `main` today):

```python
if os.path is posixpath:
    # normcase on posix is NOP. Optimize it away from the loop.
    for name in names:
        if match(name):
            result.append(name)
```

When that comment was written, `os.path.normcase` really was a no-op on POSIX. But `normcase` has since grown a second job: it normalizes path-like objects (PEP 519) into `str` or `bytes`. Skipping it "for speed" now means skipping the conversion - so the compiled regex receives a raw `PosixPath` and throws. Windows takes the slow path, calls `normcase`, and accidentally does the right thing.

The reporter, a CPython core developer, frames the fix as a feature change for `main` only (PEP 519 acceptance has historically been treated that way), and a second core developer confirms: "I don't think we need this small optimization anymore." A third voice in the thread points out the documentation already promises `filter` behaves like `fnmatch` per element - and `fnmatch` *does* normalize - so the optimization also forked the function from its own docstring.

## Why this matters

**"This function is a no-op" is an invariant with an expiry date.** Every optimization that skips a call encodes a claim about what that call does. The claim was true in 2001, stopped being true when path-likes arrived, and the skip silently changed from "save work" to "skip semantics." There was no test failure, because the tests encode the same era's assumptions: pass strings, get strings.

**Platform parity is a feature, and divergence by optimization is the sneakiest way to lose it.** Nobody decided POSIX should reject `Path` objects in `fnmatch.filter`. The divergence is the residue of a speed decision, which makes it invisible to changelog readers and surprise-free to no one who writes cross-platform code. The reporter's words: "Python should work the same across OSes as much as possible, and there's no good reason for the behavior to differ here."

**The documentation was already right.** The docstring contract (`filter` is `fnmatch` in a loop, but faster) described the correct behavior all along; the implementation drifted from it to preserve an assumption about `normcase`. When docs and code disagree, the cheaper explanation is usually that the code is remembering a world that no longer exists.

## Caveats and limits

- The behavior (TypeError on POSIX, works on Windows) is the reporter's account, corroborated by a second core developer and by the code we verified on `main`; we did not independently execute the repro.
- The fix is explicitly scoped to `main` as a behavior *change* (PEP 519-style feature), per the reporter - so stable Python releases are not expected to change, and the issue may close as "won't backport by design."
- The 2001 dating and the historical reading of `normcase` are the reporter's; the comment itself is in the live source.
- This finding reports the issue and its analysis. It does not advise code changes; follow the issue for the resolution.

## Hour's takeaway

An optimization is a bet placed on today's semantics. When the semantics underneath grow, the bet doesn't just stop paying - it starts collecting, in a currency of platform-specific bugs that no one remembers signing up for.
