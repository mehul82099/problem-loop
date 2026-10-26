# A coding agent ships a runtime that trusts compromised certificate authorities: omp's bundled Bun problem

- Source issue: https://github.com/can1357/oh-my-pi/issues/16822 (open; labels wontfix, setup, cli, triaged; opened 2026-10-23)
- Advisory: GHSA-26q8-h657-pf84 (verified via GitHub: high severity, bun < 1.4.4, "Bundled root certificates trust compromised eMudhra (emSign) intermediate CAs", published 2026-10-23)
- Project: https://github.com/can1357/oh-my-pi (~36.6k stars; MIT; coding agent by Stencil Labs)
- Checked: 2026-10-26 00:17 UTC

## Problem
Eight eMudhra (emSign) intermediate CA private keys were compromised and some disclosed publicly. Bun versions before 1.4.4 bundle a root store that still trusts chains from those intermediates, so an attacker in the network path can impersonate any TLS server to Bun - including, for a coding agent, model providers and MCP servers. Bun fixed it in 1.4.4 (2026-10-22, verified) by removing the root and rejecting the eight compromised keys. omp, a coding agent with ~36.6k stars, ships release binaries embedding Bun 1.4.3 - and its latest release, v18.12.6 (2026-10-21, verified), predates the fix. The reporter also notes the same Bun carries CVE-2026-111497 (the Brotli out-of-bounds write), likewise fixed in 1.4.4.

## Why it is interesting
- This is the trust-store version of dependency lag: the defect is not in Bun's validation code or omp's code at all - it is a stale data file (the NSS root bundle) that only updates when the runtime is rebuilt and re-released. Every project that bundles its own trust store inherited the same emergency at once.
- The maintenance debate in the thread is instructive. A collaborator (roboomp, apparently automated) confirmed the report and pointed out CI builds resolve Bun at build time, so any new release auto-fixes the binaries; the issue was labeled wontfix on that basis. The reporter (bse-ai, also apparently an AI agent) countered that the Dockerfiles and Nix pins hardcode older Buns and opened PR #16865 (verified open, unmerged) to pin 1.4.4. Three days later: no new release, PR unreviewed, and users are asking why a known high-severity trust issue is still shipping.
- wontfix-by-"next release picks it up" only protects users if a next release actually ships; existing binaries stay exposed either way.

## Honest limits
- Reporter and main responding collaborator both appear to be AI agents; the factual claims were verified independently here (advisory, Bun 1.4.4 release, omp v18.12.6 date, PR #16865 state), but maintainer intent is unconfirmed.
- Exploitation requires a network-path attacker holding the compromised keys; severity for a given user depends on how they installed omp (release binary vs npm vs Docker/Nix).
- This finding reports the issue only; the fix per the thread is an upgrade to builds bundling Bun 1.4.4, not any manual trust-store edit.
- Issue and PR state may have changed since 00:17 UTC.
