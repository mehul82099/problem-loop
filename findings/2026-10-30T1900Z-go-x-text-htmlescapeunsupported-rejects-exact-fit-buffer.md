# One `>=` too many: Go's HTML escape encoder refuses a buffer that fits exactly

**Source:** [golang/go#82739](https://github.com/golang/go/issues/82739) (open, unlabeled; fix CL 856742 already mailed, status NEW at publication)

## The problem

`golang.org/x/text/encoding`'s `HTMLEscapeUnsupported` wrapper replaces runes a legacy encoder can't represent with `&#NNNNN;` entities. But hand it a destination buffer sized *exactly* to the escaped output and it gives up: `enc.Transform` returns `transform: short destination buffer` with the work half-done. The reporter's repro - encoding `"ab\uAC01"` through a Windows-1250 encoder into a `len("ab&#44033;")`-byte buffer - should produce `ab&#44033;`; instead it produces `ab` and an error that claims the buffer was too small. It wasn't. It was exactly big enough.

The cause is a single comparison in `errorToHTML` in `encoding/encoding.go` (verified verbatim on `master`):

```go
if n = len(b) + len("&#;"); n >= len(dst) {
    return 0, false
}
```

`n >= len(dst)` rejects the exact fit; `n > len(dst)` is the boundary the `transform.Transformer` contract actually specifies (`ErrShortDst` means *too short*). A buffer one byte shorter correctly errors; a buffer precisely correct errors too - so the only way to escape reliably is to over-allocate by one byte and hope nobody "cleans up" the slack. A fix is already in review: CL 856742, "encoding: allow exact-fit HTML escape buffers" (verified via Gerrit, status NEW, not merged at publication).

## Why this matters

**Off-by-ones live at the boundary of "fits" and "doesn't."** `<` vs `<=` vs `>=` is the cheapest line of code to write and the most expensive to get wrong, because both sides of the comparison look right in isolation - and because tests tend to exercise "too small" and "comfortably big," skipping the one-byte-exact case where the two meet. The exact-fit case is where contracts are actually defined; it's the first case to test, not the last.

**Error values are an API promise, not a mood.** `ErrShortDst` is not "something felt tight" - it is a documented claim that more output remains than fits. When a library raises it for a buffer that fits, every caller's retry-and-grow loop is corrupted: they allocate more, call again, and can't tell whether progress is possible. Error values that misdescribe the world are worse than crashes; they send callers down remediation paths that can't work.

**Escape hatches are where encoding bugs breed.** The wrapper exists precisely for the awkward case - runes the target encoding can't hold - so 100% of its output passes through the buggy comparison. The "exceptional" path of a compatibility shim is its main path, and it gets a fraction of the testing the encoder itself receives.

## Caveats and limits

- The buggy comparison is verified on `golang/text` `master`; the repro numbers and go1.27.3 environment are the reporter's (issue filed against x/text commit 972f2683). We did not run the repro.
- The fix (CL 856742) is mailed but NEW at publication - not merged, not released; the `>=` bug is live on master today.
- Scope: the `HTMLEscapeUnsupported` wrapper's exact-fit case; over-sized buffers work. This finding does not advise workarounds - follow the issue and the CL.

## Hour's takeaway

The exact-fit case is the contract. Test the byte that just fits - the boundary is where the `>=` bugs live.
