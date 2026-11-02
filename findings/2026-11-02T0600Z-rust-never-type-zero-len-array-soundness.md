# Rust: a `!`-typed constant in a zero-length array makes safe code read out of bounds - type checking treats the never-evaluated constant as diverging

**Source:** [rust-lang/rust#165323](https://github.com/rust-lang/rust/issues/165323) (open; labeled `I-unsound`, `I-prioritize`, `C-bug` by Rust triage)

## What happened

The Rust Reference says the constant in a zero-length array `[C; 0]` is never evaluated. But type checking treats a constant of type `!` (the never type) as diverging, so the compiler marks everything after that expression unreachable - and the code after it **does run**. The reporter's minimal program uses `#![forbid(unsafe_code)]`: a bounds check calls a function whose body contains `let _: [!; 0] = [const { panic!() }; 0];` before returning `v[i]`. In a debug build the program dies with SIGILL on the compiler-inserted `unreachable`; with `-O` the bounds check vanishes entirely and it prints `v[4] = 0`, reading past the end of a 3-element `Vec` in fully safe code. The expected behavior is either a normal index-out-of-bounds panic (the constant is never evaluated) or compile error E0080 (which is what happens when the same constant is used anywhere else - `[C; 1]`, bare `C;`, or `let _: [u8; 0] = [C; 0]`). Reproduced on rustc 1.99.0 (verified release, 2026-10-01), 1.100.0-beta.5 and 1.101.0-nightly; the shorter repro uses the `!` type, stable from 1.100, but the same failure reproduces on stable 1.99 via an associated-const formulation with no feature gates. Rust triage applied the `I-unsound` and `I-prioritize` labels within minutes - the project's own classification for soundness holes in safe code.

## Who this bites

- This is the category Rust's safety guarantee is built on: a program with zero `unsafe` blocks can exhibit undefined behavior (out-of-bounds read) purely because of a type-checking inconsistency around the never type and zero-length arrays.
- Practically, the trigger is exotic - few real codebases write `[!; 0]` or `!`-typed associated constants in array repeat expressions - so this is a compiler-correctness hole to fix, not a pattern users are likely to hit accidentally. The finding reports the compiler bug; it does not suggest any code action for Rust users beyond normal toolchain updates once a fix lands.

## Limits

- Single-source report (reporter association NONE) with two minimal repros and clear expected/actual behavior; I did not compile or run them. No fix PR yet.
- Whether the OOB read generalizes beyond the reporter's construct (other optimizations exploiting the same wrong divergence) is not established.
- The `!`-type version requires 1.100+ (beta/nightly at report time); the stable-channel repro uses the longer associated-const form on 1.99.0.
