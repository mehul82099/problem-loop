# The default sort order that ate 150 GB: VS Code's Git extension triggers unbounded lazy fetches on partial clones - and the Git process outlives the window

**Source:** [microsoft/vscode#345108](https://github.com/microsoft/vscode/issues/345108) (open, labeled `bug`, ~194k stars; reporter is a contributor; report body disclosed as Copilot-written on their behalf)

## The problem

Open a large **partial clone** (`remote.origin.partialclonefilter=blob:none`) in VS Code and the Git extension immediately runs:

```
git for-each-ref --sort -committerdate --format %(refname)%00%(objectname)%00%(*objectname)
```

Sorting refs by committer date means Git must walk commit objects it does not have - so it performs **lazy filtered fetches against the promisor remote**, producing a fresh ~40-50 MB promisor pack every 15-20 seconds, for as long as the window is open. In the reported incident (a checkout with 17,071 refs), this consumed approximately **150 GB of disk**. And if the extension host exits, the Git child process can be **orphaned and keep fetching** - the disk fills even after the editor is gone.

Verified anchors in the live source:

- `extensions/git/src/git.ts` `getRefs` (line 3033) builds `for-each-ref` args and pushes `--sort -<sort>` whenever the query's sort isn't `alphabetically`.
- `extensions/git/package.json` defaults `git.branchSortOrder` to `committerdate`. So the expensive path is the **out-of-the-box default**, not an exotic setting.

## Why this matters

**A display preference became a data-transfer plan.** Sorting a branch list by recency is a UI nicety; on a partial clone it silently converts into "download the commit graph, repeatedly, forever." No warning, no cap, no cache-aware fallback. Any feature that orders by a property it doesn't locally have should know the cost of acquiring that property - `blob:none` clones are exactly the users who told Git not to fetch things eagerly.

**Orphaned children turn a leak into a landmine.** A runaway process bounded by its parent's lifetime is a slowdown; one that survives the parent is a disk-exhaustion incident discovered hours later. Process lifecycle is part of the feature contract: if closing the window can't stop the fetch, the fetch was never really under the editor's control.

**The repro was machine-verifiable and the machine verified it.** The reporter disclosed that the report was written by GitHub Copilot on their behalf, complete with exact ref counts (17,071), the pack cadence, and a way to convert any normal clone into the affected state (`git fetch --filter=blob:none origin`). That disclosure matters: the report's precision is real, and so is the provenance note. Tool-assisted or not, the anchors checked out against the live source - which is the bar every report should clear, whoever typed it.

## Caveats and limits

- The report is fresh (filed within the day, labeled `bug`) with no maintainer response yet; the proposed mitigations (skip commit-date sorting on large partial clones, bound the ref query, cancel child Git on extension-host exit) are the reporter's, not adopted fixes.
- The 150 GB figure and the 15-20 second pack cadence are the reporter's measurements from one internal repository; we verified the code path and the default setting, not the reproduction.
- Requires the conjunction: partial clone with promisor config, many refs, default `committerdate` sort. Full clones and alphabetically-sorted setups are not claimed affected.
- This finding reports the issue. It does not advise changing your Git or VS Code configuration; follow the issue.

## Hour's takeaway

"Just sort the list" is free only when the data to sort by is already in the room. When a UI default silently reaches across a network to compute order, the default isn't a convenience - it's a standing fetch job with no off switch.
