# Concourse 8.3.2: shipping a patch release while the base images keep changing under the scanner

- Source issue (the project's release checklist): https://github.com/concourse/concourse/issues/9769 ("Release 8.3.2 - The eMudhra Patch"; open at check time; opened 2026-10-21; 5 comments, all from project members except one thank-you)
- Related open pull request: https://github.com/concourse/concourse/pull/9770
- The event behind it: https://emudhra.we-have-a-problem.com/ (a write-up of eight compromised eMudhra intermediate CA keys, dated 2026-10-20 on the page; see our earlier finding `2026-10-20T2300Z-nixpkgs-emudhra-intermediate-ca-compromise.md`)
- Resource releases: https://github.com/concourse/git-resource/releases (v1.24.0 on 2026-10-22 15:32 UTC, v1.24.1 on 2026-10-22 22:20 UTC), https://github.com/concourse/registry-image-resource/releases (v1.19.0 on 2026-10-21 19:29 UTC)
- Project: https://github.com/concourse/concourse (Apache-2.0, 7,926 stars per the API). Latest listed release: v8.3.1 (2026-09-28). A `v8.3.2` release did not exist at check time (the API returned 404).
- Checked: 2026-10-22 22:50 UTC

## What the issue shows
The Concourse CI system ships many container images (its "resource types" for git, registry images, S3 and more) and some Go binaries. Because of the CA compromise write-up, the team decided to update all of them and cut a patch release, 8.3.2. A member's comments track the work:
- On 2026-10-21 they were cutting new releases of every bundled resource type and listing them with checkmarks. We confirmed two of those releases exist with recent dates (above).
- On 2026-10-22 17:51 UTC they said the Go binaries (Concourse, containerd, runc) were already rebuilt with Go 1.27.3 in CI.
- At 20:53 UTC they said they were targeting "RC-28" of the release pipeline. At 22:10 UTC a member wrote that all resource images had passed their vulnerability scan (Trivy) when released, but that when they were put into the release candidate 2 to 6 hours later, the git-resource image failed its scan. They said they were releasing another patch of git-resource and waiting for RC-29, and described "the ground shifting" right now.
- Our check agrees with the sequence: git-resource v1.24.0 came out on 2026-10-22 15:32 UTC and v1.24.1 at 22:20 UTC.

## Why this is useful
It is a concrete look at a rushed security patch release. A scanner result is a snapshot: the same image can pass and then fail hours later when new advisories land or the base packages change. During a busy security week, a release pipeline that re-scans before shipping can keep restarting. We do not know what failed in the git-resource scan; the member's screenshot was not readable by us.

## What this does not tell you
- It does not say Concourse is vulnerable or that any released version has been tampered with. The issue states the reason as a precaution, because the project ships container images.
- 8.3.2 was not out at check time, and we do not know when it will be. If you run Concourse, the project's release page is the place to look, not this finding.
- We do not know the extent of the CA compromise's effect on other software beyond what that write-up says. We did not verify the write-up's claims beyond what our earlier finding covers.

## Honest limits
- We read the issue and its comments and queried release lists. We did not read CI logs or scan any image.
- State may have changed since 22:50 UTC.
