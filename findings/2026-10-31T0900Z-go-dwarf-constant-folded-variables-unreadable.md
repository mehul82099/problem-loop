# Go's compiler throws away debug info for every constant-folded variable - and mem2reg makes it common

**Source:** [golang/go#82737](https://github.com/golang/go/issues/82737) (open, `NeedsInvestigation`, `compiler/runtime`; filed by a Go contributor; related issue and CL verified)

## What happened

When Go's optimizer constant-folds a local variable, the variable gets no register or stack slot - so the compiler emits either no DWARF debug entry for it at all, or one whose location covers nothing. Debuggers then report the variable as unreadable, and if an inlined function's body folds away completely, its `DW_TAG_inlined_subroutine` and line-table entries vanish too: you cannot set a breakpoint on lines that "compiled away". The reporter (JunyangShao, author_association CONTRIBUTOR) demonstrates with a 15-line program: with optimizations on, `a` and `b` get an empty 0-byte `DW_AT_location`, the intermediate `z` gets no DIE, and only one of two identical inlines gets an inline record.

Two clarifications from the issue make it more than a corner case. First, it is **not** caused by the new mem2reg pass: the same empty locations appear with `ssa/mem2reg/off=1`, for ordinary SSA-able locals. Second, mem2reg makes it much more common, because address-taken non-escaping locals now fold too: in the mem2reg variant, `main.initialize` emits no instructions at all, so its inlined-subroutine record disappears and Delve's own `TestInlineBreakpoint` fails with "could not find statement at testinline.go:17". That test failure comes via the predecessor issue [golang/go#82076](https://github.com/golang/go/issues/82076) (open, verified: "variables promoted by mem2reg lose their debug locations").

## The proposal

DWARF already has a representation for this: `DW_AT_const_value`, or `DW_OP_implicit_value` / `DW_OP_stack_value` loclist entries - the value is a compile-time constant, so the debugger can just *know* it without a location. The issue proposes emitting constant locations over the PC ranges where the value is known, and links the related change [CL 797380](https://go.dev/cl/797380) ("cmd/compile: mark mem2reg ssa values with their src names", mentioned by gopherbot - tooling, not a fix). The reporter pinged @golang/compiler; no maintainer assessment yet, NeedsInvestigation.

## Who this bites

- Anyone debugging optimized Go binaries (the default for `go build`): folded locals read as unreadable and inlined frames go missing, which misleads exactly when you are single-stepping optimized production code.
- Delve and other debugger maintainers, who get the bug reports ("variable doesn't exist") that are really compiler debug-info gaps.

## Limits

- The DWARF dumps and the Delve test failure are the reporter's evidence; I verified the issue anchors, the predecessor issue #82076, and the CL link, but did not compile the reproducer or inspect DWARF output myself (repo ~139k stars).
- This is a diagnostic-quality issue with a concrete proposal, not a correctness bug: programs run fine, they just debug poorly. The issue is one day old with no maintainer response, so scope and priority are unassessed.
- Whether emitting `DW_AT_const_value` for folded variables has binary-size or debugger-compatibility costs is not discussed in the issue yet.
