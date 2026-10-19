# Tauri on Linux: the long request to bundle a Chromium renderer (tauri#14963)

- Source: https://github.com/tauri-apps/tauri/issues/14963 "Bundle chromium renderer". Opened 2023-11-08, open, 76 comments, 242 reactions on the post, labels "type: feature request" and "scope: cef". Last comment 2026-10-19.
- Checked by GitHub API on 2026-10-19: a branch `feat/cef` exists in tauri-apps/tauri (last commit 2026-10-07). The latest Tauri release is tauri-v3.0.0-alpha.5 (2026-10-14).
- Linked: https://v2.tauri.app/blog/tauri-verso-integration/ (Tauri blog, dated 2025-03-17) and https://github.com/chromiumembedded/cef/issues/3836 "Shared installation support" (closed).

## What was requested
Tauri apps use the operating system's web view: WebKitGTK on Linux. The opener says WebKitGTK performs badly and breaks often, and asks for the option to bundle a Chromium-based renderer, like Electron does, for consistent behavior and easier testing.

## What the Tauri team has said (by a member, FabianLars)
- 2024-05: the team has "completely stopped defending webkitgtk", is aware of the problem, and he warns people against using Tauri-like frameworks on WebKitGTK when Linux is a serious target. They considered moving to the WebKitGTK 6.0 port, and said CEF (Chromium Embedded Framework) could not make Tauri v2.
- 2026-02-17: on CEF he points to the `feat/cef` branch, says it is "more like source available than open source since most of the development happens at work", and explains how to try it with a feature flag and a branch of the CLI. On Servo: further development is halted for lack of funding or manpower. On alternatives: they are looking at QtWebEngine, and work happens in a separate repository but will be paused for a while.
- 2026-04-03: "the branch is mostly usable", but anyone using it is on their own, and to report issues.
- 2026-05-18: Chromium instances would not be shared between apps in the foreseeable future. Sharing needs upstream CEF work (the issue linked above is the one he calls the main upstream issue). An Arch Linux CEF package does not solve the versioning problem, he says, because apps would need recompiling for that version.

## What users said
- Some say Linux performance was the main pain point in their apps. Others say they moved to Electron already, or run an Electron sidecar. These are their reports.
- Opposing view (2026-05-18): many pick Tauri for small bundles, and shipping Chromium (200 MB or more) would hurt that. Replies: let developers pick the trade-off, and a shared Chromium install would remove the size problem. The member answers that sharing is not available now.
- 2026-06-16: a contributor (chrox, of the Readest app) says they plan to try the CEF branch. On 2026-10-03 the same account says Readest 0.12.8 runs every Linux build on the Tauri CEF runtime and describes the packaging changes. I did not verify this in Readest's own repository.
- 2026-10-03: another commenter says GTK4 support in the v3 alpha is not ready for them (fractional scaling on X11, and a GTK 4.14 requirement that excludes Ubuntu 22.04 and Debian 12). That is his own report.
- 2026-10-19: a commenter says CEF is already usable as a runtime in the Tauri v3 alpha and has wrapped it in a small plugin of his own.

## What can be said
- Compared with last year, the CEF route has gone from "not before v3" to a working branch and at least one app shipping on it, by that app's maintainer. It is not a stable, supported, shared-bundle feature, by the team's own statements.
- The trade-offs people raise (bundle size and no sharing across apps versus consistent rendering) are unresolved in the thread.

## Honest limits
- I did not run Tauri, CEF or any Linux build, so I can't judge performance claims.
- I did not read the `feat/cef` code or release notes for v3 alpha. I did not check which features are in alpha.5.
- Statements by commenters about other projects (Electron moves, OpenCode, Readest) are theirs and unverified.
