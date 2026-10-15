# YouTube desktop GIF comments fail with HTTP 400 (browser extension has no fix yet)

- Cycle: 2026-10-15T1030Z
- Source (github): https://github.com/rayytor/desktop_gifs/issues/93
- State when checked (2026-10-15 10:04 UTC update): open, opened 2026-10-14, label `help wanted`, 428 comments, 80 reactions. The issue text says "Last updated: 14 October 2026, 18:00 UTC".
- Project: `rayytor/desktop_gifs`, a Chrome and Firefox extension that posts GIFs in YouTube comments from desktop.

## The problem

Per the maintainer's write-up in the issue: on 14 October 2026 YouTube started refusing GIF comments sent from desktop. First it was random and a retry often worked (the extension retries up to 12 times). Later the same day it refused every desktop request that carries a GIF, with `HTTP 400 INVALID_ARGUMENT`, before YouTube looked up the GIF. The same request without the GIF still goes through. The maintainer concludes YouTube now rejects the GIF field itself when it comes from the desktop site.

Error messages users see, quoted from the issue: "YouTube is refusing GIF comments sent from desktop (tried 12 times)" and "Request contains an invalid argument."

## What the issue says was ruled out

- A VPN or another country (failures reported in several countries, with and without VPN).
- Changing the region value in the request.
- A new or renamed GIF field: `tenorId` is still the only GIF field the server lists.
- Another GIF site: the issue says YouTube's GIF comments only take a Tenor ID.

The maintainer says there is no fix yet and asks for pull requests with a method that actually posts and stays up.

## Why this was picked

Fresh (one day old), concrete, reproducible by many users, and the thread already separates what is known from what is guessed.

- **user-advocate**: 10.0 - 80 reactions, 428 comments
- **skeptic**: states a concrete failure with an error code
- **builder**: a fix would live in someone else's extension, so this entry records the problem only

Runner-ups: microsoft/terminal#8914, rtk-ai/rtk#845, googlemaps/android-maps-compose#312.

## Honest limits

- Everything above is taken from the issue text on the date checked. It was not reproduced here.
- The situation is changing hourly. Check the issue for the current state.
- This repo does not try to bypass or work around any YouTube restriction.
