# FrankenPHP 1.13.2 static binary: SIGILL in `hash('sha256')` on some x86-64 CPUs

- Source issue: https://github.com/php/frankenphp/issues/2743 (open at check time; label: bug; opened 2026-10-21 19:18 UTC; 4 comments)
- A second report, now closed with no comments: https://github.com/php/frankenphp/issues/2744 (title: "1.13.2 static binaries require AVX-512 -> SIGILL on CPUs without it (DigitalOcean)")
- Release: https://github.com/php/frankenphp/releases/tag/v1.13.2 (published 2026-10-21 18:19 UTC; its notes call it a security release that picks up the PHP fixes from 21 October)
- Project: https://github.com/php/frankenphp (MIT, 11,441 stars per the API)
- Checked: 2026-10-22 00:35 UTC

## Problem
FrankenPHP is a PHP application server built on Caddy. The reporter says the `frankenphp-linux-x86_64` static binary from v1.13.2 (PHP 8.5.12) dies with SIGILL (illegal instruction, exit 132) as soon as PHP calls `hash('sha256', ...)` on a CPU that lacks the SHA extensions (`sha_ni`). v1.13.1 works on the same machine. Their guess is that the SHA-256 code uses SHA-NI without a runtime check since the move to static-php-cli v3, and they note the build settings show the zig compiler. They report a Xeon Gold 6240R (Cascade Lake) VM with no `sha_ni`. In worker mode (Laravel Octane) every PHP thread dies on the first request, and the service crash-loops.

## What others report
- A second user, on a KVM VPS (Cascade Lake, no `sha_ni`), says the whole process dies on the first request that touches `hash('sha256')`, which in Laravel is nearly every page. They say `frankenphp validate` passes and a basic health endpoint returns 200, so an upgrade plus health check can pass before real traffic kills the server.
- A DigitalOcean user (CPU without `sha_ni` and without AVX-512) and a Google Cloud user (Xeon at 2.2 GHz, AVX2, no `sha_ni`, no AVX-512) report the same crash-loop after upgrading, which they say argues against AVX-512 being the trigger.
- A fifth user on AWS reports a mixed result: a Cascade Lake instance crashes, but an older Broadwell instance (AVX2, no `sha_ni`, no AVX-512) works. They say that conflicts with "any CPU without SHA-NI", and they run a self-built 1.13.1 instead.
- Four of the commenters say the `frankenphp-linux-x86_64-gnu` asset from the same release works on their machines. The AWS commenter says they do not see it as a safe workaround for every host, citing the other issue. We saw the release page list four x86-64 Linux assets: `frankenphp-linux-x86_64`, `-debug`, `-gnu` and `-mimalloc`.

The trigger is therefore not pinned down. The reports agree on "some CPUs without SHA-NI" and disagree on whether AVX-512 matters. These are user reports and we did not verify any CPU flag.

## What the project has said
We found no comment from a maintainer on either issue (all comment authors were labeled NONE by the API). Issue #2744 was closed with no comments, and we could not tell why. We saw no linked fix and no newer release than v1.13.2 at check time.

## What this means for readers
- If you run the static `frankenphp-linux-x86_64` binary on x86-64 servers, v1.13.2 may crash on the first request that hashes with SHA-256 on some CPUs, per these reports. A passing `validate` or health check may not catch it, since several users say theirs did not.
- The release is the one that carries the 21 October PHP security fixes, so people are likely to feel pressure to move to it. We make no recommendation about which build to run. Test the exact binary on the same CPU type with a call that uses `hash('sha256')` before putting it in front of traffic.

## Honest limits
- We did not run FrankenPHP, test any CPU, or inspect the binaries. All of the CPU and crash details are from the reporters.
- We did not verify the cause. The compiler and static-php-cli remarks come from the reporter's guess.
- The situation may have changed since 00:35 UTC.
