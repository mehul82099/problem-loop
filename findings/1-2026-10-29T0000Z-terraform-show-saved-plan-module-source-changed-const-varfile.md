# `apply` trusts the plan, `show` doesn't: Terraform's const-variable module source breaks saved plans

- Source issue: https://github.com/hashicorp/terraform/issues/39468 (open, bug; opened 2026-10-28)
- Project: hashicorp/terraform (~50k stars)
- Checked: 2026-10-29 00:40 UTC

## Problem
Terraform 1.16.7: a module whose source is interpolated from a `const = true` variable (`source = "./mod_${var.ref}"`, default "a", overridden to "b" via `-var-file`) plans and applies fine - `terraform apply p.bin` uses the variable values stored in the plan file. But `terraform show p.bin` on the same saved plan fails with "Couldn't show local plan - Plan read error: Module source has changed ... Run terraform init". Reading the plan back re-evaluates the module source with the variable's default ("a") instead of the value recorded at plan time ("b"), and the module-consistency check then accuses you of changing the source since install. Two commands that should agree about the same artifact disagree; the read path is the one that's wrong. The minimal repro is three tiny files. A HashiCorp contributor acknowledged the report.

## Why it is interesting
- New-feature seams are where consistency bugs breed. `const` variables are a recent addition: a variable frozen at plan time, stored in the plan. Every consumer of variable values has to learn to read them from the plan - and `show` (a pure read path nobody associates with evaluation) apparently re-derives the source address from defaults instead. The plan/apply path got the memo; the plan/show path didn't.
- The error is a false accusation. "Module source has changed - run terraform init" tells the user they did something they didn't do, and prescribes a fix that can't help: the plan already recorded the correct source. Bad error messages during real edge cases burn the exact user trust that careful plan/apply workflows depend on - `show` is how people *audit* plans before applying them.
- Saved-plan workflows are the safety-critical path. Plan-out-then-apply-later is how teams get review and CI gates on infrastructure changes. If `terraform show` - the audit tool - can't read its own plan format in a supported configuration, the audit step silently gets skipped or the pipeline fails on a phantom.
- The asymmetry is the tell: apply reads values from the plan, show re-evaluates from config defaults. Any system with "stored intent" and "recomputed intent" paths needs both to agree, and they diverge exactly at the seams of newer features (const, interpolation, module sources - three features meeting in one edge case).

## Honest limits
- Filed ~7 hours before check; acknowledged by a contributor but no root-cause confirmation or fix yet.
- Reproduced on 1.16.7 / darwin_arm64; other platforms and versions unverified (likely version-, not platform-, specific).
- Workaround is presumably to pass the same var-file to `show`; the thread doesn't yet document one.
- Impact is the read/audit path failing; apply of the saved plan works per the report.
