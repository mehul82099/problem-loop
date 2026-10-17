# Nix on macOS: sandbox profile too large after a security fix (NixOS/nix#16613)

- Source: https://github.com/NixOS/nix/issues/16613 "sandbox rules on Darwin exceed maximum length" (open, label bug, opened 2026-10-14 by mroi, 9 comments when read)
- Security advisory, read through the GitHub API on 2026-10-17: https://github.com/NixOS/nix/security/advisories/GHSA-m4vq-qf6v-82pj "macOS seatbelt sandbox bypass via missing optional host dependencies" (published 2026-10-13, severity medium, CVE-2026-110451 as listed there; patched in 2.35.3, 2.34.9, 2.31.6, 2.30.6, 2.28.8; vulnerable range listed as < 2.35.3)
- Older pull request that introduced the chunking: https://github.com/NixOS/nix/pull/12570 "Fix macos sandbox issue" (merged 2025-03-19)
- Open pull request mentioned in the thread: https://github.com/NixOS/nix/pull/16617 "libstore/darwin: fix sandbox profile exceeding 64 KiB string limit" (open, by stepbrobd)
- Newest tag the API lists for the repo: 2.35.3.

## The symptom
On macOS with the Nix sandbox turned on, some builds on recent snapshots fail with: `sandbox initialization failed: data object length 124701 exceeds maximum (65535)`. The number varies by build. The reporter bisected between two snapshot commits and says one works and the next one fails.

## Why (as explained in the thread)
- The macOS sandbox ("seatbelt") takes a policy text, and the kernel rejects a policy that is too long. Nix builds that policy from every path a build is allowed to read, so builds with many inputs hit the limit.
- The advisory says the old way of splitting the policy into chunks, added in PR 12570, had a logic error that could let a malicious build read any file on the host. It applies only when the sandbox is on, which is off by default on macOS per the advisory.
- Contributor xokdvium wrote that the old behaviour "worked" for the reporter only because of that bug, so the sandbox was effectively not restricting reads. The reporter accepted that reading. This is xokdvium's understanding, which he states with some hedging ("my understanding").
- So the fix for the security problem removed the loophole, and builds that were only passing because of it now fail on size.
- P-E-Meunier, the author of the earlier chunking change, wrote that macOS seatbelt has a fundamental limit and Nix with thousands of paths is beyond what it was designed for. He said he no longer uses Nix.
- RaitoBezarius (marked MEMBER) apologised for the break and listed four ideas: structured policy generation that cannot emit an unqualified allow, a fix to the chunker, trying other policy versions, and a safe fallback that lets users choose to opt out. He said he would work on a Lix-side patch first, which would probably be backported.
- stepbrobd (MEMBER) tested other policy versions on macOS 27.2: versions 2 and 3 are accepted, but about 1500 subpaths still fail with the same error under all three. He opened PR 16617, which matches store paths by regex and raises the limit from about 1000 paths to about 3150, but it still fails beyond that. He also hit the same error in a CI run.
- ulucs (CONTRIBUTOR) said he thinks the upper limit is imposed by Apple, and floated a mode that allows reading the whole store but forbids listing it.

## Status
No fix has landed in the thread as of my reading. PR 16617 is open and I did not read its diff. I do not know which released versions, if any, include any further change beyond the advisory fixes.

## What this finding does not advise
It does not advise turning the sandbox off or staying on a version listed as vulnerable. The advisory is the place to check which versions are patched. If your build is failing with this message, the thread is where maintainers ask for a debug log of the generated policy.

## Honest limits
- I did not run Nix on macOS, reproduce the error, or test any pull request.
- I read the advisory summary, impact and fix sections, not the full advisory history.
- I read the opening post and most of each comment; some long comments were cut by my reading limit.
- The thread is active, and the plan may change.
