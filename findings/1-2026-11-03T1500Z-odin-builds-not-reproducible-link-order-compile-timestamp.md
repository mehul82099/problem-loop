# Odin: builds are not reproducible - same source built twice gives different binaries (separate-module link order, wall-clock ODIN_COMPILE_TIMESTAMP in debug info)

**Source:** [odin-lang/Odin#8182](https://github.com/odin-lang/Odin/issues/8182) - opened 2026-11-03 by pattystarman (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

Building the same hello-world source three times in a row with the same compiler and flags produces three different binaries in most modes. On master `e28e60a` the reporter measured: `-o:speed` identical, `-o:none` (separate modules, the default at that level) different every time, `-o:none -use-single-module` identical, `-debug -use-single-module` different every time. On the `dev-2026-09-nightly` build every mode differed, including `-o:speed`.

Two distinct causes, per the reporter:

1. **Separate-module builds link in a varying order.** The symbol set is identical but symbol order in the binary changes per build (`nm -n`: 530 lines differ for hello-world). It is not thread scheduling: `-thread-count:1` does not stabilize it, while `-use-single-module` does.
2. **Debug builds embed the wall-clock build time.** `ODIN_COMPILE_TIMESTAMP` is computed from the current time and lands as a `DW_AT_const_value` in `.debug_info` even when the program never references it, and there is no way to pin it - no `SOURCE_DATE_EPOCH` support.

The expected behavior: same source + same compiler + same flags = byte-identical output, so a released binary can be rebuilt and hash-compared; where a timestamp must be embedded, a standard pin like `SOURCE_DATE_EPOCH` should exist. The issue includes full repro commands (build loop + sha256sum, `nm -n`, `readelf --debug-dump=info`) and the measured hashes.

## Verification (checked during this finding)

- Master commit `e28e60a` exists (2026-10-05). In `src/checker.cpp` at that commit, `odin_compile_timestamp()` (lines 1181-1186) computes the value from `gb_utc_time_now()` - the wall clock - and line 1447 registers it as a global constant: `add_global_constant("ODIN_COMPILE_TIMESTAMP", t_untyped_integer, exact_value_i64(odin_compile_timestamp()));`. `checker.cpp` contains no reference to `SOURCE_DATE_EPOCH`; the stronger repo-wide claim of "no way to pin it" is the reporter's.
- The varying-link-order cause is supported by the reporter's `nm -n` diff and the `-thread-count:1` control, but was not reproduced here; I did not independently identify where module link order is decided in the compiler source.
- A maintainer has responded: Kelimion (GitHub association: MEMBER) called it a "useful notion" and said they will consider it for the Odin 2027 build-script pass (referencing discussion #7100). That is an acknowledgment, not a committed fix.

## Limits

- The hash table, `nm` diff counts (530 lines), and CPU-time measurements are the reporter's data from Debian 13 x86-64 with LLVM 20.1.8; not independently re-run.
- Only the timestamp cause is source-verified here (lines cited above); the link-order cause rests on the reporter's binary diffs and controls.
- Reproducibility of release binaries also depends on toolchain and flags matching, which is out of scope of the issue.
- Nightly behavior (all modes differ, unstable compiler-numbered symbol names) is reported as already improved on master for the naming part; only master behavior is anchor-checked here.

## Sources

- Issue: <https://github.com/odin-lang/Odin/issues/8182>
- checker.cpp at e28e60a (odin_compile_timestamp, registration): <https://github.com/odin-lang/Odin/blob/e28e60a/src/checker.cpp>
- Maintainer-referenced build-script discussion: <https://github.com/odin-lang/Odin/discussions/7100>
