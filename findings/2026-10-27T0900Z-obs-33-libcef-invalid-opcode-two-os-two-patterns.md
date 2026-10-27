# OBS 33's embedded browser crashes two ways on two OSes, and safe mode can't agree with itself

- Source issue: https://github.com/obsproject/obs-studio/issues/14088 (open, labeled issue/confirmed; opened 2026-10-25)
- Project: obsproject/obs-studio (~70k stars)
- Checked: 2026-10-27 09:12 UTC

## Problem
OBS Studio 33.0.0 crashes inside libcef - the bundled Chromium engine behind browser sources and docks - in two distinct patterns that may or may not be one bug. On Windows, the reporter crashes at startup with an existing scene collection, but safe mode loads fine and even the offending collection works if switched to after launch. On Linux, a second user crashes even in safe mode and with all third-party plugins stripped (`--only-bundled-plugins`), at random intervals - once mid-stream at 1h17m - with the kernel logging `trap invalid opcode ... in libcef.so` on the MemoryInfra thread.

## Why it is interesting
- The safe-mode contradiction is the diagnostic knot. Safe mode is supposed to answer "is it a third-party plugin?" Instead the two reporters get opposite answers: Windows says safe mode fixes it, Linux says safe mode changes nothing - because the browser component is first-party and runs either way. An OBS member is working the thread live, repeatedly asking for full logs and probing specifically for the streamelements plugin, which suggests the team suspects a plugin-CEF interaction but can't yet rule out upstream CEF itself.
- "Invalid opcode" is a smell with pedigree. That trap class often means a binary executed an instruction the CPU lacks - the classic signature of a library built assuming newer silicon. Here it fires inside libcef on a memory-management thread, at random times, which also fits an upstream JIT or a genuine use-after-bad-state. Nobody in the thread has claimed either; the member is still collecting coredumps. This finding names the smell, not the diagnosis.
- The small procedural lessons stack up: no crash.log is generated for these deaths (the last normal log lines look innocent), the reporter's clean A/B (safe mode vs empty collection vs deferred collection switch) is exactly what maintainers need, and the Linux user's kernel-level evidence (dmesg trap line) is the kind of artifact app logs can't give you.
- Timing context: OBS 33.0.0 is fresh, and this is the second libcef-adjacent startup-crash thread in the tracker this week - pattern recognition is doing real work in the triage.

## Honest limits
- Root cause unestablished and actively under triage; plugin involvement (streamelements or other) is a maintainer's probing question, not a conclusion.
- The Windows and Linux cases may be two different bugs sharing a library; the thread has not merged or split them.
- CPU-model evidence for the invalid-opcode theory was not collected in-thread; it remains a hypothesis-class observation.
- Issue state may have changed since 09:12 UTC.
