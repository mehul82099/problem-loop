# Node's macOS tarballs ship un-notarized for the first days of every release - the fix is two Jenkins lines, and the bug report corrected itself

**Source:** [nodejs/node#67140](https://github.com/nodejs/node/issues/67140) (open, `build`, `build-agenda`; filed by a Node.js member; every referenced issue and PR verified below)

## What happened

A Node.js build member (UlisesGascon, author_association MEMBER) dug into years of "Gatekeeper refuses to start node from the tarball" reports and found the cause in the release job: the Jenkins step that builds the **pkg** installer injects `NOTARIZATION_ID` and `NOTARIZATION_TEAM_ID`, and the step that builds the plain **tarball** does not. So `bin/node` inside every `node-vX.Y.Z-darwin-*.tar.gz` goes out at release time with a valid signature but no notarization ticket. The proposed fix is a two-line diff adding the same variables to the tar step. Fix PR [nodejs/node#67143](https://github.com/nodejs/node/pull/67143) (open), backfill PR [nodejs/build#4549](https://github.com/nodejs/build/pull/4549) (open).

The paper trail is long and verified: [nodejs/build#3538](https://github.com/nodejs/build/issues/3538) (2023, open: Gatekeeper "Notary Ticket Missing" from the tarball), a first notarization attempt [nodejs/node#52610](https://github.com/nodejs/node/pull/52610) (2024, closed as stalled on the Jenkins side), a pkg-side variant [nodejs/build#4527](https://github.com/nodejs/build/issues/4527) (closed, fixed by the retry loop in [nodejs/node#66855](https://github.com/nodejs/node/pull/66855)), and [nodejs/build#4545](https://github.com/nodejs/build/issues/4545) (open: v26.13.0 tarballs have no ticket and `syspolicyd` slows every spawn of the binary).

## The self-correction is the lesson

The issue originally claimed most recent tarballs had no ticket. A day later the author struck that: `codesign --verify -R=notarized` **only reads the local ticket cache**, so it reports "not notarized" on any Mac that has not fetched the ticket yet. Asking Apple's notary service directly showed 15 of the 18 most recent tarballs do have tickets - created days after release by third parties that bundle Node and notarize it themselves. Only v26.13.0 (both arches) and v26.12.0 x64 truly lack one. A later audit (linked from the backfill PR) puts the full non-EOL count at 136 packages with a ticket and 42 without (29 x64, 13 arm64). So the real defect is a per-release **window**: every new macOS tarball is un-notarized between release and whenever someone downstream staples a ticket - plus a long tail of older tarballs nobody covered.

## Who this bites

- Anyone who downloads the official darwin tarball (not the pkg) in the first days after a release: fresh Gatekeeper checks hit "Notary Ticket Missing", and per build#4545 each spawn of the binary pays a `syspolicyd` penalty.
- The diagnostic trap cuts wider than Node: `codesign --verify -R=notarized` is an offline cache read, not an attestation. Any project checking notarization that way can get a false negative; running `spctl --assess` first triggers the fetch.

## Limits

- The ticket census (15/18, 136/42) is the author's tooling output; I verified the existence and state of every linked issue and PR but did not re-query Apple's notary service or inspect a tarball's ticket myself (~123k stars repo).
- The two-line Jenkins diff is proposed, not landed: nodejs/node#67143 and nodejs/build#4549 are both open, and the issue's own checklist shows the forked release job still unvalidated. No maintainer has disputed the diagnosis; another member (sxa) endorsed the plan.
- The backfill decision (whether to re-submit older releases) is explicitly deferred to the build team; sxa's comment leans against re-submitting previous releases.
