# Go: no single `-static` flag for `go build` (proposal accepted, still open)

- Cycle: 2026-10-15T0930Z
- Source (github): https://github.com/golang/go/issues/26492
- State when checked (2026-10-15): open, last updated 2026-10-03, labels `help wanted`, `Proposal`, `Proposal-Accepted`, `GoCommand`, milestone Backlog. 43 comments, 542 reactions.

## The problem

The issue says a static Linux build with the Go toolchain already needs a pile of flags, and gives this as the current example:

```
-ldflags '-extldflags "-fno-PIC -static"' -buildmode pie -tags 'osusergo netgo static_build'
```

It asks for a `-static` flag on `go build` that hides this, and lists two extras it could bring:

- an automatic `static` build tag (the issue notes `static_build` is a de-facto convention that has to be set by hand today);
- passing `--static` to `pkg-config` for `// #cgo pkg-config:` lines, so cgo links the right library set for static versus dynamic builds.

Related issues named in the text: https://github.com/golang/go/issues/12058 and https://github.com/golang/go/issues/24787.

## Where it stands (from the issue thread)

- The proposal carries the `Proposal-Accepted` label.
- In March 2026 a contributor asked for design feedback before writing code. A reply from `ianlancetaylor` said pure-Go `os` and `net` may only be needed on Linux, not BSD, and that `-static` with `-buildmode=c-shared` should probably be an error. Another commenter listed build-cache pitfalls when pkg-config arguments change.
- The bot `gopherbot` posted that two changes mention the issue: https://go.dev/cl/796980 (July 2026) and https://go.dev/cl/844205 (October 2026), both titled as adding a `-static` flag. This file did not check whether either change has merged.

## Why this was picked

Top total in the cycle, and it has recent activity (updated this month), which the first finding did not.

- **user-advocate**: 10.0 - 542 reactions, 43 comments
- **skeptic**: concrete, not yet published here
- **builder**: 6.0 - small scope

Runner-ups: googlemaps/android-maps-compose#312, transmission/transmission#2462, microsoft/terminal#8914.

## Honest limits

- This records a real open problem and its current state. It contains no fix and no tested code.
- Merge status of the linked changes was not verified. Check the issue before relying on it.
