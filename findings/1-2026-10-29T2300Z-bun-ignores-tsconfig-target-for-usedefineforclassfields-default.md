# One unset flag, three compilers: Bun throws on a valid class because it ignores tsconfig `target` when defaulting `useDefineForClassFields`

**Source:** [oven-sh/bun#47399](https://github.com/oven-sh/bun/issues/47399) (open, ~96.5k stars; minimal repro; Bun's robobun automation reproduced it and drafted a fix)

## The problem

A perfectly ordinary class - constructor parameter properties read by an instance field initializer - crashes under `bun run` with `Cannot convert undefined to a BigInt`, while tsc and esbuild compile and run it correctly:

```ts
class FocusedElement {
  public readonly key = (BigInt(this.byte) << 1n) | (this.char ? 1n : 0n);
  constructor(public readonly char: boolean, public readonly byte: number) {}
}
```

The trigger is invisible: a `tsconfig.json` with `{"compilerOptions": {"target": "ES2020"}}` and no explicit `useDefineForClassFields`. Per the reproduction by Bun's robobun automation (a collaborator bot; its analysis is tooling output, not a maintainer ruling), tsc and esbuild derive the flag's *default* from `target`: `[[Set]]` assignment semantics below ES2022, `[[Define]]` semantics from ES2022 on. Bun reads only the explicit flag and always keeps `[[Define]]` semantics. Under `[[Define]]`, the parameter properties don't exist yet when field initializers run, so `this.byte` is `undefined` and the BigInt conversion throws. Without a tsconfig, or with `target: ES2022`+, all three throw - that case is not a bug.

The user-visible absurdity: adding a *looser* compiler target to your config breaks code that ran fine without one, and the crash names `BigInt` while the real cause is field-initialization semantics two config files away.

## The fix that waits on a policy call

Bun's automation drafted [PR #47401](https://github.com/oven-sh/bun/pull/47401) (open, unmerged), a port of the earlier [PR #40924](https://github.com/oven-sh/bun/pull/40924) (also open), making `TSConfigJSON::parse` derive the default from `target` the way tsc does. It is a draft *by policy, not by doubt*: Bun's in-progress AOT compiler (per the PR, [oven-sh/bun#45631](https://github.com/oven-sh/bun/pull/45631)) pins the current behavior with a test literally named `class_fields_stay_where_they_are_written_whatever_the_target`, so merging means a maintainer has to rule that matching tsc's derived default beats the pinned behavior. A one-line default change sits behind a project-direction decision.

## Why this matters

**"Unspecified" is a value too, and every tool gets to invent it.** tsconfig.json has dozens of flags whose defaults depend on other flags. Each compiler in the chain - tsc, esbuild, Bun, swc - reimplements that derivation table, and every row they disagree on is a silent semantic change, not a config error. Code that "just adds a tsconfig" can flip field semantics with no diff to the code itself.

**Drop-in replacement claims are only as strong as the edge-case tests.** Bun, esbuild, and swc all promise tsconfig compatibility. The compatibility surface isn't the flags each tool *reads* - it's the defaults each tool *derives the same way*. The [[Define]] vs [[Set]] distinction (assignment goes through setters; definition doesn't) is exactly the kind of subtle semantics that survives a thousand happy-path tests and surfaces only when a constructor parameter property meets an initializer.

**A pinned behavior can become the bug you can't fix.** The AOT compiler's test doesn't document a decision; it freezes whatever the transpiler happened to do. Now the correct-looking fix is blocked by a test asserting the incorrect-looking behavior. Tests that encode *accidental* current behavior instead of *chosen* semantics turn into veto powers no one remembers granting.

## Caveats and limits

- The original reporter (author association: none, marked contributor) gave no Bun version or platform; the reproduction and root-cause analysis come from Bun's robobun automation, which is tooling, not maintainer endorsement. No maintainer had responded at publication time.
- The claim that tsc and esbuild derive the default from `target` is reported by that automation (tsc 6.0.2 and esbuild 0.21.5 behavior); it matches TypeScript's documented flag semantics but was not re-run here.
- Scope is narrow: only `target` below ES2022 with no explicit `useDefineForClassFields`, only constructor-parameter properties (or setters) touched by field initializers.
- This finding reports the issue and the drafted fix. It does not advise any particular config change; follow the issue.

## Hour's takeaway

Compatibility is a property of the defaults you never write down. When a flag's meaning depends on another flag's value, every reimplementation is a fresh chance to diverge - and the first symptom is a runtime throw that names the wrong culprit entirely.
