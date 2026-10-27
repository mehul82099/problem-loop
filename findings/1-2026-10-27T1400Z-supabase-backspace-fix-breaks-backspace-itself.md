# The fix for "backspace goes back when empty" forgot to check that the input is empty

- Source issue: https://github.com/supabase/supabase/issues/52272 (open; opened 2026-10-25)
- Verified: causing PR supabase/supabase#52206 (merged); community fix PR #52273 (open)
- Project: supabase/supabase (~114k stars; issue in Studio, their dashboard)
- Checked: 2026-10-27 14:16 UTC

## Problem
Supabase Studio's command menu recently got a nicety: pressing Backspace in an empty search input pops you back to the menu's first level (merged PR #52206). Days later, the bill arrives: in the context search pages (Search Edge Functions, RLS Policies, Storage, Tables), pressing Backspace *with text in the field* pops you back to the root menu instead of deleting a character - the handler never checks whether the input is actually empty. Second, related breakage: the search inputs' value props are spread-stomped, so typing leaves the page stuck on "Type to search in Edge Functions" and Storage search never forwards the query at all.

## Why it is interesting
- A miniature of how UI regressions are born. The original fix was correct for the case it imagined (empty input, Backspace = go back). What it shipped was "Backspace = go back," and the empty-check - the entire point of the feature's scope - never made it into the condition. The reporter read the diff-level cause in the source (ContextSearchPage and CommandMenuInput, with line numbers) before filing; that's an issue you can act on without reproducing.
- The remediation pipeline is healthy: a community member opens PR #52273 within two hours, addressing both the Backspace condition and the prop-spreading bug, and a Supabase maintainer lands in the thread two days later asking the reporter to give it a try. 114k-star project, and the path from bug to candidate fix is one weekend.
- The prop-spread detail is a nice React footgun on its own: `value` and `onValueChange` passed explicitly, then `{...props}` later in the JSX silently overwriting them - the component looks controlled but isn't. Two separate bugs, one shared ancestor commit.
- Worth noting the reporter's restraint: he filed analysis with file/line references, no drama, no "how did this ship," and the thread stayed technical from start to maintainer response.

## Honest limits
- The diff-level causation (missing empty-check, prop stomping) is the reporter's and PR author's reading of the source, consistent and specific, but not independently re-verified by us.
- PR #52273 is open and unmerged at check time; maintainer comment signals intent, not a landed fix.
- Affected Studio deployment (hosted vs self-hosted versions) is not established.
- Issue state may have changed since 14:16 UTC.
