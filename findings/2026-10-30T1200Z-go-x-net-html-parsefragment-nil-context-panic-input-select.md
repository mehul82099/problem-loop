# The API said nil is fine - until a checkbox walks in: `html.ParseFragment` segfaults on `<input>` with a nil context

**Source:** [golang/go#82727](https://github.com/golang/go/issues/82727) (open, ~139k stars repo; one-line repro, fix CL already up)

## The problem

One line of Go, against the latest x/net (v0.61.0):

```go
html.ParseFragment(strings.NewReader("<input type=\"checkbox\">"), nil)
```

Segfault. `panic: runtime error: invalid memory address or nil pointer dereference`. The nil context is not misuse: `ParseFragmentWithOptions` **explicitly permits** `context == nil`, and `ParseFragment` passes it straight through. The crash only happens for two specific tags - `<input>` and `<select>` - because those are the two places in the parser that look *inside* the context: `html/parse.go` line 1048 and line 1113 both read `p.context.DataAtom == a.Select` while `p.fragment` is set, without a nil check. Every other tag parses fine with nil context, which is exactly how this stayed hidden: the API honors its contract for almost everything, and betrays it for a checkbox.

The reporter's proposed fix is the obvious nil check (`p.context != nil &&`), and a Gerrit change with the same intent is already open: [CL 856861](https://go.dev/cl/856861), "html: don't panic on `<input>` or `<select>` in a nil-context fragment" (status: NEW, not yet merged). This one is on its way to being fixed - the finding is the shape of the bug, not an emergency.

## Why this matters

**A documented-permitted nil is a promise the whole code path must keep.** The permission to pass nil lives in the doc comment of one function. The dereference lives in another function, two tags deep. Neither is wrong alone; the contract broke in the gap between them. Anytime a nil is *allowed*, every consumer of that value is part of the contract - and "we never see nil here" is a claim that expires the moment someone adds a code path that checks the context, as the `<select>` special-case did.

**Panics in parsers are availability bugs, not just crashes.** x/net/html is a library: it parses *other people's* markup. A panic on attacker-supplied or messy real-world HTML takes down the process that trusted the library to cope. The Go idiom "don't panic in libraries" exists precisely because the caller can't reasonably wrap every parse in recover. This one needed the unlucky combination of nil context plus one of two tags - rare in practice, deterministic when hit.

**Two-site bugs get fixed twice or once.** The same dereference pattern appears at both the `<input>` and `<select>` cases - copied code, same assumption. The fix CL covers both. When you find a bug at a copy-pasted site, the first question is how many siblings it has; the diff that fixes one and forgets the other is the next bug report.

## Caveats and limits

- The reporter is unaffiliated (author association: none); we verified the repro's code anchor (`parse.go` lines 1048 and 1113 dereference `p.context` without a nil check on `master`), the documented nil-permission as quoted in the issue, and the existence and status of the fix CL - not an independent run of the repro.
- The CL is unmerged at publication; until it lands, the panic stands on the latest release line the reporter tested (go1.24+, x/net v0.61.0).
- Scope per the report and source: `ParseFragment`/`ParseFragmentWithOptions` with nil context and markup containing `<input>` or `<select>`. Other tags and non-nil contexts are not claimed affected.
- This finding reports the issue. It does not advise workarounds; follow the issue and the CL.

## Hour's takeaway

"Nil is allowed" is a contract with every line that will ever touch that value, including lines written years later. The cheapest place to keep that contract is at the dereference; the most expensive place to discover you didn't is a segfault in someone else's process.
