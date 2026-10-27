# A "no behavior changed" crypto refactor turned 0 ms into 30 seconds of event-loop freeze

- Source issue: https://github.com/nodejs/node/issues/67067 (open; opened 2026-10-27)
- Verified: implicated PR nodejs/node#64211 (merged)
- Project: nodejs/node (~115k stars)
- Checked: 2026-10-27 21:20 UTC

## Problem
`crypto.createDiffieHellman(prime, generator)` with the standard RFC 3526 MODP primes now blocks Node's main thread for seconds - 0.3 s at 2048 bits, 4 s at 4096, 30 s at 8192 - on Node 24.20.0+ and 26.6.0+. The same call returned in under 1 ms on 24.19.0 and all of 22.x. The reporter bisected it to PR #64211 ("crypto: split OpenSSL 3, BoringSSL, and legacy backends"), whose commit message explicitly says no public API behavior is intentionally changed. What the refactor lost: OpenSSL's DH_check recognizes the standard named groups and skips the expensive primality proof; after the split, the check runs without that fast path. The named-group variants (`getDiffieHellman`, `createDiffieHellmanGroup`) stay fast - only the explicit-prime form regressed.

## Why it is interesting
- The invisible-fast-path pattern. The speed everyone relied on was not in Node's code at all; it was a shortcut inside OpenSSL's DH_check that recognizes RFC 3526 groups. A backend refactor that faithfully re-implements "check the prime" without knowing about "unless it is a named group" turns a constant-time lookup into a full primality check on an 8192-bit prime - on the event loop thread. Nothing in the diff looks like a slowdown.
- Production confirmation arrived within an hour. A commenter running ssh2-based SFTP hit exactly this: after their image moved to Node 24.20+, handshakes with one server (using diffie-hellman-group-exchange-*) froze for 27-30 s and failed with client-timeout. The library asks the server for an 8192-bit group, calls the explicit-prime form, and the event loop goes away for half a minute. Their preload shim is a workaround, and the thread attributes it as such - not a fix.
- The timing table is a free fingerprint. 0.3 s / 1.9 s / 4 s / 12 s / 30 s scaling with prime size is exactly what a primality check looks like; anyone hitting "SFTP suddenly slow after a Node upgrade" can match their symptom in one glance.
- A Node.js member reacted within minutes of the production report, so the thread is on the right radar - but no fix or root-cause confirmation from the project at check time.

## Honest limits
- Root cause (lost named-group fast path in DH_check after the backend split) is the reporter's bisect plus source reading; the Node project has not confirmed it at check time.
- Timings come from the reporter's 4-core Linux x64 machine; absolute numbers vary, the shape does not.
- Affected versions stated as 24.20.0+ and 26.6.0+ per reporter's measurements; earlier 26.x boundary not independently verified.
- Issue state may have changed since 21:20 UTC.
