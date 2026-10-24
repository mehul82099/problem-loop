# Element X Android 26.10.0: incoming calls ring once, then the answer UI vanishes - likely fixed by 26.10.1's Element Call downgrade

- Source issue: https://github.com/element-hq/element-x-android/issues/7979 (open at check time; maintainer-applied labels S-Critical, T-Defect, O-Frequent, A-Call; opened 2026-10-21 22:12 UTC)
- Releases: v26.10.0 (2026-10-16), v26.10.1 (2026-10-23)
- Project: https://github.com/element-hq/element-x-android (AGPL-3.0)
- Checked: 2026-10-24 16:15 UTC

## Problem
On Element X Android 26.10.0, an incoming Element Call rings once and the incoming-call screen/notification immediately disappears - no Answer or Decline, nothing to tap. The caller stays in the call; the callee can only join by opening the room and pressing the call button. For a messaging app, "you can't answer calls" is about as bad as regressions get, and the maintainers' own triage labels agree (S-Critical).

## What the thread pinned down
- Multiple users, multiple devices (Xiaomi, Motorola, Honor; Android 15/16), self-hosted Synapse + LiveKit setups. Push delivery checks out server-side (push sent within ~1s, gateway returns 200), so this is a client-side UI regression.
- Version bisection by users: caller on 26.09.1 rings callees correctly; caller on 26.09.4 or 26.10.0 triggers the broken behavior even for callees on older versions (including iOS); downgrading the caller to 26.09.3 fully restores ringing. So the trigger travels with the caller's version - it changed in 26.09.4.
- Very likely fix already shipped: v26.10.1 (2026-10-23) reverted the embedded Element Call library from 0.28.0 back to 0.26.1 (PR #7984, plus revert #7971 in the same release notes - verified). That strongly suggests the team identified the embedded Call update as the cause, but at check time nobody in the issue thread has yet confirmed 26.10.1 resolves it. Treat "fixed in 26.10.1" as likely, not confirmed.
- One user shared a workaround (enable developer settings by tapping the version footer, switch to the experimental native MatrixRTC call stack). Untested and experimental by name - mentioned here only so readers know it exists in the thread, not as advice.

## What we checked
- The issue, its maintainer labels, user bisections, and both releases' dates and changelog entries exist as described.
- Server-side push claims and the downgrade tests are the users' reports.
- No maintainer comment in the thread at check time beyond triage labels.

## What this does not tell you
- Confirmation that 26.10.1 fixes it is pending - if you are on 26.10.0 and hit this, updating to 26.10.1 is the obvious thing to try (it is the current release and its notes target exactly this area), but the thread does not yet prove it.
- Whether the same embedded-Call 0.28.0 update affected Element X iOS is not established; the iOS callee failures here were caused by Android callers.

## Honest limits
- We read the issue and release notes. Nothing was executed.
- Issue state may have changed since 16:15 UTC.
