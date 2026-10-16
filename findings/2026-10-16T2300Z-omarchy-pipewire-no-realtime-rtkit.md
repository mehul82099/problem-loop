# Omarchy: PipeWire runs without realtime priority on a stock install

- Source: https://github.com/omacom/omarchy/issues/9390 (open, label `bug`, opened 2026-08-31, last activity 2026-10-16)
- Open fix PRs, both verified open and unmerged through the GitHub API on 2026-10-17:
  - https://github.com/omacom/omarchy/pull/12428 "Install rtkit so PipeWire gets realtime priority" (head dac602f)
  - https://github.com/omacom/omarchy/pull/7971 "Let the compositor and audio graph take the realtime priority they ask for" (head bf58535)

## The problem
The reporter (michelbob) says Omarchy 4.0.2-1 does not install `rtkit`, so PipeWire cannot get realtime scheduling. Its `data-loop` threads stay at `SCHED_OTHER`, priority 0. At startup the journal shows `mod.rt: RTKit error: org.freedesktop.DBus.Error.ServiceUnknown`. The usual fallbacks are also missing: `ulimit -Hr` is 0, `/etc/security/limits.d/` is empty, and the user is in no realtime group. A later commenter (wbnns) adds that the shipped PipeWire and WirePlumber user units set no `LimitRTPRIO` or `LimitNICE` either.

Effect, as reported: invisible at idle, but audio can drop out when the CPU is saturated. wbnns saw zero xruns in 30 days of normal use, which fits "invisible until load".

## What commenters report (their measurements, not run here)
| Who | Hardware | Result after installing only `rtkit` and restarting audio units |
|---|---|---|
| michelbob | stock install | `data-loop` goes to SCHED_RR priority 20 |
| piotrsynowiec | Intel T2 MacBook | pipewire and pipewire-pulse at RR 20, wireplumber at RR 1 |
| wbnns | ThinkPad X1 Carbon Gen 8 | same baseline, same RTKit error |
| staruxian | HP Victus, Ryzen 5 7535HS | RR 20 / RR 20 / RR 1, no reboot, crackling on a USB headset was the symptom |
| dyedfox | ThinkPad E16 Gen 1 | RR 20, was seeing garbled audio after resume, will report back if it recurs |
| h5tark | desktop, USB DAC | RR 20, a stuck xrun loop was the symptom, results after a few days still pending |

Two of the later reports (suspend/resume and the USB DAC loop) explicitly say scheduling is a plausible cause but not proven. The DAC report points at PipeWire and `snd-usb-audio` recovery as the likely root of that loop.

## Two routes to the same goal
The `omarchybot` account (an automated reviewer, which says its checks were done by AI models) describes both open PRs:
- `rtkit` (#12428): restarts take effect without a reboot, and each request is mediated with a priority cap. Hazard it names: an `xdg-desktop-portal` started before `rtkit` existed may report a zero realtime budget until next login.
- `realtime` group (#7971): needs a reboot and grants the limit to every process of the user. It also covers Hyprland.

It says they do not conflict if both land, and that the choice is up to the maintainer. It also says aarch64 already lists `rtkit` in its package file.

## Honest limits
- I did not install or measure anything. Every priority number above is a commenter's report.
- Statements by `omarchybot` about its own reproduction and about repository contents are not independently checked here. I only confirmed that the two PRs exist, are open, and have the titles and head commits listed.
- The issue is a mix of reports, and a few of them were also written with AI assistance (the thread says so). Agreement across hardware is real signal, but none of it shows that missing realtime priority caused the audio glitches.
- Which PR the maintainers will merge is not decided in the thread.
