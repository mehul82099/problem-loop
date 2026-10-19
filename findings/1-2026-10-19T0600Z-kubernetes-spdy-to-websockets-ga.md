# Kubernetes: kubectl exec, attach and port-forward move from SPDY to WebSockets (KEP-4006)

- Source: https://github.com/kubernetes/enhancements/issues/4006 "Transition from SPDY to WebSockets". Opened 2023-05-15, open, 99 comments, labels include stage/stable, tracked/yes, lead-opted-in. Last updated 2026-10-19.
- The KEP text: https://github.com/kubernetes/enhancements/tree/master/keps/sig-api-machinery/4006-transition-spdy-to-websockets (README and kep.yaml read 2026-10-19; kep.yaml says status "implementable", stage "stable", latest-milestone "v1.38", alpha v1.29, beta v1.31).
- KEP update that sets GA for 1.38: https://github.com/kubernetes/enhancements/pull/6364 (merged, opened 2026-09-14, by the API).
- Docs pull request for the GA: https://github.com/kubernetes/website/pull/58158 "Graduate WebSocket streaming feature gates to Stable in v1.38" (open, opened 2026-10-19).

## What it is
Commands like `kubectl exec`, `kubectl attach` and `kubectl port-forward` (and `kubectl cp`, built on exec) need two-way streaming between kubectl and the API server. The KEP's summary says that today this uses SPDY/3.1 and that, for the leg between kubectl and the API server, it moves to WebSockets.

## Timeline (from the tracking issue, written by the KEP owner, and the KEP file)
- Alpha in v1.29 and beta in v1.31, with pull requests listed for each. The listed stable work includes pull requests in the upstream `gorilla/websocket` library (#978 and #982) and several in kubernetes/kubernetes.
- 2026-06-09: a contributor (jpbetz) says that after talking with the owner they are not progressing the KEP in v1.37 and it can be dropped from that release.
- 2026-09-14: the owner posts that the target is stable (GA) in v1.38. On 2026-09-18 a co-owner adds the lead-opted-in label and the v1.38 milestone.
- The release team's bots and members post routine checklists through September and October: PRR freeze (about September 22 to 23), enhancements freeze (about September 29 to 30), and a docs placeholder-PR deadline (Thursday October 29, asked early by October 22). On 2026-10-19 the owner links the docs pull request above.

## What this means, and does not
- As of 2026-10-19 the issue says the GA is targeted for v1.38, with the KEP updated and a docs PR open. Targeting a release does not guarantee it ships in that release, and I did not check the v1.38 release schedule or whether the code PRs listed as stable have merged. The issue's checkbox for stable code PRs is ticked, and that is the owner's own tracking.
- The change as described is about the kubectl-to-API-server leg. I did not read the compatibility and security sections of the KEP in detail, so I make no claim on how it affects proxies or older clusters. If you run proxies or gateways in front of an API server, read the KEP's own sections on that before upgrading.

## Honest limits
- I did not run any version of kubectl or test either protocol.
- I did not open the individual code pull requests, or the release schedule.
- The thread has 99 comments and most are release team routine. I read the last ten and the issue body, not all of them.
