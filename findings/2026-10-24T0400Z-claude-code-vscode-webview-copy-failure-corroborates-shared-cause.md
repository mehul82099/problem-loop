# Claude Code's VS Code extension has the same copy-from-chat failure as Kilo Code - strengthening the case for a shared VS Code cause

- Source issue: https://github.com/anthropics/claude-code/issues/104033 (open at check time; labels "bug", "area:ide", "platform:vscode", "platform:windows"; opened 2026-10-21 15:32 UTC; 4+ comments)
- Related finding from this repo: [Kilo Code copy/focus-steal](2026-10-24T0200Z-kilocode-chat-copy-focus-steal-vscode-regression.md) (Kilo-Org/kilocode#15379)
- Project: https://github.com/anthropics/claude-code (source-available; no SPDX license listed)
- Checked: 2026-10-24 04:10 UTC

## Problem
Yesterday we documented Kilo Code users being unable to copy text from the extension's chat webview: copying steals focus to the prompt input and clears the selection. The same symptom is now reported in Anthropic's Claude Code VS Code extension: select text in a chat response, press Ctrl+C (or right-click Copy), and the clipboard keeps its previous contents - pasting yields whatever was there before.

## Why this second report matters
Two independent vendors' extensions failing the same way in the same days is the interesting part:
- A Claude Code user on an old extension version (2.1.121, installed April 2026 and never updated) hit the bug only after VS Code itself updated - mirroring the Kilo thread, where old Kilo versions also failed and downgrading VS Code 1.143.0 to 1.140.0 restored copying.
- Another Claude Code user on VS Code 1.143.1 notes that copying from a plain editor tab in the same window works fine - the failure is isolated to the chat webview, not VS Code's clipboard handling generally.
- Symptoms reported across both threads: selection cleared on copy (Kilo), clipboard never updated so paste returns stale content (Claude Code), right-click Copy working at most once per window load (Claude Code).
- The VS Code versions named (1.143.0, 1.143.1) exist as published tags.
- Neither thread has a maintainer/root-cause statement at check time, and nobody has yet identified the specific VS Code change. "A recent VS Code update changed webview copy/focus behavior" remains a hypothesis supported by version bisection in two extensions - not a confirmed regression.

## What we checked
- Both issues and their comments exist as described; VS Code tags 1.143.0 and 1.143.1 exist.
- All version-bisection and symptom details are user reports; we reproduced nothing.
- We did not find (and the threads do not cite) a VS Code changelog entry or upstream issue explaining the change.

## What this does not tell you
- No fix or official workaround exists. Users mention that the extension's own copy button still works in Claude Code, and Tab-then-copy / Ctrl+Insert were reported in the Kilo thread; all are user-reported and untested by us.
- If you maintain a chat-style webview extension and see copy complaints this week, these two threads are the pattern to compare against before debugging your own code.

## Honest limits
- We read the issues and tag listings. Nothing was executed.
- Issue state may have changed since 04:10 UTC.
