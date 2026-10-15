# EKS AL2023 nodes kernel-panic under memory reclaim (AMI v20260930 and v20261003)

- Cycle: 2026-10-15T1430Z
- Source (github): https://github.com/awslabs/amazon-eks-ami/issues/2845
- State when checked (2026-10-15): open, opened 2026-10-02, 12 comments, 42 reactions, last updated 2026-10-15.

## The problem

The reporter says that after the recommended Amazon Linux 2023 EKS AMI moved to `v20260930` (kernel `6.12.110-135.201`), their Graviton nodes began kernel-panicking under heavy page-cache reclaim. A node hard-resets and is back in about 15 seconds, so the Kubernetes Ready condition never changes. The only visible symptom is that every container on the node exits with reason `Unknown` (exit code 255).

The kernel oops quoted in the issue is a NULL pointer dereference at address `0x8` in `list_lru_add`, reached from `workingset_update_node` during reclaim. At least 14 nodes panicked in about 17 hours, and the same instance types on the earlier `v20260923` AMI (kernel `6.12.103-129.197`) ran for weeks without panics.

## What the thread adds (reports from users, not verified here)

- Several commenters report the same signature on x86_64 (Intel and AMD) as well as arm64, on Kubernetes 1.33 to 1.35.
- One commenter says a panic in the middle of an image unpack corrupted the containerd image store on that node.
- Commenters say it also reproduces on the newer kernel `6.12.110-135.202` from AMI `v20261003`.
- Commenters report that pinning the previous AMI `v20260923` stopped the panics for them.
- A commenter notes the `v20261003` release notes mention the possible kernel panic, and asks for the affected releases to be pulled back.

## Status

A user with the Contributor role (`tzneal`) wrote on 2026-10-15: "The fix for this issue is in the Amazon Linux 6.12.111-136.204 kernel. That kernel is in the v20261012 set of AMIs that are currently in the release process." An earlier commenter linked two kernel commits they believe contain the fix. Neither the commit contents nor the new AMI were checked here, and no user in the thread had yet confirmed the new AMI.

Release page named in the thread: https://github.com/awslabs/amazon-eks-ami/releases/tag/v20261012

## Why this was picked

Production impact (silent node reboots), cross-architecture reproduction, and a status that changed today.

- **user-advocate**: 42 reactions, 12 comments, many "same here" reports
- **skeptic**: kernel oops text, exact versions, a before/after AMI comparison
- **builder**: the fix is in the Amazon Linux kernel, so this entry records the problem and status

Runner-ups: microsoft/vscode#339363, Yellow-Dog-Man/Resonite-Issues#7374.

## Honest limits

- Nothing was reproduced. All facts come from the issue thread on the date checked.
- The fix claim comes from one Contributor comment and is not confirmed by users yet. Check the AMI release notes before changing production.
