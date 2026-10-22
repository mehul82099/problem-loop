# React Aria `useHover`: hover state can get stuck after mixing touch and mouse

- Source issue: https://github.com/adobe/react-spectrum/issues/10823 (open at check time; label: bug; opened 2026-10-21 18:17 UTC; 7 comments)
- Proposed fix (open, not merged, base main, 2 files changed): https://github.com/adobe/react-spectrum/pull/10824
- Code history the reporter cites: PR #7838 (closed, "Fix Toast hover and focus behavior", 2025-02) and PR #9715 (closed, "hover is applied after closing a modal with touch in safari iOS 26", 2026-03)
- Project: https://github.com/adobe/react-spectrum (Apache-2.0, 15,976 stars per the API)
- Checked: 2026-10-22 03:35 UTC

## Problem
The reporter says that on touchscreens and touch-plus-mouse devices, using several items built on `useHover` (for example checkboxes in `react-aria-components`) can leave `isHovered` stuck at `true`, shown as `data-hovered="true"`, on more than one item at once. They read the source of `useHover.ts` at commit 7ef23022 and point to three things:

1. `triggerHoverEnd` clears its saved target and pointer type before it returns early for a touch event, so an item that is already hovered can lose the target it needs to end the hover.
2. `triggerHoverStart` overwrites the saved pointer type before its touch check, so a later cleanup when the item becomes disabled may not clear hover.
3. The timer that ignores emulated mouse events after a touch is not cleared, so two taps within 500 ms can cut the second one's window short.

## What the project said
- A contributor asked for a reproduction, and a member then posted a StackBlitz plus a console snippet that sends touch events. The member says that, with that snippet, one item stays in the hovered state after a touch on another, and that the page log never shows the hover end. That is the member's description. We did not run it.
- Contributors discussed how realistic the case is. One said it resembles something produced by an experimental PR (#10786, open, "experiment with exhaustive edge case discovery") and that switching between touch and pointer in one interaction seems unnatural, but also that it is worth fixing. A member said it should be easy to reproduce on touch laptops. The reporter replied that they use a touchscreen laptop and hit it when scrolling with the trackpad and then tapping the screen.
- A fix PR (#10824) was opened. It was open and unmerged at check time, and we did not read it.

## What this means for readers
- Per the project's own member, the bug can be shown with a script, and the project agrees it is worth fixing. How often real users hit it is disputed in the thread, and no one measured it.
- This affects visual hover state (for example `data-hovered`). The thread does not describe data loss or any security impact.
- We don't give a workaround.

## Honest limits
- We did not run the StackBlitz, the console snippet, or a touch device.
- The three-point analysis is the reporter's reading of the source. The maintainers have not endorsed it, and the fix PR may not match it.
- The snapshot was taken about 9 hours after filing and may be out of date.
