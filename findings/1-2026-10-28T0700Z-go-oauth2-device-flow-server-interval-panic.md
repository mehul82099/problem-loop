# The device-flow spec lets the server pick your polling interval - Go's oauth2 only guarded the zero case

- Source issue: https://github.com/golang/go/issues/82658 (open; opened 2026-10-28; fix CL 855381 already referenced by gopherbot)
- Project: golang/go x/oauth2 (the standard OAuth2 package; repo ~132k stars)
- Checked: 2026-10-28 07:12 UTC

## Problem
RFC 8628 device authorization lets the server tell the client how often to poll via an `interval` field. Go's x/oauth2 `DeviceAccessToken` only special-cases `interval == 0` (replacing it with the RFC default of 5 seconds) and feeds everything else straight into `time.NewTicker(time.Duration(interval) * time.Second)`. So a server that answers `"interval": -1` crashes the client outright: `panic: non-positive interval for NewTicker`. A very large interval also panics - the multiplication overflows int64 and wraps negative, hitting the same ticker guard. Any Go program doing device-flow auth against a misbehaving or hostile authorization server is one JSON field away from a crash; the reporter demonstrates it with a three-line httptest server.

## Why it is interesting
- The trust asymmetry is the story. Device flow is designed for input-constrained devices (TVs, CLIs) where the server is expected to pace the client - so the spec legitimately hands a timing value to the server. The library treated "came from the server" as "sane": zero was handled because the RFC says zero means "use the default," but negative and overflowing values were never contemplated. Validation covered the spec case and missed the adversarial case, which is exactly where panics live.
- Two bugs for the price of one field. The negative interval is an input-validation miss. The large interval is an arithmetic-overflow miss: `time.Duration(interval) * time.Second` silently wraps for values over ~292 years (int64 nanoseconds), turning a huge-but-positive number into a negative one. Either path, same panic line. A single missing bounds check hosts two distinct failure classes.
- A panic in a library is worse than an error in a library. Callers of DeviceAccessToken reasonably expect an error return for bad server behavior; instead the process dies. For a CLI doing device login this is a nuisance; for a long-running service handling many device flows it is a denial-of-service primitive handed to the authorization server - worth noting this finding describes the flaw only and does not advise any exploitation.
- The fix pipeline worked fast: filed at 05:50 UTC, and gopherbot linked a fix CL ("don't panic on an invalid device flow interval") within about an hour. The report is minimal, reproducible, and names the exact line - the kind of issue that gets fixed, not debated.

## Honest limits
- The fix CL exists but is unmerged at check time; the panic is live in x/oauth2 master.
- Real-world exploitability depends on whether a program's authorization server is attacker-influenceable; most deployments point at trusted providers. Severity is therefore context-dependent - described as a robustness flaw, not a scored vulnerability.
- The overflow path arithmetic is the reporter's reading of the duration multiplication; consistent with Go's int64 duration semantics, not independently re-derived.
- Issue state may have changed since 07:12 UTC.
