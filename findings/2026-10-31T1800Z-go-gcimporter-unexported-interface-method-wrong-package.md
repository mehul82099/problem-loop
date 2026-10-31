# Go's deep export data stamps another package's unexported interface methods with the wrong package - and `unitchecker` then rejects valid code

**Source:** [golang/go#82747](https://github.com/golang/go/issues/82747) (open; a fix change, [CL 856622](https://go.dev/cl/856622) "internal/gcimporter: qualify interface methods with declaring package", is already posted but not merged; every anchor verified on x/tools master)

## What happened

When package `b` declares a defined interface type whose underlying type is an interface from package `a` with unexported methods (`type BI a.AI`, or the generic `type BGI[T any] a.GI[T]`), serializing `b` with `gcimporter.IExportData` qualifies those unexported methods with **`b`** instead of their declaring package **`a`**. After an export/import round-trip, `b.BI` carries method `b.m` rather than `a.m` - and in Go, an unexported method name is package-scoped, so `a.Impl` (which implements `a.m`) no longer satisfies `b.BI`. A downstream package `c` that passes `a.Impl{}` to `b.Accept` fails to type-check: "a.Impl does not implement b.BI (missing method m)".

This is not an exotic corner: the deep export mode of `gcimporter.IExportData` is what `go/analysis/unitchecker` uses - verified on x/tools master: `unitchecker.go` calls `IExportData` (line 702) and `IImportData` (line 415), and `func IExportData` lives at [iexport.go#L320](https://github.com/golang/tools/blob/master/internal/gcimporter/iexport.go#L320). Any multichecker-style analyzer run across such packages hits the phantom "missing method" failure on code that `go build` accepts.

The reporter's repro is three small packages and the exact two-line error output. The reporter also pinpointed the fix direction - qualify interface methods with their declaring package - and the fix change CL 856622 with exactly that title was posted against the issue within hours (gopherbot cross-reference, attributed to tooling; the CL is real and verified to exist, but review/merge is pending).

## Who this bites

- Anyone running `unitchecker`-based analyzers (custom multicheckers, some CI lint setups) over code that derives local interface types from other packages' interfaces with unexported methods - the analyzer reports type errors on code the compiler accepts.
- Generic code makes it more reachable: `type BGI[T any] a.GI[T]` hits the same misqualification, and generic interface embeddings are increasingly common in shared libraries.
- It also poisons the export-data cache: once `b`'s bad export data is written, every importing package re-derives the wrong method set.

## Limits

- The failure output is the reporter's; I verified the x/tools source layout, the `IExportData`/`unitchecker` call sites, the fix CL's existence and title, but did not run the three-package repro (go repo ~139k stars).
- Whether the bug affects the compiler's own export data (`gcimporter` under the compiler's unified IR path) or only x/tools' deep export mode is not established in the issue; the report scopes it to `IExportData`/`IImportData` and unitchecker.
- The fix CL is posted, not merged; timing and backport policy for x/tools are maintainer decisions.
