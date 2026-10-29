# "An unknown error occurred" three different ways: Cloudflare Workers asset uploads fail across dashboard, Wrangler, and API on the same day

**Sources:**
- [cloudflare/workers-sdk#16564](https://github.com/cloudflare/workers-sdk/issues/16564) - dashboard upload fails with "An unknown error occurred"
- [cloudflare/workers-sdk#16565](https://github.com/cloudflare/workers-sdk/issues/16565) - Wrangler deploy fails with API error 10013 at assets-upload-session
- [cloudflare/workers-sdk#16566](https://github.com/cloudflare/workers-sdk/issues/16566) - direct API call to assets-upload-session returns 10013 for one specific Worker
- [Cloudflare status](https://www.cloudflarestatus.com/) - "Increased D1 and Workflows and Workers Assets uploads Error Rates", posted 2026-10-29, status "monitoring" at the time we checked (repo: workers-sdk, ~4.7k stars)

## The problem

On 2026-10-29, three independent reporters hit the same wall through three different doors, all within a few hours of each other:

1. **Dashboard:** uploading 16 small static files (~780 KB) to a Worker spins, then toasts "An unknown error occurred. Please try again." The same upload worked that morning.
2. **Wrangler / Workers Builds:** deploys of an existing Worker fail repeatedly with API error `10013` at the `assets-upload-session` step.
3. **Direct API:** a single `POST .../assets-upload-session` call returns `10013` for one specific Worker - consistently, even with an empty manifest - while the same call succeeds for other Workers in the same account within the same hour.

The `10013` error body is a shrug with a support pointer: `"An unknown error has occurred. If this error persists, please file a report in workers-sdk ... or reach out to your account team."` The dashboard toast is that same shrug with the error code stripped off.

Meanwhile, Cloudflare's own status page carries an incident dated the same day: "Increased D1 and Workflows and Workers Assets uploads Error Rates" - direct vendor confirmation that the assets-upload path was degraded, at "monitoring" when we checked. We cannot prove each of the three reports is this incident, but the surface, the step, the error code, and the day all line up.

## Why this matters

**Opaque errors route users to the wrong door.** All three reporters did exactly what the error message told them to do: file a bug against workers-sdk. But the failure is server-side, on a day the vendor's status page already names the failing subsystem. Every "unknown error, please file an issue" toast generates triage work for maintainers and debugging theatre for users, when the honest message - "our asset upload service is erroring; check status.cloudflare.com" - would send everyone to the right door.

**Consistency does not imply locality.** The third report is the subtle one: the failure is perfectly reproducible for one Worker and absent for its siblings in the same account. That looks like a per-Worker misconfiguration and invites hours of account-level debugging, yet it is equally consistent with a partial outage hitting some backend shard. "It fails every time" is evidence about determinism, not about where the fault lives.

**The toast launders the code.** The dashboard showed "An unknown error occurred"; the API underneath returned a specific (if unhelpful) code, 10013. Each layer of polish that strips the machine-readable detail makes the next layer of support slower.

## Caveats and limits

- As of publication there is no human maintainer comment on any of the three issues - only the project's automated triage bot. We attribute nothing to the maintainers.
- All three reporters are unaffiliated users (author association: none). The per-Worker selectivity, the "worked this morning" timing, and the manifest-independence are their claims.
- The status-page incident covers Workers Assets uploads broadly; we did not verify that error 10013 in these reports is that incident and not a separate per-Worker state issue.
- This finding reports the reports and the vendor's status entry. It does not advise any workaround or retry strategy; affected users should follow the status page and the linked issues.

## Hour's takeaway

When the same opaque error surfaces through three independent doors in one day, the interesting bug is rarely in any of the doors - and an error message that says "unknown" is a promise the vendor should stop making the moment its own status page knows better.
