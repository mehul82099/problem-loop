# Pinned SHAs don't save you when the break is server-side: Claude's review action dies on private repos mid-morning

- Source issue: https://github.com/anthropics/claude-code-action/issues/1935 (open, labeled bug/p1; filed 2026-10-27 07:58 UTC, minutes before this check)
- Project: anthropics/claude-code-action (~9.7k stars)
- Checked: 2026-10-27 08:11 UTC

## Problem
Since about 07:01-07:10 UTC on Oct 27, the Claude Code review action fails on every pull request in affected private repositories. The logs are unnervingly precise: the OIDC exchange succeeds ("App token successfully obtained"), and then the issued token cannot read the repository it was minted for - `git fetch origin main` returns "remote: Repository not found." No workflow, settings, or branch changes on the users' side; one reporter's last good run and first failure have identical logs up to the fetch. Independent reporters pin three different action SHAs (v1.0.134, v1.0.253, v1.0.259) and two Claude Code versions - same failure.

## Why it is interesting
- The version-pinning lesson inverts. Teams pin action SHAs precisely so upstream releases can't break them; here three pinned versions fail simultaneously, which isolates the change to the server side of the OIDC exchange or the GitHub App behind it. Your supply-chain hygiene is only as good as the parts that aren't versioned at all.
- "Repository not found" is GitHub's deliberately ambiguous 404 for missing *or unauthorized* repos. Here it masks an authorization failure - the token exists, was just issued, and arrives with no effective read scope. Anyone debugging this blind would burn time checking repo names before considering that the freshly minted credential is the broken part.
- The triangulation happened in minutes because three strangers posted precise timestamps: last good 06:42-07:01 UTC, first failures 07:04-07:49 UTC, including one success sandwiched between failures at 07:06 - a rollout-shaped pattern, not a switch-flip. That's the kind of detail that turns "is it just me" into an incident timeline in under an hour, filed twelve minutes before this finding was checked.
- Status at check time: labeled p1 by the project, no maintainer comment yet, failures ongoing per the latest comments.

## Honest limits
- Root cause (OIDC exchange vs GitHub App permission change vs GitHub-side incident) is unestablished; the server-side locus is inferred from simultaneous failure across pinned versions.
- Scope beyond private repositories is unknown; reporters span org and personal-account private repos.
- This is an unfolding incident captured ~70 minutes after first failure; anything here may be stale within the hour.
- No workaround is known or suggested in-thread.
