# MuseScore 4.7.5 freezes on startup for Arch users - and the community narrowed it to pipewire-alsa in two days

- Source issue: https://github.com/musescore/MuseScore/issues/35381 (open; label crash; opened 2026-10-23 22:15 UTC)
- Project: https://github.com/musescore/MuseScore (~15.3k stars)
- Checked: 2026-10-25 13:10 UTC

## Problem
MuseScore Studio 4.7.5 (verified release, 2026-09-08) renders its start screen and then freezes - no input, no repaint on resize - on up-to-date Arch Linux, across both the official AppImage and the distro package, and across Hyprland, KDE Plasma, i3, GNOME and openbox. Not the window manager, then.

## The community bisect, in public (all attributed)
- First suspect: PipeWire. Arch shipped pipewire 1.6.10 on 2026-10-22 (verified on archlinux.org) - the day before the first report. Two users found downgrading PipeWire to 1.6.9 fixes it.
- But 4.6.x works fine on PipeWire 1.6.10 while every 4.7.x freezes - so it is an interaction, not simply "the PipeWire update is broken".
- The twist: prompted by a contributor's diagnostic question, a user found their MuseScore audio backend was set to ALSA, switched it to native PipeWire, restored PipeWire 1.6.10 - and 4.7.5 starts fine. Two more users confirmed. Current suspect: the pipewire-alsa compatibility path, not PipeWire itself.
- Workaround status: switching MuseScore's audio backend to PipeWire is a benign settings change with three user confirmations. The PipeWire *downgrade* also works but means holding back a system package - this finding reports that, it does not recommend it.

## What this does not tell you
- No MuseScore developer root-cause or fix yet; only a community contributor's diagnostic help so far. Nothing filed against PipeWire at check time that we found.
- Whether non-Arch distros are affected once they ship pipewire 1.6.10.

## Honest limits
- We read the issue and all ten comments, and verified the MuseScore release and the Arch pipewire package date via their official sources. We did not run MuseScore or Arch; every behavior claim is a user's.
- Issue state may have changed since 13:10 UTC.
