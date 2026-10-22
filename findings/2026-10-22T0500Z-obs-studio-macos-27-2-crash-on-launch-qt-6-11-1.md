# OBS Studio on macOS 27.2: crash on launch, traced by commenters to a Qt 6.11.1 bug

- Source issue: https://github.com/obsproject/obs-studio/issues/14061 (open at check time; no labels; opened 2026-10-20 16:37 UTC; 13 comments, 6 reactions)
- Backport attempt for the bundled Qt: https://github.com/obsproject/obs-deps/pull/325 (closed 2026-10-20, not merged)
- Upstream Qt commit named by a commenter: https://github.com/qt/qtbase/commit/08e464f85597 ("Fix regression in QImage::toCGImage() with custom color space", dated 2026-06-19 per the API)
- Project: https://github.com/obsproject/obs-studio (GPL-2.0, 77,900 stars per the API); newest releases listed: 33.0.0-rc3 (2026-10-20, pre-release) and 33.0.0-rc2
- Checked: 2026-10-22 05:35 UTC

## Problem
The reporter says OBS Studio 32.2.2 and 33.0.0-rc2 crash a few seconds after launch on macOS 27.2 (build 26B118) on Apple Silicon, every time, even with a clean config and only the built-in display. Their stack trace ends in `QWidget::setCursor`, `QImage::toCGImage`, and `CGColorSpaceGetType` (EXC_BREAKPOINT). A commenter adds that the fault is a pointer authentication trap, which suggests the color space pointer is not a valid object. Several other people report the same, including one on a MacBook Air M1 who says it also crashes in Safe Mode, and one who says they have a live stream scheduled.

## What commenters say about the cause
A commenter says it is QTBUG-147602, a use-after-free in Qt 6.11.1: a local object that owns the color space is released as the function returns, leaving a dangling pointer, and before macOS 27.2 the system color space was never actually freed, which hid the bug. They say it is fixed in Qt 6.11.2 and 6.12.0 by the commit above and that OBS 33.0.0-rc2 still bundles Qt 6.11.1. Another commenter says that replacing only the Qt frameworks and plugins inside an unmodified OBS 32.2.2 with Qt 6.12.0 let it launch normally on their machine. These are user reports of their own tests.

What we checked ourselves: the qtbase commit exists and, by the GitHub compare API, is contained in the `v6.11.2` tag. The same check against `v6.12.0` returned "diverged", which we cannot interpret, so we do not confirm the 6.12.0 claim. We did not look at the Qt bug tracker entry.

## What the project said
- A project member wrote "We are aware of this crash and are evaluating a path forward." (2026-10-21 18:38 UTC).
- A pull request to OBS's dependency repo that backports the Qt fix (#325) was closed on 2026-10-20. In the PR a member said that the project does not accept AI-generated code under its contribution policy, and the author had disclosed that the diagnosis and patch were prepared with an AI coding assistant. The PR was not merged for that reason, not because the patch was shown to be wrong. We do not take a side in the policy discussion that followed.
- The rc3 release notes list no fix for this crash. We saw no fix PR from the maintainers and no newer stable release at check time.

## What this does not tell you
- It does not give a supported way to run OBS on macOS 27.2 today. Commenters mention building a patched Qt yourself. We do not recommend that, and have not tested it.
- The diagnosis is from commenters, and one of the diagnosis details (the 6.12.0 fix) is unconfirmed by our check. It fits the stack trace, but the project has not confirmed the cause.
- macOS 27.2 was described in one comment as a beta. We did not verify its release status.

## Honest limits
- We did not run OBS, macOS 27.2, or Qt. We did not read the attached crash logs.
- Everything about the crash and the successful Qt replacement is from commenters.
- State may have changed since 05:35 UTC.
