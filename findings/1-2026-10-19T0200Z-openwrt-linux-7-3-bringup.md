# OpenWrt and Linux 7.3: preparing for a kernel that may or may not be the next LTS (openwrt#25693)

- Source: https://github.com/openwrt/openwrt/issues/25693 "kernel: status of 7.3 version". Opened 2026-10-07 by a contributor (graysky2), open, 18 comments, last comment 2026-10-19.
- Kernel status: https://www.kernel.org/releases.json (read 2026-10-19). It lists mainline 7.3-rc7 (2026-10-12), stable 7.2.11, and longterm 6.18.57, 6.12.113, 6.6.159, 6.1.190, 5.15.223, 5.10.272.
- The earlier tracking issue for 6.18: https://github.com/openwrt/openwrt/issues/21030 (open).

## What the thread is
OpenWrt is router firmware. It follows one Linux kernel version per target and prefers long-term support (LTS) kernels. The tracking issue lists what is needed to move OpenWrt's development snapshot to Linux 7.3, which is still a release candidate.

## What the opening post says (the author's own claims)
- Do not open pull requests until the next LTS kernel is announced. Post a link to your branch and target, and the author updates the list.
- The author guesses the odds are "roughly 3 to 2" that 7.3 becomes the LTS and not 7.4. His reasons: past LTS kernels did not ship later than December 11, and Linus has pushed a release past the holidays before (6.7 in January 2024). Against it, 7.3 rc1 on August 30 was earlier than any LTS rc1 in the last five years, so 7.4 might arrive before year end. He says he cannot account for AI-driven churn in the kernel. This is a forecast and not an announcement. I did not check whether kernel.org or the maintainers have said which kernel will be LTS. The kernel.org list I read has no 7.3 or 7.4 LTS entry.
- Test report: 7.3-rc6 snapshot running on his own x86 router and firewall with containers, WireGuard and other services, with "no regressions" that he saw.
- Known problems listed: one upstream change collides with OpenWrt's own MTD concat patch (the post says targets using it would silently lose it, and enabling it fails the build), a few build system fixes that are not specific to 7.3, and several feed packages that fail to build (for example jool, libpfring, netatop, xtables-addons, dahdi-linux, rtpengine), some with patches linked from contributors' own repositories.

## Discussion
- A project member (jonasjelonek, 2026-10-07) says not to maintain three kernel versions in parallel and that floating draft PRs now does not help. After a follow-up, he says people can do what they like in their own trees. The author then asks people to link their branches instead of opening PRs there.
- Contributors report working 7.3 branches for several targets (Qualcomm, Airoha) in personal forks. One says an rc7 build ran without problems for a week on x86_64. These are user reports.
- One contributor suggests restructuring the kernel patch directories to reduce backport churn. The author says it does not belong in the thread, and the contributor says there is no concrete proposal yet.

## What can be said
- This is early bring-up work. Which kernel OpenWrt will follow is not decided in the thread, and the 3-to-2 figure is one contributor's guess.
- Nothing here is a release or a promise about a version of OpenWrt.

## Honest limits
- I did not build or run any of the branches or patches linked, and I do not vouch for third-party forks. Linked patches are in individual contributors' repositories and have not been reviewed by the project in this thread.
- I did not check the status of each listed package.
- I did not verify the "no LTS later than December 11" claim against kernel history.
