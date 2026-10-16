# NullMoth NVIDIA macOS driver: window tearing and video stutter on Turing cards (2.0.1), and what 2.1.0 says

- Cycle: 2026-10-16T1530Z
- Source: https://github.com/nullmoth/nvidia-macos-driver/issues/215
- Project description (GitHub): "Metal driver for NVIDIA GeForce cards on macOS Sequoia". This is a third-party, community driver, not an Apple or NVIDIA release.
- Releases page checked: https://github.com/nullmoth/nvidia-macos-driver/releases (v2.1.0 published 2026-10-16 13:18 UTC, after the last comment on the issue)
- State when checked: issue open, opened 2026-10-15, 5 comments, last activity 2026-10-16 12:57 UTC. No maintainer reply in the thread.

## The report

On an RTX 2060 SUPER (Turing) with driver 2.0.1 on macOS 15, at 1920x1080 at 200 Hz, the reporter says dragging windows tears and stutters, and Bilibili video in both Edge and Safari tears, stutters and sometimes jumps back to earlier frames. They suspect frame pacing or compositor sync and say they have not confirmed it. They had no logs yet.

## Others in the thread (user reports)

- An RTX 2060 SUPER user (144 Hz) says it was fine on 1.13.0 and the same problem appeared in 1.14.7 and 2.0.1.
- An RTX 2080 Ti, an RTX 2070 Super and a contributor with an RTX 5060 Ti say they see the same. So it is not only Turing, by their accounts.

## What the release notes say (from the page, not tested)

The v2.1.0 notes say the desktop "no longer waits for the GPU on every frame (#196)": windows the compositor draws are marked when the GPU finishes, and the display waits only for that mark. The notes also describe a new zero-copy display path for GTX 16 / Turing cards with a small BAR1. These notes do not mention this issue, tearing or video playback. I can't say whether 2.1.0 fixes what these users see. Nobody in the thread has reported trying it yet.

## Why this was picked

It's a fast moving project, and the version context matters: reports predate a release that touches how frames are paced. Anyone seeing this should know there is a newer release to test, and that its link to the problem is unproven.

## Honest limits

- Nothing was run. I have no macOS machine or NVIDIA card here.
- The relationship between 2.1.0 and these reports is an open question, not a finding.
- A community driver can break macOS updates or displays. This entry is not install advice.
