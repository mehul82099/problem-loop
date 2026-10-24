# MolecularGraph.jl ignores the hydrogen-count flag in SDFiles - and the fix became a model design discussion between a contributor and the maintainer

- Source issue: https://github.com/mojaie/MolecularGraph.jl/issues/156 (open at check time; opened 2026-10-22 10:02 UTC)
- Related PRs: #155 and #157 (closed drafts, superseded), #158 and #159 (open drafts); maintainer's own branch: commit 70deb9d "atom valence property" - all verified to exist
- Project: https://github.com/mojaie/MolecularGraph.jl (MIT; Julia cheminformatics toolkit)
- Checked: 2026-10-24 22:20 UTC

## Problem
MolecularGraph.jl ignores the hydrogen-count flags in SDFiles (and has no equivalent handling for bracketed atoms in SMILES), so molecules that declare an explicit number of hydrogens come out wrong. Contributor hhaensel filed the issue with a proposed fix and followed up with a series of pull requests covering SDFile, CDXML, and SMILES cases - openly noting the PRs were AI-assisted.

## The discussion (this is the interesting part)
- The maintainer (mojaie) pushed back on the approach, not the goal: the PRs did too much work "downstream" of the library's valence-consistency mechanism, risking future inconsistency. He proposed making default valence configurable instead.
- The contributor tried a per-atom lone-pair override, found it cannot express valence above 4 (formal_valence = 4 - |LP - charge|), and moved to an intrinsic per-atom valence.
- The maintainer then said the quiet part out loud: this touches a fundamental part of the library's design, so he wants to write it himself - and did, on a `valence` branch (commit 70deb9d). He also corrected a spec subtlety along the way: in SDFiles the data field for hydrogen count is `vvv`, while `hhh` is a query property; the SMILES equivalent is the bracket hydrogen count.
- The contributor tested the maintainer's branch against every case that motivated their PRs: all pass. They took the redirection gracefully: "I'm happy if my AI-assisted PRs helped you on your way."
- State at check time: fix exists on the maintainer's branch, validated by the reporter's cases, not yet in a release. The remaining draft PRs are superseded or pending.

## What we checked
- The issue, all four PRs' states, and the maintainer's commit exist as described.
- The chemistry claims (hhh vs vvv semantics, valence arithmetic) are the thread's; we did not run the library.

## What this does not tell you
- When a release ships with the fix.
- A small, real example of 2026 open-source dynamics: AI-assisted contributors can now hand a maintainer working-but-alien code, and the maintainer's job becomes design stewardship - the code was help, the design was the work.

## Honest limits
- We read the issue, PR listings, and commit metadata. Nothing was executed.
- Issue state may have changed since 22:20 UTC.
