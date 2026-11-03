# CPython: should `_PyTuple_Resize()` copy when the tuple's hash was already computed? A core-dev design thread

**Source:** https://github.com/python/cpython/issues/161226 (opened 2026-11-03 UTC by CPython core dev Victor Stinner, open, linked PR gh-161227 unmerged, active discussion)

## The situation

This one is a live design discussion between CPython core developers rather than a user bug report, and the interesting part is exactly that the right answer is not obvious. Background: a recent bug (gh-158219, verified closed) showed that if a codec or other machinery computes the hash of a freshly created `bytes` object, later in-place mutation leaves the cached hash wrong. The fixes set a pattern across the C API: `_PyBytes_IsMutable()` now returns false once the hash is computed, `_PyBytes_Resize()` was changed to copy in that case, and `PyUnicode_Resize()` has copied in that case since 2011. Stinner's proposal: bring `_PyTuple_Resize()` in line - if the tuple's hash was already computed, return a copy instead of resizing in place. He lists every in-tree caller (tkinter's FlattenContext, itertools' `batched_next`, code objects, generic aliases, structseq) and notes none computes the hash before resizing, so the change costs CPython itself nothing.

## The open question

Guido van Rossum pushes back on the design, not the goal: why copy at all? Just clear the cached hash - copying is more work, and a computed hash at resize time should only ever happen if the tuple escaped its construction phase, which is arguably always a bug in the caller. He also notes the same reasoning would have applied to `PyUnicode_Resize()`, which took the copy route anyway. Stinner's reply lays out the compatibility tradeoff: mutating in place after the hash was used is unsafe, and the function already fails with SystemError when the tuple is not uniquely referenced - so raising SystemError on a cached hash is an option too, but it could break third-party C extensions that rely on the old behavior, where quietly returning a copy keeps them working.

## Why it matters

This is how hash-consistency invariants actually get enforced in a runtime that third-party C code links against: each `_Py*_Resize` variant is a small one-way door, and the choice between copy, clear, and raise decides whether buggy extensions silently corrupt dict lookups, keep working, or start crashing. The bytes-side precedent shows the failure mode is real, not theoretical.

## Caveats

- This reports an ongoing maintainer discussion; no consensus or merged fix exists yet (linked PR gh-161227 is open). Nothing here is a recommendation for user code.
- The historical anchors cited in the thread (gh-158219, gh-158585, the 2011 unicode behavior) were spot-verified as real; the claim that no in-tree caller pre-computes the hash is the author's.
- Positions summarized above are the participants' own words, compressed - read the thread for the full exchange.
