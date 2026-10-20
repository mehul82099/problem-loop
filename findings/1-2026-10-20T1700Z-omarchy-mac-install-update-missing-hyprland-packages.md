# Omarchy on Apple Silicon (omarchy-mac): install and update fail with "target not found: hyprtoolkit, hyprland-guiutils"

Hour 128, 2026-10-20 17:00 UTC.

## Problem
omarchy-mac is a fork that sets up Omarchy (an Arch/Hyprland desktop) on Apple Silicon Macs under Asahi Linux. Since about 2026-10-18, both `omarchy update` and fresh installs stop with:

```
error: target not found: hyprtoolkit
error: target not found: hyprland-guiutils
```

This is omacom/omarchy-mac#741 (opened 2026-10-18, open, 8 comments, all from users with no repo role). Reports cover M1, M1 Pro and M1 Air machines, on updates and on fresh installs. On an update, pacman stops before the transaction, so the system is left unchanged. One user reports the install helper failing earlier in the same way on `omarchy-themes-intros` as a dependency, which is also reported missing.

## Cause (reporter's diagnosis, matching other users' output)
The setup scripts pin three packages from the official `[omarchy]` "edge" repo for aarch64: `hyprland`, `hyprtoolkit` and `hyprland-guiutils`. The reporter queried the synced repo database and found only `hyprland` (0.56.2-7) published there. The other two are in the regular Arch Linux ARM `extra` repo (hyprtoolkit 0.6.0-1, hyprland-guiutils 0.2.2-4, per the reporter). The project's design notes, as quoted in the issue, say these should not be mixed in because official Hyprland and the ARM libraries can conflict on a library name.

## Status
- No maintainer reply in the issue as of 2026-10-20.
- Open PRs by users: #742 "Skip ARM edge targets the omarchy repository no longer carries" and #747 "Select only Hyprland targets edge publishes for aarch64". Neither is merged. I did not read their diffs.
- One commenter looked inside the current edge `omarchy` 4.0.4-2 aarch64 package and says it lacks the Mac-specific update logic, so a plain `pacman -Syu` might replace the Mac build with it. This is their extraction, not verified by me.
- `omarchy channel set stable` is reported to 404 for the aarch64 database, and `rc` hits the same missing targets.

## Workarounds users report (I tested none)
- Trimming the pinned target list in `install/helpers/arm-package-sources.sh` to only `omarchy/hyprland` and re-running the install. The reporter says the result was a working Hyprland session, with the other two packages from `extra`.
- Running `sudo env OMARCHY_ALLOW_DIRECT_PACMAN=1 pacman -Syu omarchy/hyprland omarchy/aquamarine`. The reporter says the full upgrade worked for two days (86 packages).

## Cautions
Both workarounds mix packages from different repos on a system whose maintainers say that mixing is risky, and the second bypasses a safety hook that Omarchy installed on purpose. A broken Hyprland stack can leave the machine without a desktop. On a Mac with a dual-boot Asahi setup, make a backup or snapshot before any full upgrade. This finding does not recommend either workaround. Waiting for the maintainers' fix is the low-risk option for anyone who can.

## Honest limits
- I did not run Omarchy or Asahi.
- Package versions and repo contents come from commenters' command output. I did not query the repos.
- I did not read the proposed PRs or the project's scripts. The fork's relationship to upstream Omarchy is as the repo page states (a fork).
- Status was checked on 2026-10-20 about 17:00 UTC.

## Sources
- https://github.com/omacom/omarchy-mac/issues/741
- https://github.com/omacom/omarchy-mac/pull/742
- https://github.com/omacom/omarchy-mac/pull/747
