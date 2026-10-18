# Docker Swarm: a manager sometimes shows (or takes) another node's identity after a rolling upgrade (moby#46167)

- Source: https://github.com/moby/moby/issues/46167 "swarm:Two nodes have the same node ID" (open since 2023-08-08, 23 comments, labels status/0-triage, kind/bug, area/swarm, version/29.9; last comment 2026-10-18)
- Also checked by API: https://github.com/moby/moby/issues/46462 (closed, "Intermittent duplicate host name shown in docker node ls output", referenced by a commenter); latest moby release: docker-v29.9.1 (https://github.com/moby/moby/releases/latest)

## What people report
Across 2023 to 2026, users of multi-manager Swarm clusters report the same pattern, usually during a rolling "drain, upgrade packages, reboot, reactivate" cycle:
- `docker node ls` flips every few seconds between two states. One manager sometimes lists its own hostname, and sometimes a duplicate of another node's hostname and details. A separate entry shows `Down` and is not claimed by any node (no node shows `*` next to it). Reports are on Docker versions from 20.10 to 29.x and on Debian and other hosts.
- One user says the duplicate node was running containers identical to another node's. Another says services with hostname constraints went down, which caused a production outage.
- Frequency is unclear. One user sees it in roughly 10 to 20 percent of updates on some clusters and never on others, and no one has a reproduction. A contributor (s4ke) said in 2024 it would be hard to reproduce and asked for maintainer guidance. A maintainer (neersighted) asked in August 2023 for unredacted `docker info`. I did not find a maintainer diagnosis in the comments I read.
- On 2026-10-16 a contributor (vvoland) tagged another contributor (corhere), the only maintainer-side action in recent months that I saw.

## The newest and most detailed claim (unverified)
A commenter on 2026-10-16 posted a long report, which he says was prepared with ChatGPT, for Docker Engine 29.9.1 on a 3-manager, 1-worker cluster. He says a manager received a valid certificate signed by the cluster CA but with another manager's node ID, after a daemon restart overlapping a Raft leader election, and that he matched it to a record in historical Raft logs from a backup. He anonymised every identifier and withheld the certificates, and says he has no deterministic reproduction. I cannot check any of this, since the evidence is redacted, so treat it as a hypothesis from one user and not a confirmed root cause. Another user on 2026-10-18 reported the same kind of hostname swap on 29.9.1 after a manager was briefly offline, with correct node IDs, and says restarting the Docker daemon on the affected host fixed it. That is also a single report.

## Recovery steps in the thread, and why this finding does not recommend them
One user described removing the `Down` ghost entry, which unexpectedly removed his real manager from the swarm, so he had to force-leave and rejoin it. Others suggest re-initialising the swarm. These steps change cluster membership and can cost data or availability. This finding does not recommend any of them. Anyone with a production Swarm should read the thread, back up their cluster state, and ask the Moby maintainers or their vendor before changing membership.

## What can safely be said
- The symptom is reported repeatedly by independent users and the bug is open and unassigned as far as I could see.
- No one has found a reliable trigger. Reports share a pattern of rolling upgrades with reboots, sometimes with manager connectivity disruption.
- If you run Swarm managers, a cautious habit that follows from the reports is to upgrade one manager at a time and check `docker node ls` from every manager before moving on. That is my reading of the thread, not guidance from the project.

## Honest limits
- I read the 23 comments and the issue body, not any Swarm source code. I did not set up a cluster or try to reproduce.
- The Raft and certificate evidence is a single user's redacted analysis that I could not verify.
- I do not know whether any fix is in progress.
