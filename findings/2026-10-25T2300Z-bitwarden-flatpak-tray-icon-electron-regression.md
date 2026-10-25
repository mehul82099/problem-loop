# Bitwarden's broken Linux tray: a Chromium change two projects upstream broke every Flatpak Electron app's StatusNotifierItem

- Source issue: https://github.com/bitwarden/clients/issues/24012 (open; opened 2026-10-21)
- Upstream: https://github.com/electron/electron/issues/53307 (verified: "StatusNotifierItem broken in Flatpak", closed, labeled blocked/upstream) → Chromium issue 554905106
- Project: bitwarden/clients (~14k stars)
- Checked: 2026-10-25 23:16 UTC

## Problem
Bitwarden Desktop 2026.10.0 on Linux Flatpak cannot register its tray icon as a StatusNotifierItem. On KDE Plasma the fallback is a blurry, oversized legacy XEmbed icon that ignores clicks, plus a second generic "background app" icon - two broken Bitwarden entries where one working icon used to be.

## The dependency-chain story (verified link by link)
- The reporter did the bisection work: 2026.9.1 shipped Electron 43.2.0 (last known good); 2026.10.0 ships Electron 43.5.0 (affected). The regression window is Electron 43.3.0+ inside Flatpak sandboxes.
- Electron's own tracker confirms the shape: electron/electron#53307 is titled exactly "StatusNotifierItem broken in Flatpak" and carries a blocked/upstream label. A contributor there traced it further to a Chromium regression (upstream tracking issue 554905106) in how the tray service name gets registered.
- So the chain is: Chromium change → Electron 43.3.0+ → Bitwarden 2026.10.0 Flatpak → broken tray on KDE Plasma. Any Flatpak Electron app on those versions is presumably in the same boat; Bitwarden is just where it got reported well.
- Bitwarden has escalated internally (tracked as PM-45451 per their bot and a collaborator), but an app-side fix is limited until the upstream fix propagates.
- One caution on symptom-matching from the thread: a duplicate-tray-icon complaint looks identical, but bitwarden/clients#22124 (verified open since July 2026) predates this Electron build by months - same symptom, older and separate cause.

## Honest limits
- The Electron version bisection and Plasma behavior are the reporter's; we verified the linked issues and their labels/state via GitHub's API, not by running the Flatpak.
- The Chromium issue is referenced from the Electron thread; we did not verify its current status on the Chromium tracker.
- Whether Electron 45 (the milestone on the upstream issue) resolves it, and when Bitwarden picks that up, is unsettled at check time.
- Issue state may have changed since 23:16 UTC.
