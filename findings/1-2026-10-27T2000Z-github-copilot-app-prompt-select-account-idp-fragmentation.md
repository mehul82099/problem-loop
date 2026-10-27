# One OAuth parameter, two incompatible enterprise IdPs: a "fresh sign-in" fix breaks MCP auth

- Source issue: https://github.com/github/app/issues/5115 (open; opened 2026-10-27)
- Verified: sibling issue github/app#5089 (open); Ping Identity doc linked by reporter
- Project: github/app (~2.2k stars; the GitHub Copilot desktop app tracker)
- Checked: 2026-10-27 20:15 UTC

## Problem
The GitHub Copilot app v1.1.32 cannot complete OAuth sign-in for remote MCP servers protected by PingFederate. Clicking Sign in sends an authorization request with `prompt=select_account`; PingFederate immediately bounces back with `error=invalid_request, error_description=select_account currently unsupported for prompt`. For the reporting org, every custom MCP server is now unauthenticatable - "production-blocking." Sibling issue #5089 reports the identical failure against Workato (which rejects the same parameter with `account_selection_required`), and narrows the regression window: v1.1.30 works, v1.1.32 fails. The likely source is quoted from the v1.1.31 release notes: "Clicking Sign in on an MCP server now starts a fresh sign-in instead of silently reusing cached authorization."

## Why it is interesting
- A security-minded fix colliding with spec fragmentation. "Always start a fresh sign-in" is a reasonable hardening decision, and `prompt=select_account` is a legitimate OIDC Core parameter. But OIDC support is a menu, not a contract: Ping Identity's own documentation says its authorization server does not support that value. The app picked one legal way to force re-authentication and instantly lost every enterprise IdP that doesn't implement it - PingFederate and Workato confirmed in two issues, likely more unreported.
- The reporter's homework is the model version of regression reporting. They linked the IdP vendor's own doc proving the parameter is unsupported, found the sibling issue with the second affected IdP, bisected the version window (1.1.30 good, 1.1.32 bad), and quoted the exact release-note line that probably introduced it. A maintainer could pick this up with zero additional repro work.
- It shows where enterprise auth actually lives: not in the spec, but in the intersection of what the biggest IdP deployments bother to implement. A change that is correct against OIDC Core can still be a breaking change against the installed base - and the installed base is what signs people in at 9am.
- Confirmation is spreading: a second org posted the same failure in-thread within hours, while no GitHub response had appeared at check time.

## Honest limits
- The regression-source attribution (v1.1.31 fresh-sign-in change) is the reporter's reading of release notes plus the version window; GitHub has not confirmed the root cause.
- Affected IdP count is two confirmed (PingFederate, Workato); others unknown.
- The thread contains off-topic email-reply noise from an unrelated user; signal per above.
- No vendor response or workaround in the thread at 20:15 UTC; issue state may have changed since.
