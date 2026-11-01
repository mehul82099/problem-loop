# bun:test: a failing matcher on a huge value can silently **pass** - the test runner turns an assertion failure into green while building the error message

**Source:** [oven-sh/bun#47606](https://github.com/oven-sh/bun/issues/47606) (open, hours old; release tags verified)

## What happened

A matcher that should fail on a value whose printed form exceeds JavaScript's maximum string length (~2.1 GB of text) does not fail cleanly. On Bun 1.4.2 (verified: [bun-v1.4.2](https://github.com/oven-sh/bun/releases/tag/bun-v1.4.2), Sep 5), `expect(value).toBeNull()` on such a value **returns without throwing** after ~40 seconds - the assertion silently passes, because building the failure message itself hits "Cannot create a string longer than 2147483647 characters" and the error is swallowed. On 1.4.4 (verified: [bun-v1.4.4](https://github.com/oven-sh/bun/releases/tag/bun-v1.4.4), Oct 22) it does throw - but after ~38 seconds, with "Error: The error message exceeds the maximum string length", which says nothing about the actual assertion. Neither behavior exists for smaller values: at ~0.5 GB printed the matcher fails immediately and correctly.

The false pass is the nightmare scenario for a test runner: the suite goes green on an assertion that evaluated to false. The reporter's real-world trigger is ordinary: a happy-dom `HTMLElement` from a rendered React tree prints its entire reachable object graph (gigabytes), so `expect(screen.queryByRole('dialog')).toBeNull()` on an element that *exists* passed silently on 1.4.2 - a UI regression test reporting success while the bug it guards is present.

Second defect in the same report: deep-equality matchers ignore `Bun.inspect.custom`. A class defining that hook gets its short form in `toBeNull`/`toBe` messages, but `toEqual`/`toStrictEqual`/`toMatchObject` walk the raw object anyway - on a happy-dom element that's a process-aborting `memory allocation of 94489280512 bytes failed` on 1.4.2, and a >9-minute hang on 1.4.4. The reporter searched for duplicates (closest: [#2570](https://github.com/oven-sh/bun/issues/2570), closed, "String and JSON size limits" - verified) and suggests three fixes: never let message-formatting failure turn a failed assertion into a pass, bound received/expected printing like Jest's `pretty-format` maxDepth/maxWidth, and honor the custom inspect hook in deep-equality diffs.

## Who this bites

- Any Bun test suite asserting against DOM/happy-dom nodes, large buffers, or cyclic framework objects: one oversized received value flips a failing assertion to a silent pass (1.4.2) or a 40-second cryptic failure (1.4.4) - and the 1.4.2 path means CI can merge broken code with green checks.
- Library authors who added `Bun.inspect.custom` precisely to keep test output sane: the hook works for identity matchers and is ignored by the equality matchers where the damage is worst.

## Limits

- The timings, the false pass, and the happy-dom trigger are the reporter's, on Windows x64; I verified both release tags, the related issue's state, and the report's internal consistency, but did not run the repro (repo ~96k stars).
- Whether the false-pass path exists on macOS/Linux or is Windows-specific is untested in the report.
- No maintainer response yet (issue is hours old); the three suggested fixes are the reporter's, unendorsed.
