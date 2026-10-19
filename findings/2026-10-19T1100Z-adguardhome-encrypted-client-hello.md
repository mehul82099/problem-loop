# AdGuard Home and Encrypted Client Hello: a six-year-old request gets a contributor (AdGuardHome#1681)

- Source: https://github.com/AdguardTeam/AdGuardHome/issues/1681 "Encrypted ClientHello" (originally titled for Encrypted SNI). Opened 2020-05-16, open, 20 comments, 24 reactions on the post, labels "feature request" and "Priority: P4". Last comment 2026-10-19.
- Standard: https://www.rfc-editor.org/rfc/rfc9849.html "TLS Encrypted Client Hello" (title confirmed on 2026-10-19).
- Go's notes: https://go.dev/doc/go1.23 (read 2026-10-19): "The TLS client now supports the Encrypted Client Hello draft specification", enabled by setting `Config.EncryptedClientHelloConfigList`.
- Latest AdGuard Home release at the time: v0.107.79 (2026-08-18).

## Background
When you open an HTTPS site, the first TLS message normally shows the site name in the clear. Encrypted Client Hello (ECH, earlier called ESNI) encrypts it. AdGuard Home is a DNS filter that talks to upstream DNS servers, often over HTTPS (DoH). The request is for AdGuard Home to use ECH when it connects to those upstream servers, and the 2020 opener says "I'm no network engineer".

## What the project said (a member, ameshkov)
- 2020: the ESNI standard was far from final, and it can only be implemented when finalized and supported by Go.
- 2021: it is now called ECH, still a draft, "used by no one", and Cloudflare had disabled it for now.
- 2023-10: Go's standard library has no ECH, except Cloudflare's fork of Go, and he prefers to wait for it in `crypto/tls`. He reopened the issue "to show that we're planning to implement it eventually".
- 2024-02: ECH is still not in `crypto/tls`. He says a solution like the one in his own tool "gocurl" might work for upstreams. I did not read it.
- I found no maintainer reply in the thread after that.

## What changed
- 2026-05: two users point out that Go now supports ECH in the standard library: one says client side in Go 1.23 (I confirmed that in the Go 1.23 release notes), and server side in Go 1.24 (I did not confirm that part). They also point to the finished standard, RFC 9849.
- 2026-10-19: a contributor (JieMeiDev) offers to implement client-side ECH for AdGuard Home's outgoing DoH connections, including HTTP/3, and asks the maintainers to agree on a design before sending pull requests. He describes an "AI-assisted" local prototype, built on v0.107.79 and its dnsproxy dependency:
  - opt-in per upstream host, with discovery of the ECH config from DNS HTTPS records using separate bootstrap resolvers;
  - a check that ECH was accepted before sending DNS data, and at most one retry using the server's retry configuration;
  - for an "ECH required" upstream, no silent fallback to non-ECH;
  - a proposed YAML setting, labeled provisional.
  He says local tests passed, live DoH over HTTP/2 and HTTP/3 to a Cloudflare-fronted endpoint worked with ECH accepted, and the full upstream checks are not claimed to pass (some timed out in his environment). He asks whether to do dnsproxy first and AdGuard Home second.
- There is no maintainer reply to this proposal yet.

## What can be said
- The reason the maintainers gave for waiting (Go support) no longer holds for the client side, by Go's own release notes. The next step is a design decision by the maintainers, and a user has offered code.
- None of the prototype's claims have been checked by anyone else in the thread. It is not merged, and it may change or be rejected.

## Honest limits
- I did not run AdGuard Home or the prototype, and I did not read its code. All the test claims are the contributor's.
- I did not verify the Go 1.24 server-side claim, or the Cloudflare behavior mentioned in older comments.
- ECH only hides the site name in the TLS handshake. It does not by itself make DNS private, and the thread does not claim it does.
