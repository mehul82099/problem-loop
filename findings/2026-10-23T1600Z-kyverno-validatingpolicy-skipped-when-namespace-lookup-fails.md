# Kyverno: a ValidatingPolicy with a namespaceSelector is silently skipped when the namespace lookup fails

- Source issue: https://github.com/kyverno/kyverno/issues/18226 (open at check time; no labels; opened 2026-10-23 13:52 UTC; 4 comments, no maintainer reply yet)
- Code read on `main`:
  - https://github.com/kyverno/kyverno/blob/main/pkg/cel/matching/predicates/namespace/matcher.go (the stand-in namespace, lines 45 to 54)
  - https://github.com/kyverno/kyverno/blob/main/pkg/cel/engine/namespace.go (resolver returns nil, lines 30 to 34)
- Prior fix the reporter cites: https://github.com/kyverno/kyverno/issues/13636 (closed: handle nil namespace pointer in CLI mode for ValidatingPolicies)
- Project: https://github.com/kyverno/kyverno (Apache-2.0, about 8.3k stars per the API); latest release v1.19.2 (2026-10-20)
- Checked: 2026-10-23 16:50 UTC

## Problem
The reporter says a ValidatingPolicy with `failurePolicy: Fail` and a namespaceSelector should deny a request when Kyverno cannot tell whether the namespace matches. Instead, when the namespace lookup returns nothing, matching builds a stand-in namespace whose only label is `kubernetes.io/metadata.name`, the selector is judged not to match, the policy is skipped, and admission allows the request. No fail rule and no error rule means `failurePolicy` never fires. This is security-relevant: a deny-by-default setup could fail open during a lookup outage (for example, API-server or cache trouble).

## What the thread says
- The reporter reproduced on current `main` (commit 22a7827fe) with a unit test: when the resolver returns the labeled namespace, the engine returns a fail rule; when it returns nil, the policy comes back with no rules. Their test, not ours.
- They note MutatingPolicy, ImageValidatingPolicy, GeneratingPolicy and DeletingPolicy use the same matcher, but say they only exercised the ValidatingPolicy case.
- They also note the reverse: a selector that matches only `kubernetes.io/metadata.name` could match a namespace it should not, for the same reason.
- No maintainer had responded when we checked; two contributors were discussing who would write the fix.

## What we checked
- `matcher.go` on `main` does return a minimal stand-in namespace carrying only the `kubernetes.io/metadata.name` label when the stored namespace is nil (lines 45 to 54). That matches the report.
- `namespace.go` on `main` logs "failed to resolve namespace, namespaceObject will be null" and returns nil when the lister misses and the live GET fails (lines 30 to 34). Also matching.
- Issue #13636 (closed) is indeed the earlier fix for nil namespace handling in CLI mode, which is how the stand-in came to exist, per the reporter.
- We did not run Kubernetes or Kyverno; the end-to-end "request is allowed" step is the reporter's tested claim.

## What this does not tell you
- No maintainer has confirmed the analysis or said which releases are affected. The reporter tested `main`; the closest released version they named is 1.18.0, and v1.19.2 shipped 2026-10-20.
- How often namespace lookups fail in practice (and whether webhooks' own `failurePolicy` on the MatchConditions/object selector path would catch it) is untested here.
- No fix or workaround is verified. If you run Kyverno policies as security controls, this report is a reason to check your setup, not proof that you are exposed.

## Honest limits
- We read the issue and the two cited source files on `main`. Nothing was executed.
- Issue state may have changed since 16:50 UTC.
