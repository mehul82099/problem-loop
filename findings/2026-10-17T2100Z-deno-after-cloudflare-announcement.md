# Deno joins Cloudflare: what the Deno runtime's status is, and what the community is asking (denoland/deno#37030)

- Source: https://github.com/denoland/deno/issues/37030 "The state of Deno after the Cloudflare announcement" (open, opened 2026-10-15 by bartlomieju, 8 comments and 34 reactions when read; the author says it will be pinned and updated)
- Announcement posts, both fetched on 2026-10-18 and both dated October 9, 2026:
  - https://deno.com/blog/cloudflare "Deno is joining Cloudflare" (by Ryan Dahl)
  - https://blog.cloudflare.com/deno-joins-cloudflare/ (by Kenton Varda and Ryan Dahl)
- Earlier issue asking for a pinned notice: https://github.com/denoland/deno/issues/36995 (closed, opened 2026-10-09)
- GitHub API on 2026-10-18: repository license MIT. The "latest release" it returns is v2.9.7, published 2026-09-17.

## What the project says
From the Deno blog post:
- The whole Deno team is joining Cloudflare. They say they will put future development into a shared platform (built around Cloudflare Workers and Durable Objects, and a project called celld) instead of continuing a separate runtime and hosting service.
- The company will support the Deno runtime for another year with monthly releases containing bug fixes and security updates. After that year it ends its own development of the runtime. Deno stays open source and the post says others who want to continue it are welcome.
- Deno Deploy (the hosting service) will keep running for six months and then shut down, with migration support for paying customers moving to Cloudflare Workers.
- JSR (the package registry) will continue, with infrastructure moving to Cloudflare. It also says it will keep supporting `rusty_v8`.

From the GitHub issue (written by a maintainer, bartlomieju):
- Until October 2027: a 2.9.x LTS release every month, security reports handled as before, and canary builds from `main`.
- No new feature work. Feature pull requests will be closed without merging. Well-written bug-fix pull requests will be merged. Feature request issues stay open and are labelled.
- Features that landed on `main` after the 2.9 branch was cut (examples given: `deno sync-types` and removing the internal TypeScript fork) will be reverted so `main` matches 2.9.
- Deno is MIT-licensed and anyone is free to fork. They are "considering ways to organize development beyond October 2027" and ask interested people to contact bartlomieju.

## What commenters said
- Several commenters (matthewruzzi, jflatow, daniellacosse, DanteASC4, neonbyte1) said they want Deno to continue, and asked about a nonprofit or foundation home. matthewruzzi named the OpenJS Foundation as an option and said there was related discussion in the Node.js channel of that foundation's Slack. That is his report, not a decision by anyone.
- jflatow (marked CONTRIBUTOR) said he prefers one community effort over a fork. daniellacosse said a Discord community of over 100 active members is coordinating around a fork but would prefer an official handover to a steward.
- Questions in the thread: does JSR stay active (answered in-thread by a commenter, citing the Deno blog, yes), and who will maintain `@std/*` (not answered in the comments I read).

## What this shows and does not show
- It shows the vendor's stated plan: a year of maintenance releases, then the company stops, no new features meanwhile, and Deploy shuts sooner.
- It does not show any foundation, fork, or new maintainer being agreed. People have only expressed interest.
- Plans can change. The issue says it will be updated.

## Honest limits
- I read the two blog posts' opening parts and the Deno post in full. I did not read the whole Cloudflare post.
- I did not check Deno's roadmap beyond these pages, and I did not check how many dependants rely on Deno.
- Apart from the repository licence, the API facts above, and what I fetched, everything comes from the maintainers' and commenters' own statements.
- The "latest" release the API returns (v2.9.7, 2026-09-17) is just what it showed. I did not confirm whether a newer release exists.
