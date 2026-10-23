# WinGet: `winget upgrade`, `list` and `export` hard-crash for the whole machine when one package has overlapping ARP version ranges

- Source issue: https://github.com/microsoft/winget-cli/issues/6616 (open at check time; label "Needs-Triage"; opened 2026-10-23 21:23 UTC; 8 comments). Duplicates/related: #6613, #6614, #6615 (all open, same error)
- Package-side data issue: https://github.com/microsoft/winget-pkgs/issues/460509 (open: Microsoft.PowerShell duplicate version 7.6.8 / 7.6.8.0)
- Code read on `master`: https://github.com/microsoft/winget-cli/blob/master/src/AppInstallerSharedLib/Versions.cpp (`VersionRange::operator<` throws E_INVALIDARG on overlap, around line 583)
- Trigger release: PowerShell v7.6.8, published 2026-10-22 per the GitHub API
- Checked: 2026-10-23 22:50 UTC

## Problem
The reporter says that when the winget source contains a package with overlapping ARP `VersionRange`s - reproduced with Microsoft.PowerShell 7.6.8 and 7.6.8.0 - global commands like `winget upgrade`, `winget list` and `winget export` abort with "0x80070057: The parameter is incorrect", making them unusable for the whole machine, not just for that package. They trace it to `VersionRange::operator<` throwing and the CLI catching it as a fatal unexpected error.

## What the thread says
- Several users confirmed within minutes, including on ARM (Surface 11), and three near-identical issues were filed the same evening (#6613, #6614, #6615), all still open.
- One user's log shows the match phase also finding "multiple matches for installed package [Google Chrome]", suggesting the PowerShell duplicate may not be the only trigger in the wild. Their log, not verified by us.
- One user tried `winget pin add` on PowerShell and reports `winget upgrade` still failed - so pinning did not help them.
- A workaround people mention is uninstalling PowerShell 7.6.8 (or installing 7.6.7 instead). That is community advice, not official; uninstalling a shell you use has its own risks, and we did not test it.
- No Microsoft maintainer had responded when we checked.

## What we checked
- `Versions.cpp` on `master` does throw E_INVALIDARG from `VersionRange::operator<` when either range is empty or the two overlap (the `THROW_HR_IF` at about line 583), which matches the reported crash path. We did not trace every caller.
- The winget-pkgs data issue (#460509) exists and is open, and PowerShell 7.6.8 was released on 2026-10-22, one day before the reports - consistent with the timing.
- We did not run winget.

## What this does not tell you
- Whether Microsoft will fix the client (skip the bad package), the package data, or both is unknown; no maintainer verdict yet.
- The full set of affected packages is unknown; PowerShell is the confirmed trigger, Chrome is a maybe from one log.
- If the package data is corrected in winget-pkgs, the crash may stop even without a client update.

## Honest limits
- We read the issues and the cited source on `master`. Nothing was executed on Windows.
- Issue state may have changed since 22:50 UTC.
