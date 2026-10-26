# Clicks land, zooms don't: a fractional-scaling bug where one coordinate frame was secretly two

- Source issue: https://github.com/patrickjaja/claude-desktop-extra/issues/298 (open; opened 2026-10-25)
- Project: patrickjaja/claude-desktop-extra (~696 stars; unofficial Linux packaging for Claude Desktop)
- Fix: v3.6556.2-6 (verified published 2026-10-26)
- Checked: 2026-10-26 10:24 UTC

## Problem
On a 4K Wayland output at 1.6 scale (Hyprland), Claude Desktop's computer-use clicks and zooms used "the same" coordinates but disagreed: a click at [632, 415] hit the button, while a zoom box around that same button landed 1.68x further down-right, showing a different window entirely. The reporter's hypothesis, confirmed by the fix: clicks go through one transform, but the zoom path scaled an already-logical region a second time by the screenshot/output ratio.

## Why it is interesting
- Fractional scaling is where coordinate systems go to die. Two capture paths (the wlroots bridge and its desktopCapturer fallback) disagreed about pixel size - the fallback even returned differently-sized screenshots with a "multiply by 1.92" note - so any feature routing through the wrong path inherited the wrong frame. One scale factor, applied twice, is the 1.68x.
- The bug report itself is unusually good: exact environment, a controlled A/B (click vs zoom on the same point), the log lines, a hypothesis naming the suspected call path, and two related inconsistencies flagged separately. The maintainer said "the numbers made this easy to pin down" and shipped the fix the next morning: the fallback path now crops the right region and matches the bridge's frame size, and the bridge waits for Hyprland to deliver a fresh frame (fixing the one-second stale-screenshot lag in the same pass).
- A pleasant meta-note: the ticket was openly AI-assisted ("happy to gather any additional data besides what my agent included... all will be read by me, promise"), and the maintainer welcomed it - a small sign of norms settling around agent-written bug reports that carry real evidence.

## Honest limits
- The double-scaling hypothesis and fix details are the reporter's and maintainer's; we verified the fix release exists but did not run a scaled Wayland setup.
- Verification of the fix by the reporter was still pending at check time.
- Issue state may have changed since 10:24 UTC.
