# setup-gcloud hangs when dl.google.com stalls (setup-gcloud#738)

- Source: https://github.com/google-github-actions/setup-gcloud/issues/738 "The endpoint dl.google.com is stalling and dropping TCP transfer streams". Opened 2026-10-13, 10 comments, 26 reactions on the opening post. Still open on GitHub at the time of checking, though two commenters report it resolved.
- Action input reference: https://github.com/google-github-actions/setup-gcloud/blob/main/action.yml (has `skip_install` and `version` inputs, read 2026-10-18).

## What was reported
- The reporter: setup-gcloud (pinned to the v3.0.0 commit) could not download `google-cloud-sdk-568.0.0-linux-x86_64.tar.gz` from dl.google.com on 2026-10-13. The log shows "Request timeout" twice with 10 and 14 second waits, then the step fails. The day before it worked.
- A commenter says it affected requests from Europe but not the US. Another, on self-hosted runners in GCP europe-west1, says the same file returned HTTP 200 from a non-EU host, and that a job hangs about 9 minutes before failing.
- Others report related timeouts on the same host that were not setup-gcloud: an Android SDK XML file via curl (one commenter says it worked with browser-like headers, and guesses a WAF problem), and `dnf` installs of Google packages. These are user reports and the cause is not confirmed anywhere in the thread.
- One commenter says switching a self-hosted apt runner to the apt repository fixed his job.
- 2026-10-14: two commenters say it works again. No one from Google or the action's maintainers comments in the thread.

## Checks I made on 2026-10-18 (evening UTC)
- An HTTP HEAD request from this sandbox to the tarball URL named in the log returned 200 in about 0.05 seconds. This is one request from one location, not a test of the EU regions. It does say the file still exists.
- Latest release of setup-gcloud is v3.0.1 (2025-08-28). I did not check what v3.0.0 vs v3.0.1 changes, and the thread does not claim the version matters.

## Practical read
- The failure was in the download of the SDK, not in the action's logic. Anything that avoids that download avoids this failure: the `skip_install` input uses the SDK already on the runner (GitHub-hosted images include it, according to the input's own description), or a runner image with the SDK preinstalled.
- Do not assume `skip_install` is right for you: it uses whatever gcloud version is on the machine. Check that it has the components you need first.

## Honest limits
- Cause unconfirmed. "Regional CDN problem" and "WAF" are commenters' guesses.
- I did not reproduce the stall, and my single successful request says nothing about EU egress.
- I did not test the apt route or `skip_install` in a workflow. I only confirmed that the input exists.
- The issue stays open, so the maintainers may consider it unresolved or just not triaged. I have no information on that.
