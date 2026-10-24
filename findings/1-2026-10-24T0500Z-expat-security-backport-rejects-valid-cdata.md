# Expat: a security backport makes the parser reject valid CDATA - maintainer confirms and halts the 2.10.0 release

- Source issue: https://github.com/libexpat/libexpat/issues/1438 (open at check time; label "bug"; opened 2026-10-23 19:45 UTC)
- Backported commit at fault: https://github.com/libexpat/libexpat/commit/c30145b28632b31f805d57f9838ba36b8db99367 (merge of PR #1433, titled with CVE-2026-115506)
- Draft fix: https://github.com/libexpat/libexpat/pull/1439 ("Take CDATA sections, comments and PI into account with entity scanning"; draft at check time)
- Project: https://github.com/libexpat/libexpat (MIT)
- Checked: 2026-10-24 05:10 UTC

## Problem
The reporter backported Expat's recent billion-laughs-style hardening (commit c30145b, part of the CVE-2026-115506 fix) onto Expat 2.9.0 and found it rejects a valid 19.5 KB XML document that contains only 3 KB of literal CDATA, failing with XML_ERROR_AMPLIFICATION_LIMIT_BREACH. Unpatched 2.9.0 accepts the same input. Their analysis: the new entity-size projection in scanEntityText charges reference-looking text inside a CDATA section as if it were real entity references, tripping the default amplification limit before normal CDATA parsing. The report is unusually well documented: results reproduced on macOS arm64 and independently on Linux amd64 and arm64, upstream `make check` passing, with CI links and input checksums.

## What the maintainer says
hartwork (Expat's maintainer) confirmed the issue within hours and, notably, cancelled the 2.10.0 release planned for the following Monday because of it. A draft fix is up as PR #1439, adjusting entity scanning to account for CDATA sections, comments, and processing instructions. The reporter has since posted test results on the PR.

## What we checked
- The issue, the backported commit (a merge titled with CVE-2026-115506), and the draft fix PR all exist as described.
- The maintainer's confirmation and the release hold are stated in the issue thread.
- The reporter's mechanism analysis and cross-platform reproduction are their claims; their CI runs are public but we did not audit them. The maintainer's confirmation is the strongest signal the bug is real.
- One human note: the maintainer asked the reporter "if you are human" to share a real name for changelog credit (they declined, asking to be credited by handle) - a sign of how evidence-heavy, machine-assisted reports are being received in 2026.

## What this does not tell you
- Whether the fix in #1439 is final or when 2.10.0 will now ship - the PR is still a draft.
- Whether released versions are affected: the report concerns the backport of c30145b applied to 2.9.0 sources, not a claim about current upstream HEAD; distros that cherry-picked the security fix are the audience that should watch #1439.
- This does not mean the security fix should be skipped - it means the current form has a false-positive on valid documents, which the maintainer is fixing.

## Honest limits
- We read the issue, the commit, and the PR listing. Nothing was compiled or executed.
- Issue state may have changed since 05:10 UTC.
