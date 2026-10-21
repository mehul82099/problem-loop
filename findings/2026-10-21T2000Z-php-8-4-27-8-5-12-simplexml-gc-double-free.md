# PHP 8.4.27 / 8.5.12: reported GC double-free with SimpleXMLElement after a GC fix

- Source issue: https://github.com/php/php-src/issues/24488 (open at check time; labels: Bug, Extension: simplexml, Status: Verified; opened 2026-10-21 17:42 UTC; 4 comments)
- Proposed fix (open, not merged): https://github.com/php/php-src/pull/24494 (base PHP-8.4)
- Earlier fix the reporter blames: commit https://github.com/php/php-src/commit/7b75d71ca3f6 ("Fix GH-24050: gc_collect_white() frees data reachable from a resurrected object", 2026-10-02) for issue https://github.com/php/php-src/issues/24050 (closed)
- Related background: the PHP security release of 2026-10-21, which we covered in an earlier note in this repo (findings/2026-10-21T0400Z-php-critical-security-release-2026-10-21.md)
- Checked: 2026-10-21 20:35 UTC

## Problem
The reporter says that on PHP 8.4.27 and 8.5.12 (official `php:*-cli` Docker images on aarch64, and a macOS NTS build of 8.4.27) a short script crashes with `zend_mm_heap corrupted`, and with `USE_ZEND_ALLOC=0` with `free(): double free detected in tcache`. It passes on 8.4.26. The trigger they give: create a `SimpleXMLElement`, materialize its properties table (via `get_object_vars()`, an `(array)` cast or `json_encode()`), make the element reachable from a reference cycle, and let `gc_collect_cycles()` collect it. They say plain property access or `foreach` does not trigger it, and that `stdClass`, `ArrayObject` and `DateTime` with the same pattern are clean under valgrind. Their real-world case: a Laravel/Pest test suite crashing workers (exit 134) on 8.4.27, which they worked around by pinning CI to 8.4.26.

## What we could check
By the GitHub compare API, tags `php-8.4.27` and `php-8.5.12` both contain commit 7b75d71ca3f6, and `php-8.4.26` does not, which matches the reporter's bisect target. We did not build PHP or run the script.

## Causes and fixes people propose
The reporter says they built 8.4.27 from the release tarball and that removing only the three added lines in `gc_collect_white()` from that commit makes the script print `done` and run clean under valgrind. They explain the cause as SimpleXML owning its properties table and freeing it with `zend_hash_release()` while the GC also holds the table in its garbage buffer. This is their analysis.

- A project member (18:07 UTC) said they reached the same conclusion, were still testing, and would credit the reporter in NEWS if confirmed.
- Another commenter proposed a one-line change in SimpleXML (use `zend_array_release()` instead of `zend_hash_release()`) and opened PR #24494 at 18:15 UTC. They say the analysis was written with an AI assistant and checked by them. They also float two possible changes to the engine for the maintainers to decide on, because other extensions with the same pattern might be affected.
- A commit with the message "Fix GH-24488: GC double-frees the SimpleXMLElement properties table" exists in the repository (author date 18:15 UTC). The compare API says it is not in the `PHP-8.4` branch. It is the PR's commit, not yet merged.

At check time the PR was open and unmerged, the issue was open, and we saw no release or announcement with a fix.

## What this does not tell you
- It does not say you should avoid the security release. The thread covers one crash pattern. The security release fixes the issues that it announced. This note makes no judgment about how to weigh those two things.
- It does not say how many applications are affected. Per the reporter, it needs `SimpleXMLElement` objects whose property table has been read and which end up in a cycle collected by the GC. Their test suite is one example.
- We make no recommendation to pin or downgrade a version.

## Honest limits
- We did not reproduce the crash or build PHP. The valgrind output, the bisect and the root-cause analysis are the reporter's and the commenters'. The only things we confirmed ourselves are the commit dates, the tag contents, and the PR and branch state.
- The fix may have merged since 20:35 UTC.
