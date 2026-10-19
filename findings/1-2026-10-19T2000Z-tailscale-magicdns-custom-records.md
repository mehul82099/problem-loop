# Tailscale: custom records and aliases in MagicDNS, requested since 2021 (tailscale/tailscale#1543)

- Source issue: https://github.com/tailscale/tailscale/issues/1543 "FR: Support custom records in MagicDNS". Opened 2021-03-18, open. Labels: "L3 Some users", "P2 Aggravating", "T0 New feature", "fr", "pod/network-features". 1,184 reactions on the post, about 109 comments, last updated 2026-10-19.
- Tailscale docs read 2026-10-19: https://tailscale.com/docs/features/magicdns and https://tailscale.com/docs/features/tailscale-services (last validated Oct 7, 2026, per the page).
- A separate request, https://github.com/tailscale/tailscale/issues/16214 "FR: add records to MagicDNS", was closed as a duplicate in 2025 (state and date from a search result excerpt).

## The request
The first post says a customer wants DNS aliases, such as `example.<tailnet>.ts.net`, that always point to a machine (for example `staging-1`). Later comments broaden it: CNAME-style aliases for one machine that runs many services behind a reverse proxy (Caddy, nginx), custom names so a service works the same on and off the LAN, and one user wants a second, short name for a machine whose real name is longer than 15 characters.

## What Tailscale staff said in the thread
- 2021-07-21 (a Tailscale member, bradfitz): a client-side `ExtraRecords` field was added, not yet supported server-side.
- 2022-01-13 (same member): the feature "means a number of things to different people", and exposing it needs care. His examples: a record under `foo.net` needs the OS to send queries for that name to the Tailscale resolver, but some OSes can only route `*.foo.net`, which then needs forwarding to the system's upstream DNS that Tailscale cannot always find; a `foo.<tailnet>.ts.net` record raises questions if a machine named `foo` exists or appears later, and about certificate challenges; and sharing a node raises whether the record is shared. He wrote they were "leaning towards shipping this soon" with limits, namely no `*.ts.net` or `*.tailscale.net` records, and DNS servers set with override on. That was in 2022.
- 2022-03-22 and 2022-07-01 (a Tailscale contributor): no update promised, and the issue's priority labels reflect the number of thumbs-ups. He expected the first release to be a new field in the policy file. The policy file route is his expectation from 2022, not something I confirmed shipped.
- I did not find a later staff reply in the comments I read, which ended at 2026-10-09.

## What users say and suggest
- The common use case is one machine with many services behind a reverse proxy, and wanting `service.machine` names without port numbers. Others want names that work whether they are on the LAN, the VPN or the public Internet.
- Workarounds named in the thread, all by commenters and not tested by me: running a separate DNS server (such as Pi-hole, as a machine on the tailnet) and setting it as the tailnet's DNS; a Tailscale Services and Kubernetes-ingress approach (2026-10-03). The Tailscale Services docs page says a service gets a stable MagicDNS name that stays the same when it moves to another host. A reply on 2026-10-04 says this does not give a name that resolves from outside Tailscale, and the first commenter answers that public DNS was not the point of the request.
- A long 2026-06-15 comment says it was written from a conversation with an AI assistant and then edited by the author, and covers Node Sharing with outside users. I read only the start.
- There is an argument (2026-06-05 to 2026-06-08) over whether the feature should be free on all plans. Tailscale's docs say MagicDNS itself is available on all plans. Nothing in the thread says what pricing a custom-records feature would have.

## What can be said
- 1,184 reactions makes this a heavily requested feature, and a Tailscale member gave detailed reasons for caution in 2022. As of the last comments I read, there is no linked design, pull request or shipped feature for aliases or custom records in MagicDNS itself.
- If you need aliases today, the thread's options all involve running or using something outside MagicDNS. This note does not recommend one. Check the current Tailscale docs for your plan and version before changing DNS settings, since wrong DNS settings can break name resolution on every device in a tailnet.

## Honest limits
- I did not run Tailscale or test any workaround.
- I read the comments marked as from Tailscale staff and the ones with the most reactions, plus the last ones. I did not read all 109.
- "Staff" here means the GitHub association shown on the comment (member or contributor), and I did not verify roles beyond that.
