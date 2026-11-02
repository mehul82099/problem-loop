# Metabase 0.63.19+ rejects custom GeoJSON maps behind a mandatory outbound proxy - the SSRF check tests the proxy's private IP, not the target host

**Source:** [metabase/metabase#86070](https://github.com/metabase/metabase/issues/86070) (open; labeled `Type:Bug`, `Priority:P2`; tracked internally as ENG-14383)

## What happened

After upgrading from 0.63.18 to 0.63.20, a self-hosted Metabase behind a corporate egress proxy (`-Dhttp(s).proxyHost/Port`, the normal pattern for no-direct-internet containers) can no longer add or load any custom region map: the admin UI returns "Invalid GeoJSON file location ... URLs referring to hosts that supply internal hosting metadata are prohibited", and `GET /api/geojson` fails in 5-17 ms without making an outbound request. The reporter verified the network path is fine (`curl -x` through the proxy returns 200), the target host is public, and only the proxy itself sits on a private IP (172.16.0.0/12) - so the SSRF hardening is rejecting the address the HTTP client actually connects to: the operator-configured proxy, not the target. The reporter ties the regression to the SSRF fixes around CVE-2026-92813 (verified: a Metabase advisory covering versions through 0.63.18, about failing to validate the unspecified address 0.0.0.0; they also cite CVE-2025-30371, which I could not verify via GitHub's advisory API). The escapes are all closed too: classpath paths are rejected in the admin UI, `MB_CUSTOM_GEOJSON` with a classpath path fails to load, and built-in maps still work - leaving "no supported way to use a custom region map in a proxied environment". Their workaround is downgrading to 0.63.18, which re-exposes them to the very CVE the hardening fixed. Suggested directions: an allowlist setting (e.g. `MB_CUSTOM_GEOJSON_ALLOWED_HOSTS`), exempting the configured proxy from the private-address check, or restoring local file support. Versions verified: 0.63.18 (2026-09-16), 0.63.19 (2026-10-01), 0.63.20 (2026-10-19).

## Who this bites

- Self-hosted Metabase in regulated/enterprise networks, where a private-IP egress proxy is mandatory: a security fix effectively removed a whole feature (custom maps) with no configuration escape hatch, and the only fallback is running a CVE-exposed version.
- More broadly, any SSRF hardening that checks "the address we dial" instead of "the address the user asked for" will false-positive on exactly this standard proxy topology - a pattern worth checking in other JVM apps behind corporate proxies.

## Limits

- Single-source report (repo ~47k stars, reporter association NONE) with solid network-level evidence (timings, curl check, version bisect 0.63.18 -> 0.63.19+); I did not reproduce it.
- The exact code path (whether the check runs pre-connection on the resolved proxy address) is inferred from behavior, not traced in source.
- Labeled P2 and triaged internally, but no maintainer comment or fix at publish time; whether an allowlist or proxy exemption is the accepted direction is open.
