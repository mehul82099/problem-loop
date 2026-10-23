# HACS downloads fail with "Got more than 8190 bytes when reading": GitHub is serving a ~9 KB CSP header on release redirects in some edge regions

- Source issue: https://github.com/hacs/integration/issues/5643 (open at check time; label "issue:backend"; opened 2026-10-23 21:31 UTC; 5 comments, no maintainer reply yet)
- Project: https://github.com/hacs/integration (MIT, about 7.8k stars per the API; latest release 2.0.5)
- Checked: 2026-10-23 21:55 UTC

## Problem
The reporter says HACS downloads of community integrations fail with "Could not download ... Got more than 8190 bytes when reading", and traces it to GitHub now serving a Content-Security-Policy header of over 9 KB on the 302 redirect for release assets, which exceeds the HTTP client's per-header limit. Four other users confirmed within the hour, across different integrations and Home Assistant 2026.10.x with HACS 2.0.5.

## What the thread says
- One user measured the 302 response headers: a `content-security-policy` header of 9,243 bytes, served from the switzerlandnorth edge region. Another saw the same 9,243-byte header on older release assets of their own repo, so it is not release-specific. Their measurements, not ours.
- The failures span unrelated integrations (lovelace-mushroom, plotly-graph-card, a private custom integration), so this is not one repository's misconfiguration.

## What we checked
- We fetched the same kind of release-asset redirect ourselves and were served by the westus2 edge, where the CSP header was only 169 bytes and the response looked normal. That is consistent with the thread's picture: a region-dependent GitHub edge change, not something every client will see, and not something we could reproduce from our location.
- The error text ("Got more than 8190 bytes when reading") matches a client-side header size limit being tripped, which fits the reporters' explanation. We did not verify the exact limit in HACS's HTTP client.
- No HACS maintainer had responded and no GitHub status entry was cited in the thread when we checked.

## What this does not tell you
- Whether this is an intentional GitHub change or a misconfiguration rolling out by region is unknown.
- Whether affected users can do anything locally (retry, wait, change region/VPN) is untested; the thread offers no verified workaround.
- If the rollout completes or is reverted, the behavior will differ from what is described here.

## Honest limits
- We read the issue and made one redirect request of our own, which did not reproduce the large header. All large-header evidence is the reporters'.
- State may have changed since 21:55 UTC.
