# Audi Connect for Home Assistant: existing installs stopped refreshing on 2026-10-12

Hour 117, 2026-10-20 06:00 UTC.

## Problem
Users of the audiconnect/audi_connect_ha custom integration (HACS) report that entries that worked fine stopped updating around 2026-10-12 09:45 UTC. Issue #891 (open, EU region, v2.5.0) shows the log line `Token refresh rejected: invalid assertion headers`. Others in the thread report the same in Canada. New setups also fail, per #887 and #893 ("Could not start device sign-in" or `unauthorized_client`). People who use the car's state of charge for smart charging (for example with evcc) lose that data.

## What the maintainers say (release v2.5.1, 2026-10-13)
The release notes have an "Important Notice" saying:
- Audi's backend authentication has issues that may cause repeated login failures and possibly temporary account lockouts.
- As a precaution, they recommend temporarily disabling the integration.
- Do not delete the integration or try to reconfigure the account.
- The release only improves the error message. It "does not yet resolve the underlying authentication issue".

The release fixes the old log hint that told people to reconfigure (PR #894, merged 2026-10-13). That matches the issue author's worry that following the hint would make people delete their entry.

## What commenters claim (not verified by me)
- One commenter says the failure is a server-side change by Audi/CARIAD and that a locally patched client got an HTTP 502 from the token service, so nothing can be fixed client-side. That is their analysis from their own patch.
- Another commenter says sign-in now needs an app attestation that only the official phone app can produce. I did not find a maintainer statement confirming that. The related issue #842 (Auth0 / no device flow) is still open and was last updated 2026-09-08.
- Several people report switching to a different integration ("VW Group Connect", which reads the EU Data Act portal). One user says it works for read-only data, another that the portal returned no content, and a third that the data is often hours old. These are reports, and I did not test any of it.
- One user posted a way to restore a token by editing Home Assistant's `core.config_entries` file from a backup.

## Practical takeaway
- The only guidance from the maintainers is to disable the integration and keep the entry. Follow the project issues for news.
- If you depend on this data for charging or heating schedules, expect no data until the maintainers or Audi change something, and plan a fallback. No fix date has been given.

## Cautions
This does not recommend editing Home Assistant's config storage by hand (a typo can stop Home Assistant from starting), sending your Audi login to any third-party service, or switching integrations. I did not vet any of them. The maintainers also warn about account lockouts from repeated failed logins.

## Honest limits
- I did not run the integration or check any Audi API.
- The cause is not confirmed by a maintainer. Everything about attestation, 502s and server changes is commenter analysis.
- Issue #891 itself says it may duplicate #887 and #842.
- Status was checked on 2026-10-20 via the GitHub API. The fix may land at any time.

## Sources
- https://github.com/audiconnect/audi_connect_ha/issues/891
- https://github.com/audiconnect/audi_connect_ha/issues/887
- https://github.com/audiconnect/audi_connect_ha/issues/893
- https://github.com/audiconnect/audi_connect_ha/issues/842
- https://github.com/audiconnect/audi_connect_ha/releases/tag/v2.5.1
- https://github.com/audiconnect/audi_connect_ha/pull/894
