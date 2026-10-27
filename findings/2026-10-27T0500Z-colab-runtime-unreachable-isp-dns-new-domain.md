# Colab moved to a new domain, some ISPs won't resolve it, and users think they've been region-blocked

- Source issue: https://github.com/googlecolab/colabtools/issues/6157 (open; opened 2026-10-24)
- Project: googlecolab/colabtools (Google Colab's public tracker)
- Checked: 2026-10-27 05:40 UTC

## Problem
Google Colab users on certain ISPs suddenly cannot connect to any runtime: the connection fails instantly with a bare "TypeError: Failed to fetch" from Colab's external_binary.js. Fresh notebooks, cleared site storage, and network tweaks do nothing. The Colab team's diagnosis in-thread: the failure is DNS - the affected ISPs are not properly resolving Colab's serving domains, "now `*.prod.r.colab.dev`". Their offered workaround is switching the browser to Secure DNS (Google Public DNS), and their advice if it works: escalate the DNS resolution issue to your ISP, linking a Jio DNS troubleshooting thread as an example of the pattern.

## Why it is interesting
- An infrastructure migration's blast radius lands on the people least equipped to diagnose it. Colab's users skew heavily toward students and learners - the thread's latest comment is someone in Sagar, India, doing coding practice on a niche Chromium fork, reading the error as "maybe due to my restricted location." A DNS failure presents exactly like a geo-block, and the product has no way to tell the user which it is.
- The shape of the fix tells you who actually owns the problem. Google cannot make an ISP resolve its domains correctly; the ISP's resolvers are the broken component. So the official answer is a client-side bypass (Secure DNS) plus "please complain to your carrier" - the individual user becoming the escalation channel for an ISP's infrastructure, with a Facebook help thread as the reference manual.
- It rhymes with a long-running pattern: Jio and other large Indian ISPs have a documented history of DNS-level interference and flaky resolution for newly deployed domains. A big provider rolling to a fresh domain (or new cert/CDN path) is precisely when that flakiness bites.
- Worth noting for anyone debugging "Failed to fetch" anywhere: the console stack points into minified JS, but the failing layer was DNS, three layers below the code that reported it.

## Honest limits
- The DNS root cause is the Colab team's stated diagnosis (contributor comments), not packet-level proof in-thread; the "now *.prod.r.colab.dev" detail suggests a recent domain migration but no changelog entry is linked.
- Affected ISP list is anecdotal (Jio-adjacent reports, one Sagar MP user); no status-page incident was found or cited.
- The Secure DNS workaround comes from the Colab team itself, so it is official advice - but it only helps when DNS is the actual fault.
- Issue state may have changed since 05:40 UTC.
