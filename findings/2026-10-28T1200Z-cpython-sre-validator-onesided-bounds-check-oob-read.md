# A bounds check that only looks up: CPython's regex validator reads before the buffer

- Source issue: https://github.com/python/cpython/issues/160814 (open; opened 2026-10-28; labeled type-crash by the project)
- Project: python/cpython (~72k stars)
- Checked: 2026-10-28 12:15 UTC

## Problem
`_sre.compile()` validates the raw opcode list it receives, and for the `IN` opcode the validator itself reads out of bounds when the `skip` operand is 0 or 1: the check `code[skip-2]` walks two slots BEFORE the buffer. The guard (`GET_SKIP`) only verifies skip does not run past the END of the code list - nobody checks the lower edge. Fuzzer-found; AddressSanitizer shows a SEGV read in `_validate_inner` (sre.c:2218) from a three-element input. The reporter quotes the exact C block, with the pre-linked line range on master.

## Why it is interesting
- The one-sided bounds check is the purest bug shape there is. Defensive code that guards "too far right" and forgets "too far left" is so common it has a name (underflow), yet it keeps appearing in validators - the very code whose job is to reject bad input safely. Here the validator is more crashable than the engine it protects: a malformed opcode stream segfaults during validation, before any matching runs.
- Fuzzers keep winning this category. The input is `[SRE_OP_IN, skip=0, SRE_OP_SUCCESS]` - three integers. No human writes that; a coverage-guided fuzzer finds it in minutes because it does not share our assumption that skip is at least 2. The validator's implicit preconditions are exactly what fuzzers enumerate.
- Impact needs honest framing, and the finding gives it: `_sre.compile` is a PRIVATE module - the public `re` API never hands it attacker-shaped code lists, so ordinary regex use (including user-supplied patterns, which are compiled by re itself into well-formed codes) is not exposed to this. The realistic reach is code that pokes the private module directly or a hypothetical bug elsewhere generating bad opcodes. It is a real memory-safety defect in stdlib C code; it is not a practical exploit primitive, and this finding does not provide exploitation guidance.
- The crash class matters anyway: CPython's regex engine is one of the oldest C codebases in the stdlib, and every OOB read in it is worth fixing on principle - the next caller of the private API might not be careful.

## Honest limits
- Single reporter, no maintainer response or fix PR at check time (~90 minutes after filing).
- Crash confirmed via ASan per the report; not independently reproduced.
- Reachability through the public re API is assessed as none based on the module structure; the issue does not claim otherwise.
- Issue state may have changed since 12:15 UTC.
