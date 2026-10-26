# GitHub changed DNS on westus2 runners, and now a security agent that allowlists domains only knows one IP per domain

- Source issue: https://github.com/step-security/harden-runner/issues/708 (open; opened 2026-10-23)
- Saga: harden-runner#705 and actions/runner-images#14925 (both verified open; GitHub's westus2 DNS experiment blocks binding 127.0.0.1:53 since 2026-10-12)
- Project: step-security/harden-runner (~1.3k stars; egress-filtering agent for CI)
- Checked: 2026-10-26 18:31 UTC

## Problem
On GitHub-hosted runners in westus2, harden-runner in block mode records exactly one A record per allowed domain - then drops connections to that domain's *other* IPs. The reporter's logs are textbook: agent records `mirror.gcr.io -> 173.194.202.82`, curl tries `173.194.43.82`, dropped. registry.npmjs.org and even GitHub's own hosts fail the same way. Every retry lands on a different IP of the domain, so retries essentially never succeed.

## Why it is interesting
- This is chapter two of a platform experiment colliding with security tooling. Chapter one (verified): GitHub began trialing DNS configuration changes on westus2 runners on Oct 12; harden-runner's agent could no longer bind 127.0.0.1:53, and its fallback restarted Docker and killed service containers (#705). The fix for that shipped - and chapter two is this subtler failure: resolution now works, but only one answer survives the agent's recording, so multi-homed domains are allowlisted for one IP and blocked on the rest.
- The regional A/B evidence is clean: one user ran the same workflow 14 times - all 4 jobs scheduled to westus2 failed, all 10 on other regions passed. GitHub scheduling becomes the dice roll that decides whether your CI is green.
- The workaround users landed on is ironic for a security tool: switch from `block` to `audit` - keep visibility, drop enforcement - until the agent learns the new DNS world. The vendor says it is in direct conversation with GitHub.
- Process credit: the original report (from a prolific OSS maintainer) pins exact action SHAs, agent versions, image IDs, and linked runs; a later comment even carries an explicit AI-assistance disclosure for its debugging captures. This is how cross-vendor incidents should be filed.

## Honest limits
- Root cause ("GitHub is experimenting with DNS on westus2") comes from the vendor's member comment and the linked runner-images issue, not a GitHub announcement; the experiment's scope and timeline are unpublished.
- No fix released at check time; affected users are on audit mode or pinned away from ubuntu-latest.
- Log excerpts are the reporters'; we verified the linked issues exist and match the described saga.
- Issue state may have changed since 18:31 UTC.
