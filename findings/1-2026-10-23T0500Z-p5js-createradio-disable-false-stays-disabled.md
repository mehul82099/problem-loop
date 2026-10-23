# p5.js 2.x: `createRadio().disable(false)` never re-enables the radio inputs

- Source issue: https://github.com/processing/p5.js/issues/9316 (open at check time; labels "Area:DOM", "Good First Issue", "p5.js 2.0+"; opened 2026-10-22 07:04 UTC; 5 comments)
- Code read on `main`: https://github.com/processing/p5.js/blob/main/src/dom/dom.js (`self.disable` at lines 1546 to 1550 in our read)
- HTML reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/disabled
- Project: https://github.com/processing/p5.js (LGPL-2.1, about 24k stars per the API); releases per the API: v2.3.4 (2026-09-25) and v2.4.0-rc.1 (2026-10-20, a pre-release)
- Checked: 2026-10-23 05:45 UTC

## Problem
The reporter says that in p5.js 2.3.4, after `radio.disable(true)`, calling `radio.disable(false)` leaves the radio inputs disabled. Their sketch shows the inputs still have `disabled === true` and keep a `disabled` attribute with the string value `"false"`. They tested in Firefox 157 on Fedora, in the p5.js web editor.

## Why, per the thread and the source
- A commenter traced it to `self.disable` in `src/dom/dom.js`, which runs `radioInput.setAttribute('disabled', shouldDisable)` for each input. With `false`, that sets the attribute to the string `"false"` rather than removing it.
- We read `main` and confirmed this: lines 1546 to 1550 loop over the radio inputs and call `setAttribute('disabled', shouldDisable)`. There is no `removeAttribute` path.
- This matches how HTML boolean attributes work. MDN describes `disabled` as a Boolean attribute: the control is disabled when the attribute is present, whatever its value. So `disabled="false"` still disables the input.
- The same commenter says they have a fix (set the `disabled` DOM property with a Boolean and remove the attribute on `false`) plus unit tests, with all 118 DOM tests and the linter passing locally. No pull request was open when we checked; the issue is labeled "Good First Issue" and a maintainer-side reply asked them to wait for assignment before opening one.

## What this does not tell you
- There is no merged fix and no released version with one. The commenter's fix and test results are their own report; we did not see the code or run the tests.
- We confirmed the suspect code is on `main`, but did not check whether v2.4.0-rc.1 behaves differently at runtime.
- We did not run the reporter's sketch.

## Honest limits
- We read the issue, the cited source on `main`, the MDN reference, and the release list. No code was run.
- Issue state may have changed since 05:45 UTC.
