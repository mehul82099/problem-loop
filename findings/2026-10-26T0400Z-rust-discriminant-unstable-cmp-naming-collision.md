# Rust's API design knot: how to compare enum discriminants without freezing enum layouts, and why "unstable" is the wrong word for it

- Source issue: https://github.com/rust-lang/libs-team/issues/925 (open; api-change-proposal, I-libs-nominated; opened 2026-10-25)
- Prior art: https://github.com/rust-lang/rust/pull/106418 (verified open since January 2023: "Implement PartialOrd and Ord for Discriminant")
- Checked: 2026-10-26 04:20 UTC

## Problem
Rust's `Discriminant<T>` deliberately does not implement `Ord` - because if it did, the source-code order of your enum variants would silently become part of your crate's public, semver-covered API. Reorder two variants for readability and you have broken downstream consumers. But sometimes you genuinely need *any* consistent order (hand-rolling `Ord` on enums, opportunistic sorting). A new API Change Proposal suggests `Discriminant::unstable_cmp`: an explicitly unstable ordering you can use without a stability promise.

## Why it is interesting
- The naming collision surfaced within hours. A libs team member (kennytm) pointed out that "unstable" already means something specific in std: `sort_unstable`, where "unstable" means equal elements may be reordered - not "may change between compiler versions". Every existing use of the word in std points the other way, so the proposed name would teach the wrong lesson. Another member floated `semvar_unstable_cmp` (semver-unstable) since usage is rare enough to afford a long name; the proposer is open to renaming.
- The deeper design question is three years old: PR #106418 has been open since January 2023 proposing to just implement `Ord` for `Discriminant`, and the libs member on this thread still prefers it. The ACP is effectively a compromise candidate - expose the capability, withhold the guarantee - and the thread is a live example of how Rust weighs power against accidental API commitments.
- Process note: the proposal follows Rust's ACP path with a linked Zulip thread (rustbot auto-opened it), so the decision happens in the open across two venues.

## Honest limits
- Four comments at check time; the ACP is hours old and no team decision or seconding has happened. The rename discussion may be the easy part.
- We did not evaluate the soundness of the proposal itself; this reports the debate, not a verdict.
- Issue state may have changed since 04:20 UTC.
