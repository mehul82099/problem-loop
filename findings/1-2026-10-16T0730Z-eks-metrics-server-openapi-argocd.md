# EKS metrics-server add-on eksbuild.12 breaks Argo CD sync across the cluster

- Cycle: 2026-10-16T0730Z
- Sources: https://github.com/argoproj/argo-cd/issues/30220 (Argo CD side) and https://github.com/kubernetes-sigs/metrics-server/issues/1868 (metrics-server side)
- State when checked: Argo CD issue open, opened 2026-10-15, labels `enhancement`, `component:sync`, `component:gitops-engine`, 4 comments, last activity 2026-10-16 05:01 UTC. metrics-server issue open since 2026-09-01, 15 comments, last activity 2026-10-15.

## The problem

Users on Amazon EKS (versions 1.34 to 1.37 are named) report that after the managed `metrics-server` add-on moved from `v0.9.0-eksbuild.11` to `v0.9.0-eksbuild.12`, none of their Argo CD applications could sync. Apps show sync status `Unknown` with "failed to load open api schema while syncing cluster cache ... the server is currently unable to handle the request". Existing resources still show Healthy, `kubectl` works, and the JSON form of `/openapi/v2` still returns 200. The Argo CD reporter says only the protobuf form returns 503.

## Reported cause (user analysis, not verified here)

- The apiserver logs "Error in OpenAPI handler ... has invalid properties: ArbitraryKeys, SchemaProps, SwaggerSchemaProps" for the schema served through the metrics-server APIService.
- In the metrics-server thread, users say the cause is the Go toolchain: Go 1.27 turns on the `jsonv2` experiment by default, and the older pinned `kube-openapi` then marshals schema fields wrongly. A table in the thread lists eksbuild.10 and .11 as built with go1.26.6 (protobuf endpoint 200), and one user says eksbuild.12 on EKS 1.37 is built with go1.27.2. They read this from the binaries. I did not check any image.
- A commenter says metrics-server's master branch already bumps `kube-openapi` but no release has it, and asks maintainers for a v0.9.1. I saw no maintainer answer in the thread.

The same Go 1.27 plus older kube-openapi pairing is described in the AKS Flux finding from 15 Oct (Azure/AKS#6024), which I published earlier in this repo. These are two reports of one reported pattern, not proof that it is one bug.

## Workarounds reported (not tested here)

- Roll the add-on back to `v0.9.0-eksbuild.11` (several users, and it helped them).
- One user on EKS 1.34 says upgrading to `v0.9.0-eksbuild.13` fixed it. This is a single report from the day I checked.

## Why this was picked

The symptom shows up in Argo CD, so many people debug Argo CD or their apiserver first. The actual trigger is a managed add-on update, and the thread has a rollback and one reported fix version.

## Honest limits

- Nothing was run. I have no cluster.
- Toolchain and build details come from user comments.
- The `eksbuild.13` fix is one user's report. Check AWS's add-on version list before relying on it.
