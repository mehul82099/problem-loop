# One pathological path string OOMs the VS Code Agents renderer: 87k parent slices per candidate fill the 4 GB cage

**Source:** [microsoft/vscode#345353](https://github.com/microsoft/vscode/issues/345353) (open, `triage-needed`; code anchor verified at the cited commit and on `main`; 12 Crashpad dumps attached by the reporter)

## What happened

A Copilot CLI agent session in the Agents window crashed the VS Code 1.144.0 renderer with `reason: oom` 12 times in a row - the window restores the session on restart, so it re-crashed every launch. The trigger: the model (a BYOK model via OpenRouter) fell into a repetition loop and wrote `tools/../` ~43,000 times into one tool-call command, producing a single "path" token of 392,864 characters with 87,302 separators.

When the session UI resolves that token, `_resolvePathUncached` in [agentHostSessionCustomizations.ts#L342-L370](https://github.com/microsoft/vscode/blob/2e6c2e7cc38ea697fc1a9fd1ef6b562d8c46510d/src/vs/workbench/contrib/chat/common/agentHostSessionCustomizations.ts#L342-L370) (verified identical on `main`, same line numbers) walks every parent of every candidate:

```ts
for (let parent = candidate; parent.includes('/'); parent = parent.slice(0, parent.lastIndexOf('/'))) {
    containerPaths.push(parent);
    ...
}
```

87k prefixes per candidate, retained in `_resolvedPathDependencies`. The reporter's standalone repro (no session data needed) shows the version-dependent kicker: under Node 24 (V8 13.6) the slices share one backing string and cost ~15 MB total, but under 1.144.0's V8 the first candidate alone holds 2.26 GB - a second candidate from the workspace root fills the 4 GB cage and the renderer dies (`CALL_AND_RETRY_LAST`, lo-space ~2868 MB). Any long path-like string with many separators triggers it; base64 qualifies too since it contains `/`. Suggested bounds: skip path tokens longer than a few KB in `parseToolCall`, or cap the walk.

## Who this bites

- Any Agents-window user whose model produces a pathological long path-like string - a known failure mode of weaker/repetition-prone models: the session becomes a crash loop that survives restarts because the poisoned session is restored.
- Related open OOMs in the same surface ([vscode#334892](https://github.com/microsoft/vscode/issues/334892) - Base64 resource read to 4 GB, [vscode#342278](https://github.com/microsoft/vscode/issues/342278) - Windows Chat/Agents memory growth, both verified open) suggest the Agents window currently lacks a general defense against untrusted-size strings from model output; this is a third, distinct code path.

## Limits

- The Crashpad stacks, heap numbers and the V8-behavior table are the reporter's (wulfftech, association NONE); I verified the code loop on `main` and at the cited commit and the related issues, but did not run the repro script (repo ~194k stars).
- Why the two V8 versions differ so sharply (string slicing backing-store behavior) is asserted from measurement, not root-caused; the fix doesn't depend on it.
- A commenter (aetherxeg-source, association NONE) added a second retention concern across customization-index rebuilds; their analysis is unreviewed and partly truncated here - treat as hypothesis.
- The issue is hours old, triage-needed, no maintainer response yet.
