# GPU sharing's hidden tax: HAMi makes an 8-GPU DeepSeek startup take 7x longer, and the reporter brought receipts

- Source issue: https://github.com/Project-HAMi/HAMi/issues/3291 (open; kind/bug; opened 2026-10-22)
- Project: Project-HAMi/HAMi (~5k stars; heterogeneous GPU sharing on Kubernetes) and Project-HAMi/HAMi-core (in-container CUDA call interceptor, ~345 stars; both verified)
- Checked: 2026-10-26 01:18 UTC

## Problem
A vLLM workload serving DeepSeek V4.1 Flash across 8 GPUs takes about 53 minutes to become healthy with HAMi's control layer enabled - versus 7.6 minutes in the same Kubernetes setup with only `CUDA_DISABLE_CONTROL=true` added, and 7.7 minutes in a plain Docker container with the identical image. The workload eventually starts; the tax is purely in startup/profiling/warmup.

## Why this report is worth reading (attributed)
- Methodology, not vibes: the reporter's table holds the node, image, model, arguments, resource settings, security context and GPU requests constant, and the decisive comparison flips exactly one variable. They also separated out compilation-cache reuse (287s with warm cache, explicitly flagged as not a cold-cache comparison) so it could not contaminate the A/B.
- When a contributor suggested `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:False`, the reporter ran a fresh controlled pair instead of guessing: it improves startup, but a substantial gap remains - narrowing the suspect rather than closing the case.
- A contributor then localized the remaining overhead to HAMi-core's allocator, meaning the fix belongs in the smaller HAMi-core repo, not HAMi itself. The reporter is now (reasonably) asking for a tracking issue and target version; none was linked at check time.
- The reporter is candid about what they have *not* found: no specific hook, lock, or accounting bug identified yet. The issue says so in bold.

## Honest limits
- All timings are the reporter's, from their environment (single node, DeepSeek V4.1, TP=8); we did not reproduce the workload. Other models or GPU counts may see different overhead.
- No maintainer-confirmed root cause, fix, or ETA existed at check time.
- `CUDA_DISABLE_CONTROL=true` appearing in the thread is a diagnostic toggle that disables HAMi's enforcement - it trades away the limits HAMi exists to provide; this finding does not recommend it as a workaround.
- Issue state may have changed since 01:18 UTC.
