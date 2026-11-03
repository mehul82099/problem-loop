# OpenInference llama-index instrumentation drops Gemini thinking, cached, and tool-use tokens for GoogleGenAI

**Source:** [Arize-ai/openinference#4222](https://github.com/Arize-ai/openinference/issues/4222) - opened 2026-11-03 by lalith0407 (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

With `llama-index-llms-google-genai` (`GoogleGenAI`), the LlamaIndex instrumentor never reads the provider's `usage_metadata`. GoogleGenAI stores it as a plain dict in `response.raw["usage_metadata"]`, but `_Span._extract_token_counts` only looks under `raw["_raw_response"]` (the Vertex shape) or via `getattr(raw, "usage_metadata")` - which is always `None` for a dict. The span then falls back to `additional_kwargs`, where GoogleGenAI puts only `completion_tokens = candidates_token_count`.

Consequences for Gemini 2.5 / 3 thinking models, per the reporter:

- `llm.token_count.completion` excludes `thoughts_token_count` (billed at the output rate), so prompt + completion no longer equals total. In their repro: completion=80 although the model used 900 thinking tokens, total=2180 vs prompt+completion=1280.
- `llm.token_count.completion_details.reasoning` and `llm.token_count.prompt_details.cache_read` (from `cached_content_token_count`) are never set.
- `tool_use_prompt_token_count` is not added to the prompt.

They also note the Vertex branch maps only prompt/candidates/total, so Vertex responses with thinking tokens have the same completion/reasoning gap, and that `openinference-instrumentation-google-genai` already handles all of these - so the same model reports different token counts depending on which integration traces it. The repro is fully offline: `google.genai` `Models.get` / `Chat.send_message` are patched to return a real `types.GenerateContentResponse` with prompt=1200, candidates=80, thoughts=900, cached=1024, total=2180.

## Verification (checked during this finding)

- In `_handler.py` on `main` (`python/instrumentation/openinference-instrumentation-llama-index/.../llama_index/_handler.py`), `_extract_token_counts` (line 779) does exactly what the report describes: it reads `raw.get("_raw_response")` for the Vertex shape and otherwise falls back to `getattr(raw, "usage_metadata", None)` - which returns `None` when `raw` is a plain Mapping, so GoogleGenAI's dict-shaped `usage_metadata` is never picked up. The `additional_kwargs` fallback immediately follows.
- In `openinference-instrumentation-google-genai`'s `_utils.py` on `main`: `tool_use_prompt_token_count` is added to the prompt count (lines 60-61), `cached_content_token_count` is emitted (62-65), and `thoughts_token_count` is added to completion with a reasoning detail (82-91). So the cross-integration discrepancy is real as described: the google-genai instrumentor handles these fields, the llama-index one does not.
- The Vertex-branch claim (only prompt/candidates/total mapped) was not separately traced.

## Limits

- The repro was not executed here; token numbers are quoted from the issue. The extraction-path mechanism is confirmed by the source reading above.
- The reporter's association is NONE. As of writing there is no maintainer response; the only comment is the repository's automation bot (tooling output, not maintainer triage).
- Whether `additional_kwargs` contents vary by llama-index-llms-google-genai version (e.g. whether `thoughts_token_count` ever appears there) was not assessed.

## Sources

- Issue: <https://github.com/Arize-ai/openinference/issues/4222>
- llama-index _handler.py (main): <https://github.com/Arize-ai/openinference/blob/main/python/instrumentation/openinference-instrumentation-llama-index/src/openinference/instrumentation/llama_index/_handler.py>
- google-genai _utils.py (main): <https://github.com/Arize-ai/openinference/blob/main/python/instrumentation/openinference-instrumentation-google-genai/src/openinference/instrumentation/google_genai/_utils.py>
