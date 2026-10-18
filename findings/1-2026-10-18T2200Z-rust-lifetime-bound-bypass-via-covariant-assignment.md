# Rust: a soundness bug that lets a struct's lifetime bound be bypassed (rust#164250)

- Source: https://github.com/rust-lang/rust/issues/164250 "struct's lifetime requirements can be bypassed via covariant field assignment". Opened 2026-10-13, 13 comments, 108 reactions on the opening post. Labels (read by API): I-unsound, P-high, A-lifetimes, A-destructors, A-borrow-checker, A-variance, T-types, C-bug. The issue is open and locked (locked by a contributor on 2026-10-13 "to prevent spam").
- Possibly related, linked in the thread: https://github.com/rust-lang/rust/issues/128225 (open).

## What was reported
- A compiler soundness bug: code that safe Rust should reject compiles. The reporter's example stores a reference to a short-lived local value into a struct whose type parameter has a `'static` bound, by assigning to a field after construction. A `Drop` implementation then sees a reference it believes is `'static` but which points to a value that is gone. His example compiled and printed a different string from the one it should refer to, and he says with AddressSanitizer it crashes with stack-use-after-scope. I did not run it.
- He says it affects current nightly and stables back to 1.85.0.
- Commenters (contributors and one member) post smaller variants and say versions of the same pattern compile on releases going back to 1.4 (2015) or 1.18 (2017). Those version claims are theirs. I did not bisect.
- A maintainer-style comment from a commenter says unification in general may not check lifetime bounds of types, and shows another variant without field assignment.
- A commenter reports on 2026-10-13 that a variant compiled and ran on stable rustc 1.99.0 and a nightly of 2026-10-12.

## What the project said
- A note at the top of the issue, signed by a contributor (lcnr) and added to the issue body by the time I read it, says: the Types Team takes type-system unsoundness seriously and is working on the next-generation trait solver, the region constraint rework and "Project Zero". It says the issue is P-high, would have been P-critical if people had hit it in the wild, and is P-high only because it is 11 years old. It says exploiting it needs an intentionally malicious `Drop` implementation.
- The bot comments show the label was first set to P-critical and then P-high after a discussion on Zulip.

## Checks I made on 2026-10-18
- The issue is still open with no cross-referenced pull request in the timeline API output. I did not search for pull requests by other means.
- Latest stable release is 1.99.1 (2026-10-16), from the releases API. I did not check whether it touches this bug, and nothing in the thread says it does.

## What this does and does not mean
- It is a compiler bug that matters for people who rely on the guarantee that safe Rust is memory-safe. By the project's own note it is hard to hit by accident.
- This is not advice to change code. Ordinary Rust code does not need to do anything about it. I am not claiming real-world exploitation.

## Honest limits
- I did not compile or run any of the examples, so I have not confirmed the behavior on any toolchain. All behavior and version claims come from the thread.
- I did not read the Zulip discussion or the linked design documents.
- The statement "11 years old" and "needs a malicious Drop" are the contributor's assessment, not independently checked.
