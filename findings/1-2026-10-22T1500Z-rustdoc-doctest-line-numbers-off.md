# rustdoc: doctest failure line numbers are wrong when the doc comment has non-doc lines in between

- Source issue: https://github.com/rust-lang/rust/issues/164685 (open at check time; labels: T-rustdoc, A-libtest, C-bug, A-doctests, needs-triage; opened 2026-10-21; 6 comments)
- Reproducer repository named by the reporter: https://github.com/raldone01/rustdoc-tests-incorrect-line-numbers (exists; its `src/lib.rs` matches the code shown in the issue as far as we read it)
- Project: https://github.com/rust-lang/rust (Apache-2.0 per the API, 120,668 stars)
- Latest Rust releases per the API: 1.99.1 (2026-10-16) and 1.99.0 (2026-10-01). The reporter used rustdoc 1.98.1.
- Checked: 2026-10-22 15:40 UTC

## Problem
The reporter has a crate-level doc comment where some code fences are toggled with `#![cfg_attr(..., doc = "```ignore")]` lines. When one of the doctests fails under `cargo test --features bar`, Cargo lists the failure as `src/lib.rs - (line 15)` and `src/lib.rs - (line 8)`. The reporter says those numbers are wrong, so you cannot jump to the failing example. They also ask for the usual `file:line` form that editors turn into links.

## What the thread says
- A project member replied on 2026-10-22 that "the line numbers offset is indeed off" and said they would look at it.
- The same member later says it also happens with blank lines or ordinary `//` comments between doc lines, and explains the cause as: anything that is not processed as Markdown (the doc-comment lines themselves) is not counted when the current line is computed. That is their diagnosis, which we did not check in the source.
- The reporter asked that the `:<line>` format also be added. A member answered that a plain unit test run prints no line number, to which the reporter answered that doctests do print one and that this is the point of the issue. That exchange has not settled whether a `file:line` format will be added.
- The issue is labeled `needs-triage` and no fix pull request was linked at check time (we looked at the issue's cross-references and found none).

## What this does not tell you
- It does not show which Rust versions are affected. The reporter used 1.98.1, and a newer stable, 1.99.1, is out. We did not run the example on it.
- The cause is the member's brief diagnosis only.
- The `file:line` request is a feature request on top of the bug and may be split off.

## Honest limits
- We did not run `cargo test` or rustdoc. We read the reproducer's source file and the issue.
- State may have changed since 15:40 UTC.
