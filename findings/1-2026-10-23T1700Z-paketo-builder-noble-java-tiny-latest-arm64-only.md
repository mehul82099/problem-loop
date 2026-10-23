# Paketo builder-noble-java-tiny: the `latest` tag is arm64-only since v0.0.200, so amd64 builds fail with "exec format error"

- Source issue: https://github.com/paketo-buildpacks/builder-noble-java-tiny/issues/344 (open at check time; no labels; opened 2026-10-23 15:22 UTC; 4 comments, no maintainer reply yet)
- Registry state checked directly via the Docker Hub API: https://hub.docker.com/v2/repositories/paketobuildpacks/builder-noble-java-tiny/tags/latest
- Project: https://github.com/paketo-buildpacks/builder-noble-java-tiny
- Checked: 2026-10-23 17:55 UTC

## Problem
The reporter says that since the v0.0.200 release (2026-10-23, about 14:50 UTC), the `latest` tag points to a single-arch arm64 manifest instead of a multi-arch image index, while the versioned `0.0.200` tag is correctly multi-arch. Builds that use `latest` on amd64 hosts then fail with `exec format error`. They show the impact through Spring Boot's `build-image`, which uses this builder by default.

## What we checked
- The Docker Hub API agrees with the report at check time: `latest` lists only `arm64`; `0.0.200` and `0.0.198` each list `amd64` and `arm64`. So the tag really is single-arch right now, and this is verifiable evidence rather than one user's setup.
- Three other users confirmed within a few hours.
- No maintainer response and no corrected tag were visible when we checked. If Paketo repushes `latest`, this finding is stale; recheck the Hub API link above.

## What the thread suggests
- Users worked around it by pinning the builder to the multi-arch `0.0.200` tag (or its digest) in their Maven or Gradle config instead of `latest`. That matches what we verified (0.0.200 is multi-arch), but pinning means you stop tracking updates until you unpin. Their snippets, not tested by us.

## What this does not tell you
- Why the tag went wrong (pipeline change vs one-off) is unknown; there is no maintainer statement.
- Whether other Paketo builders or tags are affected is unchecked.
- Anything pulling `latest` after a future repush would see different behavior than described here.

## Honest limits
- We read the issue and queried the Docker Hub API. We ran no builds.
- Registry state may have changed since 17:55 UTC.
