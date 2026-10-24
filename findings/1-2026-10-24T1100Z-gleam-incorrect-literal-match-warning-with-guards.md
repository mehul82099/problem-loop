# Gleam's "match on a literal" warning is wrong when guard clauses decide the branch - and the fix is now a design debate

- Source issue: https://github.com/gleam-lang/gleam/issues/6442 (open at check time; label "discussion"; opened 2026-10-23 11:07 UTC)
- Project: https://github.com/gleam-lang/gleam (Apache-2.0, about 22k stars; latest release v1.19.2, 2026-10-12)
- Checked: 2026-10-24 11:15 UTC

## Problem
On Gleam 1.19.0, this case expression draws a "Match on a literal value" warning on `case Nil`:

```gleam
case Nil {
  Nil if x > y -> todo
  Nil if z <= x -> todo
  Nil -> todo
}
```

The warning says you can already tell which branch will match - but that is false when guard clauses decide the branch: with guards, the compiler cannot know at warning time whether the first or second `Nil` branch (or the catch-all) runs. The warning text claims certainty the language does not have. A minimal, self-contained logic point that does not need a compiler to evaluate.

## What the thread says (it is a live design discussion)
- A core team member (giacomocavalieri) confirmed on Discord this was not intended behavior and asked for the issue; the reporter volunteered to fix it, with a plan to extract the "case used as if" detection and special-case Nil.
- lpil (Gleam's creator) then pushed back: he is not convinced removing the warning is right, thinks the warning is at least pointing at the wrong code (it highlights the case subject, not the pattern), and asked for the Discord reasoning to be posted publicly - which the reporter did via screenshots. lpil's latest comment questions the motivation, noting that the idiom for guard-only branching is `case Nil { _ if ... -> ... }`, and that writing `Nil` instead of `_` looks equivalent to him.
- So at check time: everyone agrees the warning behaves oddly (changing `Nil` to `_` in the patterns silences it, which exposes that the pattern shape - not the matched value - drives the warning); the open question is whether the fix is to suppress it, retarget it, or keep it.

## What we checked
- The issue and the maintainer exchange exist as described; v1.19.0 exists (v1.19.2 is current).
- The core logical claim - guards make branch selection undecidable at lint time - is self-evident from the code shown; the reporter's full reproduction is theirs, not run by us.

## What this does not tell you
- No fix is decided; the discussion is the finding. Do not read the thread as "the warning will be removed" - the language's creator is actively questioning that.
- A harmless curiosity, not a soundness bug: code compiles and runs the same either way; only the diagnostic is misleading.

## Honest limits
- We read the issue and release data. Nothing was compiled.
- Issue state may have changed since 11:15 UTC.
