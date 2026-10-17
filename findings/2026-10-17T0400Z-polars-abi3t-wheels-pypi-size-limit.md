# Polars free-threaded wheels are waiting on PyPI project size limits

- Source: https://github.com/pola-rs/polars/issues/27955 "Upload abi3.abi3t wheels" (open, label `enhancement`, opened 2026-06-12, last comment 2026-10-17)
- Blocking request, state checked through the GitHub API on 2026-10-17: https://github.com/pypi/support/issues/11990 "Project Limit Request: polars-runtime-compat - 50 GB" (open). Two sibling requests, https://github.com/pypi/support/issues/11991 (polars-runtime-32) and https://github.com/pypi/support/issues/11992 (polars-runtime-64), are also open.
- Other links verified: conda-forge PR 386 "build for py314t" (merged), polars PR 21914 "Test free-threaded in ci" (open, unmerged), polars issue 21889 "Build fails with free-threaded Python" (closed).

## The problem
Polars builds on free-threaded Python, but there are no free-threaded binaries on PyPI, so users need a Rust compiler. The issue author (ngoldbaum, who says he wrote the abi3t support in PyO3 and Maturin) asks for `abi3.abi3t` wheels. One such wheel per platform would cover Python 3.15 and later, which keeps the number of wheels per release fixed.

## What the thread says (attributed, not tested here)
- orlp (Polars side) on 2026-06-16: if there is a stable ABI for free-threaded Python, Polars should release wheels for it. He later says the abi3t wheel will "definitely" come but a 3.14t-specific wheel might never ship.
- ngoldbaum says dependencies such as connectorx (no sdist), orjson and grpcio are likely stumbling blocks for CI on free-threaded builds.
- On 2026-07-22 pavelzw notes conda-forge builds polars for cp314t, so pixi users have a compiled option.
- On 2026-10-06 orlp says Polars will wait for the official 3.15 release and ship in the next Polars version after it. He adds that PyPI space is the blocker: the project has already deleted yanked releases to stay within limits, and more wheels would make this worse, and links the PyPI request above.
- On 2026-10-17 mbUSC asks whether alternatives exist if PyPI does not respond, such as dropping very old releases.

## The PyPI request
The request, per its text, is for 50 GB on `polars-runtime-compat`, one of three runtime packages per Polars release. It lists wheels from about 47 MB to 58 MB, about 421 MB for eight wheels plus the sdist, and monthly releases. A bot comment on 2026-08-26 says 18 other limit requests were ahead of it, and that PyPI support is one paid staffer plus volunteers. On 2026-09-18 a PyPI-side commenter (Thespi-Brain) offered 30 GB instead of 50. ritchie46 (Polars) accepted that on 2026-09-19. On 2026-10-06 he asked for an update, saying he does not want to delete old releases, and asked that the two sibling requests be handled together or the release stays blocked. On 2026-10-15 mbUSC says this blocks free-threaded builds. The request is still open and I saw no later PyPI reply.

Rough arithmetic from the numbers above: at about 421 MB per release per package and monthly releases, a 30 GB cap is around 70 releases' worth for one package before any extra wheel types are added. That is my estimate from the issue's figures, not a PyPI statement.

## Honest limits
- I checked nothing on PyPI itself. Sizes, caps and release cadence are quoted from the issue text.
- "Blocks free-threaded builds" is how Polars maintainers and commenters describe it. Polars' plan to wait for 3.15 is also stated by one maintainer, not a project-wide announcement.
- Whether the 30 GB bump was applied is not shown. The thread says it was offered and accepted, and later messages still describe the blocker.
- I did not test any wheel or build.
