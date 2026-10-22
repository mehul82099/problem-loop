# Atlassian VS Code extension: Bitbucket Cloud sign-in fails with "Invalid client_id"

- Source issue: https://github.com/atlassian/atlascode/issues/1954 (open at check time; no labels; opened 2026-10-21 19:13 UTC; 5 comments from other users, none from the project)
- Project: https://github.com/atlassian/atlascode (Apache-2.0, 134 stars per the API). Newest releases listed by the API are nightly builds, the latest `v4.1.202-nightly` (2026-10-16)
- Bitbucket status page at check time (API summary): "All Systems Operational"
- Checked: 2026-10-22 17:50 UTC

## Problem
The reporter says that signing in to Bitbucket Cloud from the extension fails. Bitbucket's OAuth page shows "Invalid client_id - This integration is misconfigured. Contact the vendor for assistance." They say:
- In VS Code on Windows, "Login with OAuth" fails with that page.
- In a Dev Container the extension offers only "Login with API Token", and entering `https://bitbucket.org` switches it back to OAuth, which fails the same way. They say the code that picks the form returns "None" for Bitbucket with a non-custom URL, so no token form shows.
- Both 4.0.32 (stable) and 4.1.202 (pre-release) send the same Bitbucket Cloud client ID, so switching versions does not help. Jira Cloud sign-in works in the same setup.
- They want OAuth fixed, or an API-token login for Bitbucket Cloud, as Jira Cloud has.

## Who else sees it
Four commenters over 2026-10-22 say they get the same error: on Windows 11 (VS Code 1.143.0, both extension versions), macOS, and Ubuntu. One of them notes that Jira Cloud OAuth works for them. This points to something on the OAuth app side, but none of this tells us where the fault lies.

## What we checked ourselves
- The Bitbucket status page API reported all systems operational. That says nothing about a single OAuth consumer, so it neither supports nor contradicts the report.
- We could not read the extension's source for the client ID: the code search needed a sign-in, and a direct read of one source file did not find the string. We therefore do not confirm the reporter's claim about the client ID or the form-selection code.
- Two older Bitbucket authentication issues exist (#1939 and #1942, from September 2026). Their symptoms differ ("Credentials refused"), so we do not treat them as the same problem.

## What this does not tell you
- No one from the project has replied, and no cause is confirmed. "Invalid client_id" on an OAuth page could mean the app registration was changed or removed, but that is only a general reading of the message, not something the thread establishes.
- We do not suggest sign-in workarounds. In particular, do not create your own OAuth consumer, or enter tokens in unfamiliar forms, on the strength of this thread.
- Whether non-VS Code Atlassian tools are affected is not covered.

## Honest limits
- We did not sign in to Bitbucket or run the extension.
- The reporter's technical details are unverified by us.
- State may have changed since 17:50 UTC.
