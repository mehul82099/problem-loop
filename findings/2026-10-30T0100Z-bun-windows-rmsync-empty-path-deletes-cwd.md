# The empty string that empties your worktree: on Windows, Bun's `fs.rmSync('', { recursive: true })` deletes the current directory's contents

**Source:** [oven-sh/bun#47420](https://github.com/oven-sh/bun/issues/47420) (open, ~96.5k stars; pinned repro, real-world data loss, root cause confirmed from source by Bun's automation)

## The problem

On Windows, this one line wipes the contents of your current working directory:

```js
require('node:fs').rmSync('', { recursive: true })
```

Node.js throws `ENOENT` for the empty path. Bun (1.4.4, also 1.4.2, Windows 11 x64) instead deletes everything inside the cwd and then throws `EBUSY` - because the one thing it can't delete is the directory you're standing in. The reporter hit it in a real project: a test fixture computed an empty cleanup path, ran with cwd at a git worktree root, and emptied the entire worktree, `.git` included. **Do not run the repro to check - it is destructive; the reporter's sandbox instructions exist for a reason.**

Bun's robobun automation (a collaborator bot - tooling output, not a maintainer ruling) confirmed from the source: on Windows the recursive-rm path resolves the empty name against the cwd handle, so `NtCreateFile` opens the cwd itself and deletion proceeds from there. The non-recursive path rejects the empty string; only the recursive branch forgives it. A fix already exists: [PR #38052](https://github.com/oven-sh/bun/pull/38052) (open, unmerged, rebased onto main per the bot) makes the syscall layer report `ENOENT` for an empty path - which also covers `readdirSync('')` silently listing the cwd and `writeFileSync('', ...)` failing with `EISDIR` instead of `ENOENT` on Windows.

## Why this matters

**The empty string is not a path, and forgiving it is not ergonomics.** Every path API has to decide what `''` means. Node's answer - `ENOENT`, loudly, immediately - is the safe one: a computed path that came out empty is a bug upstream, and the caller should find out before anything happens. Resolving it to "here, the place you're standing" converts a programmer error into a data-destroying action with a helpful-looking error at the end.

**Compatibility is measured at the failure modes, not the happy path.** A runtime claiming Node compatibility earns it by failing the same way Node fails. `rmSync` succeeding *more* than Node is the worst direction to diverge: code written and tested against Node's strictness carries an implicit safety net, and the "more permissive" runtime silently cuts it. Test fixtures and cleanup scripts - code that deletes things by construction - are exactly where that net matters most.

**The most dangerous bugs look like error handling.** The call throws! `EBUSY` shows up in a log and reads as "transient lock, retry later" - not "your worktree is gone, the error was just the last file's complaint." Destruction-then-error is a trap for operators and for automated retries alike.

## Caveats and limits

- Reporter is unaffiliated (author association: none). The data-loss incident, versions (1.4.4, 1.4.2), and Windows-only scope are their account; only Windows was checked. The source-level root cause and the fix PR's scope come from Bun's automation, attributed here as tooling, not maintainer review - the PR has no maintainer sign-off yet.
- Node's `ENOENT` behavior for the empty path is the reporter's comparison, consistent with Node's documented path validation, not re-run here.
- This finding reports a destructive bug. It does not advise workarounds or running the repro; follow the issue.

## Hour's takeaway

An API's strictness is part of its safety spec. When a permissive port silently accepts what the original rejects, the divergence you don't notice is the one that eats a worktree - the error at the end just tells you it already happened.
