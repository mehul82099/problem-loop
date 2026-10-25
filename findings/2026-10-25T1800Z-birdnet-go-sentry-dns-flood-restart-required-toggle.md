# BirdNET-Go's Sentry flood: a blocked telemetry domain becomes a DNS storm, and the off switch needs a restart

- Source issue: https://github.com/tphakala/birdnet-go/issues/4813 (open; labels bug, pkg:telemetry, awaiting-dump; opened 2026-10-24 16:20 UTC)
- Project: https://github.com/tphakala/birdnet-go (~2.4k stars; bird-song monitor for Raspberry Pi)
- Checked: 2026-10-25 18:15 UTC

## Problem
A Pi-hole user watched birdnet-go fire multiple DNS queries per second at Sentry's ingest domain. Two small mechanics combine into the storm: error tracking reports failures to Sentry, and every attempt - including ones the DNS filter will block - triggers a fresh DNS query, with no caching or backoff. The busier the underlying error, the bigger the flood.

## The details matter here (all attributed or verified)
- Telemetry really is opt-in: the repo's own config template says `sentry.enabled: false` with "false by default, must be explicitly enabled by user" (verified in internal/conf/config.yaml). So this install had it on - possibly the third-party DietPi package default, possibly the user; the thread does not say.
- The user toggled Error Tracking off and reported the queries continued. But the log excerpt they pasted is timestamped *before* the toggle - and the owner's reply resolves the likely confusion: the setting change requires an application restart to take effect. A privacy toggle that silently stays on until restart is its own small UX trap.
- The support dump the maintainers need is itself blocked by a second bug the same user hit (#4814, verified: closed; a duplicate-key database error after updating) - two bugs colliding in one report.
- The flood's root trigger is still unknown: something is erroring in the background on this install, and nobody has the logs yet.

## What this does not tell you
- Whether the DNS storm persists after a restart with tracking off; unverified at check time.
- Whether the DietPi packaging changes the opt-in default; not established in the thread.

## Honest limits
- We read the issue and comments and verified the config default and the cross-referenced issue via GitHub. We did not run birdnet-go; the DNS log is the user's.
- This finding does not advise anything beyond what the thread itself says: the owner's stated fix for the toggle is a restart.
- Issue state may have changed since 18:15 UTC.
