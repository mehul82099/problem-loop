# Official `node` Docker images lag the Node.js security release, with identical placeholder-looking digests

- Source issue: https://github.com/nodejs/docker-node/issues/2663 (open at check time; labels: build process, security release; opened 2026-10-21 12:27 UTC; 5 comments)
- Node.js releases checked: https://github.com/nodejs/node/releases/tag/v24.22.1 (and v22.23.4, v26.12.1), all published 2026-10-21 about 10:38 UTC per the API
- Image repo: https://github.com/nodejs/docker-node
- Checked: 2026-10-21 16:30 UTC

## Problem
The Node.js project published security releases 22.23.4, 24.22.1 and 26.12.1 on 21 October 2026. The v24.22.1 release notes (we read them via the API) say "This is a security release" and list several CVEs. The reporter of the docker-node issue says that hours later the new official `node` image tags on Docker Hub (for example `26.12.1-trixie-slim`, `24.22.1-alpine`, `22.23.4-trixie-slim`) all showed the same digest, `eb37f586...4aef`, instead of a unique one each, and calls it a broken checksum or missing images. A commenter adds they could not patch systems that depend on the official containers hours after the announcement.

## What the project said
- A project member (13:20 UTC): the images "are being built right now".
- A contributor (13:35 UTC) pointed to the README section "Release Availability". We read it: the repository starts a build when Node.js releases appear, the build "can take several hours", and images "may initially appear on Docker Hub with incomplete or missing OS/ARCH listings" while architectures are backfilled.
- The same contributor (15:07 UTC) asked people to discard the earlier links and check again from the tags page, and gave an example for `26.12.1-trixie-slim` with a different digest, `80eccfd7...4d8b`.

The repository commit adding "Node.js 22.23.4, 24.22.1, 26.12.1" is dated 2026-10-21 10:43 UTC, about five minutes after the Node.js releases.

## Our own check
At about 16:27 UTC we asked the Docker Hub API for three tags. The digests it returned were different from each other and from the reporter's value, and last-updated times were between 14:40 and 14:44 UTC:

- `24.22.1-alpine`: `sha256:6a1c190e...9a3d`
- `26.12.1-trixie-slim`: `sha256:1653c74b...0422`
- `22.23.4-trixie-slim`: `sha256:817bd940...602c`

That fits the project's statement that the first listings were incomplete and were later replaced. We did not pull images, compare them with what Docker Hub's page shows, or check that the Node.js version inside matches the tag.

## What this means for readers
- If you build from an official `node` tag the same day as a Node.js security release, a tag can exist before its images are complete. The project documents this and says builds can take hours.
- Tags and digests change as the build finishes. If you pin by digest, take the digest after the build is done, not from the first listing.

## What this does not tell you
- It does not say any image was wrong or tampered with. The project's explanation is a staged build, and the later digests we saw are consistent with that, but we only compared tag listings.
- It does not say the issue is closed. It was still open at check time.

## Honest limits
- We did not pull or run any image, and we did not verify the contents of any digest.
- The "same digest" observation is the reporter's. We could not see the earlier state.
- Docker Hub's API output is one reading at one time. Digests can change again.
