# Docker BuildKit: cache mounts cannot be moved or shared between machines

- Cycle: 2026-10-15T0845Z
- Source (github): https://github.com/moby/buildkit/issues/1512
- Issue state when checked (2026-10-15): open, opened 2020-05-27, labels `kind/enhancement` and `help wanted`, 62 comments, 544 reactions.

## The problem

`RUN --mount=type=cache` keeps a directory on disk (for example a Go or pip cache) between builds. The issue says regular remote instruction cache does not work for cache mounts, because they are not tracked by cache key and are just a location on disk shared by builds. It calls maintaining this cache between nodes something that has to be done as part of the build.

The issue links earlier requests for exporting cache mount contents: https://github.com/moby/buildkit/issues/1474 and https://github.com/docker/buildx/issues/244.

## What the issue proposes

- Do not try to merge cache mounts into the remote cache backends. The author argues cache mounts are throwaway data, and restoring them may take about as long as rebuilding them.
- Let users choose where the cache lives when it is not on top of the snapshots, with a pluggable backend behind a Go interface. The example in the issue is a flag like `docker build --cache-mount id=gocache,type=volume,volume=myvolume .`, using a Docker volume or a host bind mount.

That is a proposal in the issue text, not a shipped feature. Check the issue for current status before relying on it.

## Why it was picked

Highest total in the cycle with no veto. Scores from the Discussion stage:

- **user-advocate**: 10.0 - 544 reactions, 62 comments
- **skeptic**: 2.0 - title has no problem words (the scorer reads only the title and first 300 characters)
- **builder**: 6.0 - scope looks small enough for one cycle

Runner-ups in the same cycle: VSCodeVim/Vim#2007, golang/go#26492 (`-static` flag), prettier/prettier#5287.

## Honest limits of this entry

- It records a real, still-open problem with its source. It does not contain a fix.
- The scoring that picked it favours old, popular issues. A weakness already noted in the README.
