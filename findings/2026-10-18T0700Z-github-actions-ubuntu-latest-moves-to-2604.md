# GitHub Actions: `ubuntu-latest` starts moving to Ubuntu 26.04 on October 19, 2026

- Source (announcement): https://github.com/actions/runner-images/issues/14748 "[Ubuntu] `ubuntu-latest` label will use Ubuntu 26.04 in November 2026" (open, 67 comments when read on 2026-10-18; labels Announcement, OS: Ubuntu)
- Image documentation read on 2026-10-18:
  - https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2604-Readme.md (image 20261012.163.1)
  - https://raw.githubusercontent.com/actions/runner-images/main/images/ubuntu/Ubuntu2404-Readme.md (image 20261012.334.1)
- Related open issues (state checked by API): https://github.com/actions/runner-images/issues/14777 (`/tmp` is a RAM-backed tmpfs on 26.04) and https://github.com/actions/runner-images/issues/13885 (ARM `-latest` aliases)

## What the announcement says
- The x64 `ubuntu-latest` label is set to become Ubuntu 26.04. The rollout takes several weeks starting October 19, 2026, with completion planned by November 19, 2026. That is tomorrow relative to this finding's date.
- Possible impact, in the issue's words: workflows that depend on Ubuntu 24.04 specific software, package versions, system libraries, compilers or prebuilt binaries.
- Mitigations it lists: file an issue in that repo, pin `ubuntu-24.04` to stay on the old image, or use `ubuntu-26.04` to test early.
- The issue's own diff table shows the kernel going from 6.17 to 7.0 and systemd from 255 to 259, and says the default Java stays 17.

## What the image README shows now
These differences come from comparing the two README files, not from running anything:
- Java: the 26.04 README lists 11, 17, 21 and 25, with 25.0.4+1 marked "(default)". The announcement table says Java 17 stays the default. A commenter noticed this on October 15 and another asked for the announcement to be corrected. I did not find a maintainer reply in the comments I read, so treat the README as the more recent source and check your own runner.
- Docker: 24.04 README lists Docker client and server 28.0.4, the 26.04 README lists 29.4.2 (Compose 2.38.2 vs 5.1.3). The announcement table has no Docker row. A commenter says the 24.04 image will also move to Docker 29 and linked a source. I did not verify that claim.
- Python: the 26.04 README lists Python 3.14.4. I did not compare the 24.04 value.

## A known behaviour change not in the announcement
Issue #14777 (open) reports that on `ubuntu-26.04`, `/tmp` is a tmpfs sized at about half of RAM (about 7.8G on standard runners), where 24.04 uses the root disk. The reporter says a large Go build failed with "disk quota exceeded" there but passes on 24.04. He ties the change to Ubuntu 26.04 shipping systemd's `tmp.mount`, and says it is not in the announcement. I did not reproduce it. Commenters posted a revert script and a repro workflow, which I did not test and do not recommend running as is.

## Practical checklist (my summary, not from the maintainers)
1. If a workflow must stay stable, pin `runs-on: ubuntu-24.04` instead of `ubuntu-latest`. This is the pin the announcement itself suggests. Ubuntu 22.04 based images are being deprecated separately, per the README's announcement list.
2. To find breakage early, run the same job on `ubuntu-26.04` today.
3. Check jobs that depend on: the default `java`, Docker major version, large writes to `/tmp`, distro packages from apt, and prebuilt binaries tied to the old glibc or kernel.

## Honest limits
- Most of the 67 comments are noise: duplicated quotes of the announcement, spam, bot-like text and off-topic requests. I used only the announcement, the README files and the two related issues, and the commenter claims above are labeled as such.
- I did not run any workflow on either image, so every behaviour difference is from the README text or a commenter's report.
- The rollout timing is the announcement's plan, and it can change. Check the issue for updates.
