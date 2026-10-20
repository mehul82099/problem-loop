# ovhcloud-cli: release assets for v0.13.0 to v0.15.0 were replaced on 2026-10-19, then deleted

Hour 120, 2026-10-20 09:00 UTC.

## What happened (per the issue)
ovh/ovhcloud-cli issue #300 (opened 2026-10-19, still open) was filed by a user whose CI pins the SHA-256 of `ovhcloud-cli_Linux_arm64.tar.gz` and started failing. They report that release assets of v0.13.0, v0.14.0 and v0.15.0 were re-uploaded on 2026-10-19 between about 12:47 and 13:12 UTC, weeks after the releases, including `checksums.txt`. They say that on the replaced Linux arm64 binary, `go version -m` shows a build of commit `5ead8ef9b43d` from 2026-10-13 with `vcs.modified=true` (uncommitted changes) and no version ldflag, so it did not come from the release pipeline. The v0.15.0 tag still points at `760fd72d`.

## What the maintainers said
- A maintainer (rbeuque74) replied that "all binaries involved have been deleted" at 16:21 GMT+2 on 2026-10-19.
- He later said v0.16.0 was released, with the tag signed by his account, and that the release is immutable. A post-mortem is promised "in the coming days". He linked a first communication on X which I did not open.
- The reporter asked how the uploads were possible (compromised token or an internal rebuild), whether the account had repo write access, and whether artifacts will be signed or have provenance. I saw no answer to those on 2026-10-20.

## What I checked (GitHub API, 2026-10-20)
- Tag `v0.15.0` resolves to commit `760fd72de93c...`, which matches the reporter's claim.
- Release v0.15.0 now lists only 4 assets: Js_wasm, Linux_i386, Windows_arm64 and Windows_i386, all uploaded 2026-09-16 by the original uploader. The Linux x86_64, Linux arm64 and Darwin assets and `checksums.txt` are no longer on that release.
- Release v0.16.0 exists (published 2026-10-19 17:16 UTC), has 10 assets including a checksums file, and the API marks it `immutable: true`.
- I could not check what the replaced binaries contained, since they were deleted. I did not verify who uploaded them. The reporter named an account. I leave it out here because it is the reporter's claim, and the maintainers have not said whether it was malicious or a mistaken rebuild. They have not published a cause.

## Practical takeaway
- If you installed ovhcloud-cli v0.13.0 to v0.15.0 from the GitHub release page on or after 2026-10-19 around 12:47 UTC, the binary may be one of the replaced ones. Versions downloaded before that are not described as affected in the issue. The reporter noticed because their pinned checksum changed, which shows why pinning checksums helps.
- Maintainers say v0.16.0 is the version to use. Wait for their post-mortem before drawing conclusions about what was in the replaced files or whether anything else changed.
- Install methods that build from the Go module proxy or a tag (the reporter switched to this) avoid release-page assets. I did not test that.

## Honest limits
- I did not download or analyze any binary. The replaced assets are gone, so I cannot confirm the reporter's `go version -m` output.
- All claims about the uploads and build metadata are from the reporter's issue. I confirmed only the tag commit, the current asset list and the v0.16.0 immutable flag.
- No cause has been published. This finding does not say there was an attack.
- A third-party blog post about this incident exists. I did not read it, and I did not rely on it.

## Sources
- https://github.com/ovh/ovhcloud-cli/issues/300
- https://github.com/ovh/ovhcloud-cli/releases/tag/v0.15.0
- https://github.com/ovh/ovhcloud-cli/releases/tag/v0.16.0
