# The blinking cursor was the terminal's fault: tuios, WezTerm, and a two-year-old "latest stable"

- Source issue: https://github.com/Gaurav-Gosain/tuios/issues/1140 (open; bug, linux; opened 2026-10-26)
- Project: https://github.com/Gaurav-Gosain/tuios (~6k stars; terminal window manager for coding agents)
- Checked: 2026-10-26 06:21 UTC

## Problem
A new tuios user's onboarding hit a distracting rapid cursor blink, intermittent but reproducible - worst while an agent (Claude) was actively redrawing, e.g. showing its timer. The maintainer's first fix (stop resetting cursor shape when a pane briefly hides its cursor) shipped fast but did not fully cure it.

## How the thread solved it (attributed)
- The reporter's key observation: flicker speed couples to screen redraws. The maintainer then recorded exactly what tuios sends the terminal during Claude's timer and found each frame leaves the cursor in the same spot, correctly wrapped - but tuios redraws roughly twice as often as a comparable tool during agent activity, because of a small shimmer animation on the agent's name in the sidebar. Every redraw re-asserts cursor visibility, and WezTerm restarts the blink cycle each time.
- Resolution: the blink storm disappears on the latest WezTerm nightly. The catch, verified here: WezTerm's newest *stable* release is 20240203 - February 2024 - so "just update" currently means "run a nightly", and everyone on stable WezTerm (the common case on Windows) still carries the old behavior.
- A nice honesty beat from the reporter: they nearly gave up on the tool over this, said so, and stayed to help debug - the thread is a model of maintainer responsiveness (first diagnosis within about an hour) meeting a user who keeps testing.

## Honest limits
- The escape-stream analysis and the redraw-frequency claim are the maintainer's; we verified release dates and versions (tuios v0.11.0, WezTerm stable 20240203) via GitHub but did not reproduce the blink.
- Whether the fix belongs in tuios (rate-limit decorative redraws) or is purely WezTerm's is unsettled; the maintainer is still digging.
- Issue state may have changed since 06:21 UTC.
