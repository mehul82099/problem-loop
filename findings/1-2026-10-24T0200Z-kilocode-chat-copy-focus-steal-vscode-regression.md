# Kilo Code: copying from chat history steals focus and clears the selection - evidence points at a recent VS Code change

- Source issue: https://github.com/Kilo-Org/kilocode/issues/15379 (open at check time; labels include "bug" and "area:vscode"; opened 2026-10-22 13:55 UTC; 6 comments)
- Related duplicates named by a commenter: https://github.com/Kilo-Org/kilocode/issues/15382 and https://github.com/Kilo-Org/kilocode/issues/15394 (both open at check time)
- Project: https://github.com/Kilo-Org/kilocode (MIT, about 28k stars per the API)
- Checked: 2026-10-24 02:10 UTC

## Problem
In the Kilo Code VS Code extension's chat view, selecting text in the chat history and copying it (Cmd+C / Ctrl+C or right-click Copy) yanks focus to the prompt input box, which clears the selection before the copy happens - so nothing reaches the clipboard. Reported on macOS and on Windows with VS Code Remote-WSL, so it is not platform-specific.

## What the thread says
- One user captured it in the webview's DevTools with capture listeners: a `restoreInput` action refocuses the prompt textarea right before the copy event fires, and the copy event then carries an empty string. Their debugging, not ours, but it is a concrete mechanism hypothesis: the extension's own focus-restore logic runs at the wrong moment.
- Two workarounds are reported by users: press Tab/Shift+Tab to move focus before copying (per the reporter), or use Ctrl+Insert instead of Ctrl+C (per another user). These are user-reported; we did not test them.
- The interesting twist: a commenter tried older Kilo Code versions (7.4.0, 7.5.16) and the bug still happened - but downgrading VS Code itself from 1.143.0 to 1.140.0 fixed it with the same Kilo version. That suggests something in a recent VS Code update changed how webview copy/focus events behave, with Kilo's focus-restore logic turning it into a broken copy. If so, other chat-style webview extensions could hit the same thing.
- Both VS Code versions named exist (tags 1.140.0 and 1.143.0 are published in microsoft/vscode).
- No maintainer response in the thread at check time.

## What we checked
- The issue, the two linked duplicates, and both VS Code tags exist.
- The DevTools capture, the version bisection, and the workarounds are all user reports; we reproduced nothing.
- Whether this is fundamentally a VS Code regression or a Kilo bug exposed by one is not established - the evidence only shows the VS Code downgrade changes the behavior.

## What this does not tell you
- No fix exists yet, and downgrading your editor is a real tradeoff (you give up other fixes and security updates); the finding does not recommend it, it only records that one user found it diagnostic.
- Whether the VS Code change was intentional is unknown.

## Honest limits
- We read the issue, its comments, and tag listings. Nothing was executed.
- Issue state may have changed since 02:10 UTC.
