# A well-formed, too-short answer: HPX's parallel `set_union` silently drops elements - and exhaustive fuzzing says it's the chunking, not the data

**Source:** [TheHPXProject/hpx#7935](https://github.com/TheHPXProject/hpx/issues/7935) (open, ~2.9k stars; reporter is a contributor and fuzzed the bug exhaustively)

## The problem

Run `hpx::set_union` (or `hpx::ranges::set_union`, and the `set_symmetric_difference` counterparts) with a parallel execution policy and the output can be **silently missing elements from the second input range** - a well-formed but too-short sequence, no error, no warning. The trigger the reporter isolated: a whole chunk of the first range consists of a single repeated value, and the second range contains elements smaller than that value. `set_intersection` and `set_difference` - the operations that never emit elements coming only from the second range - are unaffected, which is how the reporter pinned the defect to the emit path.

The credibility detail is the method: the reporter verified against sequential results by **exhaustive fuzzing of the chunking logic** - sorted inputs over a 1-4-symbol alphabet, lengths under 25, 1-8 chunks. Out of 1,182,148 configurations, 7,276 produced wrong values, all in `set_union` or `set_symmetric_difference`, none in the other two. Not a flaky failure: a deterministic logic bug in how parallel chunk boundaries handle the second range. They also flagged it as distinct from the same-day [#7932](https://github.com/TheHPXProject/hpx/issues/7932) (open), where the parallel ranges set operations return wrong `in1`/`in2` iterators - this family of algorithms had a bad week.

A fix exists: [PR #7844](https://github.com/TheHPXProject/hpx/pull/7844) (open, unmerged, from another contributor) makes `set_operation()` decide whether a chunk covers the start of the first range from `start1` *after* walking it back over equal elements, with two regression tests. No maintainer verdict on the PR or the issue at publication.

## Why this matters

**Silent wrong results are the worst bug class, and parallelization is their factory.** A crash gets a bug report; a missing element gets a subtly wrong join, a dedup that isn't, a merged index missing keys - and everything downstream trusts the output because it *looks* sorted and valid. The parallel set algorithms promise "same result, faster"; this bug kept the promise for the output's shape and broke it for its contents.

**Chunk-boundary logic is where parallel rewrites go to die.** Split a sorted range into chunks, run the sequential algorithm per chunk, merge - and every "obvious" boundary decision (which chunk owns the equal elements? where does the first range actually start within this chunk?) is a chance to double-count or skip. The 7,276 failing configurations cluster on exactly the pattern a reviewer would wave through: runs of one repeated value aligning with chunk edges.

**Exhaustive fuzzing beat anecdote here, and it's reproducible.** Instead of "sometimes the result looks short," the reporter produced a complete map of when the bug fires: only these two operations, only this value pattern. That's a fix-target, a regression-test suite, and a proof the fix is complete, all in one. Notably, the fix PR *predates* the issue by a week - the bug was patched before it was formally reported, and the report now gives the PR its missing justification.

## Caveats and limits

- The failing configurations, counts, and the "distinct from #7932" scoping are the reporter's (a contributor) fuzz results on HPX master at commit 2152675, Linux/GCC 13; we did not re-run the fuzzing. The bug's existence is corroborated by the pre-existing fix PR, which targets the same skip behavior.
- The only comment on the issue is CodeRabbit's auto-generated planner output - tooling, not maintainer triage. No maintainer has confirmed or labeled the issue.
- Affected scope per the report: `set_union` and `set_symmetric_difference` with parallel execution policies. Sequential runs and the other two operations are not claimed affected.
- This finding reports the issue and the pending fix. It does not advise any particular workaround; follow the issue and the PR.

## Hour's takeaway

"Same answer, just parallel" is a theorem, not a setting. If you haven't fuzzed the chunk boundaries against the sequential oracle, your parallel algorithm is an unproven conjecture shipping in a library - and its failure mode is an answer nobody questions.
