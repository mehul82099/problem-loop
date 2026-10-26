# A mod's force-feedback bug wrenches steering wheels fully right - and players debugged the trigger themselves

- Source issue: https://github.com/TecnaGamer/BeamNG.Earth/issues/284 (open; opened 2026-10-25)
- Project: TecnaGamer/BeamNG.Earth (~1.2k stars; a 1:1-scale streamed Earth mod for BeamNG.drive with floating origin and LOD streaming)
- Checked: 2026-10-26 22:35 UTC

## Problem
With BeamNG.Earth installed, force feedback occasionally drives the steering wheel to full right lock and holds it there until the game restarts. Confirmed across at least four wheel ecosystems in two days: Logitech G920, Logitech G29, Fanatec GT DD Pro, and Moza R5. One user notes the same symptom existed in BeamNG 0.40's first release and was fixed in official hotfixes - and that it does not happen in the unmodded game, only with the mod loaded.

## Why it is interesting
- The comment thread is community debugging at its best. Within hours, users converged on the trigger class: anything that switches or re-initializes input context. Opening the map (M), pressing Esc to pause, and swapping vehicles all provoke it; binding the map key to a wheel button avoids it; pausing with J before opening menus prevents it; deleting and respawning the car (a plain reset is not enough) clears a locked wheel.
- One observation does more diagnostic work than the rest combined: a G29 user who inverts FFB found the wheel locks fully LEFT instead. That single data point says the bug is a saturating software torque command with a fixed sign - not a hardware fault, not a mechanical jam - and inverting the pipeline inverts the lock direction.
- The safety angle is real and the thread knows it. A direct-drive wheel slamming to full lock is a wrist hazard; a Fanatec owner called it "sub optimal for my wrist," and another user flatly says the bug can hurt people. Reported mitigations (all user-discovered, none official): turn FFB off, pause before menus, respawn the car.
- Root cause is untouched so far. The mod's floating-origin rebasing and per-vehicle FFB re-initialization are obvious suspects given the trigger class, but no maintainer comment or code pointer exists yet - an open loop for a nasty class of hardware-interface bug.

## Honest limits
- No maintainer response at check time; the trigger/workaround list is entirely crowd-sourced and uncontrolled - mileage will vary.
- The "fixed in BeamNG 0.40 hotfixes" claim is one user's recollection; we did not diff BeamNG's patch notes.
- Workarounds are user reports, not verified fixes; anyone with a strong direct-drive wheel should treat the safety note seriously and consider disabling FFB until a fix lands.
- Issue state may have changed since 22:35 UTC.
