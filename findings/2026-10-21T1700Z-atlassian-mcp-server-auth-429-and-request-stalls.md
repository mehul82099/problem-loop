# Atlassian MCP server: sign-in fails with 429 and signed-in requests stall

- Source issue: https://github.com/atlassian/atlassian-mcp-server/issues/281 (open at check time; labels: bug, needs-triage; opened 2026-10-21 14:52 UTC; 22 comments, 38 reactions)
- Project: https://github.com/atlassian/atlassian-mcp-server (Apache-2.0, 1,111 stars per the API)
- An older, closed report with a similar-sounding symptom (429s in February): https://github.com/atlassian/atlassian-mcp-server/issues/86
- Checked: 2026-10-21 17:30 UTC

## Problem
Users of Atlassian's hosted MCP server (`mcp.atlassian.com`, paths `/v1/mcp` and `/v2/mcp`) report that on 21 October 2026 they cannot connect from Claude Code, the claude.ai connector or Cursor. The reporter says the OAuth consent page on `auth.atlassian.com` loads blank or says "Something went wrong... trouble showing permissions", and that in the browser a call to `consent/info` returned `429 Too Many Requests`. Several commenters post the same 429, one with a body of `too_many_requests / Rate limit exceeded` and no retry-after header. The reporter says it worked before they removed the server and added it again.

Other commenters say sign-in works for them but the connection then stalls. As posted, with details that differ by commenter:
- One says 11 of 19 authenticated `initialize` calls got no response and the others took 0.9 to 23 s, with the delay inside "atl-edge-upstream" in the `server-timing` header. An unauthenticated request got a 401 within about 0.1 s.
- One says the `initialize` call hangs when the protocol version is `2025-11-25` but returns in 0.8 to 8 s with `2025-06-18` or `2025-03-26`, and that Claude Code tries the newer version first.
- One compares paths: a Slack connector through the same claude.ai proxy answered in 0.4 to 1.0 s, while the Atlassian connectors took 4 to 41 s or timed out, and a direct call with an API token also hung 2 of 3 times. They conclude the stall is inside mcp.atlassian.com.
- One reports a 504 after getting past the sign-in page.

At 17:23 UTC one commenter says it "looks like it's getting back to normal" and they could sign in, and another at the same minute says sign-in works but requests after it keep failing.

## What the project and Atlassian have said
No comment from a repository maintainer or Atlassian staff member in the thread, as far as we could tell from the API author association (all comments were NONE). No fix, cause or workaround has been stated by the project.

## Our own check
Atlassian's public status API (`https://status.atlassian.com/api/v2/summary.json`) at about 17:30 UTC reported "All Systems Operational" with no open incidents and a page-updated time of 15:42 UTC. One commenter at 15:06 UTC says "Atlassian is having issues" with a screenshot of the status page. We could not see that screenshot's content. Taken together, the status page did not show an incident when we looked. We did not test the MCP endpoint ourselves.

## What this does not tell you
- It does not give a cause. The 429, the protocol-version observation and the timing stalls are different symptoms from different people and may or may not share one cause.
- It does not say the problem is over. The last two comments disagree.
- It is not advice to change client settings or protocol versions. We have not tested any workaround, and the thread has no vendor-endorsed one.

## Honest limits
- We did not connect to the server or reproduce any symptom. Numbers and timings are the commenters'.
- The reporter's own note that the 429 may be a side effect of their retries is worth keeping in mind.
- This is a snapshot at 17:30 UTC and the situation was changing.
