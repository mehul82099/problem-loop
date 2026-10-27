# PowerShell Gallery blames your "source location" while its own downloads flap

- Source issue: https://github.com/PowerShell/PowerShellGallery/issues/357 (open; opened 2026-10-27)
- Verified: repo PowerShell/PowerShellGallery (official gallery tracker)
- Checked: 2026-10-27 18:06 UTC

## Problem
For two days, `Install-Module` against the PowerShell Gallery has been failing at random with "Source Location 'https://www.powershellgallery.com/api/v2/package/...' is not valid." The source location is fine. Each retry fails on a different package, on different machines (Windows Server 2022 Azure VM and Windows 11), different networks, and both PowerShell 5.1 and 7.6. Commenters confirm the same: one sees it on Azure machines and a work notebook ("seems to be global"), another has ANY module install intermittently failing - Pester, AWS.Tools - locally and in CI pipelines.

## Why it is interesting
- A misleading error message doing real damage. "Source Location is not valid" points the user at their own configuration - TLS settings, repo registration, proxy - and the reporter dutifully checked all of it (TLS 1.2 verified, two machines, two networks, two PowerShell versions) before concluding the problem is upstream. How many people are re-registering their gallery repository today because the error told them to?
- The randomness is the signature. A different package failing on every successive attempt is not how auth, TLS, or config bugs behave; it is how a load-balanced backend with some sick members behaves. The pattern itself is diagnostic, and the thread shows several users independently converging on it.
- The blast radius is build infrastructure. Install-Module sits at the top of countless CI pipelines (the second commenter's failing step list is a real one: Pester, AWS.Tools.Installer, then module installs). When the gallery flaps, builds fail nondeterministically - the worst kind of failure to chase, because re-running the pipeline "fixes" it until it doesn't.
- No Microsoft acknowledgment in the thread at check time. Independent corroboration inside the thread (Azure VMs, work notebooks, CI pipelines, unrelated module names) is what elevates this from one user's network to an apparent incident window.

## Honest limits
- Root cause is unknown; "backend/CDN flapping" is inference from the random-failure pattern, not confirmed by Microsoft.
- No official status or acknowledgment seen in the thread at 18:06 UTC; the gallery's status page was not independently checked.
- Scope ("global") is asserted by affected users across several networks, not measured.
- Intermittent by nature: may already be recovering or worsening since 18:06 UTC.
