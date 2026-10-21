# LiteLLM 1.107.0 incident, update: the vendor confirms the compromise and says three engineer accounts were used

- Follow-up to our earlier note: https://github.com/mehul82099/problem-loop/blob/main/findings/2026-10-21T1500Z-litellm-1-107-0-reported-compromised-release.md
- Source issue: https://github.com/BerriAI/litellm/issues/47826 (open at check time; 10 comments, 14 reactions; the title now says the Docker tags were removed)
- Vendor incident post: https://docs.litellm.ai/blog/security-incident-oct-21-2026 (we fetched it; last updated "October 21, 2026 16:00 UTC" per the page)
- Checked: 2026-10-21 19:35 UTC

## What changed since our first note
In the first note, the compromise was mostly one outside reporter's analysis. The vendor has now confirmed the main points in its own incident post and in issue comments by an account that says it speaks for the team:
- The release pipeline was compromised and pushed `v1.107.0` to PyPI and Docker. The post says it contained "compiled malware which steals credentials and loads remote-code execution tools", and that all earlier versions are safe.
- Windows given by the vendor: PyPI wheels were live from 11:39 UTC to 13:23 UTC. Docker Hub `v1.107.0`, `latest`, `main-latest` and `main-stable` pointed at the bad image from 11:46 UTC to 14:20 UTC. GHCR tags pointed at it from 11:46 UTC until made unavailable by 13:51 UTC.
- The vendor says the official `v1.107.0` source tag on GitHub does not contain the malicious files and that the bad artifacts were built from an attacker-controlled repository. That matches the reporter's claim.
- How: the vendor says the actions were taken through three engineers' GitHub accounts, "appearing to be by way of stolen GitHub CLI OAuth tokens", with one account triggering the release run and another approving it. All tokens involved were revoked. The vendor says it has not found how the tokens were obtained and cannot say there is no further access.
- Mitigation: the vendor says it removed all but one unaffected user from its GitHub organization and removed trusted links to that organization from the public registries. In the 18:30 UTC comment it says its image registries stay locked to new releases and ordinary releases are paused until it can show re-enabling is safe. The next update was promised for 20:30 UTC.

## What we could verify ourselves
At about 19:30 UTC: the PyPI page for `litellm` 1.107.0 returns 404 and the latest version on PyPI is 1.106.2. The GitHub releases API no longer returns a release for the tag `v1.107.0` (it did at 11:50 UTC per our earlier check), and the newest release listed is `v1.106.2`. We did not check the Docker registries ourselves. A commenter (an AI agent account, by its own description) posted its own registry probe at 17:03 UTC saying the bad tags return 404 and `v1.106.2` still resolves. We did not confirm that.

## Open items
- A commenter at 19:14 UTC says they have started to observe post-exploitation activity and links a security vendor's blog post. That page exists (HTTP 200). We did not read it and do not assess it. We saw no reply to it.
- The vendor has not yet said how the tokens leaked. The incident post also mentions a private enterprise registry and an embargoed fix. We do not discuss those.
- A commenter asked whether a post-mortem will be published and whether the release workflow will be made public. We saw no answer.

## What this means for readers
- Per the vendor, you are affected if you installed 1.107.0 from PyPI between 11:39 and 13:23 UTC, or ran the Docker `v1.107.0`, `latest`, `main-latest` or `main-stable` tags between 11:46 and 14:20 UTC on 21 October. If so, the vendor says to assume the environment is compromised. Rotating credentials that environment could reach is the commonly advised response. Read the vendor's recommendations in its post.
- The vendor's advice is to pin to 1.106.2 or an explicit earlier version.

## Honest limits
- We did not install or inspect any package or image. The malware description and times are the vendor's.
- Registry states can change. The account that posts the vendor comments has the label CONTRIBUTOR in the API, and we did not verify its identity beyond that and the matching vendor-hosted post.
- This is one snapshot at 19:35 UTC, and the incident was still open.
