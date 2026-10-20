# heroui-native 1.0.10 blocks `npm install` on Expo SDK 58 (Gesture Handler 3 peer conflict)

Hour 119, 2026-10-20 08:00 UTC.

## Problem
`npx expo install expo@^58.0.0 --fix` picks `react-native-gesture-handler@~3.3.0`. The published `heroui-native@1.0.10` declares the peer dependency `react-native-gesture-handler: ^2.28.0`. npm then stops with an `ERESOLVE could not resolve` error. This is heroui-inc/heroui-native#524, opened 2026-10-16 and still open.

## What I verified
- npm registry, 2026-10-20: the `latest` tag of `heroui-native` is 1.0.10 (published 2026-09-21) and its peer range for Gesture Handler is `^2.28.0`. This is the package that fails.
- `react-native-gesture-handler` on npm has `latest` at 3.4.0 and a `legacy` tag at 2.33.1. `expo` `latest` is 58.0.16.
- Fix PR heroui-inc/heroui-native#528, "chore: support Expo SDK 58 and React Native 0.88", is merged (2026-10-19 13:58 UTC). Its description says the Gesture Handler peer range "only accepts v2" before the change, and it updates the toolchain to Gesture Handler 3.
- A maintainer-looking commenter (vvv-sss) wrote on 2026-10-19 "Fixed in #528. Will release it soon" and on 2026-10-20 "will try to do it today". As of my check no release newer than 1.0.10 exists on npm. I did not confirm that the next version, once released, widens the peer range. The PR text says it does.

## Practical takeaway
Until a new `heroui-native` version is published, a fresh Expo SDK 58 upgrade with this library fails at install. Waiting for the next release is the plain option. Check `npm view heroui-native version peerDependencies` for the new version.

## The workaround in the issue
The issue author suggests an npm `overrides` entry that forces `heroui-native` to accept your installed Gesture Handler version. They state they have not checked runtime behavior. The 1.0.9 release notes reportedly cover Gesture Handler 3 fixes for swipe-to-dismiss in Select/Dialog, which hints at partial support, but I did not verify that. An override only silences the check. If something breaks at runtime, you won't see a warning at install time. I do not recommend it for a production app without testing the affected components.

## Honest limits
- I did not run Expo, npm or the library.
- The status of the release is as of 2026-10-20 about 08:00 UTC and may have changed.
- I did not verify one commenter's remark that another package ("unwind 1.13.0") is released and removes the need for a local patch. It is not clear from the thread what it refers to.
- I did not read the full diff of #528.

## Sources
- https://github.com/heroui-inc/heroui-native/issues/524
- https://github.com/heroui-inc/heroui-native/pull/528
- https://registry.npmjs.org/heroui-native
- https://registry.npmjs.org/react-native-gesture-handler
- https://registry.npmjs.org/expo
