# .NET JIT: `p[i] += x` uses a separate address instruction, and a JIT engineer says the "tighter" form may be slower

- Source issue: https://github.com/dotnet/runtime/issues/136228 (open at check time; labels: tenet-performance, area-CodeGen-coreclr; opened 2026-10-21; 4 comments)
- Related open issue named by the reporter: https://github.com/dotnet/runtime/issues/104538 ("JIT: Recognize more addressing modes")
- Project: https://github.com/dotnet/runtime (MIT, 18,375 stars per the API)
- Checked: 2026-10-23 00:55 UTC

## Report
The reporter compares two ways of writing the same update: a compound assignment `p[i] += x` through a pointer, and the written-out form `p[i] = p[i] + x`. They say the C# compiler emits the target address once and duplicates it for the compound form, and that the .NET JIT (x64, on .NET 9.0.20 and an 11.0 release candidate, fully optimized) then computes that address with a separate `lea` instruction and keeps it in a register, while the written-out form folds the address into both the load and the store. They say that in a loop with two such updates per element, the compound form costs two extra `lea`s and two registers per iteration. After a maintainer asked for a case without `unsafe` code, a commenter showed array and span versions with the same pattern in the compiler output. We did not run any of this.

## What the JIT engineers said
- A member first said they were "not entirely sure" that replacing the `lea` with an addressing mode is an obvious performance win, and asked for a repro without unsafe code.
- Another member later wrote a longer answer: the smaller version with the address folded into both instructions "doesn't strictly mean it is faster", and is "likely over twice as slow". Their reasons, in their words and not checked by us: on newer Intel CPUs a feature that predicts store-to-load forwarding does not work when the load or store uses the index part of an address; a `lea` with all three address parts is slower than one with one or two parts; so they estimate about 4 cycles per iteration for the `lea` version against 4 to 9 for the folded one. They advise confirming with CPU throughput modeling tools, and note that hoisting an address computation out of a loop is a core optimization.
- No decision, assignee or fix. The issue is labeled for performance and code generation and remains open.

## What this does not tell you
- The cycle counts are one member's estimate. They are not benchmarks, and CPU generations differ. We did not measure or model anything, and did not check Intel or AMD documentation.
- It does not say the JIT output is optimal. The member only says the "obvious" fix may be slower, and the thread leaves open whether another change would help.
- It is not a reason to rewrite code. Do not change `+=` to a written-out form on the strength of this thread; the reporter's own comparison shows only instruction count, and the engineer says that is not the same as speed.

## Honest limits
- We read the issue and its comments. We did not look at the JIT output ourselves or read the related issue beyond its title and state.
- State may have changed since 00:55 UTC.
