# Rust compiler: two different source paths can collide and swap file contents (rust-lang/rust#164348)

- Source: https://github.com/rust-lang/rust/issues/164348 "miscompilation via engineered StableSourceFileId hash collisions" (open, locked to status updates, labels P-high, I-miscompile, regression-from-stable-to-stable; opened 2026-10-15 by jsnell)
- Library-side discussion, split out: https://github.com/rust-lang/rust/issues/164415 "Should path separators participate in Path/PathBuf `Hash` impl?" (open)
- Pull requests, state checked through the GitHub API on 2026-10-17, none merged:
  - https://github.com/rust-lang/rust/pull/164458 "Avoid stdlib's `impl Hash for Path` for stable hashing" (open, by Zalathar, opened 2026-10-17)
  - https://github.com/rust-lang/rust/pull/164384 "Make `impl Hash for Path` not use custom intermediate hash cycle" (open)
  - https://github.com/rust-lang/rust/pull/161652 "ensure absolute paths hash differently from relative ones" (open)
- Older, closed: https://github.com/rust-lang/rust/pull/127297 (merged 2024-07-07, improved Path hash for prefix collisions) and https://github.com/rust-lang/rust/issues/127254

## The report
The reporter (jsnell) says `rustc` identifies source files by a hash of their path, and the `Path` hash is weak: it ignores path separators and only mixes in component lengths. He says it is easy to build two plausible-looking paths that collide, for example `data/baselines/table.rs` and `database/line/stable.rs`. When they collide, he says `rustc` compiles the second file using the first file's contents. He attached two repro scripts and says he tested 1.99.0 and nightly-2026-10-11. He points out a security angle: code reviewers would not expect file substitution, so two files added in separate commits could hide a backdoor. He proposes keying source file ids on a cryptographic hash of the whole path, unnormalised.

## What others said (attributed)
- Zalathar (marked MEMBER) suspects, "not fully confirmed", that the cause is `StableSourceFileId` using the `Hash` implementation of `FileName`, which goes to `PathBuf`'s hash, while the rest of the compiler treats the id as unique.
- The issue was marked P-critical by the bot, then P-high, after Zulip discussion.
- jieyouxu (MEMBER) said the library fix for `Path` hashing is a separate question, and that the compiler should use its own hasher even if the library one changes. He locked the issue and moved library talk to #164415.
- joshtriplett (MEMBER, writing for the libs team) asked for a fix to `Path` hashing rather than only switching away from it.
- the8472 (MEMBER) argued `Hash` only promises equal keys hash equally, not that different keys never collide, so code that relies on uniqueness is already wrong. He also said it weakens resistance to hash-flooding denial of service if attackers pick the paths.
- teor2345 (MEMBER) noted that the hash-flooding model needs collisions to be unpredictable, and that letting `/a/b` and `/ab` collide makes them predictable.
- Several non-members suggested length-prefixing or hashing a separator between components.

## Where it stands (as of my reading, 2026-10-17 evening IST)
No fix has landed. Three related PRs are open. #164458 is described in the thread as something that might unblock the libs-side change. I did not read any diff. The latest stable release shown by the GitHub API is 1.99.1. The reporter tested 1.99.0, and I do not know whether 1.99.1 changes anything.

## What this means for ordinary users
Per the report, you need two files with engineered names in the same build. This is mostly a concern if you build code from people you do not fully trust, and rely on code review to catch what is in each file. The thread does not recommend any user-side workaround, and I am not suggesting one.

## Honest limits
- I did not run the repro scripts or test any compiler version. Everything about the collision comes from the reporter and the maintainers.
- I did not check whether the example path pair collides.
- The cause is stated as a suspicion by Zalathar, not a confirmed diagnosis.
- Priority labels come from a bot after Zulip talk that I cannot read.
- The thread is active and the status may change quickly.
