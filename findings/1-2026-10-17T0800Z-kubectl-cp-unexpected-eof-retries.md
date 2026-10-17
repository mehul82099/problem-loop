# kubectl cp: "Dropping out copy after 0 retries, unexpected EOF" and the `--retries` flag

- Source: https://github.com/kubernetes/kubectl/issues/1425 (open, labels `kind/bug`, `triage/needs-information`, opened 2023-05-05, 7 reactions; a triage bot posted on 2026-10-17 that it has not been updated in over a year and should be re-triaged)
- Docs read on 2026-10-17: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_cp/ - lists `--retries int`: "Set number of retries to complete a copy operation from a container. Specify 0 to disable or any negative value for infinite retrying. The default is 0 (no retry)."
- Related, state checked through the GitHub API: https://github.com/kubernetes/kubernetes/issues/60140 "kubectl cp fails on large files" (closed, 223 comments); https://github.com/kubernetes/enhancements/issues/4006 "Transition from SPDY to WebSockets" (open, label `stage/stable`).

## The problem
Reporter GithubShanLe ran `kubectl cp pod:/home/log ./test` (client 1.24, server 1.22, which is outside the supported skew) and saw `Dropping out copy after 0 retries` and `error: unexpected EOF` on most attempts. Only about two in ten succeeded. The 2023 triage replies asked for a leading slash and closer client and server versions.

Later commenters on newer clients report the same error, often on large files: younsl copied a 300 MB JSON file on client v1.29.1, and Elyytscha and codablock hit it again in 2024 and 2025.

## Workaround reported by several people
Add `--retries 10` (JCSadeghi, 2023, confirmed by younsl and Elyytscha). Elyytscha's log shows `Resuming copy at 83996672 bytes, retry 1/10`. The docs page above confirms the flag exists and defaults to no retries. A negative value retries forever, so a cap such as 10 avoids an endless loop if the failure is not transient.

## A possible cause (one commenter's analysis, not confirmed by maintainers)
codablock (2025-10-15) says `kubectl cp` runs `tar c` in the pod through `exec`, and that `exec` sometimes drops the last bytes of stdout, so the local `tar x` fails. He reproduced it with this loop, which failed after a few iterations with `tar: short read` (the command is in the issue):
create a 200 MB file in the pod with `dd`, then repeat `kubectl exec ... -- tar c /tmp/test-file | tar t`.
He could only reproduce it when piping `exec` output directly into `tar`, and guessed at a missing final flush or signal handling. This is a guess, and it matches the maintainers' pointer below.

## What the maintainers said
brianpursley (2023-07-19) accepted the issue and wondered if it relates to kubernetes/kubernetes#60140, adding that the SPDY-to-WebSockets work (enhancement 4006) may fix it. That is a possibility, not a statement that it does. I did not check how far that work has gone beyond its `stage/stable` label, or whether it applies to `cp`.

## Honest limits
- I ran nothing against a cluster. Error messages, versions and the effect of `--retries` are the commenters' reports, and the flag's semantics come from the docs page.
- Retrying can mask data problems: a successful retry resumes from a byte offset per the log, but I did not verify file integrity in any case, so after a retry, checking sizes or checksums is sensible. That advice is mine, not from the thread.
- The cause above is one person's hypothesis. The issue is still labelled `triage/needs-information`.
