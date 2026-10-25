# The .NET security release that broke CI: aka.ms pointed at a storage account refusing public access

- Source issues: https://github.com/actions/setup-dotnet/issues/794 (open; bug, needs triage; opened 2026-10-25 19:42 UTC) and https://github.com/dotnet/core/issues/10660 (release announcement, open)
- Checked: 2026-10-25 20:15 UTC

## Problem
Within hours of Microsoft's October 2026 out-of-band .NET security release (the Brotli CVE-2026-111497 builds, announced in dotnet/core#10660), CI pipelines worldwide started failing in `actions/setup-dotnet` and anything using `dotnet-install` with a channel: the `aka.ms` latest-version links redirected to `dotnetorigin.blob.core.windows.net`, and every blob there answered 409 "Public access is not permitted on this storage account". Reports in setup-dotnet#794 span v5 and v6 of the action, Windows and Linux, runtime and SDK (10.0.14, 10.0.403, 8.0.427).

## What the thread established (community diagnosis, attributed)
- Commenters toby6578 and dylan-smith traced it precisely: the redirect target storage account lost public access, and even *older* builds on that host (10.0.12/10.0.13) returned 409 - so the whole host was locked down, not just the new artifacts. The same files served fine from the `builds.dotnet.microsoft.com` CDN. Their curl transcripts are in the thread.
- A viable dodge existed for pinned installs: passing an exact `--version` makes dotnet-install skip the aka.ms channel lookup entirely.

## What we verified directly
- At 20:14 UTC, `aka.ms/dotnet/LTS/dotnet-runtime-linux-x64.tar.gz` now 301s to `builds.dotnet.microsoft.com` (200) instead of the blob host - the redirect was repointed, which matches the "working now" reports in the thread around 20:24 UTC.
- The blob URL itself still returns 409; the fix was routing around it, not unlocking it. Total user-visible breakage window: roughly one hour.

## Honest limits
- The root-cause *explanation* (storage account misconfiguration during release) comes from community members, not Microsoft; no official postmortem was linked at check time.
- We verified redirect behavior with curl; we did not rerun a setup-dotnet workflow.
- Incident state may have evolved since 20:15 UTC.
