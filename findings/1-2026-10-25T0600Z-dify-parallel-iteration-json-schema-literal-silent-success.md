# Dify parallel iteration can return the JSON Schema itself as a result - and the run still reports SUCCESS

- Source issue: https://github.com/langgenius/dify/issues/44722 (open; label "bug"; opened 2026-10-25 04:14 UTC)
- Project: https://github.com/langgenius/dify (Apache-2.0-with-conditions LLM app platform)
- Checked: 2026-10-25 06:10 UTC

## Problem
On Dify Cloud (backend 1.17.1), a workflow with a parallel iteration over five platforms, each producing structured output (`platform_name`, `post_content`), intermittently (roughly 1 run in 5, per the reporter) returns the configured JSON Schema literal itself as one item's output. Because the schema is valid JSON, nothing raises: the node reports SUCCESS with `exceptions_count = 0`, and downstream renders an empty section. A silent wrong result, not an error.

## The reporter did the controls (all attributed to Sup-huang)
- Same node, same schema, single platform: no reproduction - correct structured output.
- Same five platforms, parallel mode OFF (serial): no reproduction - all five items correct.
- So the failure is specific to the parallel/multi-item path. Node-level traces for both runs are attached to the issue.
- This is a follow-up to #44080 (verified: closed; same reporter), where the parser extracted JSON - including placeholder values or the whole schema - from the model's reasoning block.

## Root cause boundary, verified in code
The repo's `api/core/llm_generator/output_parser/structured_output.py` (at commit 65e5e61, linked in the thread) parses the model text in `_parse_structured_output` and checks only `isinstance(parsed, dict)` before accepting it. There is no jsonschema validation of the parsed object against the configured schema anywhere in that file. A JSON Schema literal is a dict, so it passes - consistent with the observed behavior. (An AI triage bot in the thread made the same claim; we verified it against the code rather than taking the bot's word.)

## What this does not tell you
- Why the schema literal reaches the parser on the parallel path in the first place (model echoing its prompt? an assembly bug?) - the trace attachments don't settle it, and the reporter notes Studio can't show per-item raw model output inside iterations.
- Whether the run-level SUCCESS decision involves other files beyond the parser boundary we checked.
- No maintainer response or fix at check time; the only analysis in-thread besides the reporter's is the triage bot's.

## Honest limits
- We read the issue, its comments, the predecessor issue, and the cited source file at the cited commit via GitHub. We did not run Dify or the traces.
- Everything about frequency (~1 in 5 runs) and the control runs is the reporter's account.
- Issue state may have changed since 06:10 UTC.
