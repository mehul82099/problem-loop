# Kubernetes: the "Killing" event does not say why a container was killed (kubernetes/kubernetes#81723)

- Source issue: https://github.com/kubernetes/kubernetes/issues/81723 "Give the proper reason for killing pods". Opened 2019-08-21, open, labels "sig/node", "kind/feature", "lifecycle/stale", "needs-triage". 328 reactions on the post, 89 comments from about 46 accounts.
- Docs read 2026-10-19: https://kubernetes.io/docs/tasks/debug/debug-application/determine-reason-pod-failure/ and https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/ .

## The request
The reporter (2019, GKE on Kubernetes 1.12) says the kubelet logs "Killing container ... Need to kill Pod" with the event reason "Killing", which does not tell you whether the container was killed for a failed liveness or readiness probe, for exceeding a memory limit, or because a deployment rolled out or scaled down. He wants to count those cases separately in a monitoring system, such as alerting on OOM kills vs. normal turnover. He wrote in the thread that the kubelet knows the reason but does not surface it in the event.

## What the thread says
- The first responder (2019, a contributor) pointed to the docs page above and a `kubectl get pod ... -o go-template` command reading `.lastState.terminated.message`. The reporter replied that this works for one pod you look at but not for cluster-wide metrics, since the information is only on the live pod object.
- A 2021 commenter makes the same point: once a pod is deleted, the terminated state is gone, so the "Killing" event should carry the reason, or the kubelet should emit a second event for OOM or error exits. A 2020 commenter noted the eviction manager already records an event with a message when it kills a pod, and asked whether the request was for a similar new event.
- A 2022 commenter shared a CronJob that logs pod status every 10 minutes. It is a monitoring workaround from a commenter and I have not tested it. A job that lists pods needs a service account with read access to pods, so check permissions before using anything like it.
- Many comments are "this should be obvious" and +1s. One asks people to use reactions instead.
- Maintainer activity is thin: a member added and removed triage labels in 2025 and wrote that the issue seems not tracked by SIG Node because of a missing triage label. Since then the only replies are the stale bot and people removing the stale label. The latest event, on 2026-10-19, is the bot's standard stale comment again, which is why this issue shows as recently updated. Nobody in the thread, as far as I read, has proposed a design or opened a PR.

## What can be said
- Per the thread and the docs, the reason is visible on a live pod's container status (a terminated state has a reason and exit code). What the issue asks for is a record that survives after the pod is gone and is easy to count.
- I did not verify what the current kubelet emits in its Killing event. The issue text is from 2019, and the thread has no later confirmation either way beyond comments up to 2022 that describe the same behavior.
- This is a sign of how long a well-liked request can sit without triage, with 328 reactions. It is not a sign that the project has decided against it.

## Honest limits
- I did not run a cluster or check the kubelet source.
- I read the human comments in full and skipped most bot posts.
- Reactions show interest, not who runs which Kubernetes version today.
