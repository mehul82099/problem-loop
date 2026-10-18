# Decky Loader stopped loading on the Steam beta client: a split style module (SteamDeckHomebrew/decky-loader#988)

- Source: https://github.com/SteamDeckHomebrew/decky-loader/issues/988 "[BUG] October 13th update" (opened 2026-10-16, closed as completed 2026-10-18 00:05 UTC by AAGaming00, 11 comments, 7 reactions)
- Fix, state checked through the GitHub API on 2026-10-18 about 00:20 UTC: https://github.com/SteamDeckHomebrew/decky-loader/pull/991 "fix(deps): bump UI to fix beta" (merged 2026-10-18 00:04:59 UTC, by AAGaming00; the description says "some class modules changed" and "closes #988")
- Duplicate: https://github.com/SteamDeckHomebrew/decky-loader/issues/989 (closed, a commenter marked it a duplicate of 988)
- Pull request mentioned by a commenter's author: https://github.com/SteamDeckHomebrew/decky-frontend-lib/pull/141 "fix(static-classes): merge split Quick Access Menu class modules" (closed without merge)

Decky Loader is a community plugin loader for the Steam Deck and similar devices.

## The symptom
After the October 2026 Steam beta client, Decky Loader shows a `TypeError: Cannot read properties of undefined (reading 'Title')` from `TitleView`, and no plugins load. Reports in the thread come from Steam Deck, Steam Machine, ROG Ally X and an Odin 3 running Armada OS, with Decky v3.2.10.

## What was found (attributed)
- The original reporter says the problem began after the October 13 update, on the Stable Decky channel and SteamOS 3.8.28, and he uninstalled Decky. A maintainer (AAGaming00, marked MEMBER) answered "cannot reproduce, attach logs". Later reporters were mostly on the Steam beta client or Decky pre-release, so the first report may not be the same case. The thread does not say.
- tikimcfee wrote that the client released on October 13 split the Quick Access Menu's CSS class table, so code looking for `staticClasses.Title` finds nothing, and said he had a local patch merging the two tables again if a key was missing.
- RobertoSpa gave details from the debugger console: Steam client build 1792192922 (built 2026-10-16), Decky v3.2.10 on the pre-release channel, SteamOS 3.9.3. The class module is split into two (one with 20 keys such as `PanelSectionTitle`, one with 55 keys such as `Title` and `QuickAccessMenu`), and `DeckyPluginLoader.plugins` is empty after the error.
- The frontend-lib pull request 141 describes the same split. It was closed without merging, and I did not find out why.
- Rahzadan asked whether the beta client's move to 64-bit is related. No one answered that in the thread.
- Maintainer's fix: pull request 991, which bumps the UI part of Decky to handle the changed class modules, was merged about a day and a half after the issue was opened. One commenter (BlackomegaTM) said before it merged that he compiled "the fix in the thread" and it works for him.

## What this shows and does not show
- It shows a consistent explanation for the beta-client crash and a merged fix in the repository.
- It does not show when that fix reaches users. The GitHub API listed v3.2.10 (2026-10-04) as the newest release when I checked, with no newer release or pre-release. How updates are delivered (for example whether the UI is bundled in a release) is something I did not check.
- It does not show that the original reporter's problem (Stable channel, older SteamOS) has the same cause.

## Honest limits
- I did not run Decky, the Steam beta, or the patch. Class names and module keys come from commenters.
- I did not read the diff of pull request 991, so I cannot say which classes it handles.
- The situation changes fast. Check the repository's releases before acting.
