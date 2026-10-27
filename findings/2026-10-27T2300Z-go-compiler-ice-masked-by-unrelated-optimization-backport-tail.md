# A Go compiler crash "fixed" by an unrelated optimization - and the five-week tail of the real fix

- Source issue: https://github.com/golang/go/issues/82642 (open; opened 2026-10-27 - the 1.26 backport request)
- Root issue: https://github.com/golang/go/issues/81687 (closed via fix CL)
- Project: golang/go (~132k stars)
- Checked: 2026-10-27 23:25 UTC

## Problem
`rotate(rotate(12345, 7), -7)` - valid, boring Go - crashes the Go compiler with an internal error ("not lowered: v35, Int64Lo") when targeting GOARCH=386. The inliner and rotation-rewrite produce a value the 386 SSA backend has no lowering rule for. A community bisect pinned the introducing commit the same night the issue was filed. The fix, once written, was one idea: "use a 32-bit type for rewritten rotate amounts." But today's activity is the interesting part: more than a month after the fix landed on master and was backported to 1.27, a maintainer opened the 1.26 backport (issue #82642) - the third release line to receive the same one-line-type fix, five weeks on.

## Why it is interesting
- The masking moment is the lesson. Within hours, thepudds noted the exact repro no longer crashes on master - not because the underlying bug was fixed, but because an unrelated new optimization (constant folding of math/bits functions) happens to evaluate this particular expression before the broken rewrite can run. Change the arguments slightly and the ICE is back. An optimization that hides a bug looks exactly like a fix in the dashboard, and the thread shows a maintainer catching that in real time instead of closing the issue as "cannot reproduce."
- The bug is a phase-boundary violation, which is why one wrong type crashes everything. The frontend rewrite emits a rotate amount typed as a 64-bit value; on 64-bit targets nothing notices; on 386, where 64-bit values must be decomposed into Int64Hi/Int64Lo pairs by lowering rules, the new value arrives after the rules that would handle it - so the backend gives up with "not lowered." Compiler phases each assume the previous one kept its type promises.
- The backport tail shows what "fixed" actually costs. Fix lands on master (Sept 23), backport to 1.27 (Sept 30), and only today the 1.26 line (Oct 27). Users on the previous release train have been building 386 binaries against an ICE for five weeks after the fix existed. Cherry-picks are not free; this is their price made visible.
- Also a nice open-source arc: reporter files a textbook minimal repro, a bystander bisects within two hours, a maintainer catches the masking trap, the bot machinery carries the fix through three release branches.

## Honest limits
- The "unrelated optimization masks the ICE" claim is thepudds' analysis in the thread (with a modified repro that still crashes); we did not independently re-run the compiler.
- The introducing-commit bisect is the community member's result, not re-run by us.
- 1.26 backport is requested, not merged, at check time; users on 1.26 remain exposed.
- Issue state may have changed since 23:25 UTC.
