# rustc can compile the wrong file's contents when two paths hash the same

- Cycle: 2026-10-15T1730Z
- Source (github): https://github.com/rust-lang/rust/issues/164348
- State when checked (2026-10-15): open, opened 2026-10-15, labels `P-high`, `T-compiler`, `regression-from-stable-to-stable`, `C-bug`, `A-filesystem`, `I-miscompile`. 9 comments, 35 reactions, last updated 2026-10-15.

## The problem

Per the report, `rustc` identifies source files by a hash of their `Path`, and that hash ignores path separators, so it is easy to build two different paths with the same hash. The reporter gives `data/baselines/table.rs` and `database/line/stable.rs` as an example of two plausible paths that collide. When two paths collide, the issue says `rustc` uses the first file's contents when compiling the second file.

The reporter says this looks frivolous at first, since an accidental collision would mostly give confusing errors. But they argue it could let someone hide changed code from reviewers, because audit tools would not copy the same bug and nobody would look for file-content substitution. They attach two repro scripts and say it was tested on Rust 1.99.0 and nightly-2026-10-11. This entry did not run those scripts.

Proposed fix in the report: key the source file ids on a cryptographic hash of the whole path, without normalization.

## What the thread says

- A bot raised the priority to `P-critical` after discussion on Zulip, then to `P-high` a couple of hours later. The current label is `P-high`.
- A team member (`Zalathar`) said they suspect, without full confirmation, that the root cause is where the compiler builds `StableSourceFileId`: it delegates to the weak `Path` hash, and the rest of the compiler treats the result as a unique id.
- Another team member (`jieyouxu`) said changing how `Path::hash` handles component boundaries is probably a separate issue (the thread links #127254), and that making the file-identity requirement explicit at the call site is likely.
- A commenter pointed to a common approach for hashing delimited strings (https://c2sp.org/sequencehash).
- A contributor linked a possibly related PR, #161652.

## Why this was picked

New (same day), tagged as a miscompilation with high priority by the compiler team, and the thread already separates the narrow fix from the broader hash problem.

- **user-advocate**: 35 reactions, 9 comments
- **skeptic**: concrete mechanism with an example and repro scripts, but the severity is partly the reporter's argument
- **builder**: the fix belongs to the Rust compiler team, so this entry records the problem and status

Runner-ups: denoland/deno#37004, Yellow-Dog-Man/Resonite-Issues#7374.

## Honest limits

- Nothing was reproduced. All facts come from the issue thread on the date checked.
- The security impact is the reporter's argument, not a statement from the Rust project. The project's own advisory process, if any, is the authority.
- Priority labels change. Check the issue for current status.
