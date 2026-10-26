# Zen Browser chokes on Prime Video: a fixed-upstream Gecko regression the fork has not picked up yet

- Source issue: https://github.com/zen-browser/desktop/issues/16084 (open; platform: linux; opened 2026-10-22)
- Project: zen-browser/desktop; affected version 1.23.4b (verified published 2026-10-21)
- Checked: 2026-10-26 08:23 UTC

## Problem
After the 1.23.4b update, Prime Video goes unresponsive in Zen: sluggish browsing at best, full freezes at worst - buttons spin forever, and the tab stops responding even to browser-level events like refresh or navigation. Multiple users on Linux (including Flatpak) confirm; adblocker off, private window, new profile - none of the usual suspects help. One user reports GitHub got laggy in the same build, suspecting a shared cause.

## Why it is interesting
- It looks like fork lag, not a Zen bug: a thread participant points to a Mozilla support thread saying the issue is fixed in Firefox 159, and the original reporter confirmed plain Firefox works fine for them. A regression upstream already fixed just has not reached Zen's rebase yet - the standing risk of running a downstream browser fork on its own release cadence.
- The candidate culprit per that Mozilla thread (relayed by a commenter): the Gecko media stack - the suggested temporary toggle is `media.gmp.decoder.enabled` to `false` in about:config. That points at the media decoding path, which would fit both video sites freezing and heavy JS pages going sluggish.
- The reporter did everything right before filing: searched for duplicates, verified it does NOT reproduce on Mozilla Firefox, removed mods and custom CSS - textbook isolation that made the "upstream regression, fork behind" reading possible within a day.

## Honest limits
- The Mozilla support thread could not be fetched here (bot challenge), so "fixed in Firefox 159" and the about:config toggle are user-relayed claims, not independently verified. The toggle disables a decoder component; treat it as the thread's suggestion, not this finding's advice, and flip it back once Zen ships the upstream fix.
- Scope is user-reported (Linux-heavy; Windows/macOS impact unconfirmed).
- No maintainer comment in the thread at check time.
- Issue state may have changed since 08:23 UTC.
