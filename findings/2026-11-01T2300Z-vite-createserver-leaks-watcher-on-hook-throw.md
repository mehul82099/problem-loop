# Vite `createServer()` rejects when a plugin hook throws - but keeps the file watcher (and workerd) running, so your CLI never exits

**Source:** [vitejs/vite#23965](https://github.com/vitejs/vite/issues/23965) (open; reporter offered to send the fix, no PR at publish time)

## What happened

When a plugin throws in `configureServer` or `buildStart` during `createServer()`, the promise rejects - but the file watcher that was already started stays open, so the calling process never exits. Because the call rejected, the caller never receives a server object and has nothing to call `close()` on: the resources are unreachable *and* alive. The reporter's repro (linked repo, verified to exist) starts one child process per hook: throws from `config` and `configResolved` exit fine (they run before the watcher starts), throws from `configureServer` and `buildStart` hang past the 5s kill timeout; with `server.watch: null` all four exit. With `@cloudflare/vite-plugin` the leak also keeps a workerd process running, widening it from "process hangs" to "orphaned worker runtime". The reporter's workaround is telling: add an `order: 'pre'` plugin whose only job is to capture the server reference so it can be closed when a later hook throws - users shouldn't need to smuggle out a handle the API won't give them. Reproduced on vite 8.3.5 (released 2026-10-21, verified).

## Who this bites

- Every CLI, test runner, or editor integration that drives Vite through the JS API rather than the `vite` binary (Vitest-style wrappers, scaffolding tools, `vite dev` wrappers in monorepos): one buggy or misconfigured plugin turns a clean error into a hung process with no handle to fix it - CI jobs run to the timeout instead of failing fast.
- The shape is a classic partial-construction leak: an initializer that starts resources in stages and, on a late failure, cleans up nothing it already started - made worse by the rejection contract withholding the only handle that could close them.

## Limits

- Single-source report (repo ~78k stars, reporter association NONE) with a public repro I did not run; macOS demonstrated, but the watcher lifecycle is platform-independent in principle.
- The reporter's "config/configResolved run before the watcher starts" explanation is their inference from behavior, not yet confirmed against source in the issue.
- No maintainer response or fix PR yet; the reporter's pre-plugin workaround is the only mitigation and is unvetted by the maintainers.
