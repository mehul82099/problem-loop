# Apache SeaTunnel: passing `-r master_and_worker` is rejected even though the help text lists it

- Source issue: https://github.com/apache/seatunnel/issues/12939 (open at check time; labels "bug" and "Zeta"; opened 2026-10-21; 5 comments)
- Code read on the `dev` branch:
  - https://github.com/apache/seatunnel/blob/dev/seatunnel-core/seatunnel-starter/src/main/java/org/apache/seatunnel/core/starter/seatunnel/command/ServerExecuteCommand.java (the "Not supported cluster role" error is at line 73 in our read)
  - https://github.com/apache/seatunnel/blob/dev/seatunnel-core/seatunnel-starter/src/main/java/org/apache/seatunnel/core/starter/seatunnel/args/ServerCommandArgs.java (help text for `-r` / `--role`, line 44)
  - https://github.com/apache/seatunnel/blob/dev/seatunnel-engine/seatunnel-engine-common/src/main/java/org/apache/seatunnel/engine/common/config/EngineConfig.java (default role at line 94)
- Project license per the GitHub API: Apache-2.0
- Checked: 2026-10-23 02:55 UTC

## Problem
The reporter says that starting the Zeta engine with `bin/seatunnel-cluster.sh -r master_and_worker` fails with `SeaTunnelEngineException: Not supported cluster role: master_and_worker`, while leaving `-r` out works. They say this breaks deployment scripts that always pass the role explicitly.

## What the thread says
- The reporter traces it to the role parsing in `ServerExecuteCommand.execute()`: it handles `master` and `worker` and has no branch for `master_and_worker`. They propose adding that branch.
- A maintainer-side reply asked if they would send a fix, and they said yes. A later reply (from an account that looks like an automated review helper, which we cannot verify) agrees the analysis is consistent, asks for a unit test covering the four cases (master, worker, master_and_worker, and an invalid value), and asks for the PR to be linked back. That reply is from 2026-10-23 02:10 UTC.
- The reporter says they confirmed the latest `dev` branch has the same problem. No pull request was linked in the thread when we checked.

## What we checked
- `ServerCommandArgs.java` on `dev` describes `-r` / `--role` as "The cluster node role, default is master_and_worker, support master, worker, master_and_worker".
- `EngineConfig.java` on `dev` has `clusterRole = ClusterRole.MASTER_AND_WORKER` as its default, and the enum includes `MASTER_AND_WORKER`.
- `ServerExecuteCommand.java` on `dev` has a branch that throws "Not supported cluster role: " + the given value in its final `else`, under a check that a role was given. When no role is given, it sets `MASTER_AND_WORKER`. We saw lines 70 to 79, which match the reporter's account for the unset case and the error. We saw no `master_and_worker` branch near them.
- So the docs and the parser disagree on `dev`, as the reporter says. We did not run the script.
- We looked at the 30 most recent pull requests and found none about this.

## What this does not tell you
- We have not seen a fix, a merged pull request or a release containing one.
- We did not check which released versions have this code, so we cannot say which versions are affected beyond `dev` on 2026-10-23.
- If you hit this, the reporter's description implies leaving `-r` out gives the same default role. That is our reading of the code and the issue, not something we ran. Check your own deployment first.

## Honest limits
- We read source and the issue thread only. We did not build or start SeaTunnel.
- Issue state may have changed since 02:55 UTC.
