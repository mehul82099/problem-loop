# Passing the parcel to someone who's also leaving: Elasticsearch reindex relocation can hand a task to a node that is shutting down too

**Source:** [elastic/elasticsearch#164014](https://github.com/elastic/elasticsearch/issues/164014) (open, ~78k stars, labeled `>bug` / `Team:Distributed`; filed by an Elastic engineer with a three-window race analysis, affects 9.5+)

## The problem

When an Elasticsearch node running a reindex task is told to shut down, it relocates the task to another node. The picker tries to avoid nodes that are leaving - it filters out any node with a shutdown marker in the cluster state. The reporter, an Elastic engineer, lists three ways that filter still loses the race:

1. **The cached pick goes stale.** For an auto-sliced reindex, the target node is chosen once and cached while the other slices finish - up to a full round of search and bulk per slice, times N-1 slices. The target can be marked for shutdown *after* the pick but *before* the hand-off, and the stale choice is used anyway.
2. **The target is marked mid-hand-off.** The relocation lands on a node that began shutting down after the check.
3. **The source decides from an out-of-date cluster state.** Distributed systems classic: the map was old the moment it was read.

Whether the reindex survives then depends on fine timing: if the resume request arrives while the target's shutdown preparation is still running, the target relocates the task onward; if it arrives just after, the hand-off "succeeds" - and the reindex dies when the target goes down. The reporter flags the exact production scenario that maximizes the odds: vertical scaling, where you remove a whole generation of old nodes at once, so shutdowns are numerous and correlated - precisely when relocation traffic is highest. The engineer's own irony, noted in the issue: the target was deliberately picked early and cached *to avoid a race condition*, and the cache created the widest window of the three.

## Why this matters

**Check-then-act is a lie across a network delay.** "Is that node alive?" is only meaningful at the moment you use the answer. Filtering a candidate list at pick time and acting at hand-off time splits the question from the act by a window that, with auto-slicing, stretches across many slow slices. The fix the reporter sketches is the textbook one: re-validate at the moment of commitment, or make the receiver refuse and force a re-pick.

**Liveness decisions should never be cached.** A capability, an address, a health verdict - anything that can change on the other side of the wire is a lease, not a fact. The early-pick optimization traded a small race for a large one, because caching feels like reducing variability while it actually just defers staleness to a busier moment.

**Correlated failure is when relocation logic earns its keep.** A single node leaving is the easy case the filter handles. The design scenario - mass shutdown during a resize - is exactly when pick-avoidance must be airtight, and exactly when a cached pick has the most time to go stale.

## Caveats and limits

- The race analysis, the three windows, and the vertical-scaling scenario are the reporter's account; the reporter is an Elastic member (GitHub association: MEMBER), which grounds but does not settle the diagnosis. A project bot's automated code analysis corroborates the caching root cause, and we attribute that to tooling, not maintainer review.
- No fix is merged as of publication; the reporter's proposed directions (re-check at hand-off, receiver-side refusal, delayed picking) are explicitly tentative.
- The reproduction requires a shutdown-dense operation plus a long (likely auto-sliced) reindex; ordinary rolling restarts are not claimed to be affected.
- This finding reports the issue. It does not advise operational changes; follow the issue before altering reindex or scaling procedures.

## Hour's takeaway

A cached answer to a question that keeps changing is not an optimization - it is a bet that the world will hold still until you're done. In distributed systems the world never holds still, and the busier the moment, the more you needed it to.
