# ty: should a Python type checker warn about a non-exhaustive match? (ty#1060)

- Source: https://github.com/astral-sh/ty/issues/1060 "Rules for not exhaustive `match` case statements". Opened 2025-08-20, open, 11 comments, 13 reactions on the post, labels control flow, lint, strict. Last comment 2026-10-19.
- mypy's version of the check: https://mypy.readthedocs.io/en/stable/error_code_list2.html (section "Check that match statements match exhaustively", read 2026-10-19).
- ty rule list: https://github.com/astral-sh/ty/blob/main/docs/reference/rules.md (read on 2026-10-19).
- Parent issue named in the thread: https://github.com/astral-sh/ty/issues/887 (closed).

## The question
ty is a Python type checker from Astral (the Ruff team). The reporter asks for a warning when a `match` statement over an enum or other finite type leaves a case unhandled, like pyright's `reportMatchNotExhaustive`.

## What the maintainers said in 2025
- A Ruff maintainer says it fits ty better than Ruff, because it needs type information, and moves it to ty.
- A ty contributor (sharkdp) says it could be a separate opt-in rule, but a non-exhaustive match is not wrong in Python. For fine-grained opt-in today, ty already checks `assert_never` in a final `case _`, and he links a ty playground example.
- A member (AlexWaygood) says mypy offers it as an opt-in error code and that he believes pyright's is on by default. To him, on by default is too opinionated, since it is "more of a lint rule informed by type information than a typing error per se".

## What changed this year
- 2026-07-16: a user notes it is implicitly caught when a function's return type excludes `None`: dropping a `case` makes ty report that the function can return `None` (his example, not run by me).
- 2026-10-17 and 2026-10-19: two users reply that a missing case is a bug in nearly all their code, that opt-in options suffer from "unknown unknowns" (you cannot opt in to a check at a place you did not know to), and that in other languages it is a compile error.
- No maintainer comment after September 2025 in the thread. The issue has no milestone that I could see in the labels.

## What I checked
- mypy documents the check as opt-in via `--enable-error-code exhaustive-match` (matches the maintainer's statement).
- The ty rule reference I read (main branch) lists `invalid-match-pattern` among its match-related rules, and I found no rule for non-exhaustive match in it. The latest ty release at the time was 0.0.89 (2026-10-16). I did not search the full rule list by hand or check the latest docs for the released version.
- I did not check pyright's default.

## What can be said
- Today, with ty, you get exhaustiveness only through `assert_never` or a return type that forces it. The maintainers' stated position was that a default-on rule is too opinionated, and a separate opt-in rule could make sense. No one has decided either way in the thread.

## Honest limits
- I did not run ty on any example, so the `assert_never` and return type behavior are as described by commenters.
- The pyright default and the "other languages" claim are commenters' statements, not checked.
- A year-old maintainer position may have changed since. I can't tell from this thread.
