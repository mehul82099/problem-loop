# IronCalc: named ranges work alone but not inside formulas; a fix is now in review

- Source issue: https://github.com/ironcalc/IronCalc/issues/1581 (open at check time; no labels; opened 2026-10-21 22:32 UTC; 4 comments)
- Fix PR: https://github.com/ironcalc/IronCalc/pull/1587 ("Named ranges now support formulas", open, not merged)
- Related older bug the reporter links: https://github.com/ironcalc/IronCalc/issues/1384 ("COUNTIF/*IFS family returns #VALUE! for single-cell reference arguments", open since 2026-08-22)
- Project: https://github.com/ironcalc/IronCalc (Apache-2.0, about 4.2k stars per the API)
- Checked: 2026-10-23 10:50 UTC

## Problem
The reporter says a workbook with about 50 named cells and ranges imports into IronCalc and the names appear, but named *ranges* do not work. They later narrowed it: a `COUNTIF` that refers to a named range fails, and pointed at the existing COUNTIF bug #1384.

## What the thread says
- A maintainer asked for an example; a community member attached an .xlsx with many named-range test cases and said most cases work but some fail. We did not download or open the file.
- The maintainer then confirmed the gap directly: "We indeed did not implement named ranges with formulas. So I decided to take this opportunity to implement them."
- A fix PR, #1587, is now open and cross-referenced from the issue. It was not merged when we checked, and we did not read its diff or run its tests.

## What we checked
- The issue, its comments, and the linked issue #1384 all exist as described. #1384 is a separate, older report that the COUNTIF family returns `#VALUE!` for single-cell reference arguments, still open.
- PR #1587 exists, is open, and its title matches the maintainer's stated plan.
- The project is a spreadsheet engine; the maintainers confirmed the missing capability in their own words, so this finding does not rest on the reporter's claim alone.

## What this does not tell you
- We cannot say exactly which formula-plus-named-range combinations fail. The community test file exists but we did not evaluate it.
- There is no released version with the fix; #1587 is still under review.
- Whether #1384 is the same root cause or an adjacent one is the reporter's reading, not confirmed by the maintainer in the thread.

## Honest limits
- We read the GitHub thread and listings only. We did not open IronCalc, the test workbook, or the PR diff.
- Issue state may have changed since 10:50 UTC.
