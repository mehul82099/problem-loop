# rustfmt: formatting `cfg_select!` can silently delete comments (nightly only)

- Source issue: https://github.com/rust-lang/rustfmt/issues/7209 (open at check time; labels include "C-bug", "A-comments", "regression-from-nightly-to-nightly"; opened 2026-10-23 06:21 UTC; 7 comments)
- Tracking issue the maintainer cites: https://github.com/rust-lang/rustfmt/issues/7191 ("cfg_select! follow-ups to #7183", open; the maintainer says this report is its "case 2")
- Related: https://github.com/rust-lang/rust/pull/160998 (merged: restrict cfg_select! formatting to the nightly release channel), https://github.com/rust-lang/rust/issues/160944 (closed), https://github.com/rust-lang/rustfmt/issues/7045 (closed, cfg_select! broken in expr position)
- Project: https://github.com/rust-lang/rustfmt (Apache-2.0, about 7k stars per the API)
- Checked: 2026-10-23 14:45 UTC

## Problem
The reporter (a Rust language team member) shows a real `cfg_select!` block from libc-adjacent code where running rustfmt deletes comments, including a comment explaining platform behavior. Comment loss matters more than a formatting mistake because it is silent: nothing fails to compile, and the change can be missed in a diff.

## What the thread says
- A rustfmt maintainer confirmed this is a known case in the follow-up tracker and said they will look at it. No fix PR was linked when we checked.
- The exchange clarified scope: `cfg_select!` formatting is restricted to the nightly release channel (via merged PR rust-lang/rust#160998), because the style diverged from the style guide; there is no `#[feature]`-style gate for individual macros. The reporter initially thought the label "X-impacts-nightly-gated" was wrong because it reproduces with default settings; the maintainer's answer is that nightly-the-channel is what enables it, not any unstable option.
- The reporter apologized for initially calling the merge decision out too harshly once the nightly-only situation was clear, and both sides are discussing how nightly-only formatting should be handled going forward.

## What this does not tell you
- Stable rustfmt is not affected, per the maintainers' gating description and the merged restriction PR. If you run stable rustfmt, this does not apply to you.
- We did not reproduce the comment loss ourselves; the reproducer is the reporter's code block in the issue.
- There is no timeline for a fix.

## Honest limits
- We read the issue and verified each cited PR and issue by API. We ran no formatting.
- Issue state may have changed since 14:45 UTC.
