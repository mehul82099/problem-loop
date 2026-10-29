# One missing text file blocks the ecosystem: Node 26.13.0 shipped without its checksums

- Source issue: https://github.com/nodejs/node/issues/67087 (open; opened 2026-10-28)
- Project: nodejs/node (~123k stars)
- Checked: 2026-10-29 03:45 UTC

## Problem
The Node.js v26.13.0 release went out without `SHASUMS256.txt` - the plain-text checksum file that accompanies every release directory. The blast radius was immediate and cross-tool: node-gyp treats a missing checksum as a critical failure (the reporter hit it installing a package with native builds in Azure Pipelines), pnpm refused to install the runtime ("Failed to fetch SHASUMS256.txt ... status: 404"), and nvm couldn't pick up the release. The previous version (26.12.1) worked fine, isolating it to this release. A community member flagged it to a Node TSC member, who manually uploaded the file hours later - the URL now returns 200 - but noted it still doesn't appear in the directory listings, and looped in the web-infra team. Root cause of the release-process miss is unknown; the reporter observed odd extra extensions on other files in the release listing, suggesting something upstream of publication went sideways.

## Why it is interesting
- The smallest artifact carried the whole supply chain. A kilobyte text file gated three independent install paths simultaneously - not because of a vulnerability, but because every downloader correctly refuses to install unverifiable binaries. This is security posture working exactly as designed: "fail closed on missing checksums" converts a release glitch into an outage, and that is the right trade. It's worth noticing what the outage proves.
- Release integrity is a process, not a file. The recovery - a TSC member manually uploading the missing artifact after a ping - worked, but reveals the gap: if a required release artifact can be absent without the release pipeline noticing, the pipeline's completeness check is the actual bug. The still-missing directory listing entry hours later underlines that the manual fix addressed the symptom.
- A good bug report from the trenches: the reporter isolated versions, reproduced across Windows Server and WSL2, and linked the exact failing URL with response headers. It got the right people's attention within hours.
- Compare the PowerShell Gallery 404s from earlier today (hour 315): package ecosystems fail at the seams between "the artifact exists" and "the index/metadata agrees," and the failure mode users see is always a phantom 404 on something that should obviously be there.

## Honest limits
- Root cause unknown; no web-infra response at check time. The manual upload resolved the download failure, but the process gap is unexplained.
- The reporter's "files have additional extensions" observation is from a screenshot; unverified what it implies.
- Issue remains open; directory-listing inconsistency persists as of 03:45 UTC.
- Impact window was hours; most installers work again per the manual upload.
