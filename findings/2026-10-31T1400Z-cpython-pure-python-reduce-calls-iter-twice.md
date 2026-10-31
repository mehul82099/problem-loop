# CPython's pure-Python `functools.reduce` calls `iter()` twice - the C version once, and PyPy is waiting on the fix

**Source:** [python/cpython#161004](https://github.com/python/cpython/issues/161004) (open, `type-bug`, `stdlib`; code anchors verified, and **reproduced by me locally**)

## What happened

`functools.reduce` exists twice in CPython: a C accelerator and a pure-Python fallback in `Lib/functools.py`. They disagree on an edge case. The pure-Python version does `it = iter(sequence)` and then `for element in it:` - and the `for` loop calls `iter()` **again** on the iterator. An iterator that defines `__next__` but not `__iter__` (technically legal to return from `__iter__`, and handled by the C version) makes the pure-Python reduce raise `TypeError: 'Iterator' object is not iterable` while the C reduce returns the answer.

Verified at the cited commit `4aab0c4e`: [Lib/functools.py#L251-L263](https://github.com/python/cpython/blob/4aab0c4ea2c569fce374a05cdd3b91009944f82b/Lib/functools.py#L251-L263) has the double call; [Modules/_functoolsmodule.c#L1097-L1118](https://github.com/python/cpython/blob/4aab0c4ea2c569fce374a05cdd3b91009944f82b/Modules/_functoolsmodule.c#L1097-L1118) calls `PyObject_GetIter(seq)` once and then only `PyIter_Next`. The pure-Python shape is unchanged on `main`.

**My own run** (Python 3.10.12, C accelerator blocked via `sys.modules['_functools'] = None`, reporter's example): C `reduce(add, Iterable())` returns `6`; the pure-Python one raises `TypeError: 'Iterator' object is not iterable`. Matches the reporter exactly.

Why it matters beyond tidiness: [PEP 399](https://peps.python.org/pep-0399/) asks the pure-Python and C implementations of stdlib modules to behave identically, and PyPy - which consumes this very `functools.py` - was told to get the fix upstream first: [pypy/pypy#5701](https://github.com/pypy/pypy/issues/5701) (open, verified). The reporter acknowledges the glossary says an iterator "should" define `__iter__`, so this is a conformance-polish bug, not a crash: the fix is replacing the `for` with an explicit `while`/`next` loop.

## Who this bites

- PyPy users (and any non-C implementation importing CPython's `Lib/functools.py`): code that reduces over a bare `__next__`-only iterator works on CPython-with-C-accelerator and breaks on PyPy.
- CPython itself when the C accelerator is absent (restricted builds, testing of the fallback path).

## Limits

- The reporter tested on 3.12/3.14/3.16 (macOS); my run was 3.10.12 (Linux), so the divergence spans at least that range. Repo ~78k stars.
- The issue is hours old, no maintainer response yet; whether CPython considers a `__next__`-only iterator a supported input is the open question (the glossary language is on the reporter's side only weakly - "should", not "must").
- The fix is trivial but behavioral: after it, the pure-Python reduce would accept inputs it previously rejected, which is the intended PEP 399 alignment.
