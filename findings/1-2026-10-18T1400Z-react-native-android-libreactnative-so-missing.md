# React Native on Android: "SoLoaderDSONotFoundError: couldn't find DSO to load: libreactnative.so" in production crash reports (react-native#55637)

- Source: https://github.com/react/react-native/issues/55637 (open since 2026-02-20, 63 comments, labels "Needs: Author Feedback" and "Needs: Repro", last updated 2026-10-18). The repo owner is shown as `react` in the API today, and the reporter's older links point at `facebook/react-native`.
- Earlier issues named by the reporter, state checked by API: https://github.com/react/react-native/issues/49111 (closed as completed 2025-03-03, titled "SoLoaderDSONotFoundError on Android 11 Emulator") and https://github.com/react/react-native/issues/55562 (open at the time I looked).

## The report
The reporter (React Native 0.83.1, new architecture and Hermes on) says production Android devices, mainly Android 11 and 12, crash at start with `SoLoaderDSONotFoundError: couldn't find DSO to load: libreactnative.so`, with a list of "existing SO sources" in the log. He has no reproduction steps beyond "run app". The project bot asked for a reproducer on 2026-02-20, and the thread has no maintainer reply that I could find, so the labels have been there since.

## What commenters add (all unverified user reports)
- Versions: reports on RN 0.81, 0.83, 0.84 and 0.86, with Expo 54 to 57, through 2026-10-18. Some crashes mention `libc++_shared.so` instead of `libreactnative.so`.
- A frequent suggestion is `jniLibs { useLegacyPackaging = true }` in `android/app/build.gradle`. Two people say it stopped the crashes, and at least one says Crashlytics still showed the crash after trying it.
- Several people say it only appears with an Android App Bundle (`bundleRelease`) and went away after switching to `assembleRelease` (an APK). That is a few anecdotes. Another person suggests removing a leftover `SoLoader.init(this, false)` in `MainApplication.kt`, after an upgrade-helper diff, and says he is still waiting to see whether it works. Others suggest pinning the `react-native` version in package.json.
- A growing group says almost all of their crashes are from a single device model, the LG Nexus 5X reported as Android 13, even though the phone officially stopped getting updates at Android 8.1. Several developers say none of their testers use that model, that reports arrive in bursts within seconds of each other, and that they cluster around the day after a release. One commenter lined up crash dates with release dates. They conclude it is probably Google Play's automated testing, but that is their inference. Nobody in the thread has confirmation from Google or from the React Native team, and one commenter notes the crash still counts against crash-free-user numbers.
- One commenter pastes a long answer from ChatGPT suggesting initialising SoLoader by hand. It is unverified, and I do not endorse it.
- The error output in several comments lists `lib/x86_64` folders on devices whose model is ARM, and some lists have an arm64 folder only. I did not analyse what this means.

## What this suggests, carefully
Two separate things may be mixed in one thread: real crashes on user devices that look like packaging or ABI problems, and crashes that only show up as bursts on one odd device model and may come from automated testing. The thread does not separate them, and I can't tell from comments which one a given report is.

## What this does not say
- It does not say which workaround is right. `useLegacyPackaging` changes how native libraries are packaged and installed, which can increase install size. Whether that is acceptable is for each app team to decide after testing.
- It does not say the Google Play bot theory is true.
- It does not say the bug is in React Native rather than in AGP, SoLoader or the device.

## Honest limits
- I read the issue body and the comments, including most of the later ones. I did not build an app, install a bundle, or open any of the linked traces beyond the pasted text.
- I could not verify that issue #55562 was ever "closed without resolution" as the reporter says, only that it is open today.
- The thread has no maintainer diagnosis, so the cause is unknown.
