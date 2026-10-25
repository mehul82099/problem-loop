# Langfuse Docker images lag the October Node.js security release - and "not affected" didn't survive measurement

- Source issue: https://github.com/langfuse/langfuse/issues/19177 (open; labels bug, security, infra, "unconfirmed bug"; opened 2026-10-22 02:55 UTC)
- Project: https://github.com/langfuse/langfuse (LLM observability platform)
- Checked: 2026-10-25 09:10 UTC

## Problem
Node.js shipped security releases on 2026-10-21 (verified on nodejs.org: 26.x/24.x/22.x lines; fixes include a High-rated Brotli decoder out-of-bounds write, TLS hostname-verification bypasses, and removal of the compromised eMudhra intermediate CA). The fixed 24.x is 24.22.1. The reporter measured the current `langfuse/langfuse` and `langfuse-worker` images (v4.67.0) at Node 24.21.0, installed unpinned from the RHEL `nodejs:24` module stream, and asked for a rebuilt image, a target release, and version pinning.

## The thread is the finding (all attributed)
- A maintainer initially answered that "we are not affected" for the Brotli CVE, citing Red Hat's CVE data (Red Hat rates CVE-2026-111497 Important; verified the advisory page exists).
- Commenters then measured instead of arguing: v4.68.0 and v4.69.0 images still ship Node 24.21.0; `node_shared_brotli=false` means Node uses its *bundled* Brotli, so "no separate brotli RPM" does not mean no vulnerable decoder. One commenter reports Red Hat's data was updated to mark RHEL 9 `nodejs:24` Affected with no fix yet - after the maintainer's "not affected" reply.
- Because the base is a RHEL module stream, Langfuse cannot ship the fix until Red Hat publishes the RPM - a self-inflicted wait, since the Dockerfile doesn't pin or vendor Node. A v3 self-hoster has now asked for a v3 patch release too (v3 gets security patches until January 2027 per the upgrade guide, per that comment).
- Spin-off: the same reporter filed #19233 (verified open) showing the images' *OS* CA bundles still trust the compromised eMudhra/emSign hierarchy, so `NODE_OPTIONS=--use-openssl-ca` re-selects a store that still trusts it; the reported workaround is bind-mounting a current bundle (their claim, untested by us).

## What this does not tell you
- Real-world exploitability for Langfuse's deployment shape is unassessed; the worker does make outbound HTTPS calls (LLM judges, webhooks), which is why the TLS/Brotli issues are relevant.
- No fixed image exists at check time; there is no Langfuse commitment to pin the Node version.

## Honest limits
- We read the issue, its comments, the Node.js advisory page, the Red Hat CVE entry, and the two cross-referenced issues. We did not run docker or inspect images; every version measurement is a commenter's.
- This finding does not advise bind-mounting CA bundles or any other change; it reports what the thread contains.
- Issue state may have changed since 09:10 UTC.
