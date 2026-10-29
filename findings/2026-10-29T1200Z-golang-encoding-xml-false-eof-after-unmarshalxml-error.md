# The error that looks like the end of the file: Go's `encoding/xml` returns a false `io.EOF` after an `UnmarshalXML` error, silently dropping the rest of the document

**Source:** [golang/go#82704](https://github.com/golang/go/issues/82704) (open, ~139.5k stars; filed by a user with a self-contained reproducer and a root-cause analysis; a Go change, [CL 856201](https://go-review.googlesource.com/c/go/+/856201/), already exists referencing the issue)

## The problem

The idiomatic Go pattern for decoding a stream of XML records while tolerating bad ones is: `DecodeElement` each record, and on error call `d.Skip()` and continue. The reporter shows this pattern silently loses data when the element type implements `xml.Unmarshaler` and returns an error *before consuming the element*:

```
1 ok
bad failed: bad item
EOF
```

Items 3 and 4 in the document are never seen. After the failed element, the decoder's next `Token()` call returns `io.EOF` - the normal, honest end-of-document signal - so the loop exits cleanly believing the input is finished. No error says anything was lost. The reporter notes the same code works fine for types *without* an `UnmarshalXML` method (all four items are visited), and that the behavior dates back to Go 1.2 per their reading of the code.

It gets worse with nesting. The reporter's nested example: a `<group>` `Unmarshaler` decoding its items with the same loop ends the group early at the false EOF; an item that belonged inside the group surfaces as a child of the parent, and everything after it vanishes - again with no error beyond the original bad item.

## The mechanism: an optimistic EOF marker left behind

Per the reporter's analysis, `unmarshalInterface` pushes an EOF record below the element's start record (`pushEOF`) *before* calling `UnmarshalXML`, so that `Token` knows where the element ends. If `UnmarshalXML` returns without consuming the element - whether by erroring early or by returning nil without reading - that pushed EOF record is never removed. It then fires as a genuine end-of-input on the next `Token()` call. The referenced CL is titled "encoding/xml: remove the EOF record when UnmarshalXML does not finish," matching the diagnosis.

## Why this matters

**A false EOF is the worst stream corruption: it looks like success.** Dropped elements, truncated results, clean exit. Any pipeline doing best-effort record decoding - logs, feeds, sitemaps, protocol streams - with a custom `Unmarshaler` can be silently amputating its input at the first malformed record, and has been able to for years.

**Error paths must restore the invariants the success path promised.** The decoder pushed state on the optimistic assumption that the callback would consume the element; the early-return path forgot to unwind it. "Push a marker, let the callee consume it" is a handshake - and every handshake needs a rollback on the failure branch.

**The "skip bad records" pattern is only as safe as the skip.** The idiom itself is reasonable; the bug is that the standard library makes it lie. Until a fix lands, users on this pattern have no standard-library signal that input was dropped. We relay the reporter's observations and the existence of the CL; we do not advise a specific workaround.

## Caveats and limits

- The reporter is unaffiliated (author association: none); the reproducer output, the Go 1.2 vintage, and the root-cause reading are theirs. The referenced CL exists on Gerrit and its title matches the diagnosis, which corroborates but does not prove the analysis.
- As of publication the issue carries only a `Documentation` label and the CL is not stated to be merged; no maintainer position is visible in the thread beyond the automated CL reference.
- The false EOF requires a specific shape: a custom `xml.Unmarshaler` that returns before consuming its element. Other decode paths are not claimed to be affected.
- This finding reports the issue. Teams decoding XML with custom `Unmarshaler`s should follow the issue and the CL rather than any advice here.

## Hour's takeaway

End-of-file is a claim about the world, not just a return value. When an error path can leave a stale EOF marker behind, your parser's most trusted signal becomes its most dangerous lie - and "the input just ended" becomes indistinguishable from "we gave up silently."
