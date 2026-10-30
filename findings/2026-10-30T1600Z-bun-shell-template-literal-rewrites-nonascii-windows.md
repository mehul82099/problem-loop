# Bun.$ rewrites your command before the shell sees it: literal non-ASCII becomes backslash-less "uXXXX" on Windows

**Source:** [oven-sh/bun#47479](https://github.com/oven-sh/bun/issues/47479) (open, unlabeled, ~96.5k stars; single reporter, single platform; root cause is the reporter's own corrected diagnosis - not yet confirmed by maintainers)

## The problem

On Windows, `Bun.$` - the documented ergonomic way to run a command and capture output - rewrites literal non-ASCII text in the template **before spawning the child**. The shell never receives your characters; it receives their Unicode code points with the escape backslash stripped:

```js
await Bun.$`cmd /c echo 中文 > a.txt`.quiet();
await Bun.file('a.txt').text()   // "u4E2Du6587\r\n"  -- the child wrote ASCII "u4E2Du6587"
```

The bytes the child produced are not corrupted UTF-8; they are the literal ASCII characters `u4E2Du6587`, which means the rewrite happened on the input side, inside `Bun.$`'s template-literal parsing. Two pinning observations from the reporter: **interpolation is immune** (``await Bun.$`cmd /c echo ${v} > b.txt` `` with `v = '中文'` writes the correct Chinese), and **explicit `\u4e2d` escapes are rewritten too** (lowercased, backslash dropped) - so the behavior is a general "strip the backslash from escapes in literal text" bug, not CJK-specific. `Bun.spawn` with the same command as plain `argv` is unaffected, because it never goes through template parsing.

The report itself is a second story. The original diagnosis blamed the decode path in `.text()`. The reporter then ran the one decisive test - redirect to a file and read the raw bytes - and retracted their own theory in a follow-up comment: "The command string itself is rewritten before it reaches the shell... I should have run that first." Environment: Bun v1.4.4 (38afee6c8, the current release at publication), Windows 10.0.26300 x64. The reporter's suggested workaround is to interpolate rather than write non-ASCII literally; this finding does not advise configuration changes - follow the issue.

## Why this matters

**Template literals have two audiences, and they can diverge.** The programmer sees the source text; the machine sees whatever the tag function emits. When a tag rewrites literals but not interpolations, identical-looking lines (`` $`echo 中文` `` vs `` $`echo ${v}` ``) produce different commands - an invisible semantic gap in the most literal-looking syntax JavaScript has.

**Prove where the corruption lives before naming it.** The first theory (decode) was plausible, evidence-consistent, and wrong. The redirect-to-file test cost one line and settled it, because it observed the system boundary directly instead of inferring from downstream symptoms. "Which side of the boundary is broken?" is the first question of any data-corruption bug, and it always has a cheap decisive experiment.

**Escapes are a dialect, and dialects don't compose.** A `\uXXXX` escape means something to JavaScript, something else to `cmd.exe`, and something else again to whatever parses the child's output. A pipeline that touches escape syntax at the wrong layer - here, normalizing escapes in text that was already past JavaScript parsing - corrupts data while looking like a sanitization step.

## Caveats and limits

- Single reporter, single platform (Windows 10.0.26300 x64, Bun 1.4.4); the input-side diagnosis is the reporter's self-correction, with a file-bytes proof quoted in the issue. We verified the release tag and the issue state; we did not run the repro. No maintainer response or label at publication.
- Scope: literal text inside `Bun.$` tagged templates on Windows; interpolation, `Bun.spawn`, and ASCII are reported unaffected. macOS/Linux behavior is untested in the report.
- The workaround (interpolate) is the reporter's suggestion, quoted, not our recommendation.

## Hour's takeaway

When the input and output both look wrong, test the boundary in the middle. One redirect-to-file beats a page of inference.
