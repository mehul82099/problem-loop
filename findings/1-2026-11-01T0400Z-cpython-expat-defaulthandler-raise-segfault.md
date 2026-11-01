# `xml.parsers.expat` segfaults when your `DefaultHandler` raises on a long non-UTF-8 token - a NULL function-pointer call the 2020 fix left behind

**Source:** [python/cpython#161060](https://github.com/python/cpython/issues/161060) (open, filed by CPython core dev gpshead with fix PR [#161061](https://github.com/python/cpython/pull/161061) open from the same author; prior-art issue verified)

## What happened

When a `DefaultHandler` (or `DefaultHandlerExpand`) callback raises, pyexpat clears all of the parser's C handlers. For documents needing encoding conversion - anything but UTF-8/ASCII, including UTF-16 - Expat delivers a token longer than 1024 bytes to the default handler **in several pieces**, re-reading the handler between pieces. The first piece triggers the raise and clears the handlers; the next piece is a call through a NULL function pointer. The reporter's repro is nine lines: same document, `encoding="utf-8"` raises the expected `ValueError("comments are not allowed")`; `iso-8859-1` and the interpreter dies with SIGSEGV. Two more paths crash identically: setting `DefaultHandler = None` from inside the callback, and a `CharacterDataHandler` that raises when `buffer_text` is flushed before a default-handler call.

The history makes it sting: the character-data handler had exactly this bug and was fixed in [#42389](https://github.com/python/cpython/issues/42389) (closed, verified) by installing a no-op handler instead of NULL - and the default handler was left out of that fix. This is the same crater, one handler over, six years later. The reporter and the fix-PR author are the same core developer (gpshead, MEMBER, verified), and the diagnosis - clear-then-re-call across chunked delivery - is stated with the mechanism, not inferred from a stack trace.

Blast radius is narrower than "everything XML": the default C `xml.etree.ElementTree`, `xml.sax` and `xml.dom.minidom` paths are **not** affected (they don't route through a user default handler this way); the pure-Python ElementTree fallback parser - used only without `_elementtree` - **is**.

## Who this bites

- Anyone validating or filtering XML with `xml.parsers.expat` directly - security-sensitive "reject comments/DTD" filters are exactly the code shape that raises from a default handler - on non-UTF-8 documents with tokens over 1 KB: a rejected document crashes the interpreter instead of raising. For a long-running service (WSGI workers, task queues), one crafted XML POST takes the whole worker down: a denial of service from data the program was specifically written to refuse.
- The utf-8-works/iso-8859-1-crashes split makes it nasty to discover in tests: ASCII-only test fixtures pass, and production dies on the first legacy-encoded feed.

## Limits

- The SIGSEGV and the chunking mechanism are the reporter's (a core dev, which raises confidence but is still a single source); I verified the issue/PR/prior-fix topology and associations, but did not compile the repro (repo ~77k stars).
- The fix PR is open and unmerged; backport targets (3.14/3.13 security branches) are not yet stated.
- The pure-Python ElementTree exposure is asserted in the issue; only direct pyexpat use has the repro.
