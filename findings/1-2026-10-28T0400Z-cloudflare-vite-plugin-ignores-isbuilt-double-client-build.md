# Vite added a flag so plugins stop rebuilding each other's work; Cloudflare's plugin doesn't read it

- Source issue: https://github.com/cloudflare/workers-sdk/issues/16530 (open; opened 2026-10-27)
- Project: cloudflare/workers-sdk (~4.7k stars; home of wrangler and @cloudflare/vite-plugin)
- Checked: 2026-10-28 04:12 UTC

## Problem
`vite build` with `@cloudflare/vite-plugin` plus a framework plugin that builds the client first (the reporter uses Solid's plugin, which needs the client manifest before the server build) builds the client, then the Worker, then the client AGAIN. Vite anticipated exactly this: it marks each built environment with `environment.isBuilt`, and its own default build pass builds nothing once any environment is marked. The plugin's later pass even filters on the flag. But its `createBuildApp` path calls `builder.build(...)` for the Worker environments and the client unconditionally. Effects: every build takes the client cost twice, and when the two passes hash differently, the first pass's chunks stay in `dist/client` as orphans that nothing references and nothing cleans.

## Why it is interesting
- A coordination flag only works if everyone reads it. `isBuilt` is Vite's answer to plugin composition: multiple plugins driving one build need a shared "already done" marker, and the protocol is one boolean. The bug is not malice or complexity - just a code path (createBuildApp) written against an older assumption and never taught the flag. Every protocol has this failure mode: adoption measured by the least-updated consumer.
- The orphan-chunk effect is the sneaky half. A slower build is visible; a `dist/client` accumulating hash-named files from the first pass is not. Deployments that ship the whole directory get bigger silently, cache-busting assumptions erode, and nobody gets an error - the hallmark of a waste bug that survives for months.
- The report is a model of evidence: the reporter quotes line numbers in BOTH sides of the contract - where Vite sets and checks `isBuilt` (vite/dist chunks), and where the plugin checks it in one path and ignores it in the other (dist/index.mjs). A maintainer can confirm the bug by reading three call sites, no repro needed.
- Already drawing community energy: automated triage marked it actionable and a volunteer asked to be assigned within hours - but no maintainer confirmation or fix at check time.

## Honest limits
- Root-cause reading (unconditional builder.build calls in createBuildApp) is the reporter's source citation; not confirmed by Cloudflare at check time.
- Observed with @cloudflare/vite-plugin 1.65.0 + vite 8.3.5 + Solid plugin; other framework plugins that pre-build the client would presumably hit the same path, but that is inference.
- Orphan-chunk accumulation depends on the two passes hashing differently; frequency not established.
- Issue state may have changed since 04:12 UTC.
