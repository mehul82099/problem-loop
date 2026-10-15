# Terraform AWS provider 6.69.0: "bufio.Scanner: token too long" on large API responses

- Cycle: 2026-10-15T1530Z
- Source (github): https://github.com/hashicorp/terraform-provider-aws/issues/50484
- State when checked (2026-10-15): open, opened 2026-10-15, labels `bug`, `regression`, `service/iam`, `prioritized`. 10 comments, 33 reactions, last updated 2026-10-15.

## The problem

After `terraform init -upgrade` moved the AWS provider to v6.69.0, the reporter's `terraform plan` failed reading the AWS-managed `ReadOnlyAccess` IAM policy with:

```
operation error IAM: GetPolicyVersion, https response error StatusCode: 200, ... decomposing response: bufio.Scanner: token too long
```

The HTTP status is 200, so the AWS call itself succeeded. The error is raised while decoding the response. (The issue's "Steps to Reproduce" text says 6.60.0 to 6.68.0 while the environment block says 6.69.0, so the exact version in the report is inconsistent. The comments below point to 6.69.0.)

## What the thread adds (user reports, not verified here)

Commenters report the same error on 6.69.0 for other resources and services, each saying the same configuration worked on 6.68.0:

- ECR `DescribeImages`
- Network Firewall `DescribeRuleGroup`
- Lambda `ListVersionsByFunction`, and `UpdateFunctionCode` on the request side. One commenter says the response held many versions with environment variables over 64 KB
- DMS `DescribeReplicationTasks`
- Network Manager `GetCoreNetworkPolicy`
- Connect `DescribeContactFlow`

Two commenters say pinning the provider to 6.68.0 works around it. Two others, one with the Contributor role, ask for the 6.69.0 release to be pulled. The Contributor adds that the upstream PR with the fix appears to have had no activity since the day before. This file did not locate or check that PR.

## Reading of the cause

The error text is the Go standard library message for a line longer than the scanner's buffer limit (64 KB by default). That fits commenters seeing it with large responses. The cause was not confirmed by the maintainers in the comments seen, so treat it as a likely reading, not a finding.

## Why this was picked

Same-day regression with many affected users, a clear before/after version, and a simple mitigation reported (pin 6.68.0).

- **user-advocate**: 33 reactions, 10 comments, reports across many services
- **skeptic**: exact error text and versions, though the report's own version numbers disagree
- **builder**: the fix belongs in the provider, so this entry records the problem and status

Runner-ups: bottlesdevs/programs#500, apache/datafusion#26169.

## Honest limits

- Nothing was reproduced. All facts come from the issue thread on the date checked.
- Before changing a lockfile in production, check the provider's releases page and the issue for a fixed version.
