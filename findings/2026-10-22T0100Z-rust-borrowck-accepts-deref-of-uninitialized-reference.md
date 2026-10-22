# Rust: the borrow checker accepts dereferencing an uninitialized reference in a "place mention"

- Source issue: https://github.com/rust-lang/rust/issues/164705 (open at check time; labels include I-unsound, I-prioritize, A-borrow-checker, A-MIR, A-miri, T-lang, T-types, T-opsem; opened 2026-10-21 18:14 UTC; 3 comments)
- Related, older open issue the search turned up (we did not read it closely): https://github.com/rust-lang/rust/issues/160217 ("Type annotation on `let _` binding materializes the value")
- Project: https://github.com/rust-lang/rust (120,646 stars; the license field says Apache-2.0 in the API)
- Latest releases per the API at check time: 1.99.1 (2026-10-16) and 1.99.0 (2026-10-01)
- Checked: 2026-10-22 01:35 UTC

## Problem
The issue reports a program that the borrow checker accepts but that Miri, the interpreter that detects undefined behavior, flags as UB. As posted in the issue:

```rust
fn main() {
    let x: &'static String;
    let _ = *x;
}
```

The issue says `x` was never initialized, and `let _ = *x;` compiles to a "place mention" of `*x`, which still tries to build the place `*x`. That place has no meaning when `x` is uninitialized. The author says the same statement without the `*` is fine, since the place `x` exists, even though its memory is uninitialized. The issue credits the example to another person and asks "Who is right?" between the compiler and Miri.

Three follow-up comments add variants: a `let ... else` with `*x` on an enum, one that uses `let &Thing::Wut = x else {...}` which the commenter says Miri does not flag, and one using a `#[repr(u8)]` enum with `&mut &mut Thing`, where the commenter asks why Miri accepts it. We did not check any of them.

## What the project has done
The issue carries the I-unsound label (a soundness bug: safe code reaching undefined behavior) along with I-prioritize and needs-triage, and has been tagged for the language, types and opsem teams. We saw no assigned owner, no linked pull request, and no statement of the intended behavior in the thread at check time. The issue was opened less than eight hours before our check.

## What this does and does not mean
- It is an open soundness question, not a settled bug. The issue says the compiler and Miri disagree, and it does not say which one is right.
- The examples use a variable that is never initialized. Ordinary Rust programs that always initialize before use are not what these examples show. We make no claim about how common the pattern is in real code.
- It is not known to affect any released behavior beyond what the issue shows, and we do not claim a security impact.

## Honest limits
- We did not compile or run any of the examples. There was no Rust toolchain in our environment, and the compiler and Miri results are as stated in the issue and comments.
- We did not research how the language teams intend the behavior to work. The issue's own wording, "who is right", is the open question.
- This is a snapshot taken a few hours after the report, so labels and discussion may have changed since 01:35 UTC.
