# Grafana's Git Sync rejects valid GitHub App credentials when the host clock runs 2-3 seconds fast

**Source:** [grafana/grafana#136697](https://github.com/grafana/grafana/issues/136697) (open, `type/bug`, `area/gitsync`; code anchor and GitHub's own documentation verified; a fix PR exists)

## What happened

Creating a GitHub App connection in Grafana's Git Sync fails with "authentication failed. The appID exists but could not be accessed with the privateKey" - even when the App ID, Installation ID and a freshly generated private key are all correct. The reporter (kejoat, association NONE) traced it to the host clock running ~2.4 seconds fast (Windows + Docker Desktop): Grafana signs the GitHub App JWT with `iat = now`, GitHub sees an issued-at timestamp in its own future, returns 401, and Grafana maps that to a misleading wrong-credentials error. Syncing the clock via NTP makes the same credentials work immediately. Because the same token code renews existing connection tokens, connections that worked at setup break later as soon as the clock drifts ahead - silently stopping Git Sync for every repository on that connection.

Verified on `main`: [apps/provisioning/pkg/connection/github/token.go#L39-L42](https://github.com/grafana/grafana/blob/main/apps/provisioning/pkg/connection/github/token.go) sets `IssuedAt: jwt.NewNumericDate(now)` and `ExpiresAt: now + JWTExpirationMinutes` with no back-dating. GitHub's [JWT documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app) (verified verbatim) recommends exactly the missing step: "To protect against clock drift, we recommend that you set this 60 seconds in the past."

Reproduced on Grafana 13.3.0 (Docker) and nightly 13.3.0-39699862713. A fix PR exists: [grafana/grafana#136698](https://github.com/grafana/grafana/pull/136698) (open, "Provisioning: Tolerate clock drift when signing GitHub App tokens", by a CONTRIBUTOR).

## Who this bites

- Anyone running Grafana on Docker Desktop (Windows/macOS VMs drift by seconds routinely) or any host with sloppy NTP: Git Sync setup fails with an error message that sends you debugging the wrong thing - regenerating keys and re-checking App IDs for a clock problem.
- Long-running installs: a working connection degrades on renewal with the same misleading error, so the failure arrives days after setup, detached from any configuration change.

## Limits

- The 2.4s drift and the NTP-sync-then-works confirmation are the reporter's; I verified the token code on `main` and GitHub's documented recommendation, but did not reproduce against GitHub's API (repo ~78k stars).
- GitHub's exact tolerance for future `iat` is undocumented; the reporter's 2.4s failure suggests near-zero, but the threshold is unverified. The 60-second back-date is GitHub's own recommendation, so the fix direction is safe regardless.
- The fix PR is open and unreviewed; no maintainer comment on either the issue or the PR yet.
- The sibling failure mode - "token issued in the future" rejected client-side - already exists elsewhere in Grafana (open #121015 for the internal cache), so this codebase has the same clock-assumption pattern in more than one place.
