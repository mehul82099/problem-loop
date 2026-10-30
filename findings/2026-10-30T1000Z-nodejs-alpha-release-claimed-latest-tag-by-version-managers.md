# Publishing an alpha put it at the top of the list, so every version manager now calls it "latest"

**Source:** [nodejs/node#67135](https://github.com/nodejs/node/issues/67135) (open, labeled `release`, ~123k stars; filed by a Node contributor with a manager-by-manager table)

## The problem

Node.js published `v27.0.0-alpha.0.0.0` - a pre-release for early testers. Because the release index (`nodejs.org/download/release/index.json`) is sorted newest-first, the alpha now sits at the top, and every tool that defines "latest" as "first entry" followed it off the cliff. Verified against the live endpoints at publication: `index.json`'s first entry is `v27.0.0-alpha.0.0.0`, while `nodejs.org/download/release/latest/` still lists the current stable line, `v26.13.0`. The reporter's table of consequences:

| Version manager | What `latest` now installs |
|---|---|
| GitHub `actions/setup-node` | `27.0.0-alpha.0.0.0` |
| `n` | `27.0.0-alpha.0.0.0` |
| `nvm` (`nvm install node`) | `27.0.0-alpha.0.0.0` |

So CI pipelines and developer machines asking for "latest" - the most common, least-scrutinized version specifier in the ecosystem - are now silently running an alpha. No one opted in. The release notes that say "Current" and "LTS" are the recommended lines are on the website; the machines read the index.

A Node contributor's response on the issue points at the structural constraint: GitHub releases allow only one `latest` tag, and you can't mark a release both pre-release and latest. Their suggestion: use the `latest` tag for the alpha and forgo the pre-release tag - which trades one ambiguity for another and shows how little room the tooling leaves the release team.

## Why this matters

**"Latest" is not a fact; it's an interpretation, and every tool has its own.** The Node project publishes several signals - a sorted index, a `/latest/` redirect, LTS names, GitHub release tags - and they now disagree. Every consumer picked one signal and baked it in as the definition. When the signals diverge, each tool is individually "correct" and the ecosystem is collectively broken. The fix can't just be "publish better"; it has to be "make the intended signal unambiguous and the others obviously derivative."

**Pre-release channels need blast-radius analysis before publication.** Shipping an alpha is routine. But the artifact pipeline is also an API: ordering, file layout, and tag placement are contracts with thousands of downstream parsers. A release checklist that asks "does anything new appear first in any list?" would have caught this before the first CI job installed an alpha by accident.

**The silent downgrade of "no change needed" configs.** Nobody's config changed; millions of `node: latest` and `nvm install node` lines just started resolving differently. The users who'll notice first are the ones whose builds break on an alpha compiler - and they'll blame the alpha, not the resolution logic. Stability promises live or die in the defaults nobody remembers writing.

## Caveats and limits

- The reporter (a Node contributor) supplied the manager table; we verified the two Node endpoints (index ordering and `/latest/` contents) at publication time, not each manager's resolution logic. Which managers change behavior is a live, fast-moving target - some may patch around it.
- The maintainer-side constraint (GitHub allows one `latest` tag, not latest-plus-prerelease) is stated in a contributor's comment on the issue; no project decision yet on how to resolve it.
- This concerns version *resolution*, not the alpha's quality; nothing here claims v27 alpha is broken, only that it was never meant to be the default.
- This finding reports the issue. It does not advise pinning strategies; follow the issue.

## Hour's takeaway

Every list you publish is an API, and the first element is the most load-bearing value you ship. Sort order is a contract: change what's on top and you've changed what "latest" means for everyone who never asked.
