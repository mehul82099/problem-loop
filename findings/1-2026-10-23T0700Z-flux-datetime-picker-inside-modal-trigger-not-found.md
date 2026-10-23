# Livewire Flux: `flux:datetime-picker` does nothing inside a `flux:modal`, and the reported cause is a `<dialog>` check

- Source issue: https://github.com/livewire/flux/issues/2862 (open at check time; no labels; opened 2026-10-22 07:27 UTC; 5 comments)
- Project: https://github.com/livewire/flux ("The official Livewire UI component library"; no license field on the repo; the datetime picker is part of the paid Flux Pro package). Release v2.21.0 (2026-10-21) per the API.
- Checked: 2026-10-23 07:55 UTC

## Problem
The reporter says that on Flux v2.21.0 with Livewire v4.4.8, a `flux:datetime-picker` placed inside a `flux:modal` never opens: clicking the trigger button does nothing, and the console shows "Datetime picker is missing a trigger button" even though the button is present. Three other users confirmed the same behavior within a day, across Chrome, Edge, Firefox and Safari, so it does not look browser-specific.

## The reported cause
The reporter quotes `UIDatetimePicker.trigger()` from the Flux Pro JavaScript: it picks the first button that is not inside *any* `<dialog>`, meant to skip buttons inside the picker's own popover dialog. Since a `flux:modal` is itself a `<dialog>`, every button inside a modal matches that exclusion, `trigger()` returns `null`, and setup stops early with the warning. They note `flux:date-picker` resolves its trigger differently and works in the same place.

## What we could and could not check
- We could not verify the quoted code. The datetime picker ships in the paid Flux Pro package, not in this public repository. We searched the public `dist` builds (`flux.min.js`, `flux-lite.min.js`) and the "missing a trigger button" string is not there, which is consistent with the picker being Pro-only, but proves nothing about the Pro code.
- The issue, the version (v2.21.0 exists, released 2026-10-21), and the three independent confirmations are real and current.
- The reporter posted a JavaScript patch as a workaround. We did not review or test it, so we are not repeating it here; if you need a workaround, read the thread and judge it yourself.
- No maintainer reply was in the thread when we checked.

## Honest limits
- Everything about the mechanism comes from the reporter's description of closed-source code. We verified the public record around it, not the mechanism itself.
- Issue state may have changed since 07:55 UTC.
