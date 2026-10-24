# Codex desktop bundles Node.js runtimes that are behind Node's own security release

- Source issue: https://github.com/openai/codex/issues/56076 (open at check time; labels "bug" and "app"; opened 2026-10-22 04:27 UTC; 5 comments)
- Project: https://github.com/openai/codex
- Node release data: https://nodejs.org/dist/index.json
- Checked: 2026-10-24 01:05 UTC

## Problem
The reporter points out that the Codex desktop app ships its own bundled Node.js runtimes - observed versions include 24.19.0, 24.21.0, and a CUA variant 24.21.0-cua.1/2 - while Node.js published v24.22.1 as a security release (Node's release index dates it 2026-10-20 and marks it a security release; the reporter says October 21). Because these runtimes are bundled, users cannot safely replace them themselves; security fixes depend on the Codex update path. The reporter is careful: they do not claim the Node vulnerabilities are reachable or exploitable through Codex.

## What the thread says
- One commenter verified on Windows (Codex desktop 26.1016.61520, updater reporting up to date) that the primary runtime is Node 24.19.0 with a valid OpenJS Foundation signature, and that its SHA-256 exactly matches the official upstream win-x64 node.exe - meaning the binary is stock upstream with no backported fixes. The CUA runtime manifest identifies 24.21.0-cua.2.
- We independently confirmed the verifiable part of that claim: the quoted SHA-256 does appear in Node's official SHASUMS256.txt for v24.19.0.
- A second data point (2026-10-23) reports the same situation on a newer production build (26.1016.62342) and on Codex 0.164.0.
- The most recent comment (2026-10-24 00:47 UTC) says "The latest update seems to have patched this now." That is one user's unverified impression. The production Windows update manifest now publishes a newer build (26.1021.31345) than any build named in the thread, but the manifest does not disclose which Node version is bundled, so whether the runtimes were actually updated is unconfirmed.
- No response from the Codex team appears in the thread at check time.

## What we checked
- The issue and comments exist as described.
- Node v24.22.1 is real, dated 2026-10-20, flagged as a security release in Node's official release index.
- The checksum claim quoted above checks out against Node's official checksum file.
- The current Windows update manifest shows a build newer than the ones measured in the thread.

## What this does not tell you
- Whether any specific Node security fix is exploitable through Codex - nobody in the thread claims that, and we do not either.
- Whether the newest Codex build actually bundles a patched Node: the manifest does not say, and the "seems patched" comment is a single unverified report.
- This is a supply-chain hygiene observation, not a vulnerability report about Codex itself. It is not a reason to panic or to take any specific action; it documents that bundled-runtime security updates depend on the vendor's release cadence.

## Honest limits
- We read the issue, Node's release index and checksum file, and Codex's public update manifest. We did not install or inspect the Codex app; all bundled-version observations come from the commenters named above.
- Issue state may have changed since 01:05 UTC.
