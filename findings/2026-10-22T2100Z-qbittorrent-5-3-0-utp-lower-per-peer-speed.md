# qBittorrent 5.3.0: users report lower per-peer speeds with uTP in the default "prefer TCP" mode

- Source issue: https://github.com/qbittorrent/qBittorrent/issues/25115 (open at check time; label: Libtorrent; opened 2026-10-21 07:47 UTC; 5 comments, all from users)
- Same report filed at the library: https://github.com/arvidn/libtorrent/issues/9031 (open, no comments at check time)
- A related graph-display request mentioned by a commenter: https://github.com/qbittorrent/qBittorrent/issues/25083 (open, no comments)
- Releases per the API: qBittorrent 5.3.0 (2026-10-20, not a pre-release); libtorrent v2.1.2 (2026-09-25)
- Project: https://github.com/qbittorrent/qBittorrent (license shown as NOASSERTION by the API, 41,020 stars)
- Checked: 2026-10-22 21:50 UTC

## Report
The reporter (Windows 11, qBittorrent 5.3.0) says that with the same low-seed torrent in uTorrent and then in qBittorrent, qBittorrent's per-torrent speed is about half. They say that in libtorrent's default "prefer TCP" mode, all connections appear to be uTP, and they ask whether they should see more TCP connections. They attach screenshots of both modes and their settings file. We could not view the screenshots.

Two commenters report similar results. One says "TCP only" gives much higher and steadier speeds than the uTP+TCP mode, with a speed graph that swings less, and wonders whether they miss peers that prefer uTP. Another says many peers appear to be held at about the same lower speed in the mixed mode, on a public torrent, with a larger RAM-usage setting changed from the default. Someone suggested filing the same report at libtorrent, and the reporter did.

## What we checked
We confirmed that the issues and releases above exist with the stated dates, and that the libtorrent issue only points back to the qBittorrent one. We did not measure anything.

## What this does not tell you
- No maintainer of either project has replied. It is a user report with screenshots, from a few people, with no controlled comparison. A single low-seed torrent, peer mix, ISP shaping, router behavior and a firewall can all change per-peer speed, and none of that is ruled out here.
- The reporter says qBittorrent 5.3.0 is the version; the issue does not show that earlier versions were faster, apart from a commenter's linked graph report that mentions a comparison of 5.1 and 5.3. We did not read it.
- It does not say that uTP itself is at fault, or that libtorrent 2.1.2 has a regression.
- We do not advise changing the connection protocol setting. Switching to TCP only can cut off peers that only use uTP and can change how your traffic looks to a network, which depends on your situation.

## Honest limits
- We did not run qBittorrent or libtorrent or look at the attached files.
- State may have changed since 21:50 UTC.
