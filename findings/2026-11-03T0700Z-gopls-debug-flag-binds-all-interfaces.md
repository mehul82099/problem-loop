# gopls: the `-debug` flag still binds 0.0.0.0 and serves open source files, after the CVE fix covered only `-listen`

**Source:** https://github.com/golang/go/issues/82821 (opened 2026-11-03 UTC, open, no maintainer reply yet)

## The problem

CVE-2026-42503 (tracked in golang/go#79211, verified closed) made gopls reject a `-listen` address with an implicit host, because `-listen=:PORT` silently binds every network interface. The fix is present in the pinned release: at tag `gopls/v0.24.0`, `gopls/internal/cmd/serve.go` rejects an addr starting with `:` with "implicitly binds all network interfaces". The same release's debug server was not covered: `gopls/internal/debug/serve.go` line 523 calls `net.Listen("tcp", i.debugAddress)` directly (both verified verbatim), so `-debug=:PORT` still binds 0.0.0.0. That debug server is unauthenticated and, per the report, serves open buffer contents, cache and analysis state, RPC traces, metrics, and `/debug/pprof/*` - including remote CPU-profile triggers.

The reporter demonstrates the exposure from a second host on the LAN: start gopls with only `-debug=:47781`, open a file through an ordinary LSP session, and the file's full contents come back over HTTP. They also describe a workspace-trust vector: vscode-go passes `go.languageServerFlags` from workspace settings to gopls's argv, so a trusted repository's `.vscode/settings.json` can start the editor's language server with the debug port bound to all interfaces while everything looks normal. The reporter notes they tried to report through security@golang.org, the mail failed from their environment, and they filed publicly while offering to move to a private channel - so this is a disclosed-attempt public report, not a drive-by drop.

## Why it matters

Incomplete security fixes are a recurring pattern: the dangerous flag gets guarded, the adjacent flag with the same semantics is missed, and the advisory's reassurance outlives the actual exposure. gopls runs on developer machines inside corporate networks, where an unauthenticated 0.0.0.0 service serving live source buffers and pprof is exactly what endpoint security is supposed to prevent.

## Cautions and caveats

- This is an unpatched exposure with a public repro; this finding describes it at the level the public issue already does and adds nothing beyond it. It does not advise any workaround; the only reliable statement available today is the report's own: the `-debug` flag path is unauthenticated and network-visible when given an interface-less address. Fix direction (apply the same host validation to `-debug`, review `-mcp.listen`, filter network-binding flags in vscode-go workspace settings) is the reporter's proposal, not maintainer guidance.
- Open with no maintainer response; reporter association NONE. The code anchors and the prior-CVE fix were verified directly at the pinned tag; the remote-fetch demonstration and the vscode-go settings claim are the reporter's.
