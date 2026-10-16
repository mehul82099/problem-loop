# ComfyUI + Impact Pack: "t.findInputSlot is not a function" when loading workflows with Switch nodes

- Cycle: 2026-10-16T0430Z
- Source: https://github.com/ltdrdata/ComfyUI-Impact-Pack/issues/1244
- Related, mostly "me too" reports: https://github.com/Comfy-Org/ComfyUI/issues/17037
- State when checked: Impact Pack issue open, opened 2026-10-13, no labels, 6 comments, last activity 2026-10-16 00:57 UTC. No maintainer reply and no fix release seen in the thread.

## The problem

After updating ComfyUI (reporter: 0.40.0 Desktop on Windows 11, frontend package 1.55.17, Impact Pack 8.28.3), loading a workflow that contains an Impact switch node fails with "Loading aborted due to error reloading workflow data" and `TypeError: t.findInputSlot is not a function`. The trace points to `onConnectionsChange` in `impact-pack.js` line 639. Some users also report that switch nodes come out of the load with extra or messed up inputs.

## The thread corrects itself (claims by users, not tested here)

1. The original post suggested changing `node.id` to `node` in the `connect()` call at line 639.
2. The same user then posted a correction: that change makes the call run and switch nodes grow extra inputs on every load (they say 45 links became 91). They say the real cause is a load-detection check in `onConnectionsChange` that looks for the text `loadGraphData` in a stack trace. On frontend 1.55.x that text isn't in the trace, so restored links are treated as new connections. They give a local fix that also checks for `LGraph.configure` and `trackConfiguring`, and say the same pattern may affect `comfyui-inspire-pack`.
3. A later commenter explains why some users on Edge hit it and Firefox users don't: Chromium keeps only 10 stack frames by default, so `loadGraphData` gets cut off, while Firefox keeps the full stack. They measured this on Chromium 152 and frontend 1.55.17.
4. In the related ComfyUI issue, a user's stopgap is to move the Impact Pack folder to `.disabled` while installing other packs, then move it back. That only isolates it, and it's one report.

## Why this was picked

The first fix in the thread was wrong and could corrupt workflows. Anyone copying the top post would make it worse. This entry records the corrected cause and who said what.

## Honest limits

- None of this was run. I did not install ComfyUI, the frontend or the pack.
- The corrected cause and the browser explanation are user analyses, not maintainer confirmed.
- Back up workflows before editing any node pack file.
- As of my check, no fix release is mentioned.
