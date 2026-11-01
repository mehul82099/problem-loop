# `docker compose build` ignores the buildx builder you selected for a named context - and resets your selection on the way out

**Source:** [docker/compose#14433](https://github.com/docker/compose/issues/14433) (open, filed by a CONTRIBUTOR; fix PR [#14434](https://github.com/docker/compose/pull/14434) open and unmerged at publish time)

## What happened

On a named Docker context - the normal Docker Desktop setup, where the current context is `desktop-linux` rather than `default` - selecting a custom builder with `docker buildx create --name mybuilder --driver docker-container --use` has no effect on `docker compose build`: Compose shells out to buildx's bake path without carrying the context's selected builder, so the build runs on the default builder instead. Worse, the report says each Compose build **resets buildx's stored selection for that context back to the default**, so even a subsequent plain `docker buildx build` - which honored the selection before - silently falls back too. `docker buildx build` on its own both uses the selection and preserves it, which isolates the misbehavior to Compose. Reproduced on Docker Compose v5.6.1 (released 2026-10-21, verified).

## Who this bites

- Anyone who created a named builder for a reason - `docker-container` driver for reproducible/isolated builds, multi-platform `buildx build --platform`, custom registry mirrors, or a remote builder - and builds through Compose on Docker Desktop: their builds quietly run somewhere else, with cache misses and missing multi-arch output as the visible symptoms and no warning anywhere.
- The state-corruption half is the sneakier bug: one `docker compose build` doesn't just ignore your configuration, it *undoes* it for every other tool that reads the same selection, so the failure outlives the Compose invocation and is hard to trace back to it.

## Limits

- Single-source report (repo ~38.6k stars, reporter is a CONTRIBUTOR); I verified the Compose v5.6.1 release and the open unmerged fix PR, but did not reproduce the builder reset myself.
- Scope as reported is named contexts; the default context path is not implicated by the report.
- No released patched version yet - the fix PR is open and unreviewed at publish time.
