# Free-threaded CPython: two threads reading `Element.text` for the first time can crash the interpreter - a lockless lazy join in `_elementtree`

**Source:** [python/cpython#161062](https://github.com/python/cpython/issues/161062) (open, filed by CPython core dev gpshead with fix PR [#161063](https://github.com/python/cpython/pull/161063) open from the same author; umbrella issues verified)

## What happened

On the free-threaded build (no GIL), the C `xml.etree.ElementTree` parser keeps text that arrives from expat in several chunks - anything containing an entity like `&amp;`, or the whitespace tails in an indented document - as a list, and joins it **lazily on first read** of `.text`/`.tail`. The join in `element_get_text()`/`element_get_tail()` (`Modules/_elementtree.c`) runs without a lock: two threads doing the first read of the same element both join the list and both drop the element's only reference to it. A debug build aborts with `_Py_NegativeRefcount: Assertion failed: object has negative ref count` at `Modules/_elementtree.c:587`; release builds can segfault. Concurrent `ET.tostring(root)` hits the same path. The default (GIL) build is not affected - the GIL serializes the join.

The reporter's repro is deterministic-shaped rather than lucky: 500 `<item>a &amp; b</item>` elements (the entity forces the chunked list), 8 threads behind a barrier doing first reads, 200 rounds. This is the fourth free-threading or shared-state crash/hang the same core dev has filed with a fix PR in the last day (after the [expat default-handler segfault](https://github.com/python/cpython/issues/161060) and the [sqlite3 shared-connection deadlock](https://github.com/python/cpython/issues/161065), each verified with open PRs). It slots into two open umbrella trackers, both verified: [#146022](https://github.com/python/cpython/issues/146022) ("Make xml.etree.ElementTree.Element usable on free-threaded builds") and [#149816](https://github.com/python/cpython/issues/149816) ("22 free-threading race conditions") - whose item (87) covers the getter racing the `text` *setter*, a different race in the same two functions.

## Who this bites

- Anyone running XML parsing under the free-threaded build - the build whose entire selling point is CPU-bound parallelism - with worker pools sharing parsed trees: a perfectly ordinary first `.text` read becomes a refcount-corrupting race. Indented documents (the common case for human-authored XML) trigger it via whitespace tails alone, no entities needed.
- The lazy-join design means the race window is *first access*, not parse time: trees built once and shared read-only across threads - the standard "parse on main, read on workers" pattern - are exactly the exposed shape.

## Limits

- The crash and the mechanism are the reporter's (a core dev, high-confidence, but single-source); I verified the issue/PR/umbrella topology and the MEMBER association, but did not run the repro on a free-threaded build (repo ~77k stars).
- The free-threaded build is still effectively opt-in/experimental for most users, which bounds current production impact; the report targets CPython main.
- The fix PR is open and unmerged; whether it locks per-element or joins eagerly is review-stage detail.
