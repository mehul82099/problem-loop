# Tailscale on macOS: the login button does nothing and the browser never opens (tailscale#18676)

- Source: https://github.com/tailscale/tailscale/issues/18676 (opened 2026-02-10, closed by a contributor 2026-02-12 as not reproducible, reopened 2026-04-14, still open; 48 comments, labels OS-macos and bug; last comment 2026-10-18)
- Related issue checked by API: https://github.com/tailscale/tailscale/issues/16606 ("add account" and "log in" menu items do nothing when connected to VPN, open)
- A blog post a commenter links as a fix, https://samy.blog/tailscale-login-problem/, did not return readable content when I fetched it, so I cannot say what it recommends.

## The report
After logging out, the reporter (Tailscale 1.94.1, macOS 26.2) says the app shows "Authentication needed" but clicking Log in, or running `tailscale up --reset` from the command line, never opens the browser. He later fixed it by uninstalling several times and restarting. A contributor (croakerbcts, CONTRIBUTOR) closed it on 2026-02-12 because they could not reproduce it and thought it might be a local setup. Reports kept arriving, and the same contributor reopened it on 2026-04-14.

## Pattern in the comments (user reports, none confirmed by the project)
Since March, dozens of people on macOS 15 and 26 and Tailscale 1.94 to 1.98, mostly the standalone app, report the same, and one reports it on Android and one on Windows. A few things stand out:
- Many of the fixes people report are about the network between the machine and Tailscale's login server, not about Tailscale itself:
  - Turning off Cloudflare WARP (several people say this fixed it at once; a user links the related issue #16606).
  - A corporate firewall or VPN (one person names Fortinet, another says their organisation's firewall), or a DNS filter that needed Tailscale's domains allowed (one person's NextDNS fix).
  - Switching to a phone hotspot, or resetting ISP hardware (one person says a "hard reset of my ISP hardware" fixed it).
  - Turning off IPv6 on Wi-Fi (one person with a command that changes the macOS network setup).
  - Enabling the app's system proxy setting through `defaults write` (one person).
  - Using the "Set Tailscale DNS" menu item, after which the login worked for two people, neither knows why.
- Ways around the browser step: running `tailscale up` in a terminal, which prints a login URL you open yourself (one commenter says that worked, another says on his machine the command printed nothing), finding the URL in the system log (one commenter shows a console line), or using a pre-made auth key with `tailscale up --auth-key`. Two commenters report the auth-key route worked.
- One commenter says the App Store app and the command line work, but the standalone app does not, which suggests the cause may depend on the build.
- A few people say it fixed itself after a while or when Tailscale's own service recovered from an outage. One of them thought the timing matched a Tailscale outage. I did not check any Tailscale status history.

## Cautions
- An auth key is a credential. If you use one, make it short-lived and single-use, do not paste it into issue threads, and revoke it afterwards. That is general advice, not from the thread.
- Commands that change your network settings (turning off IPv6, `defaults write` to the app's preferences) are things to try only if you understand how to undo them.
- Turning off a firewall or security client at work may break your organisation's policy. One commenter did it temporarily, I am not recommending it.

## Honest limits
- I did not run Tailscale or reproduce the failure. All causes and fixes are commenter reports, and many conflict, so they may be separate problems with the same symptom.
- No maintainer explanation of the cause is in the thread. The only project replies I saw are the close and reopen and one question about whether it was persistent.
- A spam-like comment in February from an account offering to "help" was reported by a maintainer, and I ignored it.
- I did not read the Tailscale source or release notes, so I do not know whether a newer release changed this.
