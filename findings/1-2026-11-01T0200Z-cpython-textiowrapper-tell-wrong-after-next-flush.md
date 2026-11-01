# `TextIOWrapper.tell()` silently returns a wrong position after `next()` then `flush()` - and `seek()` on it lands you mid-line

**Source:** [python/cpython#161055](https://github.com/python/cpython/issues/161055) (open; confirmed on current main by core dev gpshead (MEMBER), who also has the fix PR [#161056](https://github.com/python/cpython/pull/161056) open; related issues verified)

## What happened

`TextIOWrapper.__next__()` stops maintaining the decoder snapshot that `tell()` depends on and disables `tell()` outright (`OSError: telling position disabled by next() call`). But calling `flush()` afterwards re-enables `tell()` **without restoring the snapshot** - so `tell()` computes from stale state and silently returns a wrong cookie instead of raising. The reporter's eight-line repro: read a line, `next(f)`, `flush()`, and `tell()` returns `3624` instead of `10003`; `seek()` to that position and `read(3)` returns `'bbb'` from the middle of the previous line rather than `'c\n'`. The pure-Python `_pyio` implementation returns yet a third value (`9768`), also wrong - so the C and Python implementations disagree with each other *and* with the truth. gpshead confirmed both numbers reproduce on current main and noted a second trigger: `next()` as the very first read, then `flush()` + `tell()`.

This is data-corruption-grade silent wrongness: the API contract is that `tell()` returns an opaque cookie you can `seek()` back to, and here it returns a cookie that points somewhere else entirely - no exception, no warning.

The fix PR (gpshead, verified open) takes the conservative route: `flush()` re-enables `tell()` only when no snapshot state or decoded text is pending, so these cases go back to raising the honest `OSError` that `tell()` gives without the `flush()`. It does not attempt the deeper fix - the long-open [#81217](https://github.com/python/cpython/issues/81217) ("Iterating a text file by line should not implicitly disable tell", verified open) asks for `next()` to keep `tell()` working at all. Sibling issue [#161053](https://github.com/python/cpython/issues/161053) (verified open) covers `tell()` reading past the snapshot after `seek()`, which the reporter notes changed this bug's shape: before it, the stale snapshot path read out of bounds instead of just misreporting.

## Who this bites

- Any program that mixes iteration and `tell()`/`seek()` bookmarking on text files and touches `flush()` (log processors, parsers that checkpoint positions, anything syncing before a seek): positions saved after a flush are silently wrong, and seeks land mid-line.
- The C-versus-_pyio disagreement also poisons cross-implementation test suites: the same code gets two different wrong answers depending on the interpreter build.

## Limits

- The repro outputs are the reporter's plus gpshead's confirmation comment; I verified the issue/PR/related-issue topology and the MEMBER association, but did not run the repro (repo ~77k stars).
- The fix is PR-stage, not merged; its "raise instead of misreport" semantics match gpshead's comment but review may change them.
- Scope is `TextIOWrapper` (C and `_pyio`); other IO classes (`StringIO`, `BufferedReader` wrappers) are unexamined here.
