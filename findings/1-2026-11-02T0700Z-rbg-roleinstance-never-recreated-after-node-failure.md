# RBG (SGLang's K8s operator) never recreates a RoleInstance after a node failure - a closed Ready-gate permanently disables the restart policy

**Source:** [sgl-project/rbg#542](https://github.com/sgl-project/rbg/issues/542) (open; maintainer confirmed the diagnosis)

## What happened

When a member Pod of a Ready `RoleInstance` dies because its **node** failed (network partition, kubelet down), the RBG controller creates a same-name replacement Pod but never recreates the `RoleInstance` - even with `restartPolicyConfig.type: RecreateRoleInstanceOnPodRestart`. Worse, the failure self-locks: readiness flips `RoleInstanceReady` to False the moment the node goes NotReady, and `shouldRecreateInstance()` gates on that *current* condition, so by the time the eviction (~5 minutes later) could produce a restart signal, the gate is already closed. The evicted Pod never reaches `Phase == Failed` and the replacement starts with `RestartCount == 0` - the two only triggers the policy checks (`instance_scale.go:614,618` on `origin/main @ 09accf63`, verified to exist) - so the instance sits NotReady forever until someone runs `kubectl delete roleinstance`. And the replacement Pod *cannot* fix it: multi-rank inference runtimes agree on a one-shot membership at startup (NCCL `ncclCommInitRank` / TCPStore rendezvous), so a new same-rank process cannot rejoin. The reporter backs that with verified upstream evidence: vLLM documents that one dead DP rank blocks the surviving ranks' all2all indefinitely ([vllm#44428](https://github.com/vllm-project/vllm/issues/44428), quote confirmed in the issue body), vLLM's per-rank rejoin RFC was closed NOT_PLANNED ([vllm#30112](https://github.com/vllm-project/vllm/issues/30112), verified), and SGLang's only rejoin path ([sglang#15771](https://github.com/sgl-project/sglang/pull/15771), verified closed) requires relaunching the pod with `--elastic-ep-rejoin`, which RBG's same-template replacement does not do. A maintainer (association COLLABORATOR) went through the code on the same commit and agreed the two problems stack: the stability gate reads current Ready, and deleted-pod replacement produces no restart signal. The report also clears gang scheduling of blame on current main.

## Who this bites

- Anyone running multi-rank LLM inference (vLLM/SGLang) on Kubernetes through RBG: a single node failure takes an instance down permanently and silently - the controller keeps a zombie replacement that can never rejoin the NCCL group, and the restart policy the operator configured never fires.
- On-call diagnosis is nasty because each individual piece looks correct: the Pod was replaced, the policy exists, the instance is merely NotReady - with no signal that the gate closed five minutes before the replacement was even created.

## Limits

- Single-source report plus one confirming maintainer comment (reporter association NONE); I did not run the reproduction. Root-cause line numbers are as-quoted against main @ 09accf63 (commit verified to exist).
- Repo is small (~313 stars) but sits in the SGLang project; the blast radius is deployments that adopted RBG, not SGLang generally.
- No fix PR yet; the maintainer comment agrees with the diagnosis but the design decision (runtime-orchestrated recovery vs RBG rebuilding the group) is open.
