# rustfmt: `group_imports` can move a comment away from the imports it describes (rust-lang/rustfmt#6241)

- Source issue: https://github.com/rust-lang/rustfmt/issues/6241 . Opened 2024-07-14, open, labels include "C-bug", "A-comments", "A-imports", "only-with-option", "UO-group_imports" and "I-unexpected-motion". 12 reactions on the post, 8 comments, the latest two on 2026-10-19.
- Related and still open when checked: https://github.com/rust-lang/rustfmt/issues/3720 (comments on `use` statements rearranged when `use` statements are rearranged) and the tracking issue for the option, https://github.com/rust-lang/rustfmt/issues/5083 ("[unstable option] group_imports").
- Option docs, read 2026-10-19: https://github.com/rust-lang/rustfmt/blob/master/Configurations.md (section `group_imports`).
- The pull request the reporter cites as the consequence: https://github.com/rust-lang/rust/pull/126776 "Clean up more comments near use declarations", closed.

## The problem
The reporter (a Rust compiler contributor) says that with `group_imports = "StdExternalCrate"` rustfmt sorts all consecutive imports into three groups and keeps a comment attached to the single `use` right after it. If your comment was written about a whole run of imports, the reformatted file can show it above a different import, so its meaning changes. He says in the issue that it makes it effectively impossible to have a comment that applies to a chunk of imports. His suggested fix: treat a comment line like other statements (such as a `mod`), which the docs say split imports into separate sets, so each side is grouped separately.

## Scope, per the docs
- `group_imports` is an unstable option. The docs list it as "Stable: No" with tracking issue #5083, and the default is `Preserve`, which keeps your groups. So this affects people who opted in on nightly rustfmt.
- The docs say other statements between imports cause different grouping sets. They do not say what a comment does. That gap is the issue.

## What the thread says
- A contributor (2025-10-13) lists four possible behaviors: stop grouping after a blank line plus a comment; treat the lines after as a new set to be regrouped; allow subgroups inside each of the three groups; or always format into the three groups and treat each comment as describing a single import. He says he would pick the first, and also has some sympathy for the last.
- Another commenter (2026-02-19) suggests skipping the file if its import section has comments. A project member replied that this would still leave the other cases to handle, and that once a behavior ships it cannot be changed.
- On 2026-10-19 a commenter argues the comment should stay with the grouped imports, even if some path appears twice, and shows a layout he wants. A project member replied that it is unclear whether a comment sticks to the group above or below, and that with a blank line before the comment it probably belongs to the group below. A third commenter says rustfmt should follow the Rust style guide instead.
- Nobody in the thread has posted a patch or a decision. The member's point about not being able to change shipped behavior is why the option stays unstable.

## What can be said
- This is a design question with no agreed answer, so no fix is near, as far as the thread shows. It is not just a bug to patch, because every option changes how existing code is formatted.
- If you use `group_imports` on nightly, check diffs near commented imports after formatting. I did not run it myself.

## Honest limits
- I did not run rustfmt or reproduce the reorder. The example is from the reporter.
- I read the issue and all its comments, and checked the linked issues by title and state only.
- I did not check the style guide text the last commenter cites, or whether the option behaves differently in the latest nightly.
