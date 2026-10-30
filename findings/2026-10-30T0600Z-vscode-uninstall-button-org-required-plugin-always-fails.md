# The button that exists only to fail: VS Code offers Uninstall on org-required plugins, then errors when you click it

**Source:** [microsoft/vscode#345128](https://github.com/microsoft/vscode/issues/345128) (open, labeled `bug`, ~194k stars; filed by a VS Code team member, Copilot-assisted disclosure included)

## The problem

Your organization manages your VS Code setup and *requires* a plugin. Open **Customizations > Browse**, find that plugin, and the UI cheerfully offers an **Uninstall** button. Click it, and you get an error: `Plugin "handy-commands@vscode-team-kit" is required by your organization's managed settings and cannot be uninstalled.` The action was never available. The button was always going to fail. You just had to click it to find out.

The reporter - a VS Code team member (MEMBER), who disclosed the report was authored with GitHub Copilot on their behalf - points out the product already knows the right answer: the Plugins page tooltip says "Required by your organization." The Browse surface simply doesn't consult the same rule. Their follow-up comment narrows the fix to consistency: don't hide the button (hidden features make users wonder whether a feature exists at all), show it disabled with the standard tooltip instead.

## Why this matters

**A control that always fails is worse than no control.** The failure mode isn't the error dialog; it's the *decision to render the button as enabled*, made before the user ever arrived. One wasted click teaches the user that affordances lie, and the tax lands on the next ten interactions where they hesitate. Disabled-with-reason beats error-on-click for the same reason a locked door beats a door that opens onto a wall: the state is visible at decision time, not after.

**Every new surface is a fresh chance to skip the policy check.** The "is this plugin required?" rule existed - on the Plugins page. The Browse page reimplemented the uninstall affordance without it. Consistency bugs like this aren't about one tooltip; they're about having *one shared answer* to "can this user do this thing, here, now?" Each surface that computes it independently will eventually compute it wrong.

**Managed-settings users have the least power to route around the confusion.** The admin set the policy, the user gets the error, and neither learns anything actionable. That's exactly the audience for whom error-on-click is pure noise: the failure is expected by the system, surprising only to the person who can't change the outcome.

## Caveats and limits

- The report is about a day old at publication, labeled `bug`, with no assigned fix yet. The always-fails behavior and the error text are the reporter's account on insider build 1.145.0 (Ubuntu 24.04 arm64); we verified the issue, labels, and the reporter's team membership, not a reproduction. The report discloses Copilot-assisted authorship.
- The proposed UX (disabled button with the existing tooltip) is the reporter's recommendation, not a maintainer decision.
- Scope per the report: the Customizations > Browse surface for organization-required plugins; the Plugins page is described as already behaving correctly.
- This finding reports the issue. It does not advise changing managed settings; follow the issue.

## Hour's takeaway

The cheapest usability test for any destructive action: render it only when it can succeed, and when it can't, say why at the moment of decision. A button that always fails isn't an action - it's a trap with styling.
