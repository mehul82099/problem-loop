# Claude Desktop (Windows Store/MSIX) ignores `--user-data-dir` since 2.42304.0

- Source issue: https://github.com/anthropics/claude-code/issues/103068 (open, labels: bug, platform:windows, area:desktop; opened 2026-10-17)
- Checked: 2026-10-20 19:10 UTC

## Problem
Users who ran two Claude Desktop accounts side by side on one Windows login, by starting a second copy with `--user-data-dir=<dir>`, report that this stopped working after the Microsoft Store (MSIX) build 2.42304.0.

Reporter's description (unverified by us):
- With the default instance running, the second copy hands off to it and exits, and the default window comes to the front.
- With nothing running, the second copy stays alive but shows the default profile, not `<dir>`.
- It worked from v2.26454.0 through v2.37337.1. The reporter says the 2.42304.0 changelog does not mention a change to launch arguments or data folders.

## What other commenters say
- One commenter (2026-10-19) says they read the 2.42304.2 main bundle. Their claim: a new "user-data move" step computes its target from `LOCALAPPDATA` only (`%LOCALAPPDATA%\Claude-Data\<package family>`). Once the default profile has moved there, every launch is sent to that folder whatever `--user-data-dir` says. Their suggested fix: treat an explicit `--user-data-dir` like the existing `CLAUDE_USER_DATA_DIR` and skip the move.
- Another commenter (2026-10-20) describes the same mechanism from the app logs (`[user-data-move] already_moved`) and says it is enabled per account.
- Same commenter reports that after an auto-update to 3.1623.0 their `--user-data-dir` instances log `stay_chosen_folder`, a reason they had not seen in 2.42304.2, and speculates a proper fix may be arriving. They asked others on 3.1623.0 without a workaround to confirm. We saw no confirmation in the thread.
- A third account confirms the symptoms on 2.42304.2.

## Workarounds in the thread (not endorsed here)
Two commenters posted workarounds. One changes the `LOCALAPPDATA` value for the second copy; another moves profile folders and creates a blocker file. A later comment in the same thread says the first approach breaks MCP servers started through `npx`. One workaround also removes an "Open with" registry entry according to its author. A third-party tool, thomasog/multi-claude (MIT, created 2026-10-13, 5 stars at check time), is linked as applying the workaround.

We did not run any of this. Moving or deleting profile folders can lose sign-in state and data. This finding does not advise any of it. Anyone considering it should read the original comments and back up first.

## Cross-references verified by API
- anthropics/claude-code#98613: Cowork VM ID derived from user SID only, second instance cannot start its VM. Closed.
- anthropics/claude-code#98549: sign-in from a second `--user-data-dir` instance completes in the first instance. Open.
- anthropics/claude-code#18435: feature request for multiple accounts in Claude Desktop with easy switching. Open.

## Honest limits
- We did not reproduce this, did not install the app, and did not read the app bundle. The root cause is a commenter's reading of the code, not a vendor statement.
- No maintainer response was seen in the thread at check time. No fix is claimed.
- Whether 3.1623.0 fixes it is unconfirmed.
- Scope is the Store/MSIX build on Windows only.
