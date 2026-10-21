# LiteLLM 1.107.0: reported credential-stealing release (PyPI and Docker)

- Source issue: https://github.com/BerriAI/litellm/issues/47826 (open at check time; opened 2026-10-21 12:06 UTC; 5 comments; the issue body has been edited several times by its author)
- Project: https://github.com/BerriAI/litellm (61,727 stars; license field "NOASSERTION" per the API)
- Checked: 2026-10-21 15:30 UTC

## What was reported
An outside reporter says the `litellm==1.107.0` wheels on PyPI contain extra files (`cook.pth`, `cook.py`, `sitecustomize.py`) that run at Python start-up and steal credentials, and that the payload is not in the `v1.107.0` git tag but was added to the build tree before the wheels were built. In a later update they say the Docker images for `v1.107.0` and the floating tags (`latest`, `main-latest`, `main-stable`) on GHCR and Docker Hub pointed at the same infected image, and that the release pipeline built from a lookalike repository. They say they decoded the payload statically and never ran it. They list wheel hashes and image digests in the issue.

## What we could verify ourselves
- PyPI: `https://pypi.org/pypi/litellm/1.107.0/json` returned HTTP 404 at about 15:25 UTC, which fits the statement that the version was removed.
- GitHub releases, per the API: `v1.107.0` was published 2026-10-21 11:50 UTC, the previous release `v1.106.2` at 10:50 UTC. The API still lists `v1.107.0` as a published (not pre-release) release at check time.

We did not download any package or image, did not inspect the files, and cannot confirm the payload, the hashes, the digests, the "lookalike repository" claim or the timeline. Those come from the reporter.

## What the project said
An account the API labels CONTRIBUTOR (and which says it speaks for the team) replied in the issue:
- 13:50 UTC: they are treating it as SEV-0, PyPI quarantined 1.107.0, and they will update every two hours.
- 14:32 UTC: the malicious Docker images "have been removed". They are still investigating how the releases were published and have "not yet identified or locked down" the method. They say OSS users should pin to 1.106.2 or any explicit version published before now. The next update was promised for 16:30 UTC.

We checked only that these comments exist. We did not verify the account's identity beyond the label. The same comment mentions a private enterprise registry and an embargoed fix. We do not repeat or assess that.

## What this means for readers
- If you installed `litellm` 1.107.0 or pulled the Docker floating tags on 2026-10-21 (UTC), the reporter's view is that you should treat the environment as exposed and rotate credentials that were reachable from it. That is the reporter's advice and we cannot confirm exposure. Check your own install logs and image digests.
- The maintainer-side advice in the thread is to pin an explicit older version. Pinning by version or by digest instead of a floating tag is ordinary supply-chain hygiene.
- The cause of the release is unknown according to the project's latest comment, so more releases of any kind should be treated with care until the project says it has closed the hole.

## Honest limits
- Most of this is one outside reporter's analysis. It is detailed, but we verified only the PyPI removal and the release dates.
- We cannot tell whether the "clean" versions the reporter lists are clean. We did not test them.
- The situation was moving at check time. Read the issue and the project's own channels for the current state.
- Nothing here is a complete incident response guide.
