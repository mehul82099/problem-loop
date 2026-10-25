# rustc accepts a "place mention" of an uninitialized local and compiles it into real UB

- Source issue: https://github.com/rust-lang/rust/issues/164738 (open; labels include I-unsound, I-miscompile, S-has-bisection, T-lang, T-compiler, T-opsem; opened 2026-10-22 10:18 UTC)
- Project: https://github.com/rust-lang/rust (the Rust compiler)
- Checked: 2026-10-25 05:05 UTC

## Problem
Safe Rust like `let x: A; _ = x.0.0.0.0.0;` (a nested field mention of a never-initialized `Box` chain) is not rejected. Instead it compiles and, when run, dereferences whatever garbage was on the stack - null-pointer panics, SIGSEGV, or stack overflow depending on the system. Three minimal exhibits (Compiler Explorer links in the issue) cover uninitialized reads, a dropped-box read, and an assert that LLVM folds away because it can see the UB. This grew out of #164705 (verified open: "Borrow checker allows 'place mention'-dereferencing an uninitialized reference").

## Where the thread got to (all attributed)
- Reproduction quirks: the number of derefs needed varies by platform (the reporter needed 4-5); reporter maxdexh notes the garbage pointer is not always null, which is why behavior differs.
- Practical severity, per maxdexh: with optimizations on, MIR opts delete the unused reads before LLVM sees them, so "worst case here is a crash when running without optimizations" - and the code is contrived. It is still labeled I-unsound and I-miscompile: the compiler accepted code it should reject.
- Community bisection by cushionbadak using cargo-bisect-rustc: Exhibit A's runtime crash regressed in nightly-2026-09-04; the bisection lands on commit c33d8f3b (verified to exist - note it is a rollup merge, "Auto merge of #162229", so it is a window, not a single culprit PR). Exhibit B's misbehavior, strikingly, reproduces all the way back on rustc 1.0.0 under `-Zmir-opt-level=0`.
- Root-cause direction from compiler team members: dianne explains MIR lowering of derefs inserts statements before the `PlaceMention` that touch the (garbage) place, and that UB checks for raw-pointer alignment/nullness only run with `-Zub-checks`. RalfJung settles the semantics: "even emitting a PlaceMention here is already UB", so the MIR transforms are correct and the fix must be one of three: adjust MIR building, make the borrow checker reject the code, or change PlaceMention semantics.

## What this does not tell you
- No fix or assigned PR exists at check time; which of the three routes the teams will take is open.
- Whether any real-world (non-contrived) code can hit this is unknown; the reporter thinks it unlikely.

## Honest limits
- We read the issue and all 23 comments and verified the cited commit and the related issue via the GitHub API. We did not run the exhibits ourselves; every behavioral claim is the participants'.
- Issue state may have changed since 05:05 UTC.
