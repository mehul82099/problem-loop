# Safari's mitigation of the eMudhra CA key compromise is incomplete - users find 3 of 12 bad chains still trusted, and iPadOS 27.0.1 trusts all 12

- Source issue: https://github.com/galadran/we-have-a-problem.com/issues/69 (open at check time; opened 2026-10-21 21:03 UTC; active multi-user testing thread)
- Background site: https://emudhra.we-have-a-problem.com/ ("eMudhra Intermediate CA Compromise", published 2026-10-20)
- Checked: 2026-10-24 19:20 UTC

## Background
On 2026-10-20, we-have-a-problem.com reported that the private keys of eight eMudhra intermediate CA certificates were compromised; they chain to roots trusted by the Mozilla, Microsoft, Apple, and Chrome root programs. The site demonstrates possession of the keys with a signed message from the original reporter. Root programs have been scrambling to distrust the intermediates; the site tracks mitigation status per vendor.

## The finding in this thread
The site currently lists Safari as mitigated by Apple's latest updates - but users testing with the site's check say that is not the full story:
- macOS 26.7.1 (Safari): 3 of 12 test chains still connect - specifically the three "G3B" intermediates chaining to emSign Root TLS CA - G3 (DV, OV, EV variants). All other chains are rejected.
- iOS 26.7.1: 1 of 12 still trusted (the DV G3B chain).
- iPadOS 27.0.1, tested immediately after upgrading: 12 of 12 trusted - i.e. the compromised set appears entirely unblocked on that OS build at that time.
- One commenter worked out a plausible mechanism for exactly why the G3B chains slip through (an OCSP-related explanation) and a narrow local workaround; we are not relaying the workaround - manual trust-store changes are risky and theirs is unvetted - but the mechanism analysis is in the thread.
- Commenters include trust store / trust asset version numbers with their results, which is the right way to make these reports comparable.

## What we checked
- The issue and its device-by-device results exist as described; the background site and its 2026-10-20 compromise writeup are live.
- The key-compromise claim rests on the site's signed-message demonstration - the standard way to prove key possession - which we did not independently validate cryptographically.
- Every per-device result is self-reported by the named commenters; Apple has published nothing we found confirming which chains are blocked on which OS version.

## What this does not tell you
- Apple may ship trust-store updates out of band; the picture at check time (user-tested) is that the G3B subset is still accepted on current macOS/iOS, and everything was accepted on the iPadOS 27.0.1 build tested.
- This is not a reason to panic: exploitation requires an attacker to use the stolen keys against you, and other vendors' mitigations are further along. It IS a reason the site's "Safari: mitigated" label deserves a footnote, which is exactly what the issue asks for.

## Honest limits
- We read the issue and the background site. No certificates were tested from here.
- Issue state may have changed since 19:20 UTC; trust-store pushes move fast during incidents like this.
