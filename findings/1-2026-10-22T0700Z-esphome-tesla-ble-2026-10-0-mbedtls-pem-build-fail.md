# esphome-tesla-ble: build fails on ESPHome 2026.10.0 because mbedTLS PEM support was trimmed

- Source issue: https://github.com/PedroKTFC/esphome-tesla-ble/issues/401 (open at check time; no labels; opened 2026-10-21; 5 comments, 4 reactions)
- ESPHome changes named in the issue: https://github.com/esphome/esphome/pull/19088 (merged 2026-09-11) and https://github.com/esphome/esphome/pull/18877 (merged 2026-10-07)
- Earlier related issue (closed): https://github.com/PedroKTFC/esphome-tesla-ble/issues/393
- Project: https://github.com/PedroKTFC/esphome-tesla-ble (AGPL-3.0, 231 stars per the API)
- ESPHome release: 2026.10.0, published 2026-10-21 11:42 UTC, not a pre-release (GitHub API)
- Checked: 2026-10-22 07:40 UTC

## Problem
The reporter says that since ESPHome 2026.10.0 the TeslaBLE library in this package fails to compile with the error `'mbedtls_pk_write_key_pem' was not declared in this scope`. Their setup: ESP32-C3, esp-idf framework, PlatformIO toolchain, package 2026.9.0.

## Cause as described in the thread
The reporter says ESPHome 2026.10.0 trims mbedTLS to the client-only options ESPHome needs, so PEM writing (`CONFIG_MBEDTLS_PEM_WRITE_C`) is no longer on by default, and the library stores its pairing private key as PEM. We confirmed that both ESPHome PRs they cite exist, are merged, and have titles about trimming or disabling mbedTLS options. We did not read the diffs, so we cannot confirm that they switch off PEM writing specifically.

## Workaround and status
- The reporter says that adding `CONFIG_MBEDTLS_PEM_WRITE_C: y` and `CONFIG_MBEDTLS_PEM_PARSE_C: y` under `esp32: framework: sdkconfig_options` in the device YAML fixed the build, and that the device reconnected to the car with its existing key, without re-pairing. This is their own report of one device.
- The maintainer replied on 2026-10-21 that testing "all seems to work" and that the change was added to the `dev` branch. We checked: `packages/base.yml` on `dev` contains both options, and `main` does not (at check time). The maintainer later said the library itself does not need the dev version.
- Two commenters report that switching to the `dev` branch worked for them. One of them first got a build without the number controls, and a second build after resetting the build environment worked. They could not repeat the first result.
- The issue is still open. We saw no release tag or `main` change that carries the fix.

## What this does not tell you
- This is a firmware for a car's Bluetooth control. We do not advise changing options or switching branches on a device that controls a vehicle without reading the project's own instructions. We did not build or flash anything.
- It does not say whether other ESPHome 2026.10.0 builds that use PEM are affected.
- The `dev` branch is a development branch, so it may change.

## Honest limits
- We did not reproduce the build error or test the options. Results above are reports from the issue thread.
- State may have changed since 07:40 UTC.
