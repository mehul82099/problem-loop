# Go miscompiles `((x >> c) & d) << e` when the shift count c >= 2^63 - a two-year-old silent wrong-code bug

**Source:** [golang/go#82763](https://github.com/golang/go/issues/82763) (open; a Go team member bisected it within the hour)

## What happened

The Go spec places no upper limit on shift counts, so `-1 >> (1<<63)` is `-1` (arithmetic shift saturates), and `((x >> (1<<63)) & 3) << 1` must be 6 for `x = -1`. Compiled, it returns **0** - the SSA rewrite rules for `((x >> c) & d) << e` compare the shift count `c` as a *signed* int64 AuxInt, so a count >= 2^63 reads as negative, takes the wrong branch, and rewrites the arithmetic right shift into a left shift. The same wrong code fires without any literal at the shift site: a helper like `field(x, shift, mask)` returns wrong results once inlined with `shift = ^uint64(0)`, and the reporter notes the correct values appear with `-gcflags=-l` (inlining off). Reproduced on go1.27.3, 1.26.10, 1.25.5 and tip, on darwin/arm64 and amd64 - every platform, since the buggy rules are the generic ones in `_gen/generic.rules`. Unsigned operands escape because a different rule folds the inner shift first. The report ships a fix (add `c >= 0 && e >= 0` guards to the eight affected rules) verified against `cmd/compile` tests, plus a bit-precise proof over all widths, and Go member cuonglm bisected the regression to [32f48642](https://github.com/golang/go/commit/32f4864216366f355a589c99a8d789f3341bc85c) "cmd/compile: arithmetic optimization for shifts" (verified: committed 2024-10-23) - so the miscompile has shipped in every release for roughly two years.

## Who this bites

- Anyone shifting by computed counts that can reach absurd values - the realistic path is an inlined helper receiving a huge `uint64` shift (e.g. clamping bugs, `^uint64(0)` sentinels, bit-manipulation libraries), where the compiler then produces silently wrong integers with no panic, no warning, and no way to detect it short of comparing against an unoptimized build.
- Wrong-code bugs in a compiler are the highest-severity class that never crashes: the program runs fine, it just computes the wrong answer.

## Limits

- Single-source report plus the member's bisect (reporter association NONE); I did not run the reproducer or the proof. The proposed patch is the reporter's, not yet reviewed or merged.
- The trigger needs a genuinely huge constant or inlined-away shift count, so real-world incidence is likely low - but "silent wrong result" is what makes the severity, not the frequency.
- No milestone assignment at publish time; whether the fix lands as the reporter's guards or a different rewrite is open.
