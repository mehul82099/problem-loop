# Removing your finalizer with server-side apply can delete the object - and take the deletion policy down with it

**Source:** [kubernetes/kubernetes#143637](https://github.com/kubernetes/kubernetes/issues/143637) (open, labeled `kind/bug`, `sig/api-machinery`, `needs-triage`, ~128.5k stars; no maintainer confirmation yet)

## The problem

Server-side apply's merge rule, as quoted in the report from the Kubernetes docs: items missing from your applied config that no other manager owns are removed. Finalizers are a list, so when a controller applies its config minus its own finalizer, the API server removes the entries **that manager owns** - except the report shows it removes more. If that was the manager's last finalizer, the whole list is treated as that manager's to retract, and the API-server-added `foregroundDeletion` or `orphan` finalizer goes with it. Those two entries are added by the deletion machinery and owned by **no** field manager - which makes them collateral damage of a rule that deletes everything unowned.

The consequences are immediate, because an object with a `deletionTimestamp` and zero finalizers is deleted **in the same request**:

- With `Foreground` propagation, the owner vanishes while a dependent with `blockOwnerDeletion: true` still exists - the ordering the user explicitly asked for is gone.
- With `Orphan`, if the garbage collector has not yet processed the `orphan` finalizer, it will later delete the dependents the user asked to **keep**.

The escape hatches are narrow: if another manager still owns any finalizer, or if the removal is done with a JSON patch instead of apply, the deletion-policy finalizer survives. The repro is a two-ConfigMap `kind` cluster and three kubectl commands, and the report notes this SSA removal pattern is what the closed discussion #111643 ("Finalizer Removal Race Condition", verified to exist) pointed people toward - so the recommended pattern is the one that bites. At publication the issue awaits triage (the only comments are the prow bot's triage notice - tooling - and the reporter's own `/sig` command).

## Why this matters

**Ownership bookkeeping is a security boundary for shared state.** Server-side apply's whole promise is "managers only touch what they own." The unowned `foregroundDeletion` entry fell into the gap between managers - owned by no one, deleted by anyone's cleanup. Any system that partitions authority over a shared list needs an answer for entries owned by the system itself, or "unowned" becomes "up for grabs."

**Finalizers are a mutex with a side channel.** They exist to order destruction: don't delete me until I'm done, don't delete the parent until the children are gone. A bug that silently drops finalizers doesn't corrupt data directly - it corrupts *time*, letting the deletion machinery act before the ordering guarantees are met. The failures (orphaned dependents, deleted survivors) look like garbage-collector bugs and will be misfiled for years.

**The recommended pattern is the blast radius.** This is not an exotic misuse; applying your declarative config without your finalizer is the natural way to say "cleanup done." When the documented path through an API carries a landmine, every correct controller author is a future incident reporter.

## Caveats and limits

- The mechanism (last-owned-finalizer apply removes unowned `foregroundDeletion`/`orphan`) is the reporter's analysis with a runnable repro; the issue is `needs-triage` with no maintainer confirmation at publication. We verified the issue state, labels, the referenced #111643, and repo metadata - not the repro itself.
- Scope: server-side apply removing a manager's last finalizer during a Foreground or Orphan deletion; JSON-patch removal and multi-manager cases are reported unaffected.
- This finding does not advise changes to deletion policies or finalizer handling - follow the issue and SIG api-machinery.

## Hour's takeaway

"Unowned" is not the same as "deletable." Every cleanup rule needs to know whose silence it is interpreting.
