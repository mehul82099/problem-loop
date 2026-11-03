# Node.js: an HTTP/2 client session leaks forever when the server rejects the TLS handshake after the client's side completed

**Source:** https://github.com/nodejs/node/issues/67213 (opened 2026-11-03 UTC, open, no maintainer reply yet)

## The problem

When an `http2.connect()` client finishes its TLS 1.3 handshake and the server then sends a fatal alert - the common case being a rejected client certificate (expired, missing, unknown CA, revoked) - the session is marked `destroyed` but never emits `'error'` or `'close'`, and the underlying TLSSocket is never destroyed. The handle, the file descriptor, the native nghttp2 state, a pending WriteWrap, and everything captured by listeners stay alive permanently. The reporter's dependency-free repro shows 20/20 sessions leaking on every version tried: v18.20.4, v20.18.3, v22.14.0, v22.22.2, v24.16.0, v26.3.0 (all verified as real release tags), with the relevant code paths unchanged on main. Over 1000 failed connections: open FDs go 23 to 1026 and 1000 socket handles stay active. The production sighting is grimly familiar: a gRPC client reconnecting to a server that kept rejecting its expired client certificate accumulated about 6,900 leaked ClientHttp2Session objects until the process had to be restarted.

The trigger conditions are precise, which is why this survives in the wild: the alert must arrive after the client considers the handshake complete (TLS 1.3 makes this the norm for client-cert rejection), and the server must keep the TCP connection open after the alert, which OpenSSL-based servers do. A fast RST closes everything normally, so the leak hides behind network timing.

## The mechanism (reporter's analysis, spot-verified)

The native trace shows the failure in one line: the session tries to send a GOAWAY on the way down, the write can't complete on the broken TLS stream, and it "stays pending forever" - the session-close callback never runs. In the JS layer, the TLS error path for an established connection emits `'error'` without destroying the socket (`lib/internal/tls/wrap.js` L480-496, verified verbatim at v22.22.2), and http2's `socketOnError` calls `session.destroy(error)` (core.js L3229-3239, also verified), which starts a close sequence whose completion depends on that doomed write finishing. Nothing does, so nothing is released.

## Why it matters

mTLS with short-lived client certificates is standard in service meshes, and gRPC's default reconnect behavior turns one expired cert into an unbounded leak of memory and file descriptors with zero log lines - `destroyed` reads true, so casual inspection looks fine.

## Caveats

- Open with no maintainer response; reporter association NONE, but the report ships a self-contained repro, version matrix, native debug trace, heap numbers, and code citations - the two load-bearing code anchors were verified directly at the cited tag.
- The leak numbers are the reporter's measurements; this finding did not re-run the repro and does not propose a fix.
