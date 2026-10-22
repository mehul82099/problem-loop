# Node.js: building with --shared-brotli fails against Brotli 1.2.0, and the thread says to use Brotli 1.2.1 anyway

- Source issue: https://github.com/nodejs/node/issues/66894 (open at check time; no labels; opened 2026-10-21; 4 comments)
- Pull request that wraps the constant in an `#ifdef`: https://github.com/nodejs/node/pull/66895 (open, not merged, labeled commit-queue at check time)
- Node commit named in the title: https://github.com/nodejs/node/commit/03923858417d ("src: expose `BROTLI_DECODER_ERROR_FORMAT_BLOCK_SWITCH`", dated 2026-10-12, touches `src/node_zlib.cc` and one zlib test)
- Brotli release 1.2.1: https://github.com/google/brotli/releases/tag/v1.2.1 (published 2026-10-21 19:27 UTC, not a pre-release)
- Brotli commit a commenter suggested cherry-picking: https://github.com/google/brotli/commit/0ed4268a4401 ("Detect and report invalid stream earlier", dated 2026-02-27, touches `c/dec/decode.c` and `c/include/brotli/decode.h`)
- Project: https://github.com/nodejs/node (122,532 stars per the API)
- Checked: 2026-10-22 09:40 UTC

## Problem
The reporter says that configuring Node.js 26.12.1 with `--shared-brotli` (use the system Brotli library) and building fails with `use of undeclared identifier 'BROTLI_DECODER_ERROR_FORMAT_BLOCK_SWITCH'` in `src/node_zlib.cc`. They say that constant was added to Brotli after its latest release, 1.2.0, so Node should check that it exists before using it. This affects people who build Node against their distribution's Brotli, such as package maintainers.

## What the thread says
- A commenter said they would open a PR wrapping the constant in an `#ifdef`. That PR is #66895. Its labels and a bot note show an automated check flagged the account's activity as possibly automated. The bot says that is a heuristic and not proof, and the PR is still open. We draw no conclusion from it.
- A contributor suggested cherry-picking a Brotli commit. We confirmed that commit exists and what it touches; we did not check that it matches the constant.
- A commenter said Brotli 1.2.1 was released with a backport of the fix for CVE-2026-111497, which added the constant. We confirmed that the release exists and that its notes list, under "SECURITY", "CVE-2026-111497: out-of-bounds write permits remote code execution". We did not look the CVE up in a separate database, and the advisory search we ran returned nothing.
- A contributor said the compatibility fix is in the commit queue, that no release is planned for it, and strongly recommends building against Brotli 1.2.1 rather than waiting, because a binary built against 1.2.0 would be vulnerable to the CVE. This is their statement, not a project advisory.
- The Brotli release list shows 1.2.1, 1.1.1 and 1.0.10 all published within a minute of each other on 2026-10-21, which looks like backports to older lines. We did not read their notes.

## What this does not tell you
- We cannot say whether any shipped Node binary or distribution package is affected. The thread is about building Node against a system Brotli, not about the official Node downloads. We did not check how they bundle Brotli.
- It does not say which Node versions can load the vulnerable code, or whether the issue is exploitable in Node.
- We do not tell anyone to patch, rebuild, or cherry-pick. Anyone shipping Node should read the Brotli release notes and their distribution's security notices.

## Honest limits
- We did not build Node or Brotli, and did not read the Brotli diffs.
- Severity and exploitability claims are from the Brotli release notes and a contributor's comment only.
- State may have changed since 09:40 UTC.
