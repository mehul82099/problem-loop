# Four missing bytes break the handshake: how a Go upstream sync broke Xray's REALITY mimicry

- Source issue: https://github.com/XTLS/Xray-core/issues/7243 (open; opened 2026-10-23)
- Project: https://github.com/XTLS/Xray-core (~42k stars)
- Verified anchors: releases v26.10.21 (broken) and v26.9.9 (working); XTLS/REALITY commit 3c98159 "Sync upstream Go 1.27+" (2026-09-20)
- Checked: 2026-10-26 11:25 UTC

## Problem
Since Xray v26.10.21, every authenticated REALITY connection fails when the camouflage target answers with an empty TLS EncryptedExtensions - no SNI ack, no ALPN. The server logs `hs.handshake() err: payload[0]: 8, padding: -4`. The previous release works against the same target.

## The mechanism (reporter's analysis, corroborated in-thread)
- REALITY's trick is mimicry: the server replays a recorded handshake flight from the real target. The Go 1.27+ sync in XTLS/REALITY added a polite correctness fix - ack the SNI (`serverNameAck = true`) whenever the client sent one. But an authenticated REALITY connection always carries SNI, and the recorded target flight's EncryptedExtensions had no ack. The new code emits a 32-byte message where 28 were recorded; padding computes to -4 and the handshake aborts.
- A commenter explains why the "obvious" fix is wrong: clamping negative padding to zero in the mimic layer would let a 32-byte EncryptedExtensions go out against the 28-byte recording, shifting Certificate and everything after it by 4 bytes. The right fix is at the source: don't set the ack on REALITY's side.
- That fix is no longer hypothetical: a contributor reproduced the failure on a loopback rig with OpenSSL and tested the reporter's suggested patch (dropping the ack in REALITY's server) - it clears the failure and today's working targets keep working.
- A maintainer has now engaged with the design question that decides the patch's fate: how common is an empty EncryptedExtensions in real traffic? (asked in Chinese in the thread).

## Honest limits
- The byte-level narrative comes from the reporter and two commenters; we verified the releases and the upstream-sync commit via GitHub but did not run the reproduction rig.
- The tested patch is unofficial; no merged fix or maintainer-approved approach at check time.
- Users in the thread report rolling back to older versions works; this finding does not advise on version choices.
- Issue state may have changed since 11:25 UTC.
