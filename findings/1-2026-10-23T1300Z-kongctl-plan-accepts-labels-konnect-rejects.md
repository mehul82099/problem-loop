# kongctl: `plan` accepts labels that Konnect rejects at `apply` time with HTTP 400

- Source issue: https://github.com/Kong/kongctl/issues/2580 (open at check time; no labels; opened 2026-10-23 08:51 UTC; 4 comments; a maintainer wrote "thank you, investigating" and started triage)
- Related issues the reporter links: https://github.com/Kong/developer.konghq.com/issues/7707 (docs: documented label limit of 5 differs from enforced limit, open) and https://github.com/Kong/kongctl/issues/2581 (lint documentation, open)
- Docs read on `main`: https://github.com/Kong/kongctl/blob/main/internal/cmd/root/verbs/help/templates/plan.md
- Project: https://github.com/Kong/kongctl (Apache-2.0; latest release v1.21.0, 2026-10-21)
- Checked: 2026-10-23 13:50 UTC

## Problem
The reporter says that `kongctl plan` succeeds and plans a CREATE for control planes whose labels Konnect then rejects when `kongctl apply` runs, returning HTTP 400 with `rule: is_label` and the label regex `/^(([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?$/`. Their list of cases that plan accepted but apply rejected: a space or `@` in a value, a leading `-`, an empty value, a key or value over 63 characters, a key with a space, a key starting with `konnect_`, and more than 50 labels in total. They tested on kongctl 1.20.2. They point out that teams using `plan` as the review gate only discover invalid labels mid-apply, which can leave a run partly applied.

## What we checked
- The plan help text on `main` describes `kongctl plan` as "a critical step in the declarative configuration workflow, allowing you to preview changes before applying them", so the reporter's reading of plan as the review gate matches the docs' framing.
- Both linked issues exist: the docs issue confirms a separate mismatch (documented label limit of 5 vs the enforced limit), and the lint issue is about documenting lint limits.
- The reporter's regex quote comes from the Konnect error message they pasted; we did not call the Konnect API.
- They tested 1.20.2; v1.21.0 came out on 2026-10-21, and we do not know whether it changes this behavior. No maintainer verdict was in the thread beyond "investigating".

## What this does not tell you
- Whether plan-time validation is missing by design or by oversight is undecided; the reporter asks for either client-side validation or clearer docs.
- We cannot confirm each of the reporter's failing cases independently; the label regex itself is from their error output.
- If you run kongctl in CI, the safe reading is that a green plan does not prove Konnect will accept the apply. That is the reporter's demonstrated point on 1.20.2, not a guarantee about any version.

## Honest limits
- We read the issue, the two linked issues, and the plan help text on `main`. We ran neither kongctl nor Konnect.
- Issue state may have changed since 13:50 UTC.
