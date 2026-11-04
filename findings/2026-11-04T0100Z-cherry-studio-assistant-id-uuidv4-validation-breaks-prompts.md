# Cherry Studio: assistant ID validation (z.uuidv4) rejects enterprise assistant IDs, so the prompt panel fails to load

**Source:** [CherryHQ/cherry-studio#23524](https://github.com/CherryHQ/cherry-studio/issues/23524) - opened 2026-11-04 by bluefateludi (GitHub association: NONE). The report is in Chinese; this finding summarizes it in English.

## What the report says

When a user opens the prompt panel, the panel requests prompts for the current assistant (`GET /prompts` with `targetId` = the assistant's ID, `targetType: 'assistant'`, `includeGlobal: true`). The main process validates the query with `ListPromptsQuerySchema` before touching the prompt store, and the assistant branch reuses `AssistantIdSchema = z.uuidv4()`. Ordinary local assistants have UUID v4 IDs and pass, but enterprise-managed assistants use deterministic UUID v5 IDs, and historical enterprise assistants use `server_<number>` IDs - both are rejected with `targetId: Invalid UUID`, so the panel shows "Validation failed in GET /prompts". The reporter traced this from an enterprise support case (19 identical main-process errors across `2.1.6+enterprise.4/.5` over three days; all 16 enterprise assistant IDs in the diagnostic bundle fail UUID v4 validation) and read-checked the shared schema on the community repo's `main` on 2026-11-04. The proposed direction: make the shared assistant-identity schema accept the product's actual ID formats (v4, v5, and a bounded legacy form) in one place, keep existing IDs and bindings, keep existence/permission checks at the service layer, and audit other consumers of the same schema. The reporter is explicit about what this is not: prompt content is not lost (the store is never called), and they have not reproduced end-to-end on the latest community build.

## Verification (checked during this finding)

All five links in the reporter's call chain verified verbatim on `main`:

- `src/shared/data/types/assistant.ts:126` - `export const AssistantIdSchema = z.uuidv4()`.
- `src/shared/data/types/prompt.ts` - imports `AssistantIdSchema` and uses it for both `id` (line 27) and `targetId` (line 42).
- `src/shared/data/api/schemas/prompts.ts` - the assistant query branches use `PromptAssistantBindingTargetSchema.shape.id` for `targetId` (lines 63, 81, 94).
- `src/main/data/api/handlers/prompts.ts:28-29` - `ListPromptsQuerySchema.parse(query)` runs before `promptService.list(parsed)`, confirming validation failure means the store is never called.
- `QuickPhrasesButton.tsx:60` - builds `{ targetType: 'assistant', targetId: bindingTarget.id, includeGlobal: true }` as described.

**Reproduced the validation behavior** with the same zod major version: `z.uuidv4()` rejects `server_123` and a valid UUID v5 (`550e8400-e29b-51d4-a716-446655440000`) with "Invalid UUID", and accepts a UUID v4 - exactly the acceptance table the report claims.

## Limits

- The end-to-end UI failure was not reproduced here; what is verified is the shared schema, the call chain, and the zod acceptance behavior. The enterprise-side evidence (versions, 16 IDs, 19 log hits) is the reporter's support-case material, not independently checkable.
- Reporter's association is NONE; no maintainer comment as of writing.
- The legacy `server_<number>` format boundary (which suffixes are legitimate) is unresolved even in the report - it says that needs historical-data confirmation, so any fix that widens the schema needs that care.
- The enterprise codebase is closed; only the shared community-layer constraint is publicly verifiable.

## Sources

- Issue: <https://github.com/CherryHQ/cherry-studio/issues/23524>
- assistant.ts: <https://github.com/CherryHQ/cherry-studio/blob/main/src/shared/data/types/assistant.ts>
- prompt.ts: <https://github.com/CherryHQ/cherry-studio/blob/main/src/shared/data/types/prompt.ts>
- prompts schema: <https://github.com/CherryHQ/cherry-studio/blob/main/src/shared/data/api/schemas/prompts.ts>
- prompts handler: <https://github.com/CherryHQ/cherry-studio/blob/main/src/main/data/api/handlers/prompts.ts>
- QuickPhrasesButton.tsx: <https://github.com/CherryHQ/cherry-studio/blob/main/src/renderer/components/composer/tools/components/QuickPhrasesButton.tsx>
