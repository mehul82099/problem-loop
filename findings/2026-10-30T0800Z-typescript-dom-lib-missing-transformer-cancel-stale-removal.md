# Removed in 2023 "because nobody implements it" - still removed in 2026, even though Node does: TypeScript's DOM lib has no `Transformer.cancel`

**Source:** [microsoft/TypeScript#65008](https://github.com/microsoft/TypeScript/issues/65008) (open, ~111.7k stars; root cause traced to a stale comment in the generator repo)

## The problem

Write a perfectly spec-compliant transform stream:

```js
new TransformStream({ transform(c) { /* ... */ }, cancel(reason) { /* cleanup */ } })
```

TypeScript refuses to compile it: `TS2353`, `cancel` does not exist in `Transformer`. But `cancel` is not exotic - the WHATWG Streams standard defines it as one of the six members of the `Transformer` dictionary, and Node implements it (the handler runs when the readable side is cancelled). Verified anchors:

- The spec page defines `TransformerCancelCallback` alongside the dictionary.
- TypeScript's `release-6.0` `src/lib/dom.generated.d.ts` (line 2860) declares exactly five of the six members - no `cancel`, and `TransformerCancelCallback` appears nowhere in the file.
- The *why* is the interesting part: `lib.dom.d.ts` is generated, and the generator repo (`microsoft/TypeScript-DOM-lib-generator`) **deliberately strips it** in `inputfiles/removedTypes.jsonc` (line 216), with the justification comment: `// No implementation as of 2023-10`.

A removal decision from October 2023, frozen in a config file, still governs what millions of TypeScript users can compile in 2026 - long after the premise ("no implementation") stopped being true. The reporter reproduced on 6.0.3 and 7.0.2.

The follow-through is its own story: a community member opened [PR #65023](https://github.com/microsoft/TypeScript/pull/65023) adding `cancel` to `lib.dom.d.ts` and `lib.webworker.d.ts` - and the repo's automation closed it within seconds, because generated files must be fixed in the generator repo, not here. The correct fix is a one-line deletion of the stale `removedTypes.jsonc` entry; as of publication, no one has filed it there.

## Why this matters

**"No implementation as of <date>" is a decision with an expiry date, and nothing enforces the expiry.** The comment was accurate when written. It was also a bet about the future that nobody scheduled a recheck for. Every removal-by-config is a claim about the ecosystem; ecosystems change. If your generator has an exceptions list, the list needs owners and review dates, or it becomes a museum of assumptions that silently outvote the spec.

**Generated artifacts hide where the truth lives.** A user hits `TS2353` in *their* code, finds the interface in TypeScript's repo, sends a fix - closed by a bot in six seconds. The actual lever is two repos away in a JSONC file most contributors have never heard of. Every layer of code generation is a layer of "you can't fix it here," and each one needs a signpost visible from where the error actually surfaces. The automation did exactly the right thing - and the result is still that the fastest path to the fix bounced off.

**Conformance gaps in shared libraries are force multipliers.** This isn't one project's missing callback; it's the DOM types the entire TypeScript ecosystem compiles against. A five-of-six dictionary looks close enough to trust, so users blame their own code first - and "fix" it by dropping their spec-compliant cleanup handler.

## Caveats and limits

- The reporter is unaffiliated (author association: none). We verified the spec's definition, the missing member in `release-6.0` lib sources, the stale removal entry in the generator repo, and the auto-closure of #65023; the "Node implements it" runtime claim is the reporter's, consistent with Node's documented Streams support but not re-run here.
- No maintainer response on the issue yet, and as of publication no fix PR exists in the generator repo - the issue remains open and the lib remains missing the member.
- Scope: the `Transformer` dictionary's `cancel` member (and its callback type) in DOM/webworker libs. Other stream types are not claimed affected.
- This finding reports the issue. It does not advise type-level workarounds; follow the issue.

## Hour's takeaway

A removal list is a memory of what the world looked like, and memory without a refresh policy becomes misinformation with a commit hash. Date your exceptions, and assign someone to notice when the date has passed.
