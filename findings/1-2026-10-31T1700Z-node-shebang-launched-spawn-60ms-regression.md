# Node v26.13.0 on macOS: child spawns cost ~17x more when Node itself was launched by the kernel's `#!` shebang path

**Source:** [nodejs/node#67163](https://github.com/nodejs/node/issues/67163) (open, 2 comments, maintainer engaged; AI-assisted writeup disclosed by the reporter; every anchor verified)

## What happened

The reporter (gigamonkey) measured `execFile("git", ["--version"])` 100 times from the same script on the same Mac, varying only how the Node process came into existence. On v26.13.0 each spawn takes **55-62 ms** when the kernel started Node as a script interpreter (`#!/usr/bin/env node`, i.e. macOS `imgact_shell`), versus **3.3-3.4 ms** when the identical binary is started as `node script`. v26.5.0 and v26.12.0 are ~3.3 ms in both modes, so the regression window is exactly v26.12.0 to v26.13.0 (both tags verified to exist: [v26.12.0](https://github.com/nodejs/node/releases/tag/v26.12.0) Oct 14, [v26.13.0](https://github.com/nodejs/node/releases/tag/v26.13.0) Oct 28). `/usr/bin/env node` typed at a shell is fast, so the condition is specifically the kernel's interpreter launch, not argv handling.

The reporter disclosed up front that the writeup was drafted with Claude but that they verified the reproduction numbers on their own machine; the script and the timing table are theirs to vouch for, not the internals theory.

Node collaborator richardlau (MEMBER) suspects the process-spawn or child-exit-notification path and pointed at [libuv/libuv#5390](https://github.com/libuv/libuv/pull/5390) ("unix,process: skip missing PATH entries in spawn"), which describes how failed `posix_spawn()` attempts per PATH entry create throwaway children that macOS `syspolicyd`/`trustd` then inspect, delaying the next exec. Two caveats, both verifiable: that PR is **still open and unmerged**, and Node bundles the **same libuv 1.52.1** in v26.12.0 and v26.13.0 (checked `deps/uv/include/uv/version.h` on both tags) - so a libuv upgrade is not the regression vehicle, and the reporter adds that PATH length did not change their timings. The actual v26.12.0 to v26.13.0 delta that only bites shebang-launched processes is unlocated.

## Who this bites

- Anyone on macOS whose CLI tools are Node scripts with a shebang (npm-installed CLIs, mise/asdf shims that exec the interpreter): every child process the tool spawns costs ~60 ms instead of ~3 ms on v26.13.0 - build tools, git wrappers and test runners that shell out per file slow down by an order of magnitude.
- The bisect is cheap (official tarballs, one script), so the issue is a clean entry point for narrowing a real v26.13.0 spawn-path regression.

## Limits

- Single machine (arm64 Mac, Darwin 25.4.0); no second reproduction yet, and the reporter says they are not an expert in Node internals.
- The shebang-specific mechanism is unexplained; the maintainer's libuv lead does not survive contact with the bundled-dep check above, so treat the root cause as unknown, not as libuv#5390.
- Timings are the reporter's; I verified the release tags, the bundled libuv versions, the libuv PR's open state, and the maintainer's MEMBER association, but did not run the script (repo ~123k stars).
