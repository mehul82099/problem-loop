# Rust library team proposal: should `for i in 253u8..` stop at 255 instead of wrapping or panicking?

- Source: https://github.com/rust-lang/libs-team/issues/922 (an "API change proposal"; open at check time; labels: api-change-proposal, needs-fcp, T-libs; opened 2026-10-21; 8 comments)
- Earlier related proposal named in it: https://github.com/rust-lang/libs-team/issues/304 ("Avoid the common mistake of `for x in 0u8..`", open)
- Docs we checked: https://doc.rust-lang.org/stable/core/range/struct.RangeFrom.html and https://doc.rust-lang.org/stable/core/iter/trait.Step.html
- Pull requests cited by a team member: https://github.com/rust-lang/rust/pull/107962 (closed; "Add a doc note about why `Chain` is not `ExactSizeIterator`") and https://github.com/rust-lang/rust/pull/146642 (open; "Implement ExactSizeIterator for `Zip<A, Repeat<B>>`")
- Project: https://github.com/rust-lang/libs-team (Apache-2.0, 186 stars per the API)
- Checked: 2026-10-22 20:50 UTC

## The proposal
The author notes that an open-ended range such as `0u8..` behaves differently depending on the item type and the build profile:
- For integers, with overflow checks on (the usual debug setting) it panics, and with them off (the usual release setting) it wraps to the minimum value. So `for i in 253u8.. { ... }` becomes an endless loop in release builds.
- For `NonZero<u8>` it saturates and repeats the last value forever. For `char`, `Ipv4Addr` and `Ipv6Addr` it panics in both profiles.
- They give examples where this causes a bug: using `zip(0u8..)` to number items when there can be more than 256 items, and a loop that assumes every value stays inside `128u8..`.
They propose that the new range iterator, and the old one if possible, end iteration at the end of the type instead. The proposal says this would be narrowed to the new `std::range::RangeFromIter` type and tied to the move to new range types in a future edition.

## What we verified
The Rust docs say what the proposal says. The `RangeFrom` page says overflow "is allowed to panic, wrap, or saturate", that for primitive integers it follows the overflow-checks profile (panic in debug, wrap in release), and that the new iterator "will only panic after yielding the maximum value when overflow checks are enabled". The `Step` docs say the same and add "The suggested behavior is to panic when debug assertions are enabled, and to wrap or saturate otherwise." We did not run any of the proposal's code samples (no Rust toolchain in our environment).

## What the team and commenters said
- A commenter opposes it: using an open range with `zip` as a more flexible `enumerate()` is common, and an extra end check adds cost. They say the fix should be lints and education, because the range is conceptually infinite. Another notes that wrapping and saturating are cheap on hardware, asks for benchmarks, and points out that Swift's equivalent type traps on overflow (a later comment says a special compiler flag turns that into unchecked behavior).
- A member says accepting it would need a check of every marker trait and size hint that treats this range as infinite, since a `Chain` or `Zip` with it would no longer be unbounded. They cite the two pull requests above for similar reasoning.
- A member says it is "too late", because the docs now state the behavior as a stable guarantee, and that `for i in 0..` is a reasonable way to get a panic in debug on overflow.
- The author answers that the new type is barely used yet and an edition boundary is a limited window to change it. Another commenter suggests a separate `enumerate_with` method instead.
- No decision. The `needs-fcp` label is the team's marker that a formal decision step is pending, as far as we know. We did not check the team's process page for that.

## What this does not tell you
- It does not mean the behavior will change. The thread leans against it, but no team verdict is recorded.
- It does not say the current behavior is a bug: the docs describe it as permitted.
- Our reading of what the docs imply for your code is limited. If your loop could pass the end of a small integer type, an explicit bound is the clear way to write it, which is a general point and not a statement from the thread.

## Honest limits
- We read the proposal and the eight comments. We did not read the linked Zulip discussion or the earlier proposal #304.
- State may have changed since 20:50 UTC.
