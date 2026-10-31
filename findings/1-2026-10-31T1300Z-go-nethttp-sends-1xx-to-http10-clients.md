# Go's net/http sends 1xx responses to HTTP/1.0 clients - and every Go reverse proxy relays them

**Source:** [golang/go#82743](https://github.com/golang/go/issues/82743) (open, unlabeled; code anchors and the RFC text verified)

## What happened

[RFC 9110, section 15.2](https://www.rfc-editor.org/rfc/rfc9110#section-15.2) is unambiguous (verified verbatim): "Since HTTP/1.0 did not define any 1xx status codes, a server MUST NOT send a 1xx response to an HTTP/1.0 client." The reporter (ahzf, association NONE) shows Go's server ignores this for explicitly written 1xx codes: a handler calling `w.WriteHeader(http.StatusEarlyHints)` sends the `103` to an HTTP/1.0 client, on go1.27.3 and go1.24.4. An HTTP/1.0 client has no concept of interim responses, so it can take the `103` as the final response and the real `200` as body bytes.

Verified at the cited commit `67ced031`: the 1xx branch of `(*response).WriteHeader` in [server.go#L1313-L1324](https://github.com/golang/go/blob/67ced031087a7dfe99211535fc923fdc80e8bd9f/src/net/http/server.go#L1313-L1324) uses the request version only to pick the status-line protocol string - `writeStatusLine(w.conn.bufw, w.req.ProtoAtLeast(1, 1), code, ...)` - with no gate on the client's version. The automatic `100 Continue` does it right: the `expectContinueReader` is installed only `if req.ProtoAtLeast(1, 1) && req.ContentLength != 0` ([server.go#L2202-L2208](https://github.com/golang/go/blob/67ced031087a7dfe99211535fc923fdc80e8bd9f/src/net/http/server.go#L2202-L2208), verified). So the guard exists for the implicit 1xx and is missing for the explicit one.

The amplification: `httputil.ReverseProxy` relays backend 1xx responses through its `Got1xxResponse` hook via `rw.WriteHeader(code)`, and the proxy's outbound request is always HTTP/1.1, so the backend can't save you - every Go-based proxy forwards a backend's `103` to HTTP/1.0 clients. The reporter hit this through Caddy 2.11.4 passing a backend's Early Hints to `curl --http1.0`. The historical irony is verified: arbitrary 1xx writes and ReverseProxy 1xx forwarding were added on purpose ([#26089](https://github.com/golang/go/issues/26089), [#26088](https://github.com/golang/go/issues/26088), both closed) - the HTTP/1.0 edge just wasn't gated. The reporter's suggested fix is an early return in that branch when `!w.req.ProtoAtLeast(1, 1)`; HTTP/2 is unaffected.

## Who this bites

- Anything still speaking HTTP/1.0 (legacy clients, health checks, simple proxies) behind a Go server or Go-based proxy (Caddy, Traefik-style stacks) whose backends use `103 Early Hints`: the client misparses the response stream.
- The reporter found it with an HTTP/1.1 conformance suite that runs an origin behind several reverse proxies ([per-proxy results](https://github.com/Vanaheimr/HTTP1ConformanceTests/blob/6b0eb07dac4e12125809581fb83339f5521acd44/docs/TestingAgainst_Proxies.md) - link verified, the reporter's own project).

## Limits

- The wire captures are the reporter's (go1.27.3/go1.24.4 linux/amd64); I verified both server.go anchors at the cited commit, the RFC quote, the historical issues, and the doc link, but did not run the repro program. Repo ~139k stars.
- The issue is hours old, unlabeled, no maintainer response yet; the one-line fix shape is proposed, not endorsed.
- How a real HTTP/1.0 client behaves on receiving `103` varies (the reporter says "may" misparse); the RFC violation itself is not in doubt.
