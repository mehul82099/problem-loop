# The editor accepts 1e-5, the player can never score it: a stringly-typed answer key in an education platform

- Source issue: https://github.com/learningequality/kolibri/issues/15677 (open, labeled bug; opened 2026-10-26)
- Verified: originating Studio PR learningequality/studio#6258 exists
- Project: learningequality/kolibri (~1.2k stars; Learning Equality's offline-first learning platform for low-connectivity schools)
- Checked: 2026-10-27 12:14 UTC

## Problem
A teacher writes a numeric-answer question in Kolibri Studio with the answer 1e-5 or 1E5. The editor validates it as a proper xsd:double and saves it. But when a learner takes the quiz in Kolibri and types the same value, it is marked wrong - every time. The QTI player stores the learner's answer as a number and then compares String(number) against the map-key text: 1e-5 is looked up as "0.00001", 1E5 as "100000", and neither string matches the stored key "1e-5" / "1E5". The two halves of the product speak the same number and different strings.

## Why it is interesting
- The bug class is a classic: validation and execution disagree about representation. The editor's validator checks "is this a valid double" (it is), the player's scorer checks "does this string equal that string" (it isn't), and nobody owns the contract in between. The member who diagnosed it in-thread pinpoints the exact mechanism - Mapping._key/_lookup doing string comparison against text that was written in scientific notation - and the fix direction is normalizing numeric map-keys before lookup rather than comparing raw text.
- The stakes are quietly high. Kolibri is deployed in offline and low-resource classrooms; a physics or chemistry teacher using scientific notation (the natural way to write very small or large quantities) gets a question that marks every correct answer wrong, with no error message and no hint that the platform - not the student - is at fault. Grading bugs erode trust in exactly the environments where a teacher has the least time to second-guess the tool.
- The process subplot is a sign of the times: the fix plan was posted by the project's automation bot (labeled as such here - a plan, not maintainer review), and minutes after the issue opened for visibility, a first-time contributor asked to be assigned and was politely bounced by a bot because the issue isn't open for community pickup. Machines triaging, machines planning, humans waiting for a green label.
- Found the way these should be found: QA testing a Studio PR noticed the player disagreed with the editor, and the issue was transferred across repos to where the bug actually lives.

## Honest limits
- The root-cause mechanism is a Kolibri member's in-thread diagnosis (with file/method names), not verified by us in source.
- The bot-authored fix plan is tooling output; no maintainer has committed to it at check time.
- Scope (which QTI numeric types/notations are affected beyond 1e-5/1E5) is untested.
- Issue state may have changed since 12:14 UTC.
