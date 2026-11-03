# tilelang: the nvrtc execution backend corrupts CUDA graph capture in multi-context (multi-GPU, one context per thread) processes

**Source:** [tile-ai/tilelang#3775](https://github.com/tile-ai/tilelang/issues/3775) - opened 2026-11-03 by zin39 (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

In an sglang-style deployment (single process, one worker thread per GPU, one CUDA context each, 2x H200, decode CUDA-graph capture), forcing `TILELANG_EXECUTION_BACKEND=nvrtc` causes non-deterministic corruption during graph capture. The corruption surfaces *after* the tilelang launches, in unrelated downstream kernels, with three different first-failure sites across three byte-identical config runs: a `cudaError700` invalid TMA descriptor handle, `CUBLAS_STATUS_EXECUTION_FAILED` from a plain bf16 `cublasGemmEx`, and an illegal memory access in an unrelated host-JIT'd elementwise kernel. All occurred at decode capture (~100s after boot).

The differential is clean, per the reporter: `/proc/environ` censuses of every boot show the failing and passing runs differ by exactly the one env var; the default `auto` -> `tvm_ffi` backend passes repeatedly under the identical config, including a run carrying every other env var from the failing recipe. The failure is config-deterministic (every nvrtc run at this config died at decode capture) but failure-site non-deterministic (the "messenger lottery" above).

## Suspects (reporter's source reading, verified at the pinned version)

The reporter ran tilelang 0.1.12 from pip and lists capture-hostile differences in the nvrtc launch path. At tag `v0.1.12` these check out:

- `jit/adapter/nvrtc/adapter.py:265-267`: `stream=None` resolves to `torch.cuda.current_stream().cuda_stream` - the **no-device-arg** form, which in a multi-context process can bind another device's stream depending on which thread runs the call.
- `jit/adapter/nvrtc/wrapper.py`: driver-API launches via `cuLaunchKernelEx` (line 208) with `cuKernelSetAttribute` (185); context-wide L2 state mutation on the launch path - `cuCtxResetPersistingL2Cache()` (165), `cuCtxSetLimit(CU_LIMIT_PERSISTING_L2_CACHE_SIZE, ...)` (137/169), `cuStreamSetAttribute(..., CU_LAUNCH_ATTRIBUTE_ACCESS_POLICY_WINDOW, ...)` (154/161) - state that stream capture snapshots. `programmaticStreamSerializationAllowed=1` (PDL) is set at 177-178, but the reporter notes PDL also rides the generic wrapper, so it is not the differential.

The reporter's reasoning: under capture, these implicate CUfunction-to-context binding discipline (a CUfunction is context-specific; a per-device cached handle can silently bind the wrong context under thread scheduling), which single-GPU testing never exercises.

## Status and a likely partial fix

In a follow-up comment the reporter notes their 0.1.12 pin predates PR [#3359](https://github.com/tile-ai/tilelang/pull/3359) ("Honor tensor-device streams in NVRTC and CuTeDSL", merged 2026-10-27 - verified), which replaced the no-device-arg `current_stream()` with `current_stream(first_tensor.device)`. On current `main` the adapter indeed resolves `torch.cuda.current_stream(device).cuda_stream`, consistent with that fix. The reporter has not re-tested on a post-#3359 build (the default tvm_ffi backend is capture-safe for them), so whether the graph-capture corruption is fully resolved - including the context-wide L2 state mutations, which #3359 did not touch - is open.

Workaround per the reporter: do not set `TILELANG_EXECUTION_BACKEND=nvrtc` in multi-context CUDA-graph-capture deployments; the default `auto` -> `tvm_ffi` is capture-safe in their environment. Their own nvrtc setting was a leftover speculative workaround for an older issue.

## Limits

- Not reproduced here - this needs a 2-GPU serving stack; all failure observations are the reporter's. The env-var differential and repeated control runs are their evidence, not independently confirmed.
- The suspect code paths are verified at tag v0.1.12 (the version that exhibited the failure); main has since refactored the adapter.
- The reporter's association is NONE, though the report includes server logs/census methodology and offers full logs. The only other comment is a CodeRabbit automation plan (tooling, not maintainer triage).
- Whether #3359 fixes the capture corruption end-to-end, or only the wrong-stream part, is unknown to both the reporter and this finding.

## Sources

- Issue: <https://github.com/tile-ai/tilelang/issues/3775>
- nvrtc adapter at v0.1.12: <https://github.com/tile-ai/tilelang/blob/v0.1.12/tilelang/jit/adapter/nvrtc/adapter.py>
- nvrtc wrapper at v0.1.12: <https://github.com/tile-ai/tilelang/blob/v0.1.12/tilelang/jit/adapter/nvrtc/wrapper.py>
- Possibly-related fix: <https://github.com/tile-ai/tilelang/pull/3359>
