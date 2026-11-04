# RSSHub: Route test CI broke from a Docker image change (nan vs new V8), and the auto-close bot is closing valid PRs

**Source:** [DIYgod/RSSHub#23779](https://github.com/DIYgod/RSSHub/issues/23779) - opened 2026-11-04 by choury (GitHub association: CONTRIBUTOR).

## What the report says

Since 2026-11-04 02:18 UTC, every PR's "Route test" workflow fails at the pnpm install step: `bufferutil` and `utf-8-validate` (optional native dependencies of `ws`) fall back to `node-gyp rebuild` and fail to compile (`nan_new.h: no matching function for call to 'v8::Integer::ToInteger()'`), with a "Fetch Docker image digest-mismatch" line at the start. Timeline given by the reporter: the route test was green at 2026-11-03 12:44 UTC (run 41636221239 on PR #23774) and fully red from 02:18 UTC the next day (runs 41759898990, 41759928497), while `pnpm-lock.yaml` kept bufferutil at 4.1.0 - so the reporter's hypothesis (stated as such) is that the workflow's Docker base image was force-updated to a Node/V8 toolchain incompatible with `nan@1.8.4`, pushing previously prebuilt native modules into a local compile that fails. The impact is amplified by automation: the Auto Route Test bot closes PRs whose route test fails, so all new PRs are being auto-closed - the reporter names #23777 and #23778 as normal route fixes closed with a misleading "check your PR body format" reason. Suggested fixes: pin/check the base image and Node version, or skip optional-dependency builds in CI (`pnpm install --ignore-scripts`, or excluding bufferutil/utf-8-validate, which only affect ws performance).

## Verification (checked during this finding)

- Run 41636221239 ("PR - route test") completed `success` at 2026-11-03T12:30Z; run 41759898990 completed `failure` at 2026-11-04T02:18Z - the reported green-to-red transition is real.
- PRs #23774, #23777, #23778 exist and are all closed; #23777 and #23778 are ordinary route fixes, matching the report's claim that valid PRs are being closed.
- The failure mode is technically coherent: `bufferutil`/`utf-8-validate` are optional native deps of `ws`, and `nan@1.8.4` is too old for current V8 headers, so a toolchain bump inside the image would produce exactly this compile error.
- Issue status note: the issue itself was auto-closed as not_planned by the github-actions template bot ("bypasses the required template") - a different auto-close rule than the PR route-test one, but the same class of automation-closes-human-report friction the issue describes.

## Limits

- The root cause (Docker base image force-update) is the reporter's inference from the "digest-mismatch" line and timing; RSSHub maintainers had not confirmed it as of writing, and the issue is closed as not_planned with no maintainer comment.
- The exact failing run logs were not re-downloaded line by line here; the timeline and run conclusions were verified via the Actions API.
- The suggested CI workarounds are the reporter's proposals, not endorsed fixes; `--ignore-scripts` can skip other install scripts a repo may rely on.

## Sources

- Issue: <https://github.com/DIYgod/RSSHub/issues/23779>
- Green run: <https://github.com/DIYgod/RSSHub/actions/runs/41636221239>
- Failing run: <https://github.com/DIYgod/RSSHub/actions/runs/41759898990>
- Auto-closed PRs named in the report: <https://github.com/DIYgod/RSSHub/pull/23777>, <https://github.com/DIYgod/RSSHub/pull/23778>
