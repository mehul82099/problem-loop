# Obtainium's cert-store fix trips GrapheneOS's dynamic-code-loading guard - and there is no good option

- Source issue: https://github.com/ImranR98/Obtainium/issues/3442 (open, pinned by the maintainer; labels bug+enhancement; opened 2026-10-24 04:08 UTC)
- Project: https://github.com/ImranR98/Obtainium (~20.8k stars, GPL-3.0)
- Checked: 2026-10-25 03:05 UTC

## Problem
After updating to Obtainium 1.7.2, GrapheneOS users get the system warning "Obtainium tried to perform DCL via memory" - GrapheneOS flagging dynamic code loading via memory, a hardening restriction.

## The tradeoff, per the maintainer (verified where possible)
- Maintainer ImranR98 explains 1.7.2 switched HTTP requests to the cronet_http package so Obtainium uses Android's built-in certificate store fully - previously Flutter ignored user-added/removed certs, and Obtainium had even baked in certs for specific sites. The v1.7.2 release notes confirm "Use embedded Cronet and the Android trust store (#3200) (#3172)" (verified).
- But Cronet's Dart callback path (package:jni) triggers GrapheneOS's RESTRICT_MEMORY_DCL. He links two upstream issues: flutter/flutter#191385 (verified exists - and note it was closed 2026-09-01 as "not being tracked in the Flutter issue tracker") and dart-lang/sdk#64137 (verified open: "investigate ways to run AOT compiled code on Graphene OS when DCL is restricted").
- The maintainer's stated workaround is a GrapheneOS settings toggle for the app (Settings > Apps > Obtainium > Exploit protection > Dynamic code loading via memory > allow). He also says he missed it because GrapheneOS allows DCL by default, so most users never see the warning.
- Users push back in the thread: allowing DCL makes it "impossible to fully trust that all the code in the app has been signed by the developer". The maintainer argues the fix is worth keeping - the OS, not each app, should own certificate handling - and has pinned the issue rather than reverting.

## Why it is interesting
A correct-on-paper improvement (respect the OS trust store instead of app-level cert hacks) collides with a correct-on-paper hardening (block in-memory dynamic code loading), and the only fix lives upstream in Dart/Flutter. Everyone is right; users in the middle get a scary warning.

## What this does not tell you
- Whether Dart/Flutter will ship a fix or a timeline; dart-lang/sdk#64137 has one comment at check time.
- Whether Obtainium might later offer a non-Cronet fallback build; the maintainer has not offered one.

## Honest limits
- We read the issue, its comments, the v1.7.2 release notes, and the two upstream issues via the GitHub API. We did not run Obtainium or GrapheneOS.
- The settings-toggle workaround is the maintainer's own instruction; whether to relax a hardening flag is each user's call - this finding does not advise it.
- Issue state may have changed since 03:05 UTC.
