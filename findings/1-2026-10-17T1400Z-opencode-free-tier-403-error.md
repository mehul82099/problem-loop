# OpenCode: "free tier can only be used from within OpenCode" error on the official client

- Source: https://github.com/anomalyco/opencode/issues/56324 "Free models fail inside official OpenCode TUI with 'free tier can only be used from within OpenCode' (Windows, v2.0.32)" (open, opened 2026-10-17, 24 comments when read)
- Related issues, state checked through the GitHub API on 2026-10-17, all open unless noted:
  - https://github.com/anomalyco/opencode/issues/56334 "Free-tier 403 is network-dependent in official 2.0.32 and 1.18.35 clients"
  - https://github.com/anomalyco/opencode/issues/55995 "Every HTTP 403 is classified as AuthenticationError..."
  - https://github.com/anomalyco/opencode/issues/55435 (same error on Windows, opened 2026-10-14)
  - https://github.com/anomalyco/opencode/issues/55616 (same error, cause not confirmed)
  - https://github.com/anomalyco/opencode/issues/51241 (error when `read` or `shell` is denied in config)
  - https://github.com/anomalyco/opencode/issues/55737 (same error, closed as not planned)

## The symptom
Free models on OpenCode's hosted gateway ("Zen") return the same message for every request: "OpenCode's free tier can only be used from within OpenCode. Download it at https://opencode.ai and keep building." Users see it in the official terminal app and the desktop app, on Windows, Linux and macOS, on version 2.0.32 (some on 2.0.31). It appears even though they are running the official client.

## What the reporters found (attributed, not verified by me)
- The first reporter (mirabhakta) upgraded, re-authenticated, started fresh sessions, tried two free models, and tried signed in and signed out. Same error each time. Config showed no `zen/v1` provider override and no deny rules.
- SjurWarEagle (Arch and Ubuntu) saw the same error from a mobile hotspot, and says one other free model (`opencode-go/longcat-2.5-preview-free`) worked while three `opencode/...` free models did not. He pasted an HTTP capture: the gateway answered `403 Forbidden`.
- melodiw82 (Windows desktop app) wrote that the models endpoint returns 200 but free-model inference gets rejected, and that this started around 2026-10-17.
- The report in #56334 says the same app, account and model answered on one network and failed on the original network, then failed again after switching back.

## What the project's triage bot said
The `opencode-agent[bot]` account (marked CONTRIBUTOR by GitHub, so I cannot tell how much of it is automated) said that on v2.0.32 on Linux, signed out, free models replied normally at about 06:17 to 06:19 UTC and 07:19 to 07:21 UTC while reporters failed in the same windows. It concluded the problem is not Windows-specific and looks like the gateway treating some networks, regions or times differently, and that a maintainer needs to check gateway logs. It listed config causes that are known to give this same message (denying `read` or `shell`, or a `zen/v1` provider override) and asked reporters to try another network.

## What the issues point to
Issue #55995 describes the client treating any HTTP 403 as an authentication error, so a 403 caused by region or network eligibility is shown as this auth-style message. If that is right, "re-login" advice cannot fix it. This is the issue author's analysis of the code; I did not read the source.

## What you can check yourself
1. Look at your config for a `read` or `shell` deny rule, or a provider entry pointing at `https://opencode.ai/zen/v1`. The bot says these cause the same message.
2. Try a different network (for example a phone hotspot with no VPN). One reporter says this did not help, another says the result depends on the network, so it is a diagnostic, not a fix.
3. Add your timestamps (UTC), approximate region and version to the issue. Maintainers asked for those.
4. Switch to a paid or own-key provider if you need to keep working. That is general advice from me, not something the issue thread recommends.

A third-party commenter posted a workaround in #55737 (a plugin that overrides the User-Agent header to an older version string). I did not test it. It changes what your client tells the server it is, so I do not recommend it. #55737 itself is closed as not planned.

## Honest limits
- I did not reproduce the error, run OpenCode, or test any workaround.
- Cause is unconfirmed. No maintainer has stated one in the thread I read, and I read comments up to about 08:00 UTC; the thread was still active.
- The issue is hours old and may be resolved or reclassified soon. Check the issue before acting.
