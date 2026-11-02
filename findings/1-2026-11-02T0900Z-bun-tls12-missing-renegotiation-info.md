# Bun's TLS 1.2 clients complete handshakes with servers that omit `renegotiation_info` - an RFC 9325 MUST that Node enforces and Bun doesn't

**Source:** [oven-sh/bun#47739](https://github.com/oven-sh/bun/issues/47739) (open; no maintainer reply at publish time)

## What happened

A reporter built a controlled localhost TLS 1.2 peer (tlslite-ng, a temporary CA trusted via `NODE_EXTRA_CA_CERTS`, verification enabled) and tested Bun 1.4.4's global `fetch` and `WebSocket` against two paired handshakes differing only in whether the server acknowledges the `renegotiation_info` extension. When the acknowledgement is present, everything works. When it is absent - the peer strips extension 65281 before serialization so the handshake is otherwise coherent and authenticated - **Bun completes the TLS 1.2 handshake and serves the HTTPS request (200) and the WebSocket upgrade anyway**, while native Node (v24.18.0, tag verified) rejects the same peer with `ERR_SSL_UNSAFE_LEGACY_RENEGOTIATION_DISABLED` before any application traffic. The RFC text backs the reporter's expectation verbatim: RFC 9325 §3.5 (verified against rfc-editor.org) says TLS 1.2 clients MUST send `renegotiation_info`, and "if the server does not acknowledge the extension, the client MUST generate a fatal handshake_failure alert" - explicitly because connecting to a server that doesn't support it "is not safe ... regardless of whether either endpoint actually implements renegotiation." Controls in the repro confirm Bun still rejects untrusted certificates, so this is a specific gap in extension validation, not broken verification generally. The repro is a runnable zip with hash-pinned dependencies and a `--node` comparison mode.

## Who this bites

- Anything using Bun's `fetch`/`WebSocket` against TLS 1.2 servers (legacy enterprise, embedded, IoT endpoints are where TLS 1.2 lives): a class of peer that every other major TLS stack refuses - because its presence signals a TLS implementation missing a security-critical extension - is silently accepted.
- This is a client-side weakening, so the practical risk is Bun applications talking to misconfigured or hostile TLS 1.2 servers; it is not a server vulnerability and does not affect TLS 1.3. The finding reports the RFC violation; it does not assess exploitability beyond the reporter's handshake-level evidence.

## Limits

- Single-source report (repo ~85k stars, reporter association NONE) on Linux with Bun 1.4.4 (release verified); I did not run the attached reproduction, so the behavior table is as-reported.
- No maintainer triage yet; whether the gap sits in Bun's TLS glue or an inherited library default is not established.
- The Node comparison version (24.18.0) is verified to exist but is not the newest 24.x; no cross-version bisect on the Bun side either.
