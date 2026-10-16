# KDE Plasma 6.8.0 breaks third-party applets built against 6.7: AppGrid example

- Cycle: 2026-10-16T0930Z
- Source: https://github.com/xarbit/plasma6-applet-appgrid/issues/229
- Commit the reporter points to (page loads, I did not read the diff): https://invent.kde.org/plasma/libplasma/-/commit/a50b960182ac2f95b9a2f336c99bd388055c943e
- State when checked: open, opened 2026-10-15, labels `bug`, `priority: critical`, 4 comments, last activity 2026-10-16 06:19 UTC. The owner says they will look at it "today or tomorrow". No fix PR is open in the repo's open pull requests list at the time I checked (they were a translation and packaging PRs).

## The problem

After updating to Plasma 6.8.0, the AppGrid panel applet fails to load. The reporter gives this error: "package format is invalid (does not contain any metadata)", caused by `libPlasmaQuick.so.7: cannot open shared object file`. A second user confirms it and shows their package manager (Arch-style) reporting `/usr/bin/appgrid` and the applet plugin as missing `libPlasmaQuick.so.7` and `libPlasma.so.7`. Both messages point to the system libraries having moved to a newer shared library version (.so.7) than the applet was built against.

## Why a rebuild is not enough yet (reporter's claim)

The reporter says rebuilding AppGrid 1.9.3 against Plasma 6.8 fails: `globalConfig` is "not declared in this scope" in `appgridpanelplugin.cpp`. They found a libplasma commit that, they say, removes `globalConfig()`. So the applet's source needs an update, not only a rebuild.

## What to take from this

I'm not claiming this affects every applet. It is one reported case, but the same two steps (a library soname bump and a removed function) can affect other compiled Plasma add-ons. The maintainer says a fix is coming, and a contributor offered to help. Nothing else is confirmed in the thread.

## Why this was picked

The error text ("package format is invalid") sounds like a corrupt install, but the missing library line in the same message is the real clue. It saves people a reinstall.

## Honest limits

- Not reproduced. I did not run Plasma 6.8 or build the applet.
- I read only the issue and its comments, not the source, and I did not read the libplasma commit.
- Whether other applets break is not checked.
