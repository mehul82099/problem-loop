# AlDente Pro 1.40 makes clamshell-mode displays drop every few seconds - eight users, no developer reply yet

- Source issue: https://github.com/AppHouseKitchen/AlDente-Battery_Care_and_Monitoring/issues/1858 (open; no labels; opened 2026-10-24 20:04 UTC)
- Project: https://github.com/AppHouseKitchen/AlDente-Battery_Care_and_Monitoring (~9.2k stars; issue tracker for the macOS battery app)
- Checked: 2026-10-25 12:10 UTC

## Problem
Immediately after updating to AlDente Pro 1.40, a MacBook in clamshell mode (lid closed, external displays) starts dropping both displays every few seconds - screen dark, music stops, lock-screen flicker - then they come back. Opening the lid or quitting AlDente stops it. The reporter attached a debug bundle and video.

## Thread state
- Eight users confirm "same here" across at least two macOS versions (26.7.1 and Sequoia per comments) within 16 hours; several attach debug files.
- User-reported workarounds: quit the app, or downgrade to 1.39.4 (one user reports the downgrade fixed it; we have not verified the downgrade path or its safety).
- One paying user wrote "I'm a paid user but will be uninstalling, sorry."
- No developer or maintainer response at check time. AlDente is a paid product (Pro tier) and this is its public tracker; the regression has been visible there for ~16 hours with no acknowledgment.

## Why it is notable
Charge-limit software sits in the power path, and this bug shows the blast radius when it misfires: whatever 1.40 changed is aggressive enough to trigger macOS display/lock behavior every few seconds, but only in clamshell mode - a config where the app's whole user base relies on external displays. The thread is also a small study in regression triage by pattern: lid open vs closed, app on vs off, version 1.40 vs 1.39.4.

## What this does not tell you
- What changed in 1.40; AlDente Pro is closed-source and the thread has no developer diagnosis.
- Whether free-tier users are affected; reporters so far are on Pro.
- Whether the downgrade is officially supported or safe for settings/battery calibration data - it is one user's report.

## Honest limits
- We read the issue and all nine comments via the GitHub API. We did not run AlDente or macOS; every behavior claim is a user's.
- Issue state may have changed since 12:10 UTC.
