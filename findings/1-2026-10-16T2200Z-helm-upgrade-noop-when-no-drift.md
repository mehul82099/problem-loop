# Helm: should `helm upgrade` do nothing when there is no drift?

- Source: https://github.com/helm/helm/issues/32624 (open, opened 2026-09-04, last activity 2026-10-16)
- Related: https://github.com/fluxcd/helm-controller/issues/1583 (open, 14 comments, "Drift detection never re-renders templates, so charts using lookup drift out of sync silently")
- Status when written: a design proposal is wanted, no implementation exists in the thread.

## The problem
Per the issue author (matheuscscp), `helm upgrade` writes to the cluster and to Helm storage even when nothing differs. The requested behaviour:

1. Run a dry-run.
2. If any object fails the dry-run, abort the whole upgrade.
3. Only perform the upgrade if the dry-run shows drift.

This is different from `--dry-run`, which only reports. The author says Flux users want it because Flux's Helm drift detection compares the manifest stored in Helm storage with the cluster. It does not re-template the chart, so values that come from `lookup` can change without Flux noticing (this is the title of the linked Flux issue).

## What the thread says (claims attributed, not tested here)
- banjoh (maintainer role not verified here) on 2026-09-18: it makes sense at first glance, but hooks, post-renderers and `lookup` need defined behaviour. He recommends a HIP (Helm Improvement Proposal) first, targeting charts v3 as an experimental feature, and prefers an enum such as `--upgrade-strategy` over a boolean.
- matheuscscp replies that Flux users need `lookup` and post-renderers to work, that he does not know what to do about hooks, and that he would make it the default in Helm 5 and drop the old behaviour in Helm 6. He says Flux's kustomize-controller already works this way.
- lubronzhan offered on 2026-09-24 to write the HIP. matheuscscp said to go ahead and that Flux blocks implementation on merged RFCs.

## The open design questions (our reading of the thread)
| Question | Why it is hard |
|---|---|
| Hooks | A pre-upgrade hook may have side effects, so a "no-op" upgrade could still need to run or skip them. Nobody in the thread proposes an answer. |
| `lookup` | Output depends on live cluster state, so the rendered result can differ between dry-run and real run. |
| Post-renderers | They change the final YAML, so they must run inside the dry-run too. |
| Flag shape | Boolean gate versus an enum for extensibility. Not settled. |
| Release history | If nothing changes, whether a new revision is recorded is the core of the request. |

## Honest limits
- I did not run Helm or reproduce anything. This finding summarises a public discussion.
- I searched the helm/community repo through the GitHub search API for a HIP on this topic and found none. That does not prove none exists, for example in a fork or an unmerged branch.
- Whether lubronzhan has started the HIP is not shown in the thread.
- The Helm 5 and 6 timeline comes from one commenter's wish, not from a maintainer commitment.
- Claims about Flux behaviour are the commenters' own.
