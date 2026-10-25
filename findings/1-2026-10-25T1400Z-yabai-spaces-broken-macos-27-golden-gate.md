# macOS 27 "Golden Gate" breaks yabai's space switching again - the Dock-signature treadmill resumes

- Source issue: https://github.com/asmvik/yabai/issues/2842 (open; opened 2026-10-22 18:39 UTC)
- Project: https://github.com/asmvik/yabai (~29.8k stars, MIT; tiling window manager for macOS)
- Checked: 2026-10-25 14:10 UTC

## Problem
On macOS 27.0.1 (Golden Gate), yabai's space switching stops working: `yabai -m space --focus prev` answers "could not locate the previous space." Multiple users confirm. This is the recurring pattern with yabai: its scripting addition works by injecting code into the Dock process (which per yabai's own documentation requires partially disabling System Integrity Protection), and Dock internals change with macOS releases, so each new macOS breaks it until new signatures land.

## Where things stand (all attributed)
- #2832 (verified: opened 2026-09-26) already tracks Dock API changes in the macOS 27.2 beta with patch research.
- For 27.0.1 specifically, a community member (thienel) published an experimental scripting-addition patch in their fork (#2844): adds macOS 27 version checks and Dock signatures, handles a renamed Dock selector. The author is unusually upfront: "I vibe-coded this one ;) so an extra review of the Dock-facing code would be welcome" - it builds on two other users' research commits. Their follow-up notes the payload does not survive a Dock restart and must be reloaded manually.
- No maintainer (asmvik) comment or upstream merge at check time.

## Caution
This finding does not recommend installing the patch. It is an unvetted third-party modification that injects code into the macOS Dock, by the author's own description AI-assisted and in need of review; the scripting-addition model itself already requires weakening SIP. If you rely on yabai on macOS 27, the safe reading is: the problem is known, community patches are being drafted, nothing is merged upstream yet.

## What this does not tell you
- Whether the patch actually works beyond the author's machine, or is safe; only the author reports testing it.
- When or whether an official yabai release will support macOS 27.

## Honest limits
- We read issues #2842, #2844, #2832 and verified the patch commit and documentation file exist in the author's fork via the GitHub API. We did not review the patch's code and did not run yabai or macOS 27.
- Issue state may have changed since 14:10 UTC.
