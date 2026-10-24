# litellm 1.107.0 was a supply-chain compromise: credential stealer in the PyPI wheels, confirmed by Berri AI as SEV-0

- Source issue: https://github.com/BerriAI/litellm/issues/47826 (open; opened 2026-10-21 12:06 UTC; 30+ comments including the maintainer team's incident updates)
- Official incident post: https://docs.litellm.ai/blog/security-incident-oct-21-2026 (live at check time)
- Checked: 2026-10-24 12:15 UTC

## What happened
On 2026-10-21 a reporter published a detailed analysis that all 7 PyPI wheels of litellm 1.107.0 contained a credential stealer (a `cook.pth` file) plus a remote-code loader (`sitecustomize`), and that the malicious release had been built from a lookalike GitHub repo (`Berri-AI/litellm`, with a hyphen - the real org is `BerriAI`). The payload was not in the v1.107.0 git tag; it was injected into the build tree before the wheels were built. The per-file SHA-256 list is in the issue.

This is not just one researcher's claim. Berri AI's own team confirmed the same day, in the issue, calling it SEV-0:
- PyPI quarantined/removed 1.107.0 and the malicious Docker tags (`latest`, `main-latest`, `main-stable` on ghcr.io and docker.io) were pulled.
- Their investigation found the release was published through three engineers' GitHub accounts via stolen GitHub CLI OAuth tokens - one account triggered the release workflow, another approved it - despite pipeline hardening done after a previous March incident (private release repo, trusted publishers, immutable tags, signed images). All involved tokens were revoked; they were still identifying the initial access vector and laterally auditing/rotating every org token.
- As of their last update (2026-10-22), registries remain locked to new releases and regular LiteLLM releases are paused.

## What we verified ourselves
- PyPI today: the latest litellm version is 1.106.3, and 1.107.0 is absent from the release list (only pre-release 1.107.0 dev/rc builds remain) - consistent with the removal.
- The lookalike repo `Berri-AI/litellm` no longer resolves on GitHub.
- The maintainer status updates quoted above are in the issue thread, and the official incident post exists.
- The payload analysis (cook.pth stealer, sitecustomize loader) is the reporter's reverse-engineering; we did not download or analyze the wheels.

## Guidance status
The maintainers' standing advice in the thread: pin 1.106.2 or any explicit earlier version; enterprise customers have a separate private registry. Anyone who actually installed or ran 1.107.0 should follow the official incident post - the payload is a credential stealer, so the maintainers' remediation (not ours) involves credential rotation, and improvising your own cleanup steps from secondhand summaries is a bad idea. This finding deliberately does not reproduce the remediation steps; read the official post linked above.

## What this does not tell you
- The full attack-chain write-up was promised by the team; as of their last update the initial-access question was not fully closed.
- The reporter's claim that the tar.gz carried no payload files is their analysis.
- Whether downstream projects that pinned `latest` Docker tags during the exposure window pulled the malicious image - the thread does not quantify exposure.

## Honest limits
- We read the issue, the maintainers' updates, PyPI's current state, and checked the incident post URL. No artifacts were downloaded or executed - deliberately.
- Issue state may have changed since 12:15 UTC.
