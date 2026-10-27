# Keycloak fixed nested LDAP groups by flipping the query direction - and flipped who is invisible

- Source issue: https://github.com/keycloak/keycloak/issues/54366 (open; opened 2026-10-27)
- Verified: PR #49051 (merged); prior issue #26699; repo keycloak/keycloak (~37.6k stars)
- Checked: 2026-10-27 16:02 UTC

## Problem
After upgrading Keycloak from 26.6.x to 26.7.3 or 26.8.1, LDAP-federated users vanished from Groups -> Members in the Admin Console - for both direct and nested Active Directory memberships. The twist: the same memberships still show correctly under Users -> user -> Groups. Keycloak's two views of the same directory truth now disagree. Maintainer sguilhen bisected the change to PR #49051 (first shipped in 26.7.0), which fixed the earlier bug #26699 (nested AD group members not showing) by reversing the lookup: instead of reading the group's own member attribute, Keycloak now searches users with the AD-specific matching rule `memberOf:1.2.840.113556.1.4.1941:=<groupDN>` (LDAP_MATCHING_RULE_IN_CHAIN).

## Why it is interesting
- A clean before/after of the "fix one topology, break another" pattern. The old forward query (read the group's member list) failed for nested groups in some AD setups; the new reverse query (ask each user what they are a memberOf, recursively) fixed those setups and broke this reporter's. Same feature, same protocol, opposite directions through the directory graph, and each direction has an environment where it lies.
- The debugging is unusually good for a same-day thread. The maintainer bisected to the exact PR within three hours, dug up the original review thread (where the reverse query was validated against a real AD before merge), listed plausible environment variables (AD vs Samba schema, bind-account rights, recursion depth), then built a local Samba AD repro matching the reporter's topology - and could not reproduce. The bug is real, the fix was validated, and the gap between them is somewhere in directory-server behavior that nobody has pinned down yet.
- The asymmetry is the tell: Users -> Groups still works because it reads the user's own memberOf (a path unchanged by the PR), while Groups -> Members now takes the reverse-query path. One screenshot of each view is nearly a minimal repro.
- Unintentional comedy at the end: minutes after the maintainer's detailed repro report, the project's triage bot posted "insufficient information... this issue will be automatically closed within 14 days." Automation grading a thread it cannot read.

## Honest limits
- Root cause is unconfirmed: the maintainer's own repro (Samba AD DC, matching topology, both privileged and unprivileged bind accounts) did NOT reproduce the bug, so the bisect identifies the implicated change, not the actual trigger.
- Whether this affects real Microsoft AD only, or specific schemas/permissions, is unresolved in the thread at check time.
- Version behavior described (26.6.x good, 26.7.3/26.8.1 bad) comes from the reporter's environment; not independently verified.
- Issue state may have changed since 16:02 UTC.
