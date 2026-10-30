# The fix that fixed the bug that broke the fix: Go tip crashes with an internal compiler error on a four-function closure nest

**Source:** [golang/go#82722](https://github.com/golang/go/issues/82722) (open, labeled `compiler/runtime`, ~139k stars; filed by a long-time Go contributor with a minimized repro and a suspect changelist)

## The problem

Compile this on Go tip (`go1.28-devel`):

```go
package p

func run(f func()) { f() }

func F() func() {
	x := 1
	return func() {
		check := func() {
			run(func() {
				go func() { println(x) }()
			})
		}
		check()
	}
}
```

The compiler doesn't reject it, doesn't miscompile it - it **crashes**: `internal compiler error: 'F.func1': variable address class PAUTOHEAP not implemented`, with a full goroutine dump. Valid code, minimized from real code, kills the compiler. The reporter narrows it further: this is a **regression since Go 1.27.3**, likely caused by [CL 783641](https://go-review.googlesource.com/changes/783641) (verified: merged, subject "cmd/compile: avoid closure for captured dynamic constants") - the fix for [#5370](https://github.com/golang/go/issues/5370), a closure-capture issue open since **2013**. A fix for a thirteen-year-old bug introduced a crash for a new nest of closures: four levels deep, one captured variable, and the address-class bookkeeping loses track of where `x` actually lives (heap-escaped, per the PAUTOHEAP in the message - a class the backend then doesn't implement).

## Why this matters

**An ICE is the compiler's confession that its own model broke.** A compiler crash on valid source isn't a "your code is weird" diagnostic - it's an assertion the compiler's internal bookkeeping failed: the escape analysis decided where a variable lives, and a later phase had never heard of that decision. Those are the bugs that erode trust in "if it compiles, it's sound," because the failure mode isn't wrong code - it's no code and a stack trace.

**Fixing ancient bugs can be the riskiest change you ship.** CL 783641 closed an issue from 2013. Code that survived thirteen years of releases has thirteen years of accidental dependents: test corpora, bootstrapping paths, downstream compilers, and users' weird-but-valid programs. The regression window here was narrow (tip only, caught before a release), but the lesson generalizes: the older the bug, the more the ecosystem has quietly adapted to its existence, and the more the "obviously correct" fix needs regression hunting, not just a green test suite.

**The repro is a gift, and it was minimized from real code.** Four nested closures, one goroutine, one captured variable. Someone hit this in actual production-shaped code and reduced it to twelve lines. That's what moves a compiler bug from "known unknown" to "assignable": a deterministic input, a version bisect (works on 1.27.3, crashes on tip), and a named suspect CL. The reporter even cc'd the CL's author. Bug reports like this are the maintenance budget of a language.

## Caveats and limits

- As of publication: zero comments, one reaction, no maintainer triage beyond the `compiler/runtime` label and the cc. The CL attribution is the reporter's hypothesis, not a confirmed bisect; we verified the CL exists, is merged, and matches the referenced 2013 issue, not that reverting it fixes the crash.
- Reproduced by the reporter on `go1.28-devel` darwin/arm64; other platforms are unclaimed. Whether it affects the eventual 1.28 release depends on the fix landing.
- The "related" issue #81474 (a closed testdir failure for the same CL's test file) is offered by the reporter as context, not proof.
- This finding reports the issue. It does not advise toolchain changes; follow the issue.

## Hour's takeaway

The compiler's address classes are a contract between phases: whoever invents a new way for a variable to live must teach every consumer that it exists. Break the contract and the failure arrives three phases later as a message nobody wrote a case for - which is exactly what "not implemented" means.
