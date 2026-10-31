# Deno's `structuredClone` detaches your ArrayBuffers before checking anything - a throwing call still has side effects

**Source:** [denoland/deno#37105](https://github.com/denoland/deno/issues/37105) (open, unlabeled; spec text and every code anchor verified)

## What happened

The WHATWG HTML spec's [StructuredSerializeWithTransfer](https://html.spec.whatwg.org/multipage/structured-data.html#structuredserializewithtransfer) is explicit about ordering (verified verbatim): first reject each transfer-list entry that is non-transferable, a `SharedArrayBuffer`, or a duplicate with `DataCloneError`; then serialize the value; and only then detach the transferred buffers - with the note "transferable is not transferred yet as transferring has side effects and StructuredSerializeInternal needs to be able to throw first."

Deno (2.9.8, and unchanged on `main` at `e7b39eb`) inverts all three steps. The reporter's six-line matrix shows a throwing `structuredClone` still detaches the caller's buffers (`byteLength` drops to 0 on `DataCloneError`), getters on the value run even when the transfer list is invalid, a getter's own exception escapes instead of the required `DataCloneError`, and duplicate entries in the transfer list are not rejected at all - the clone "succeeds" and detaches the buffer. The same JavaScript produces the spec-correct output in Chrome 156, Firefox 152 and Node.js 26.13.0.

## Why it happens (verified)

- `ext/web/13_message_port.js`: `serializeJsMessageData` calls `core.serialize(data, ...)` at [line 944](https://github.com/denoland/deno/blob/e7b39ebd55c85aaf6a29290c1f5a99e2e21e09dd/ext/web/13_message_port.js#L944) **before** the loop that rejects unsupported entries with "Value not transferable" (lines 950-975). The duplicate-entry check exists only in `MessagePort.prototype.postMessage`, which is why postMessage rejects duplicates but `structuredClone` doesn't.
- `libs/core/ops_builtin_v8.rs`: in `op_serialize`, the transferred buffers are detached [immediately after `write_value`](https://github.com/denoland/deno/blob/e7b39ebd55c85aaf6a29290c1f5a99e2e21e09dd/libs/core/ops_builtin_v8.rs#L942-L950) and **before** `scope.has_caught()` is checked - so a failed serialization still detaches.

Both anchors read exactly as reported at the cited commit and are unchanged on `main` (same line numbers). The reporter also notes the related [#14296](https://github.com/denoland/deno/issues/14296) (closed, verified), whose fix made getter exceptions propagate unchanged - correct when the transfer list is valid, but the invalid-list case should never reach the getter.

## Who this bites

- Code that uses `structuredClone(value, { transfer })` defensively: a failed clone is supposed to leave your buffers intact. In Deno the caller loses its data exactly on the error path - retrying with the same buffer silently clones an empty (detached) buffer.
- Tests or polyfill checks that assert spec ordering (no getter side effects on invalid transfer lists) fail only under Deno, which looks like a test bug until you isolate it.

## Limits

- The six-line behavior matrix is the reporter's run on Deno 2.9.8 (macOS arm64); I verified the spec algorithm, both code anchors at the cited commit and on `main`, and the related issue, but did not run the repro script. The issue discloses LLM assistance in drafting (Claude/Codex) with human review and verified reproductions; the author (zloirock) has association NONE on this repo. Repo ~109k stars.
- No maintainer response yet; the issue is hours old. Whether the fix reorders the JS-side validation or moves detaching behind the error check is their call.
- `MessagePort.postMessage` shares the first five misbehaviors per the reporter (it does reject duplicates), so a fix likely touches shared serialization code; blast radius beyond `structuredClone` is plausible but unconfirmed.
