# "search ." says "no search list"; Go's resolver hears "use the default one" - and nonexistent domains start resolving

**Source:** [golang/go#82728](https://github.com/golang/go/issues/82728) (open, labeled `NeedsInvestigation`, ~139k stars; root cause verified against `master`; no maintainer confirmation yet)

## The problem

Put `search .` in `/etc/resolv.conf` - the documented way to say "no search domains, query every name as-is". Go's pure resolver (the `netgo` build tag) parses that line, throws the dot away, and then - because the search list is now empty - quietly reinstalls the default search list derived from the machine's hostname. The reporter's setup: hostname `server.example.com`, a wildcard record `*.example.com -> 127.0.0.1`, and a lookup for `domain.does.not.exist`. libc's resolver returns NXDOMAIN. Go's returns 127.0.0.1, because behind the scenes it issued a second query for `domain.does.not.exist.example.com` - which the wildcard happily matched. Every nonexistent name on that box now "resolves."

The mechanism is three lines apart in `src/net/dnsconfig_unix.go` (verified on `master`). The `search` case explicitly skips the root entry (lines 66-74):

```go
case "search": // set search path to given servers
    conf.search = make([]string, 0, len(f)-1)
    for i := 1; i < len(f); i++ {
        name := ensureRooted(f[i])
        if name == "." {
            continue          // the dot is silently dropped
        }
        conf.search = append(conf.search, name)
    }
```

and a little later, the emptiness the skip just created is reinterpreted as "no search line at all" (lines 141-142):

```go
if len(conf.search) == 0 {
    conf.search = dnsDefaultSearch()
}
```

The skip was itself a deliberate fix - commit `55ecc3a` ("net: allow single dot in resolv.conf search statement", fixing #54124) - made so that `search .` would stop being a syntax error. It solved the parse failure and created a semantic one: "explicitly empty" and "absent" now collide in the same representation, and absent wins. The issue is labeled `NeedsInvestigation` at publication, so maintainers have not yet confirmed the diagnosis.

## Why this matters

**"Empty" and "missing" are different facts.** The bug lives in a one-element type confusion: `[]` doing double duty for "the admin configured nothing" and "the admin configured nothing *on purpose*." Any config system that collapses those two will eventually override an explicit choice with a default - and defaults are precisely what the explicit choice was trying to escape.

**A fix can be a behavior change in disguise.** Commit `55ecc3a` is a good patch by its own lights: stop erroring on a harmless dot. But parsing is policy, and "ignore this directive" turned out to mean "invert this directive's intent." The regression test that guarded the syntax fix couldn't see the semantic side effect, because nobody had a test named "`search .` must disable the search list."

**Wildcard DNS turns correctness bugs into security-shaped ones.** A resolver that invents successful answers for nonexistent names is not just wrong; it reroutes failure handling. Retry logic, blocklists, certificate validation for internal hosts, "does this tenant exist" checks - all of them assume NXDOMAIN means no. Under a wildcard, Go's answer was 127.0.0.1: the wrong destination, delivered with confidence.

## Caveats and limits

- The code path (dot skipped; empty search list replaced by `dnsDefaultSearch()`) is verified on `master`; the observed 127.0.0.1 resolution, the go1.27.3 environment, and the libc comparison are the reporter's measurements. The issue is `NeedsInvestigation`; no maintainer confirmation or fix at publication.
- Affects Go programs using the pure Go resolver (`netgo` tag, or configurations that select it); cgo/libc resolution is unaffected per the report.
- Scope: resolv.conf semantics on Unix; we do not advise resolver or DNS configuration changes - follow the issue.

## Hour's takeaway

When your parser drops a token, ask what the emptiness it leaves behind will be mistaken for. Deleted meaning doesn't disappear - it gets re-filled by defaults.
