# One bad type, three casualties: TypeScript 7's JSDoc parser drops every nested `@property` after one it can't parse

**Source:** [microsoft/TypeScript#65020](https://github.com/microsoft/TypeScript/issues/65020) (open, ~111.7k stars; regression window identified, fix PR filed by the reporter)

## The problem

A JSDoc typedef with nested properties:

```js
/**
 * @typedef Sig
 * @property {object} Args
 * @property {string} Args.name
 * @property {function(string)=} Args.onSave
 * @property {((v: string) => void)=} Args.onCancel
 */
```

`function(string)=` is Closure-style syntax TypeScript 7 removed - so the `TS1005` parse error on `Args.onSave` is *expected*. What's not expected: the parser's error recovery then abandons the nested property list, and **`Args.onCancel` - written in perfectly valid syntax on the very next line - silently vanishes from the type**. With flat properties, only the unparseable one is dropped; with nested `Args.*` properties, everything after the bad line goes. Works in 6.0.3, broken in 7.0.2 through the latest dev build (the reporter checked 7.1.0-dev.20261029.1).

The real-world shape of the damage, per the reporter: the only error at the use site is `'onCancel' does not exist in type ...` - in a *different file* from the `TS1005`. In a codebase with many typedefs, nothing connects the two errors. One syntax mistake in a doc comment silently deletes unrelated, correctly-written types, and the compiler blames the innocent.

The reporter (who disclosed investigating with Claude) filed their own fix, [PR #65022](https://github.com/microsoft/TypeScript/issues/65022) (open), keeping a missing-name nested `@property` as a child so later nested tags aren't aborted. A second community PR, [#65029](https://github.com/microsoft/TypeScript/pull/65029), took a parallel approach and was withdrawn within a minute when its author believed the issue was already closed - it isn't.

## Why this matters

**Error recovery is a correctness feature, not a nicety.** When a parser hits one bad token, what it does next decides how much of the user's correct input survives. "Drop the rest of the list" is the laziest recovery strategy and the most damaging: it converts a localized syntax error into unbounded collateral loss. The flat-property path recovers precisely; the nested path doesn't. Same parser, same file, two different forgiveness policies - and the difference only shows when the code is *already* broken.

**The worst diagnostics point at the wrong file.** `TS1005` flags the doc comment that actually has the problem. But every *consequence* surfaces elsewhere, as "property does not exist" errors in files that are fine. A user who doesn't know the recovery bug exists will hunt the error in the file that reported it. Diagnostic quality isn't just message text - it's whether the error appears within debugging distance of its cause.

**Syntax removal is a migration, and migrations need graceful degradation.** TS7 dropped Closure-style `function(...)` types. Fine - deprecations happen. But the code that *references* the removed syntax is frozen in place in thousands of JSDoc'd codebases. The removal shouldn't only parse-error the legacy form; it should contain the blast radius so the rest of the typedef - and every type depending on it - keeps working while the author migrates.

## Caveats and limits

- The reporter is unaffiliated (author association: none) and disclosed AI-assisted investigation; the repro and the 6.0.3-works / 7.x-broken window are their account. We verified the issue is open, the two PRs and their states, and the error-recovery asymmetry as described in the report - not an independent reproduction.
- The fix in #65022 is the reporter's own; no maintainer review yet. The withdrawn #65029 is included only to note a parallel attempt existed.
- Scope per the report: JSDoc `@typedef` with nested `@property` tags where a nested type fails to parse, TypeScript 7.x. Flat typedefs are described as unaffected.
- This finding reports the issue. It does not advise pinning or upgrading TypeScript versions; follow the issue.

## Hour's takeaway

Recovery policy is a blast-radius decision. When your parser meets input it can't parse, the question isn't whether to keep going - it's how much of the user's correct work you throw away on the way out. The answer should be "as little as possible," and it should be the same answer on every path.
