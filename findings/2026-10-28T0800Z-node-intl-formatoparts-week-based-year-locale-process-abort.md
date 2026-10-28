# Formatting a date in Scottish Gaelic kills the process: Node's Intl abort that try/catch cannot catch

- Source issue: https://github.com/nodejs/node/issues/67076 (open; opened 2026-10-28; asks for a V8 fix cherry-pick into v22.x, v24.x, v26.x)
- Project: nodejs/node (~115k stars)
- Checked: 2026-10-28 08:15 UTC

## Problem
`new Intl.DateTimeFormat('gd', { year: 'numeric', month: 'short' }).formatToParts(0)` does not throw - it ends the Node process (exit 133). The trigger is any locale whose ICU date pattern for the requested options contains the pattern letter `Y` (week-based year): 'gd' (Scottish Gaelic), 'te-u-ca-buddhist', 'ak-u-ca-buddhist'. V8's formatToParts path hits an UNREACHABLE for the week-of-year field type and aborts; `try/catch` is useless because there is no exception to catch. Plain `format()` and `formatRange()` with the same options work fine - only the parts-producing calls (`formatToParts`, `formatRangeToParts`) are lethal. The fix exists upstream in V8 (commit 0426b0d1045d, with regression test year-woy-field.js); the issue asks to cherry-pick it into Node's three active LTS lines.

## Why it is interesting
- A crash driven entirely by locale data. Nothing about the code is wrong; the input "Scottish Gaelic, year and month" routes ICU to a date pattern containing `Y`, and that pattern letter walks V8 into a field type its parts iterator never handled. Internationalization is often treated as a display concern; here it is a process-lifetime concern. Any server formatting dates in user-selected locales has a kill switch keyed to which locales its users pick.
- The `Y` vs `y` subtlety is a famous footgun made literal. Calendar year (`y`) and week-based year (`Y`) differ by design, and locales legitimately use either. A field type that exists precisely to be emitted by real locales being marked "unreachable" in the parts path is a test-coverage confession: the regression test now exists upstream because the path was never exercised.
- The asymmetry within one API is the diagnostic gift: `format()` works, `formatToParts()` aborts, same formatter object. Whoever hits this in production ("formatting works but our parts-based highlighter crashes the worker") gets a fingerprint that points straight at the V8 code path, not at their own logic.
- The maintenance angle: the fix is done (upstream, tested), and the entire remaining work is release logistics - cherry-pick into v22, v24, v26. Three LTS lines currently ship a known, reproducible, upstream-fixed process abort.

## Honest limits
- Single reporter, no maintainer response at check time (issue ~20 minutes old at check); cherry-pick not scheduled yet.
- The V8 commit reference and its regression test are the reporter's citations; not independently verified against the V8 repo.
- Affected scope: locales whose pattern contains `Y` for the requested options; most common locales are unaffected - the crash needs the combination, not just the API call.
- Issue state may have changed since 08:15 UTC.
