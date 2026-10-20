# eMudhra intermediate CA compromise: how nixpkgs is tracking it

- Source issues: https://github.com/NixOS/nixpkgs/issues/576485 (CVE tracking, open, labels: security, tracking, opened 2026-10-20 17:34 UTC) and https://github.com/NixOS/nixpkgs/issues/576475 (tree-wide CA certificates, open, opened 2026-10-20 17:13 UTC)
- Background pages we read: https://emudhra.we-have-a-problem.com/ and https://lwn.net/Articles/1101643/
- Checked: 2026-10-20 23:10 UTC

## What was reported
The single-page site (dated 2026-10-20) says the private keys of eight eMudhra intermediate CA certificates were compromised, that they chain to roots trusted by Mozilla, Microsoft, Apple and Chrome programs, and that the original reporter proved it by signing a message with each key and sending it to the root programs on 2026-10-17. LWN (posted 2026-10-20) relays Mozilla's announcement: Mozilla blocked the certificates via OneCRL and updated its trust list in NSS 3.131.1, and says an attacker who can intercept a connection could use fraudulent certificates to impersonate sites. LWN, citing the site, says Chrome blocked them from 2026-10-17, Apple from the 19th and Microsoft on the 20th. We did not verify those per-vendor dates ourselves.

## What nixpkgs is doing (from the issues, verified by API where noted)
- #576485 gives a partial mitigation: add the affected root names to `security.pki.caCertificateBlacklist` ("Comodo AAA Services root" and three emSign roots, with links to NSS revisions). The issue says this mitigation was implemented in PRs #576390 and #576401. API check: both are merged (2026-10-20 13:28 and 13:34 UTC; #576401 is the release-26.05 backport).
- A member wrote at 19:37 UTC that, as of 19:30 UTC, `nixos-unstable`, `nixos-26.05` and their `-small` variants have the mitigation.
- #576475 notes that many packages bundle their own CA lists, so the system-level blacklist does not reach them. It cites a scanner (zimbatm/nix-cacert-scan) and counts 883 packages in four categories: vendored PEM bundles (95), bundles inside wheels/jars/zips (88), Java keystores (37) and CA roots compiled into binaries (663). 30 entries were ticked at the time. It was split into four tracking issues; we confirmed #576541 exists and is open.
- Commenters list per-package fix PRs (for example uv 0.13.1 to 0.13.4, merged 2026-10-20 18:34 UTC per API; the uv 0.13.4 release exists, published 2026-10-20 15:24 UTC). We did not check each other PR.
- A maintainer asked for a build hook to stop packages vendoring CA bundles. That was a discussion, with no decision seen.
- One commenter noted the CVE number in the #576485 title looks like a typo compared with the one in #576475. We did not resolve which is right, so we do not quote a CVE id as confirmed.

## What this does not tell you
- It does not say whether your machines are at risk, or whether anyone has used the keys. We found no report of abuse in what we read.
- It is not a how-to. If you run NixOS or packages from nixpkgs, read the linked issues and the vendors' own advisories, and update through your normal channel. Do not edit trust stores by hand based on this summary.

## Honest limits
- We read two web pages and the GitHub threads. We did not open the Mozilla bug or blog post or the mailing list posts, and did not check any certificate or trust store.
- We did not test the NixOS option or any package.
- Counts and per-package status come from an issue body dated 2026-10-20 and were changing as we looked.
- Most per-package PRs listed by commenters were not individually checked.
