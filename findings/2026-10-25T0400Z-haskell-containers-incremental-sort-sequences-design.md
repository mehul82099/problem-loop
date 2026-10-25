# Haskell's containers library is designing an incremental sort for Seq - live, in the open

- Source issue: https://github.com/haskell/containers/issues/1266 (open; labels feature-request + Seq; opened 2026-10-21 20:55 UTC)
- Project: https://github.com/haskell/containers (Haskell's core containers library)
- Checked: 2026-10-25 04:05 UTC

## Problem
`Data.Sequence` sorts eagerly: you pay O(n log n) even if you only need the smallest k elements. Core contributor treeowl opened this issue to design `incSort`, an incremental sort with two target properties: forcing the full result costs O(n log n), but forcing any particular element costs only O(n).

## The design conversation (all attributed)
- treeowl's plan: partition recursively with median-of-medians or QuickSelect to build a 2-3 tree, then convert it into a 2-3 finger tree. Each level is O(n), so the whole thing is O(n log n), but building just the spine needed for one element stays O(n). He asks Zemyla to check his math, and flags open questions - including whether intermediate partition results can be reused without degrading the bounds, with a sketch using a `Parted a = FingerTree (Seq a)` annotation trick.
- Zemyla had a different approach (lazy/strict min-heap states, O(n lg k) for the k-th element) and notes the finger-tree version could do better: O(n lg(min(k, n-k))).
- The discussion pulled in a 2006 ALENEX paper on optimal incremental sorting (linked in the thread); treeowl is now "convinced that my original (some years ago) method is actually optimal" and suspects his finger tree corresponds to the stack in that paper, while noting median-of-medians measured "ridiculously slow" in his old experiments.
- Practical wrinkles surface late: Zemyla points out randomness can't be used without depending on the `random` module (a real constraint for a boot library); treeowl suggests parameterizing the needed functions instead, and confirms the sort can be made stable.
- meooow25 notes a prior issue exists - #143, "Can we make Data.Sequence.sort incremental and/or faster?" (verified: opened March 2015, closed) - "but this seems to have more information now." The idea has been wanted for over a decade; this is the first concrete plan. The work grew out of #1261 (verified: "Strict prefix/lazy suffix for states?", closed).

## What this does not tell you
- No code or PR exists yet; treeowl says he will try to reproduce his old experimental method "this week", and admits the polymorphic-recursive implementation will be hard.
- The claimed bounds are the participants' in-thread analysis, not peer-reviewed or benchmarked here.

## Honest limits
- We read the issue and all twelve comments and verified the two cross-referenced issues via the GitHub API. We did not check the algorithm analysis ourselves or fetch the linked paper.
- Issue state may have changed since 04:05 UTC.
