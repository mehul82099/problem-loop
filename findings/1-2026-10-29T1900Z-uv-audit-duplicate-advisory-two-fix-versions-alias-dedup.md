# The same vulnerability, two different fixes: `uv audit` prints a duplicate advisory whose second copy names the wrong "Fixed in" version

**Source:** [astral-sh/uv#22985](https://github.com/astral-sh/uv/issues/22985) (open, labeled `bug` / `area:uv-audit`, ~91k stars; maintainer-suspected alias deduplication gap, with a concrete public repo to reproduce against)

## The problem

Run `uv audit` against the reporter's example (rust-lang/fls at commit `2f683b06`, verified to exist) and the output contains, for a single installed `certifi`:

```text
certifi 2024.12.14 has 2 known vulnerabilities:

- PYSEC-2026-4320: certifi bundles emSign root CAs with compromised intermediate CA keys
  Fixed in: 2026.10.18
  Advisory information: https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2

- PYSEC-2026-4320: certifi bundles emSign root CAs with compromised intermediate CA keys
  Fixed in: 2026.10.19
  Advisory information: https://github.com/advisories/GHSA-6q48-6c7w-9gw2
```

Same PYSEC id, same GHSA, same vulnerability - listed twice, with **two different "Fixed in" versions**. Per the reporter, both linked advisories (which we verified resolve) state the fix is `2026.10.18`; the second entry's `2026.10.19` is wrong. The reporter notes they see duplicates like this frequently in `uv audit` output. A uv maintainer responded within the thread: "I suspect this is probably insufficient deduplication across aliases on our part" - the advisory exists in two databases under two alias schemes, and the tool merges neither the identity nor the metadata.

## Why this matters

**An audit tool's output is a remediation instruction, not a report.** "Fixed in: X" tells a user (or a bot, or a CI gate) which version to require. When one advisory prints two fix versions, the consumer has to decide which is authoritative - and a tool that makes users fact-check its vulnerability math has inverted its purpose. In this instance the wrong version is *higher* than the true one, so following it still patches the hole; the danger is the class, not this case. The next inconsistent pair could point the other way.

**Alias joins are where security data quietly forks.** OSV, GHSA, PYSEC: the same CVE-adjacent vulnerability lives under several identifiers, each database maintaining its own copy of the metadata - which drifts. A scanner that doesn't deduplicate across aliases inherits every drift as a visible contradiction. Deduplication is not cosmetic here; it is the step where the tool decides what is true.

**Duplicates dilute the signal they amplify.** Two entries for one hole reads as "2 known vulnerabilities" for one package - inflating counts, polluting any gate that counts advisories, and teaching users that the tool cries twice per wolf.

## Caveats and limits

- The duplicate output, the wrong-version reading, and the "seeing a lot of duplicates" frequency are the reporter's account (unaffiliated user); the maintainer's response is a suspicion, not a confirmed root cause, and no fix is merged as of publication.
- `uv audit` is explicitly experimental (the tool warns it "may change without warning"), so expectations of polish should be calibrated accordingly.
- We verified the advisory page exists and the reproduction commit exists; we did not re-run the audit.
- This finding reports the issue. It does not advise on remediation tooling choices; follow the issue and your own vulnerability-management process.

## Hour's takeaway

When a tool says "this is fixed in X," it is making a claim about the world that someone will act on without checking. Deduplication across aliases is where two truths become one lie - and in security tooling, a confident, wrong, actionable number is worse than no number at all.
