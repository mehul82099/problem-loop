# The cache that makes inference 30x slower: Ollama's prompt cache collapses on Vulkan/RADV

- Source issue: https://github.com/ollama/ollama/issues/19201 (open, labeled bug; opened 2026-10-22)
- Project: ollama/ollama (~150k stars)
- Checked: 2026-10-26 23:35 UTC

## Problem
On Ollama 0.40.8 with Vulkan on an AMD RX 6600 XT (Mesa RADV), the second identical request to a loaded model collapses from ~78 tok/s to ~2.6 tok/s - a 29.7x throughput loss - *only* when the bundled llama.cpp host-memory prompt cache is enabled. The reporter's A/B table is admirably clean: cache on, request 1 fast, request 2 crawls; cache off, every request fast (and repeat requests get faster still). The model stays fully GPU-offloaded; nothing crashes. The feature built to speed up repeated prompts does the opposite on this driver/backend combination.

## Why it is interesting
- A perf regression with an unusually sharp trigger: not the hardware (RX 6600 XT / NAVI23), not the backend (Vulkan) alone, but the intersection with prompt caching - and the poisoned state persists until the model is unloaded, which is why the repro requires running twice without `ollama stop` in between. Anyone benchmarking with a single request would never see it.
- The triage dance is textbook: a collaborator fires back with his own environment dump from a different AMD part (a GFX1151 iGPU), implicitly testing whether it reproduces across RADV devices; the reporter answers with four days of read-only host checks (driver, Mesa 25.2.8, PCI IDs) and a full zipped evidence bundle. No maintainer verdict yet, but the bug is being narrowed publicly and methodically.
- Practical takeaway for anyone self-hosting on AMD Vulkan right now: if generation mysteriously crawls on repeat requests, disabling prompt caching is the reported A/B test and temporary relief. That is a workaround surfaced by the issue, not an official recommendation.

## Honest limits
- Single-host report (one RX 6600 XT, Ubuntu 24.04, Mesa 25.2.8); the collaborator's different-GPU test suggests it may not affect all RADV devices - scope is unestablished.
- No maintainer root-cause or fix at check time; numbers are the reporter's own benchmarks, not independently reproduced by us.
- The exact llama.cpp prompt-cache mechanism involved is asserted in the title, not yet confirmed in thread.
- Issue state may have changed since 23:35 UTC.
