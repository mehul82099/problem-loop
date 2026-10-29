# One slash too many: a dependency's `'.//index.js'` import breaks only under Vitest's `vmThreads` pool, and the culprit is a fast-path regex that never said no

**Source:** [vitest-dev/vitest#11783](https://github.com/vitest-dev/vitest/issues/11783) (open, ~17.3k stars; reporter's repro confirmed and root-caused line-by-line by a community member, who also validated a one-line fix against the built package)

## The problem

A project imports Mermaid, tests pass with `pool: 'forks'` - and break the moment the pool is switched to `vmThreads`:

```
Error: Cannot find module '.../node_modules/khroma/dist/channels/utils/index.js'
```

khroma is a transitive dependency (it comes in through Mermaid), and the missing file is not missing: Node itself resolves it fine, which is why the `forks` pool, the `threads` pool, and plain `node` all work. Only the VM pools fail.

A community member reproduced the reporter's repo on Vitest 5.0.5 (Node 20 and 22) and traced it to the relative-specifier fast path in `ExternalModulesExecutor.resolve()` (`packages/vitest/src/runtime/external-executor.ts`, line 32 - the regex verified live on `main`):

```js
const SIMPLE_RELATIVE_SPECIFIER_RE = /^\.{1,2}\/[\w\-./]+$/
```

khroma's published code contains `import Channels from './/index.js'` - note the double slash. That odd but legal specifier matches the regex, so the VM pool takes the fast path: a plain `new URL(specifier, parent)` that preserves the empty path segment in the module identifier. When that module then imports `'../utils/index.js'`, URL resolution treats `channels/` (not `channels//`) as the parent, and the result points one directory off - at a file that does not exist. Node's own resolver canonicalizes the path, erasing the double slash before anyone can trip on it, which is exactly why every non-VM pool is immune.

The commenter proposed narrowing the fast path to specifiers without empty segments (`/^\.{1,2}\/(?:[\w\-.]+\/)*[\w\-.]+$/`), keeping normal specifiers fast and deferring the weird ones to Node's resolver - and reports patching the regex into the built `dist` output makes the failing suite pass on both Node 20 and 22, on both `vmThreads` and `vmForks`. They also verified a config workaround (`server.deps.inline: ['khroma']`) that we relay as their tested claim, not vetted advice.

## Why this matters

**A fast path is a promise that the slow path was redundant.** The regex was meant to recognize "simple" relative imports and skip Node's resolver. But its alphabet - `[\w\-./]+` - happily accepts `//`, so it recognized a specifier whose resolution semantics it did not reproduce. The slow path was not redundant; it was load-bearing, precisely for the inputs that look almost simple.

**Pool parity is a test runner's core contract.** "Same tests, any pool" is the entire pitch of swappable pools. A resolution divergence that only fires in the VM pools means a CI speedup knob doubles as a correctness knob, and the failure message ("Cannot find module") accuses the dependency, not the runner - sending users to debug node_modules instead of their pool config.

**The ecosystem produces weirder input than any regex author imagines.** `.//index.js` is not hostile input; it is just sloppy generated code that Node forgives. A runner that re-implements resolution has to be exactly as forgiving as Node, byte for byte, or it inherits bug reports for every oddity npm has ever published.

## Caveats and limits

- Both the reporter and the analyzing commenter are unaffiliated users (author association: none). The reproduction, the URL-resolution mechanics, the patched-dist test results, and the workaround are the commenter's account; we verified the regex and its use site in the live source, and that the issue has no maintainer response as of publication.
- khroma is the observed trigger; how many published packages contain double-slash (or trailing-slash) relative specifiers is unmeasured.
- The proposed fix is a community patch, not a maintainer-endorsed direction; no PR is referenced in the thread.
- This finding reports the issue and the analysis. It does not advise pool changes or config edits; follow the issue for the sanctioned resolution.

## Hour's takeaway

"Almost the same resolver" is the same bug as "not the same resolver," deferred until someone imports the wrong byte. When you fast-path around a canonical implementation, your regex is no longer a filter - it is a claim of behavioral equivalence, and it had better be provable.
