# xcodes: `install` can download the Apple silicon Xcode on an Intel Mac

- Source: https://github.com/XcodesOrg/xcodes/issues/456 (open, opened 2025-12-14, last activity 2026-10-17, no labels)
- Code location cited by a commenter, checked on main on 2026-10-17: https://github.com/XcodesOrg/xcodes/blob/main/Sources/XcodesKit/XcodeInstaller.swift (line 327)
- Latest release per the GitHub API: 2.1.0, published 2026-09-14

## The problem
The reporter (diegum) ran `sudo xcodes install 26.2` on a 2019 Intel MacBook (xcodes 1.6.2). The downloaded `.xip` was the arm64 build, and `xcodebuild` failed with `Bad CPU type in executable`. Others report the same with Xcode 26.3 (kambala-decapitator), on CI runners (pronebird), and in headless setups where a manual download is hard (jacobcxdev).

On 2026-10-17 smm-h reports it still happens on xcodes 2.1.0, macOS 26.7, x86_64, installing Xcode 26.6, and gives a specific cause.

## The proposed cause (one commenter's analysis, partly checked)
smm-h's account:
1. `xcodes list` filters by machine architecture and shows `26.6 (17F113) [Universal]`.
2. The cached list holds two entries for the same version, first the Apple silicon `.xip`, then the Universal `.xip`.
3. `install` picks `availableXcodes.first(withVersion: version)`, which is the first entry, the Apple silicon one.

What I checked in the source on main: line 327 of `XcodeInstaller.swift` does read `xcodeList.availableXcodes.first(withVersion: version)`. A search of that file for "architecture" only matches the listing and printing code (lines 494 to 526), where the machine architecture and `defaultForMachine` are applied. I did not find an architecture filter near the install path. That fits the commenter's explanation, but I did not trace the full install flow or build the tool, so treat it as consistent with the code, not proven.

## Workarounds reported (not tested here)
- Download the Universal `.xip` from Apple's developer site and run `xcodes install 26.2 --path ~/Downloads/Xcode_26.2_Universal.xip` (mattrubin).
- Manual `xip -x` and move to `/Applications` (JonathanBocanegra).
- smm-h says removing only the Apple silicon entry from the cached `available-xcodes.json` and running install without `--update` fetched the Universal build, and `xcodebuild` ran.

## Context
In May 2026 one user asked whether the project is still maintained, citing a June 2025 release. The releases API now shows 2.0.0 beta in May 2026 through 2.1.0 in September 2026, so that concern was out of date by then. No maintainer reply appears on this issue.

## Honest limits
- I have no Intel Mac and did not run xcodes. All behaviour reports are the commenters' own.
- Only the line 327 expression and the location of the architecture code were verified. The claim that install never applies the filter is a reading of search results, not a full code trace.
- Whether the earlier 1.6.2 failure and the 2.1.0 failure have the same cause is not shown.
- Xcode version numbers (26.2, 26.3, 26.6) are the reporters' and were not checked against Apple.
