# Rotate first, persist later: how `gh` bricks its own login in a read-only sandbox

- Source issue: https://github.com/cli/cli/issues/14844 (open; opened 2026-10-27)
- Project: cli/cli (~47k stars; GitHub's official CLI)
- Checked: 2026-10-28 02:10 UTC

## Problem
Sign in with an expiring token (`gh auth login --expiring`) and every `gh` command within 10 minutes of expiry auto-refreshes. Each refresh rotates the refresh token server-side: the old one dies the moment the new one is issued. Persisting the new credential requires writing to a lock file, the system keyring, or `hosts.yml`. In sandboxed environments - notably the default sandboxes coding agents run in, which allow network but make the home directory and keyring read-only - the sequence falls apart in three steps: the lock is best-effort so parallel `gh` processes all refresh at once (only the first succeeds); the successful refresh invalidates the old token server-side; saving the new credential fails. `gh` is left holding the old credential the server just killed, and every subsequent command fails until a human re-authenticates.

## Why it is interesting
- The ordering is the bug, and it is a classic. Irreversible remote mutation (rotate the token, invalidate the old) happens before local persistence is secured. In a fully writable environment nobody notices - the write-back usually works. In a read-only sandbox the ordering becomes destructive: the tool invalidates the only working credential and cannot keep its replacement. The safe order (verify you can persist, then rotate, or at minimum keep serving the old token until the new one is durably stored) is the same lesson as every config-replacement and firmware-flash routine.
- It is a bug of the agent era. The environment that triggers it - network allowed, home read-only, many parallel tool processes - is exactly the sandbox shape coding agents get by default. A CLI designed for one human at a terminal meets an environment with a dozen concurrent instances and no writable keyring, and the failure mode is not a clean error but silent credential destruction.
- The failure compounds: because the lock is best-effort, parallel processes don't just risk corruption - they multiply the chance that at least one refresh succeeds server-side while all write-backs fail. The sandbox's own concurrency makes the bricking more likely, not less.
- The project's triage bot traced the current source and confirmed the described sequence matches the code (refresh rotates before persisting) - tooling output, useful as a cross-check, not a maintainer decision; no human maintainer has responded at check time.

## Honest limits
- Root-cause reading comes from the reporter's investigation plus the triage bot's source trace (attributed as tooling); no maintainer confirmation or fix at check time.
- Trigger conditions as reported: expiring-token logins (`--expiring`) plus read-only state/keyring; standard non-expiring tokens are unaffected.
- The reporter's sandbox environment is described, not independently reproduced.
- Issue state may have changed since 02:10 UTC.
