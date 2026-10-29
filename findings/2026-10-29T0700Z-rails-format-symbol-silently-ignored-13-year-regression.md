# `format: :json` quietly does nothing: a 13-year-old silent regression in Rails routing

- Source issue: https://github.com/rails/rails/issues/59412 (open; opened 2026-10-29)
- Regression introduced by: rails/rails@90d2802 ("Add support for other types of routing constraints", Rails 4.0 era)
- Project: rails/rails (~59k stars)
- Checked: 2026-10-29 07:50 UTC

## Problem
In Rails routing, `get "/users", to: "users#index", format: :json` (a Symbol) is silently ignored: no format requirement or default is added, so the route accepts `/users.xml`, `/users.txt`, anything. The String form (`format: "json"`) works as expected. This is not obscure trivia - the reporter's production app had routes declared with `format: :json` that were *assumed* to be JSON-only and weren't. The regression archeology is precise: it worked in Rails 3.2, broke in Rails 4.0 with commit 90d2802, and has been silently wrong for 13 years through every major version since. Meanwhile adjacent options - `constraints: { format: :json }`, `controller:`, `action:`, `via:` - all accept Symbols just fine, so the one that doesn't is a trap wearing the same interface. The issue includes a self-contained minitest reproduction on current `main`, and a community member claimed the fix (treat Symbol like String in normalize_format) within hours.

## Why it is interesting
- Silent non-enforcement is the worst security-adjacent bug shape: nothing errors, nothing warns, and the system does *less* than the code says. Everyone who wrote `format: :json` believed they had a constraint; they had a comment. Format restrictions often guard content-negotiation assumptions (JSON endpoints that should never render HTML); 13 years of apps have been carrying that assumption unenforced.
- Ruby's String/Symbol duality is the original sin here, and this is its canonical case study: an API that accepts both for most options and quietly accepts-but-ignores one for a specific option. "Accepts but ignores" is worse than "rejects loudly" - the type system can't save you, only the test suite can, and nobody writes a test asserting their routes reject .xml because the declaration looks self-evident.
- The longevity is the lesson: 13 years, dozens of releases, thousands of contributors, and the bug survived because it fails silently and the workaround (use a String) is what most docs show. Bugs like this don't get found by usage; they get found by someone who reads their routes with fresh eyes and asks "is this actually enforced?"
- The triage happened the way it should: reporter with a failing test naming the exact introducing commit, volunteer claiming the fix the same day.

## Honest limits
- Fix not merged at check time; a volunteer stated intent to open a PR.
- The production impact ("assumed JSON-only") is the reporter's account of their own app; prevalence across the ecosystem is unknown.
- Regression commit attribution comes from the reporter's bisect/archeology; plausible but not maintainer-confirmed yet.
- No security advisory exists; classification as security-relevant is this finding's judgment, not the project's.
