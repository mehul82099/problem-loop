# Electrobun apps ship Bun's dev tooling to end users: a measured case for a trimmed production runtime

**Source:** [blackboardsh/electrobun#599](https://github.com/blackboardsh/electrobun/issues/599) (open discussion; maintainer engaged)

## What happened

The developer of Toonflow (a 20k-star app built on Electrobun) noticed their Windows x64 installer grow from ~52.4 MiB to ~63.0 MiB after moving to Electrobun 2.0.5 / Bun 1.4.4 (both verified releases) and ran a controlled experiment: same Bun source revision, toolchain and packaging, once with the stock runtime and once with `fmt`, `lint` and the built-in TypeScript type checker removed. The runtime dropped from 109.70 to 84.94 MiB and the installer from 62.52 to 53.22 MiB - **9.3 MiB, about 14.9%** - and they propose an optional trimmed production runtime since shipped apps never format, lint or type-check at runtime. The maintainer's reply adds the deeper context from forking Bun and building Cottontail (both verified repos): JSC and its JIT dominate the binary, ICU data is what makes Windows and Linux builds so much bigger than macOS (which links ICU as a system library), and Bun keeps adding dev-facing features - his own answer is Cottontail's approach of splitting capabilities into dynamically loaded zig+js modules rather than trimming a monolith. The reporter is upfront about scope: local Windows x64 builds only, selected capability checks, no full compatibility or cross-platform validation, and the numbers don't prove the new dev features caused all of the observed growth.

## Who this bites

- Every Electrobun (and Bun-bundled desktop) app distributed to end users: download size, update bandwidth and install footprint all carry dev tooling that never runs in production, and the effect is worst on Windows/Linux because of bundled ICU.
- App developers weighing Electron alternatives: per-app savings in the 9-10 MiB range multiply across user bases, and the discussion shows the trade is real maintainer territory, not just reporter wishful thinking - though the maintainer's own trajectory points at modular runtimes rather than a trimmed Bun.

## Limits

- A discussion, not a bug: one app's local measurements (reporter association NONE, maintainer MEMBER reply verified), no published benchmark harness, single platform, and no compatibility matrix for what a trimmed runtime would break.
- The experimental patch and Cottontail's modular design are both unproven for general use; this finding reports the measurement and the maintainer's response, and does not endorse shipping a trimmed runtime.
- Whether Bun upstream would accept build options for this, or whether the growth since earlier versions is fully attributable to these features, is unresolved.
