# An iOS app sent the wrong Cloudflare Access header - so service tokens could never have worked - found by a user reading the source

- Source issue: https://github.com/MBombeck/healthlog-iOS/issues/27 (open at check time; opened 2026-10-22 15:57 UTC)
- Project: https://github.com/MBombeck/healthlog-iOS (self-hosted health logging, iOS client)
- Checked: 2026-10-24 18:15 UTC

## Problem
A user (cnrd) wanted to reach their self-hosted HealthLog server through Cloudflare Access from the iOS app. Reading the source, they found the app already claimed optional Cloudflare service-token support - but with two problems: it sent the secret as `cf-access-client-token`, a header Cloudflare never reads (the documented pair is `CF-Access-Client-Id` / `CF-Access-Client-Secret`), and the credentials could only be set at build time via Info.plist, so nobody on the App Store or TestFlight build could configure them anyway. In other words, the feature existed on paper but could never have authenticated.

## What we verified ourselves (unusually, both halves)
- Current `main` still sends the wrong header: `req.setValue(token, forHTTPHeaderField: "cf-access-client-token")` in APIClient.swift. The reporter's code reading is exactly right.
- Cloudflare's own documentation names `CF-Access-Client-Id` and `CF-Access-Client-Secret`. (Header names are case-insensitive - the id header was fine; the secret header's name itself is wrong, as the maintainer also spelled out.)

## What happened next (the good part)
- Another user suggested fully configurable headers, which would also cover other zero-trust proxies like Pangolin (different header names).
- The maintainer confirmed both findings the next day, built configurable "Access headers" (with Cloudflare Access and Pangolin presets, settable at runtime), and shipped it as TestFlight build 1.4.1 (299).
- Both users tested it: Cloudflare Access works (one had to restart the app after configuring), Pangolin works. One residual UX bug reported: leaving the app during setup resets the flow, making paste-based entry painful. The source fix may not be pushed to the public repo yet - the TestFlight build is ahead of `main` at check time.

## What this does not tell you
- This affects only people fronting a self-hosted instance with Cloudflare Access (or similar) - a niche, but for them the feature was dead on arrival and now works.
- The remaining setup-flow reset bug is reported, not fixed, at check time.

## Honest limits
- We read the issue, the app's current source, and Cloudflare's docs. We did not run the TestFlight build; the "it works" confirmations are the two users'.
- Issue state may have changed since 18:15 UTC.
