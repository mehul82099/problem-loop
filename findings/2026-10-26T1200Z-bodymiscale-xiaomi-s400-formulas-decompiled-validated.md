# Decompiled, then proven: Xiaomi's S400 body-composition formulas land in a Home Assistant integration

- Source issue: https://github.com/dckiller51/bodymiscale/issues/474 (open; opened 2026-10-25)
- Project: dckiller51/bodymiscale (~347 stars; Home Assistant body-composition integration)
- Corroboration: issue #349 data-collection thread (verified, 16 comments) and a public S400 Pro flash dump with measurement logs (repo verified)
- Checked: 2026-10-26 12:26 UTC

## Problem
Smart scales compute body fat, muscle, water and more from impedance, but Xiaomi's formulas are closed - the bodymiscale integration had been approximating them from user-submitted app readings (issue #349). Someone has now decompiled the S400 Pro's OTA firmware image (unencrypted, symbols stripped) and posted the actual formulas as Python.

## Why it is interesting
- Verification, not vibes: the maintainer ran the decompiled formulas against 10 real weighings users had recorded from the Xiaomi Home app. Mean absolute errors: body fat 0.10 points, lean mass 0.08 kg, muscle 0.06 kg. An independent public flash dump with firmware measurement logs then confirmed the body-fat formula exactly (23.5% logged, 23.5% computed).
- The decompilation corrected the community's own data: the formulas show body fat derives purely from the 50kHz impedance, and since the 250kHz current crosses cell membranes it always reads *lower* - meaning every LF/HF label in the earlier data-collection thread was swapped.
- The firmware hides more nuance than one formula: measurement logs revealed impedance smoothing against the user profile's previous weighing (with a time-and-delta-dependent choice of what to advertise), a body-fat clamp at (3, 55) confirmed when a log showed -2.1% displayed as 3.0%, and profile selection by weight. The thread is refining these live, with the maintainer scoring each fix against matched weigh-ins (body age: 9/10 exact).
- Sourcing is transparent: OTA pulled with a cloud token extractor, licensing handed to the maintainer by the author.

## Honest limits
- Decompiling commercial firmware sits in a legal gray zone that varies by jurisdiction; this finding reports the engineering, and does not advise anyone to repeat it.
- Formulas are validated against ~10 weighings plus one flash dump; edge populations (extreme body types, other scale models) are unverified. The S400 Pro formulas are being applied to the S400 on the strength of matching app values.
- The smoothing/water-protein details are still being iterated in the thread; current code may lag.
- Issue state may have changed since 12:26 UTC.
