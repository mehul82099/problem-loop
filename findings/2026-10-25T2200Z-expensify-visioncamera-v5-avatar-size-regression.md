# A camera library upgrade made Samsung photos too big to be avatars: Expensify's deploy blocker

- Source issue: https://github.com/Expensify/App/issues/104941 (open; labels DeployBlockerCash, Bug; opened 2026-10-25 21:53 UTC)
- Causing change: https://github.com/Expensify/App/pull/102898 (verified: "Upgrade react-native-vision-camera from v4 to v5", merged 2026-10-22)
- Checked: 2026-10-25 22:16 UTC

## Problem
On Android 16 Samsung devices, taking an avatar photo in the Expensify app now fails with a "size exceed" error - in staging only, not production. Regression testing caught it days after the app upgraded its camera library, react-native-vision-camera, from v4 to v5.

## Why it is interesting
- The mechanism, per Expensify's MelvinBot deploy-blocker analysis (tooling output, flagged as such in the thread): VisionCamera v5 picks the photo capture resolution differently than v4, and on some Samsung cameras it now captures at something like 4000x3000. The in-app camera passes the file through without resizing, and the avatar validator rejects anything over 6 MiB - before the user even reaches the crop step that would have shrunk it. A silent default change in a major-version native dependency, surfacing three layers away.
- The process worked exactly as designed: exploratory QA caught it on staging, the issue was labeled a deploy blocker within minutes, bots auto-assigned the PR author and reviewers, and production never shipped the regression. "Reproducible in staging: yes; production: no" is the whole point of a staging gate.
- The trade-off the team now faces, also from the bot's analysis: fix forward (resize captures over ~2880px before validation) or revert - and the revert is expensive, rolling back a native upgrade plus receipt, odometer, and attachment camera migrations.

## Honest limits
- The root-cause mechanism is MelvinBot's analysis, which itself states "medium confidence on the exact mechanism, because it hasn't been checked on a device"; no human maintainer had confirmed it at check time.
- No fix PR existed at check time (searched Expensify/App for PRs referencing the issue).
- The bug report comes from Applause contract QA, and the device list is narrow (Samsung, Android 16); scope beyond that is untested.
- Issue state may have changed since 22:16 UTC.
