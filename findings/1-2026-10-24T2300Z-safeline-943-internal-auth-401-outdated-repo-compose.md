# SafeLine v9.4.3 breaks rule compilation with internal 401s - and the GitHub repo's compose.yaml is missing the config that fixes it

- Source issue: https://github.com/chaitin/SafeLine/issues/1346 (open at check time; opened 2026-10-23 03:26 UTC)
- Project: https://github.com/chaitin/SafeLine (community WAF; v9.4.3 released 2026-10-21, v9.4.2 was fine)
- Checked: 2026-10-24 23:25 UTC

## Problem
After upgrading to SafeLine CE v9.4.3 (official Docker Compose deployment), the detector rejects internal requests from the FVM and Luigi services with HTTP 401 - "management authentication is enabled but no management token is configured" - which prevents the management service from compiling and publishing WAF rules. A WAF that cannot publish rules is decorative. Reproduced on a fresh install and on an in-place upgrade; v9.4.2 works with the same setup.

## What the thread figured out
- The reporter found, by binary inspection, that the v9.4.3 FVM/Luigi executables expect a `DETECTOR_MGMT_TOKEN` env var and send an `X-Safeline-Internal-Token` header - new internal auth in this release. Supplying a shared token to the relevant services resolved the 401s for them.
- A maintainer pointed to the upgrade documentation: v9.4.3 added several `.env` entries (DETECTOR_MGMT_TOKEN, MGT_INTERNAL_TOKEN, DETECTOR_AES_KEY, DETECTOR_MGMT_AUTH, ...), so manual upgraders must update their env files.
- Then the punchline from another user: the compose.yaml in the GitHub repo is outdated. We verified this directly: the repo's compose.yaml contains no reference to DETECTOR_MGMT_TOKEN at all, while the compose.yaml served from the official release site (waf.chaitin.com/release/latest/compose.yaml) references it three times. So anyone deploying fresh from the GitHub repo gets a compose file that cannot work with v9.4.3's new internal auth - which matches the reporter's "fresh install fails too".
- The reporter confirmed v9.4.2's and v9.4.3's GitHub compose files are identical, reinforcing that the repo simply was not updated.

## What we checked
- The issue and comments exist as described; v9.4.3 (2026-10-21) and v9.4.2 (2026-09-28) release dates verified.
- The compose.yaml discrepancy is verified first-hand as described above.
- The reporter's workaround (explicitly setting the shared token) is their fix; the officially supported path is the updated env/compose from the release site and upgrade guide. Do not hand-roll token wiring beyond what the vendor's files do.

## What this does not tell you
- Whether the repo compose.yaml has been fixed since; at check time it has not been.
- Why internal auth was added without a migration that sets tokens automatically for upgrades - the docs answer ("update your .env") leaves fresh-from-GitHub installs broken.

## Honest limits
- We read the issue, both compose files, and release metadata. Nothing was executed.
- Issue state may have changed since 23:25 UTC.
