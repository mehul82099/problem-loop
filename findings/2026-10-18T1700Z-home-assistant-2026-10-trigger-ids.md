# Home Assistant 2026.10: the new trigger selector hides your custom trigger IDs (frontend#54721)

- Source: https://github.com/home-assistant/frontend/issues/54721 "Custom trigger IDs are not displayed in the new 2026.10 trigger selector" (opened 2026-10-08, open, 19 comments, many thumbs-up; last comment 2026-10-18; it carries the milestone "2026.10", assigned on 2026-10-08 by a GitHub user named silamon, whose role I did not verify)
- Checked by API on 2026-10-18:
  - The pull request the reporter blames: https://github.com/home-assistant/frontend/pull/54130 "Add trigger ID auto-generation and selection" (merged 2026-09-15 by jpbede)
  - Its roadmap item: https://github.com/OpenHomeFoundation/roadmap/issues/66 "Improve referencing triggers in automation conditions and actions" (open)
- The reporter links the release blog (https://www.home-assistant.io/blog/2026/10/07/release-202610/, the page loads) and calls the section "The best automation feature you never used". I did not extract that section, so I do not quote it.

## What changed, from the pull request description
- The "Triggered by" condition now lets you pick triggers directly. A trigger without an ID gets an automatic one, `generated-` plus a random id, only when it is selected.
- The manual trigger-ID controls are removed from the visual editor. Explicit IDs still work in YAML, and IDs without the generated prefix are kept.
- If an automation has several triggers that share one ID, the editor shows a warning and an optional repair. After confirmation, each trigger gets a unique ID and conditions that referenced the old ID expand to include all of them, which keeps the "any of these triggers" behaviour. The dialog says templates or action data that use `trigger.id` directly may need manual updates, because those are not rewritten.

## What the reporter and commenters say (user reports, not confirmed by the project)
- The reporter, who updated from 2026.9.4 to 2026.10.0, says the picker now shows only generated IDs and ignores his descriptive manual ones. He asks that existing manual IDs be shown and the ID editor be brought back.
- Many commenters say shared IDs are how they group triggers, for example several motion sensors that mean "motion", or sensors mapped to one name for a script. They say the warning and repair rewrite their setups, and the "Triggered by" options become hard to tell apart (one says a choose action now shows `generated-` strings instead of names). Several say they are holding off upgrading to 2026.10 because of this, and others say they upgraded and regret it.
- Suggestions: bring back the ID menu, let the user choose naming for generated IDs, drop the duplicate-ID check, or add named "trigger groups" (a commenter's idea, and another commenter calls it over-engineering).
- On 2026-10-18 one commenter asks for an official statement. Every comment I read is from a non-member, and I found no maintainer reply in the thread.

## What this means if you use Home Assistant
- The change is in the visual editor. The PR says explicit IDs stay supported in YAML. I did not test whether an existing automation with shared IDs keeps running after the update, so this finding does not say it breaks or not.
- If you rely on custom or shared trigger IDs, check the release notes and this thread before updating, take a backup first, and do not accept the editor's "fix" prompt on automations you want to keep unchanged until you understand what it rewrites. That last point is my reading of the PR text, not project guidance.

## Honest limits
- I did not install 2026.10 or open the editor. Everything about editor behaviour comes from the PR description and user comments.
- The thread has no maintainer response yet. The milestone label shows the issue is on the 2026.10 milestone, which does not tell me if a change is planned.
- I did not read the community forum posts the reporter links.
