# Docker: `FROM image:tag@digest` does not check that the tag matches the digest (moby/moby#37866)

- Source issue: https://github.com/moby/moby/issues/37866 . Opened 2018-09-17, open, label "area/builder", 14 reactions on the post, 11 comments, latest 2026-10-19.
- Dockerfile reference, read 2026-10-19: https://docs.docker.com/reference/dockerfile/ . Its `FROM` syntax lines show `<image>[:<tag>]` and `<image>[@<digest>]` as separate forms, as the reporter noted in 2018. I did not find the combined form described there.
- Related tooling discussion: Sonar's rule `docker:S8431` ("Use either the version tag or the digest for the image instead of both", as quoted in a Ghost project config comment): https://github.com/TryGhost/Ghost/blob/main/sonar-project.properties and a Sonar Community thread, https://community.sonarsource.com/t/docker-s8431-makes-dependabot-upgrades-harder-to-read-and-limits-its-features/183693 . I read only the excerpts, not the full rule page.

## The behavior
If a Dockerfile says `FROM nginx:0.0.1-alpine@sha256:<digest>`, the build uses whatever image has that digest. The tag is not checked against the registry, so a wrong or outdated tag still builds. The reporter (2018) wanted either an error or a check that the tag points to that digest. This is a long-known behavior, and in the thread the maintainers describe it as how references work.

## What the thread says
- A project member (2018): a tag "is completely superseded by the digest and only exists there to be informational for the reader". If you want tag freshness, drop the digest. Another member said the builder should not special-case this, any change should apply to all commands and tools, that the current behavior is documented and some uses prefer it, and that the change would be breaking. One member wanted tags that were deleted from the registry to still be allowed.
- Later commenters (2022, 2023, 2026) say the mismatch is confusing and dangerous in one way: you can read a tag like `1.29.7` in your file and still run a seven-year-old image if the digest is old. A 2023 commenter says the same for platform plus tag plus digest. One of them (2026-03-25) says he avoids using both for that reason.
- A contributor (2025-10-03) argues the digest is there to make builds reproducible, and failing on mismatch could break that. A commenter on 2026-10-19 replies that an optional check would still be reproducible when tag and digest match, and notes that tools like Renovate keep both (tag for humans and updates, digest for pinning), while the Sonar rule above flags the combination because they do not have to match.
- No design or pull request is linked in the thread.

## What can be said
- Per the maintainers, the digest is what is used and the tag is a label. So `tag@digest` gives you a pinned image, and the tag in the file is not evidence of what is inside it.
- A tag can go stale without anything failing. If the version number matters (for security updates), a separate check is needed, for example reading the image labels or running the image to print its version. I did not test those here.
- I am not saying which of the two positions is right. Both are argued in the thread by people who use the combination.

## Honest limits
- I did not build any image or test the behavior on a current Docker version. The example digest and tag come from the issue.
- I did not verify Renovate's or Dependabot's current behavior, only what commenters and the Ghost config comment say.
- The 2018 Docker version in the report was 18.06.1. I did not check whether anything has changed since.
