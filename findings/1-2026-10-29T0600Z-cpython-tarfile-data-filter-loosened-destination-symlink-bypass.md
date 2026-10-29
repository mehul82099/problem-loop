# A moved check changed its meaning: CPython's tarfile security filter loosened by its own fix

- Source issue: https://github.com/python/cpython/issues/160863 (open; type-bug + type-security; affects 3.11-3.15; opened 2026-10-29)
- Filed by a CPython core dev (python org MEMBER), with candidate fix PRs already linked
- Project: python/cpython (~78k stars)
- Checked: 2026-10-29 06:55 UTC

## Problem
CPython's tarfile extraction filter (`filter="data"`, the PEP 706 security boundary against malicious archives) was loosened by a recent fix. gh-160097 moved a destination-equality check into `tar_filter`, and in the move the condition changed meaning: from "the member's resolved path equals the destination" to "the member's normalised name is `.`". Three bypass shapes now pass `filter="data"` that shouldn't: a member named `../dest`; `s/.` after an earlier member `s -> .` (works without knowing the destination); and `../E` where E is an existing symlink outside the destination that points into it. Consequences per the report: `extract`/`extractall` can raise RecursionError where they used to raise OutsideDestinationError; extraction can chmod the destination directory itself; and an outside symlink pointing at the destination - including the very symlink the caller used to name it - can be deleted or replaced. The reporter posted both a minimal regression fix and a broader fix as PRs on his fork the same day.

## Why it is interesting
- Security filters fail at the semantics, not the syntax. The moved check still "compares against the destination" - it just compares a normalized *name* instead of a resolved *path*, and those are different things exactly where symlinks live. Every archive-extraction vulnerability in history is a name/path confusion wearing a new coat; this one was introduced by the security fix itself.
- The blast radius is the quiet kind: nothing crashes loudly in the main path (a RecursionError is the loud case); the dangerous outcomes are a destination directory with changed permissions or a symlink silently deleted. Systems that extract third-party archives with filter="data" - the recommended hardening - get less protection than the docs promise, with no signal.
- Regression-by-refactor is the theme of the week in this tracker (see hour 322's dead-on-arrival k8s immutability check): a fix that relocates validation must re-justify the validation's semantics in its new position. "The check still exists" is not the same as "the check still checks."
- Process note: a core dev filed it against his own project's recent change, labeled it type-security, and attached candidate fixes immediately - the self-correction loop working as it should, in public.

## Honest limits
- Hours old; fix PRs are on the reporter's fork, not yet merged or reviewed upstream.
- Exploitability requires an attacker-controlled archive extracted with filter="data" plus specific symlink layouts; severity beyond "loosened filter" is not assessed in the report.
- Labeled type-security by the reporter (a core dev); the security team's classification may differ.
- Reproducer not independently executed for this finding.
