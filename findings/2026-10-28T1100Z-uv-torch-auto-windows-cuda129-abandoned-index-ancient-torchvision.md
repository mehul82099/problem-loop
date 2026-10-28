# The resolver found a version: how `--torch-backend=auto` picks a 2018 torchvision for your RTX card

- Source issue: https://github.com/astral-sh/uv/issues/22965 (open; opened 2026-10-28)
- Project: astral-sh/uv (~91k stars)
- Checked: 2026-10-28 11:15 UTC

## Problem
On Windows with a CUDA 12.x driver, `uv pip install torch torchvision --torch-backend=auto` silently resolves `torch 2.9.0+cu129` with `torchvision 0.2.0` - a wheel from 2018. Install succeeds, `import torchvision` works, basic transforms work, and the failure arrives later at runtime: ImportError on modern symbols (InterpolationMode, efficientnet_b0, torchvision.ops). Cause, fully traced by the reporter: uv's auto backend tries the cu129 index first on Windows; that index stopped getting updates at torch 2.9.0/torchvision 0.23.0 (PyTorch's RELEASE.md lists CUDA 12.9 as experimental, not listed for 2.9+); and every PyTorch index still hosts the ancient pure-Python torchvision 0.1.6/0.2.0 wheels, which declare no tight torch dependency - so 0.2.0 is the first "compatible" torchvision candidate on the first-priority index. Linux with the same driver is unaffected (its cu129 index has matching pairs), as is a CUDA 13 driver (which routes to cu132 and resolves modern torch 2.14.1/torchvision 0.29.1).

## Why it is interesting
- Constraint solving without a sanity floor. The resolver did everything correctly: it found a torchvision whose declared requirements are satisfied by torch 2.9.0. The problem is that "correct" includes a 2018 wheel whose unbounded dependency declaration means it matches everything forever. Version selection has no concept of "implausibly old for the ecosystem," so abandoned-index + permissive-legacy-wheel = a formally valid, practically broken environment.
- The delay before failure is the dangerous part. This is not an install-time error you fix immediately; it is an environment that imports and runs until someone touches a symbol added in the last seven years. CI smoke tests that import torchvision pass. The bill arrives in production notebooks and training jobs.
- It is really a supply-chain-hygiene story: two upstream decisions (an experimental CUDA version that was later abandoned on one platform, and 2018 wheels left installable on every index) combine into a trap that only one resolver on one OS with one driver range falls into. Nobody made an error; the system produced nonsense anyway.
- The workaround exists and is documented in the thread (`--index-strategy unsafe-best-match`, which compares versions across indexes instead of preferring the first index), but the default path remains broken at check time. Also notable: pip on the same index picks 0.1.6 - differently broken, equally ancient.

## Honest limits
- Single reporter, no maintainer response at check time.
- Root cause is the reporter's tracing (backend.rs order, index contents, PyTorch RELEASE.md); specific and verifiable, but not confirmed by Astral.
- Affected set: Windows + CUDA 12.x driver range (>=528.33, <580) + unpinned torch/torchvision; pinned users and other platforms are unaffected per the report.
- Issue state may have changed since 11:15 UTC.
