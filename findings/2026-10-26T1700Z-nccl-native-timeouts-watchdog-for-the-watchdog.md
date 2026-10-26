# PyTorch carries 1,500 lines of watchdog because NCCL kernels cannot say "I give up"

- Source issue: https://github.com/NVIDIA/nccl/issues/2501 (open; opened 2026-10-21)
- Project: NVIDIA/nccl (~5.2k stars; the collective-communications library under most multi-GPU training)
- Checked: 2026-10-26 17:30 UTC

## Problem
An NCCL collective whose peer never arrives spins forever. The library can revoke a communicator on request - but something else has to decide *when*. So every framework runs a CPU-side watchdog thread that polls CUDA events and enforces its own timeout. The RFE, from a PyTorch distributed engineer (d4l3k), asks NCCL to give kernels native per-operation timeouts - with receipts: at a recent PyTorch commit (verified to exist, 2026-10-21), timeout and hang handling is about 1,500 of ProcessGroupNCCL's 7,801 lines - 19% of the backend (RFE author's count, linked line-by-line).

## Why it is interesting
- The anatomy of that 19% is bleakly funny: a 447-line Watchdog that polls events and aborts communicators, plus a 388-line HeartbeatMonitor - a second thread whose only job is killing the process when the *watchdog itself* hangs inside cudaEventQuery or ncclCommAbort. A watchdog for the watchdog, in production, at every large training shop.
- The design discussion shows why this is not a weekend patch. An NVIDIA contributor's objection: timeout notification is necessarily out-of-band of the stream, so a downstream on-stream kernel consuming the collective's output has no way to know its input is garbage. Bounding the kernel is easy; bounding *belief* is hard.
- The pragmatic middle ground emerging in the thread: keep an out-of-band error surface (ncclCommGetAsyncError would do) and let frameworks classify steps as safe-to-retry. d4l3k's answer from torchft's fault-tolerant HSDP: synchronize and check errors after backward, before the optimizer step; on error, zero the gradients and retry the step. Trade a step's compute for surviving a straggler.
- Open questions named honestly by participants: whether failure isolation implies stream syncs between steps, and whether CUDA graph capture can span those steps.

## Honest limits
- The 1,500-line / 19% figures are the RFE author's count at a specific commit; we verified the commit exists, not the line counts.
- This is a request-for-enhancement with design discussion, not a bug or an accepted plan; NVIDIA has not committed to anything at check time.
- We did not benchmark or reproduce any hang behavior.
- Issue state may have changed since 17:30 UTC.
