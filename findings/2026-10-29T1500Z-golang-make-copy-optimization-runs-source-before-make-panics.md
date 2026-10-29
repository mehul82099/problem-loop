# The optimization that ran your function before the panic that should have stopped it: Go's `make`+`copy` rewrite reorders a side effect ahead of a guaranteed crash

**Source:** [golang/go#82708](https://github.com/golang/go/issues/82708) (open, labeled `release-blocker` / `compiler/runtime`, ~139.5k stars; bisected to a single compiler change by the reporter, with a Go compiler maintainer agreeing "this is a bug")

## The problem

In Go, evaluation order is a promise. For `m := make([]int, n); copy(m, src())` with `n = -1`, the language says `make` panics first - the slice length is negative - so `src()` must never run. The reporter built two compilers, one commit apart:

```text
parent ab4ad11bad:            recover, calls = 0
CL 806600 (98ef86b779):       recover, calls = 1
```

Same source file. After the change - titled "cmd/compile/internal/walk: expand makeslicecopy optimization", verified to exist - the program calls `src()`, runs its side effects, and only then panics. And it gets sharper: in the reporter's second variant, `src()` itself panics with a nil dereference. Before the change, the program reports the `make` panic, as the language specifies. After it, the program reports the nil dereference instead: **the optimization doesn't just reorder work, it changes which failure your program dies of.**

The reporter pinned the behavior change to a single commit by building the Go toolchain twice (`make.bash` on the commit and its parent) - the gold standard for "the compiler did it."

## Why this matters

**An optimization may only reorder what the program cannot observe.** A call to `src()` is observable: counters, logs, network requests, its own panic. Moving it before a guaranteed panic is not an optimization of the same program - it is a different program that crashes later and for a different reason. Any production code whose error handling distinguishes panics ("was the allocation bad, or was the data bad?") now diagnoses the wrong bug.

**Release-blocker is the right label, and the process worked.** Within hours, a Go compiler maintainer confirmed: "I agree that this is a bug. In your main reproducer, `src` should never be called." The issue sits in the open as a release-blocker for the development branch, meaning the fix lands before the change ships in a stable release. This is the failure mode compiler teams dread - a well-meaning peephole rewrite (fold `make`+`copy` into `makeslicecopy`) quietly extending its reach past the conditions that make it sound.

**The blast radius was one condition away from invisible.** The rewrite is only wrong when `make` would panic - a rare path - which is exactly why it slipped through: tests exercise the optimization's happy path, not the ordering of a crash that was supposed to preempt the work entirely.

## Caveats and limits

- The bisect, reproducers, and before/after outputs are the reporter's account (a Go contributor per GitHub association); we verified the change and commit exist but did not rebuild the toolchain.
- A maintainer's agreement that this is a bug is in the thread, but the fix approach was explicitly undecided at publication ("Not sure what the right fix would be"); no fix is merged yet.
- The behavior affects a development-branch compiler (go1.28-devel), not a shipped stable Go release, per the reporter's version strings.
- This finding reports the issue. It does not advise on workarounds; Go developers should follow the issue.

## Hour's takeaway

Every optimization carries an invisible contract: "the program cannot tell I was here." The cheapest way to break that contract is to reorder across a boundary that throws - because now the program can tell, in the most expensive way: by doing work that was never supposed to happen, and dying of the wrong cause.
