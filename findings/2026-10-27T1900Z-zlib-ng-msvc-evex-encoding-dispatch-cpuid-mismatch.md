# The CPU said AVX-VNNI, the compiler heard AVX-512: a one-byte prefix crash in zlib-ng

- Source issue: https://github.com/zlib-ng/zlib-ng/issues/2485 (open; opened 2026-10-27)
- Verified: fix PR zlib-ng/zlib-ng#2486 (open); upstream MSVC report linked by maintainer
- Project: zlib-ng/zlib-ng (~2.1k stars; the actively maintained zlib fork)
- Checked: 2026-10-27 19:10 UTC

## Problem
Build zlib-ng with the MSVC 14.53 toolset and `adler32_avx2_vnni()` comes out containing EVEX-encoded VPDPBUSD instructions. The runtime dispatcher picks that function whenever CPUID says the CPU has AVX-VNNI - but the EVEX 256-bit encoding of VPDPBUSD requires AVX512-VNNI plus AVX512VL. So a CPU that legitimately reports AVX2 + AVX-VNNI but no AVX-512 gets dispatched into a function whose first VPDPBUSD raises #UD / EXCEPTION_ILLEGAL_INSTRUCTION. The reporter pinpoints it down to the byte: the emitted instruction starts with prefix 0x62 (EVEX) when it should start with 0xC4 (VEX).

## Why it is interesting
- The whole bug lives in one byte of instruction encoding. AVX-VNNI (the VEX form, available on newer mainstream CPUs) and AVX512-VNNI (the EVEX form) compute the same thing, and MSVC 14.53 silently picks the encoding for a CPU the dispatch logic never asked about. Dispatch says one ISA, the binary contains another, and the CPU is the only honest party in the room.
- It is the third recent instance of a recognizable pattern: feature detection checks a CPUID bit, codegen assumes a superset. zlib-ng's dispatcher did exactly what it was designed to do; the compiler moved the floor under it. Any project doing runtime SIMD dispatch with a new MSVC toolset is exposed to the same class of surprise until the compiler bug (linked upstream at Microsoft's developer community) is fixed.
- The fix shows real craft, not just a workaround. Maintainer nmoinvaz links the upstream MSVC report, then within about an hour opens PR #2486: switch the function to MSVC's VEX intrinsic `_mm256_dpbusd_avx_epi32` and add a CMake probe so older toolsets simply build without AVX2-VNNI. No "disable the feature everywhere" - the optimization stays for toolchains that can encode it correctly.
- Verification culture on display: the maintainer tells the contributor exactly how to check the fix (`dumpbin /disasm` - every vpdpbusd should now start with C4, not 62), and the contributor confirms the encoding change within the hour. The one honest loose end: the original crash came from a downstream user's machine, so real-world crash confirmation is still pending.

## Honest limits
- The crash itself was reported downstream; the reporter and fix-verifier have not confirmed the fix on the originally affected machine.
- Affected scope is "built with MSVC 14.53 toolset AND run on AVX-VNNI-without-AVX512 CPUs"; other toolchains are not implicated in the thread.
- PR #2486 was open and unmerged at check time.
- Issue state may have changed since 19:10 UTC.
