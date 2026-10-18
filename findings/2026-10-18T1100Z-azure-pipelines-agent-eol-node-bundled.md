# Azure Pipelines agent still ships end-of-life Node.js versions (azure-pipelines-agent#5214)

- Source: https://github.com/microsoft/azure-pipelines-agent/issues/5214 "[BUG]: EOL/Obsolete Software: Node.js 16.x Detected" (open, opened 2025-05-19 by gidad, 9 comments, labels bug, Area: Agent, triage; a stale bot comment and a "still relevant" reply came on 2026-10-18)
- Checked on 2026-10-18:
  - Agent package table, current master: https://github.com/microsoft/azure-pipelines-agent/blob/master/docs/node6.md
  - Policy change PR: https://github.com/microsoft/azure-pipelines-agent/pull/5422 "Add Node.js version selection strategy framework with EOL policy support" (merged 2025-12-18, base master)
  - Release v4.268.0 (published 2026-01-09, now marked as a normal release; a January comment called it a pre-release at the time): https://github.com/microsoft/azure-pipelines-agent/releases/tag/v4.268.0
  - Latest agent release: v5.280.0, published 2026-10-14: https://github.com/microsoft/azure-pipelines-agent/releases/latest
  - Node.js dates: https://endoflife.date/api/nodejs.json

## The report
A user with a self-hosted agent on Debian 12 (agent 3.243.1) says security scanners flag `externals/node16/bin/node` 16.20.2 inside the agent install. Node 16 reached end of life on 2023-09-11 (endoflife.date). He asks whether Microsoft plans to remove it and whether there is a workaround.

## What the maintainers' repo shows now
- The docs table on master lists two package flavours. `vsts-agent-*` includes Node 6, 10, 16, 20 and 24, as everything that can run a task. `pipelines-agents-*` lists Node 16, 20 and 24, and describes its goal as "to not include any end-of-life version of Node".
- So the package that is supposed to avoid EOL Node still lists Node 16. Node 20 reached end of life on 2026-04-30, so that row is also past end of life today. This is my reading of the docs table and the endoflife.date dates, I did not unpack any package.
- PR #5422 adds a Node version selection framework and a setting `AGENT_RESTRICT_EOL_NODE_VERSIONS`. The PR's own diff text says that when versions are blocked by this policy, a task requiring an EOL Node fails with a message telling you to upgrade the task to Node20 or Node24, and that you can temporarily disable the check with `AGENT_RESTRICT_EOL_NODE_VERSIONS=false`. A commenter says it shipped in v4.268.0. I did not determine the setting's default value.
- That setting blocks tasks from running on EOL Node. It does not remove the Node 16 files from disk, so a scanner that looks for the binary may still flag it. That is my inference from how the PR describes it, not something the thread confirms.

## What commenters say (unverified)
- One commenter says Microsoft told customers about a year before Node 16's end of life to move off it, and that the docs table was added in May 2024, after the end of life.
- The reporter asks in April 2026 that future `pipelines-agents-*` releases drop EOL versions, noting 4.272.0 still lists Node 16 and 20. No maintainer reply is in the thread.
- On 2026-10-18 someone says Node 26 will become LTS in two days. endoflife.date lists Node 26 with an LTS start of 2026-10-28, which is ten days from the comment, so the "two days" is off.

## What this does and does not say
- It does not say the agent is vulnerable. End of life means no more upstream security fixes for Node itself, and the thread contains no specific exploit in the agent.
- It does not advise enabling or disabling the policy setting. Turning it on can make pipelines that use third-party tasks built for Node 16 fail, and I did not test that.
- It does not say whether v5.280.0, the newest release, still bundles Node 16. I only read the docs on master.

## Honest limits
- I did not install or unpack any agent package, and I did not run a scanner.
- I did not read the full PR code, only the changed file list and the lines that mention the setting.
- The thread has no maintainer response, so the plan for removing Node 16 and 20 is unknown.
