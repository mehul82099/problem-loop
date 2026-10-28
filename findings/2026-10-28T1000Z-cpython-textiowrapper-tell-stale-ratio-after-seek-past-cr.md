# tell() lies after you seek past a carriage return: CPython's stale bytes-per-char ratio

- Source issue: https://github.com/python/cpython/issues/160811 (open; opened 2026-10-28)
- Verified: reporter's fix PR python/cpython#160812 (open)
- Project: python/cpython (~72k stars)
- Checked: 2026-10-28 10:15 UTC

## Problem
`io.TextIOWrapper.tell()` can return a wrong position - one character too far - after `seek()` to a position that follows a carriage return, and on some inputs it raises UnicodeDecodeError on perfectly valid data. Mechanism, per the reporter's reading of textio.c: with universal newlines the decoder may hold a pending `\r`, so the seek cookie carries `chars_to_skip > 0`; `seek()` replays the input chunk into a fresh snapshot but keeps the bytes-per-char ratio computed by the PREVIOUS `read()`; `tell()` then multiplies that stale ratio by chars_to_skip and overshoots the snapshot buffer. Debug builds catch it with an assertion (`skip_bytes <= size(next_input)`); release builds silently hand the oversized length to the decoder. Both the C and the pure-Python (`_pyio`) implementations carry the same bug. The reporter's fix (PR #160812): set the ratio from the replayed chunk in seek(), as `_read_chunk()` already does.

## Why it is interesting
- tell()/seek() is the most quietly load-bearing API in text processing. Log tailers, resumable parsers, checkpointed stream readers - all of them bank on "tell() now, seek() later, get the same spot." This bug breaks that contract only when a `\r` is pending at cookie time, which means the corruption depends on line-ending style: CRLF or classic-Mac files trigger it, LF files don't. A portability-shaped data-corruption bug in the standard library.
- The stale-ratio detail is a beautiful instance of hidden state. The seek cookie is supposed to encode everything needed to resume; the ratio - derived state - was not refreshed on replay, so the cookie described a decoder that no longer existed. "Snapshot + derived cache" pairs fail exactly this way: the snapshot is saved, the cache survives the restore.
- Release-vs-debug divergence doubles the trouble. Debug builds abort (loud, safe); release builds continue with a decoder reading past its buffer (quiet, wrong). The same bug is a crash for developers and silent position corruption for users - so it passes CI and lands in production.
- The fix is one idea, already filed: PR #160812 changes seek() to recompute the ratio from the replayed chunk. Issue, root-cause reading, failing repro on 3.13/3.14/3.16, and patch from the same reporter within the hour.

## Honest limits
- Single reporter, no maintainer review of the issue or PR at check time (~25 minutes after filing).
- Root-cause reading is the reporter's, anchored to a specific assertion in textio.c; not independently re-derived.
- Tested on macOS; the code path is platform-independent per the report, but other platforms are unverified.
- Issue state may have changed since 10:15 UTC.
