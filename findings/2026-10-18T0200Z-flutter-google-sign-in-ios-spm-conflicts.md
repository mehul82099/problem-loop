# Flutter: google_sign_in_ios conflicts with newer iOS packages under Swift Package Manager (flutter#194435)

- Source: https://github.com/flutter/flutter/issues/194435 "[google_sign_in] Update to GoogleSignIn-iOS 10" (open, labels p: google_sign_in, package, team-ios; opened 2026-10-15 by takumiito271; 6 comments and 6 reactions when read)
- Upstream items, state checked through the GitHub API on 2026-10-18:
  - https://github.com/google/GoogleSignIn-iOS/releases/tag/10.0.0 (published 2026-09-04; the latest release the API returns)
  - https://github.com/google/GoogleSignIn-iOS/pull/626 "[App Check] Add SPM AppCheckCore 12.x support" (merged 2026-10-15 20:20 UTC)
  - https://github.com/google/GoogleSignIn-iOS/issues/655 "GoogleSignIn-iOS 10.0.0 caps AppCheckCore at 11.x and cannot coexist with firebase-ios-sdk 13" (open, opened 2026-10-16)
  - https://github.com/firebase/firebase-ios-sdk/releases (13.0.0 and 13.0.1 published 2026-10-07)
- The plugin's manifest, read from GitHub on 2026-10-18: `packages/google_sign_in/google_sign_in_ios/darwin/google_sign_in_ios/Package.swift` in https://github.com/flutter/packages, which declares `.iOS("13.0")`, `.macOS("10.15")` and depends on GoogleSignIn-iOS `from: "9.0.0"`.

## The problem
iOS dependencies are resolved by Swift Package Manager (SPM) when a Flutter project builds with SPM turned on. The Flutter Google sign-in plugin for iOS (`google_sign_in_ios`) pulls in GoogleSignIn-iOS 9.x. According to the reporter and a second commenter, that version forces `gtm-session-fetcher` below 4.0, so it cannot be combined with packages that need version 4 or 5 of it. Two examples in the thread: the ARCore iOS SDK 1.56.0 (reporter), and `firebase_messaging` 17.0.0 with firebase-ios-sdk 13.0.0 (Nazarovv676, who pasted the resolver error).

## What commenters found (attributed)
- The reporter proposes moving to GoogleSignIn-iOS 10.0.0. The release notes (which I read) say 10.0.0 is a breaking release that raises the minimum iOS to 15 and macOS to 12 and widens the `GTMSessionFetcher` range to allow 4.x and 5.x, and tell projects that must support older OS versions to stay on 9.2.0.
- qeepcologne says that widening the version range is not enough, because the plugin would also have to raise its own minimum OS to iOS 15 and macOS 12, since SPM rejects a package whose dependency needs a higher platform than the package declares. He calls it a breaking change that needs a coordinated major bump. stuartmorgan (marked CONTRIBUTOR) replied that raising a plugin's minimum OS to match Flutter's current minimum is not a breaking change, and only requires raising the minimum Flutter SDK version at the same time.
- Nazarovv676 and qeepcologne both say that GoogleSignIn-iOS 10.0.0 still cannot be combined with firebase-ios-sdk 13.0.0 because the first pins `app-check` to 11.x and the second needs 12.x. qeepcologne says he tested this with a forked manifest and filed the upstream problem. I confirmed that upstream issue 655 exists and is open, and that PR 626, which the commenter said is the change that allows App Check 12, was merged on 2026-10-15. The latest release I could see is still 10.0.0, so I cannot say whether the merged change is in any release yet.
- Workarounds mentioned in the thread (not tested by me): stay on the Firebase 12 line, or vendor the plugin with its manifest pointed at an upstream revision containing the fix.
- Tom3652 says the main blocker is firebase-ios-sdk 13.0.0.

## Status
The issue is open and has been routed to the iOS team by a triage account. No Flutter maintainer has said it will update the plugin. No pull request in flutter/packages was linked in the thread, and I did not find one by listing recent open and closed PRs, which is not a thorough search.

## What this shows and does not show
- It shows a version-range conflict whose cause is stated consistently by three commenters and is partly confirmed by upstream release notes.
- It does not show that updating the plugin to GoogleSignIn-iOS 10 would fix the Firebase 13 case; two commenters say it would not until a newer GoogleSignIn-iOS release.
- It does not show what the plugin team will do or when.

## Honest limits
- I did not build any Flutter project or run SPM, so I did not reproduce any resolver error.
- I read the `Package.swift` of the plugin and of GoogleSignIn-iOS 10.0.0 only to confirm the declared platforms and that App Check is a dependency. I did not check their version ranges line by line.
- I did not check whether CocoaPods users are affected.
