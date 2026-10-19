# Karpenter does not add nodes when you install a new DaemonSet (karpenter#731)

- Source: https://github.com/kubernetes-sigs/karpenter/issues/731 "Daemonset-driven provisioning". Opened 2023-01-23 (on the older aws/karpenter repo, now in kubernetes-sigs/karpenter), open, 44 comments, 73 reactions on the post, labels kind/feature and v1.x. Last activity 2026-10-19 (the triage bot's stale cycle).
- Project FAQ, read 2026-10-19: https://karpenter.sh/docs/faq/ (entry "When deploying an additional DaemonSet to my cluster, why does Karpenter not scale-up my nodes to support the extra DaemonSet?").
- Docs change from the thread: https://github.com/kubernetes/website/pull/40851 (merged).
- Latest Karpenter release at checking time: v1.14.2 (2026-10-16).

## The problem
Karpenter is a Kubernetes node autoscaler. The reporter had spot nodes already running, then installed a Prometheus chart whose node-exporter DaemonSet could not schedule on two of five nodes ("Too many pods"). Karpenter added no node and logged nothing.

## What the project says
- In 2023 a Karpenter contributor (tzneal) says this is the current expected behavior: Karpenter provisions capacity for the pods and DaemonSets that exist at scheduling time. To make it work for a later DaemonSet, it would have to replace existing nodes the DaemonSet does not fit on.
- Another contributor (ellistarn) recommends giving DaemonSets a high priority so they evict lower-priority pods. The evicted pods then go pending and trigger Karpenter to add nodes. The FAQ today says the same: set a high priority and `preemptionPolicy: PreemptLowerPriority`, and says the maintainers are discussing a consolidation mechanism in this GitHub issue to roll existing capacity when a new DaemonSet is deployed.
- So the maintainers' own docs describe this as a known gap with a workaround, and the issue as the place where the proper fix is discussed.

## What users added
- The reporter first reports that priority classes fixed it, but with the system-level classes, both Karpenter controllers were evicted. He then used a class at half the priority of `system-cluster-critical`. In a later comment, he says the trick did not always work with another DaemonSet. These are his experiences with his setup.
- He shares a Kyverno policy that sets a priority class on DaemonSets and says he sent it to the Kyverno policies repo. I checked that a pull request with a matching title is merged (https://github.com/kyverno/policies/pull/631). I did not read the policy.
- Others say they should not have to set priority classes on every resource, and want Karpenter to choose a bigger node when a DaemonSet does not fit. One comment says the open issue shows the product is not production-ready. A project-adjacent commenter replies that code contributions are welcome.
- 2025: a user suggests a nodepool-level minimum number of pods per node, since small instance types leave few free pod slots after system DaemonSets. Another points to a past AWS issue about why a related metric was removed.
- 2026-02-06: the reporter points at the part of Karpenter's scheduling code he thinks sizes nodes without counting DaemonSet resources. This is his reading of the code, and I did not check it.
- Since then, only triage bot messages and manual "remove-lifecycle stale" replies keep the issue open.

## What can be said
- After nearly four years, this is documented as a limitation, with a documented workaround, and not as a bug. Whether the project plans to build the consolidation mechanism is not stated in the thread. I found no maintainer comment on that since 2024.
- The priority workaround has side effects: a high-priority DaemonSet can evict other pods, and one user's experience shows it can touch the autoscaler's own pods. This is not a recommendation for any priority setting. For a production cluster, read the FAQ and test on a non-production cluster first.

## Honest limits
- I did not run Karpenter or reproduce anything.
- I read the thread and the FAQ, not Karpenter's code, and I did not read the Kyverno policy.
- User reports come from different Karpenter and Kubernetes versions, some years old, and behavior may differ in v1.14.
