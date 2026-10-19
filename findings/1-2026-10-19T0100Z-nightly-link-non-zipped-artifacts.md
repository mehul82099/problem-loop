# nightly.link and GitHub's non-zipped artifacts: why a download link still needs ".zip" (nightly.link#88)

- Source: https://github.com/oprypin/nightly.link/issues/88 "Support non-zipped artifacts". Opened 2026-02-27, open, 24 comments, 18 reactions on the post, last comment 2026-10-19 (a prototype offered, see below).
- GitHub announcement: https://github.blog/changelog/2026-02-26-github-actions-now-supports-uploading-and-downloading-non-zipped-artifacts/ (dated 2026-02-26, read 2026-10-19).
- Artifact REST docs the owner cites: https://docs.github.com/en/rest/actions/artifacts#download-an-artifact

## Background
nightly.link is a third-party site that gives public download links for GitHub Actions build artifacts, so people without a GitHub account can fetch them. Until February 2026, every artifact was a zip. GitHub's announcement says actions can now upload and download single files without zipping, and browsers can download or even display them directly.

## What the thread says
- The reporter (2026-02-27) says nightly.link URLs for such artifacts only work if they end in `.exe.zip`, which is misleading for a plain `.exe`.
- The owner (oprypin) says the downloads did work briefly and by themselves, but he then disabled them on purpose. His stated reasons: the REST API was not updated and still offers only a `.../zip` download path, and the `.zip` ending only shows up in the ephemeral redirect URL, which is undocumented. A commenter notes GitHub's own toolkit decides by the content type header or a `.zip` ending.
- On 2026-07-02 the owner says his biggest worry is malware: Google Search used to send him "Malicious or unwanted software detected" emails about the site, and he does not want to allow "even more direct" linking to executables.
- Users ask for support anyway. Reasons given: tar.gz and 7z keep permissions or compress better, and Minecraft mod `.jar` files and installers are already archives. Suggestions: an `archive=false` query parameter, a star-count threshold, a VirusTotal scan, at least a clear error message. Others push back on each (for example that star counts are easy to fake).
- The site now shows a message that non-zipped artifacts are unsupported, according to one user's screenshot. I did not open the site.
- 2026-10-19: a commenter (yzhou216) says he has a prototype and asks whether to open a pull request. His comment says: GitHub serves `.html`, `.png` and `.pdf` artifacts inline, which cannot be changed without proxying because it is in the signed redirect URL, so his version never redirects to those types and only allows archive types (`.tar.gz`, `.7z`, `.xz` and so on). `.zip` links still serve only real zips. He says the patch was assisted by an LLM and reviewed by him. There is no owner reply yet.

## What can be said
- Two parts of the problem are separate: GitHub changed what artifacts are, but its documented API still describes zip downloads, and a third party that wants to redirect to the new files relies on an undocumented redirect URL and a content-type hint.
- The owner's blocker is a safety and abuse worry, not just effort. Whether archives only is acceptable to him is not decided in the thread.
- For now, per the thread, if you need a link for a non-zip file, the workarounds are users' own: put the file in a zip, use a release, or use GitHub's own artifact link (needs sign-in).

## Honest limits
- I did not test nightly.link, the prototype, or GitHub's redirect behavior. The inline versus attachment claim comes from the prototype author's comment.
- I did not read the prototype code or verify that "archives are no riskier than zips".
- The malware concern is the owner's own account, and I did not check the emails.
