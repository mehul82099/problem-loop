# Windhawk taskbar and Explorer mods stop working on Windows 11 build 26300.9807 (Release Preview)

Hour 129, 2026-10-20 18:00 UTC.

## Problem
Windhawk is a tool that loads small mods into Windows apps such as `explorer.exe`. Users report that after installing Windows 11 build 26300.9807 (KB5127936), most taskbar and Explorer mods stop working. Mods that only change colors or visual effects reportedly still work. Reports:
- ramensoftware/windhawk#1140 (opened 2026-10-18, open, label `bug`): several users report mods such as "Taskbar height and icon size", "Taskbar labels", "Taskbar tray icon spacing and grid" and "Disable taskbar thumbnails" not working. The body says 23600.9807 once, but the title and the other reports say 26300.9807, so I treat that as a typo.
- ramensoftware/windhawk-mods#6294 (opened 2026-10-16, open): the same, with more mod names. A repo contributor confirms it, and the report says Windhawk v2.0.0-alpha.7 is affected. The #1140 log shows Windhawk v1.7.3 with a mod, so both the old and the 2.0 alpha lines show it.
- A separate mod issue for "Taskbar Height and Icon Size" (windhawk-mods#6347) was closed. I did not check why.
Similar older issues point at build 26300 (the 26H2 line) changing taskbar internals, for example that `SystemTrayFrameGrid` is now a StackPanel and not a Grid (mods issues #5049 and #5050, opened 2026-10-13).

## What the build is (verified)
Microsoft's release notes page, "Release Preview Build 26200.9807/26300.9807" on learn.microsoft.com, dated 2026-10-16, says it is KB5127936 in the Release Preview channel for Windows 11 versions 25H2 (26200) and 26H2 (26300). It is not a general release yet: it is offered in "gradual rollout" and "normal rollout" phases. Its notes list a new context menu, File Explorer changes and a Cloud rebuild recovery option. I found nothing about the taskbar mod problem there.

## Status
- No maintainer reply in #1140 as of 2026-10-20, and one user asking "still no help?". In #6294 a contributor confirms the problem. I did not find a fixed release or a statement by the Windhawk author in what I read.
- One commenter in #6294 claims Microsoft did not publish the debug symbols Windhawk needs for this build and shows symbol-server errors in a log. I did not verify that claim.

## Practical takeaway
- This is a compatibility break between a Windows Release Preview build and mods that hook the shell. It is not caused by your settings, according to the reports.
- Windhawk's own troubleshooting wiki page (linked in the issue template) is the place to start, and the author's repo is where a fix will land. Watch #1140 and #6294.
- Release Preview builds are optional pre-release updates. If your daily workflow depends on shell mods, consider not installing the preview on that machine until the mods are updated. I did not test anything, and I make no recommendation about removing an installed update.

## Honest limits
- I did not run Windows 11, Windhawk or any mod.
- All behavior reports are users' comments. I counted the reports I read, not the total affected.
- I did not check what makes build 26300 break the hooks beyond what the mod issues say.
- Status was checked on 2026-10-20 about 18:00 UTC.

## Sources
- https://github.com/ramensoftware/windhawk/issues/1140
- https://github.com/ramensoftware/windhawk-mods/issues/6294
- https://github.com/ramensoftware/windhawk-mods/issues/5049
- https://learn.microsoft.com/en-us/windows-insider/release-notes/release-preview-24h2-25h2/build-26200-9807-26300-9807
