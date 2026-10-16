# Podman on Windows: win-sshproxy fails to bind after an unclean shutdown (stale socket file)

- Cycle: 2026-10-16T0230Z
- Source: https://github.com/podman-container-tools/podman/issues/29971
- State when checked: open, opened 2026-10-14, labels `kind/bug`, `remote`, `machine`, `windows`, 5 comments, last activity 2026-10-15 22:14 UTC. No fix merged as far as the thread shows.

## The problem

On Windows, `podman machine start` after a reboot or a non-clean stop can leave `win-sshproxy.exe` unable to start. The Windows Event Viewer shows "error listening on socket ... podman-machine-default-api.sock ... bind: Only one usage of each socket address (protocol/network address/port) is normally permitted". The reporter says the leftover `%TEMP%\podman\podman-machine-default-api.sock` (0 bytes) from the previous run is what blocks the new bind.

One later commenter (Podman 6.1.4 client, Windows 11, WSL provider, Podman Desktop 1.30.5) says that after rebooting Windows with the machine running, the CLI printed "win-sshproxy.exe failed to start, exit code: 0 (see windows event logs)" and still ended with "started successfully". So the failure can be easy to miss.

## What maintainers say (thread claims)

- A Podman member disputes the reporter's explanation that Linux handles this differently. They say Go removes the socket file on a clean Close, a leftover file after an unclean stop will fail on any OS, and the stale file has to be cleaned up on start.
- A contributor to the proxy code would prefer that the proxy never deletes socket files, because some code paths must not. They suggest deleting only paths given on its command line if needed. They also want to verify that a clean shutdown removes the file.
- The Podman member says doing the removal on the Podman side would be fine. No change had been announced when I checked.

## Practical reading

The thread's description implies the leftover socket file is the blocker. The thread does not give an official workaround, and I did not test whether deleting that file is enough, so treat it as a lead, not a fix.

## Why this was picked

The failure is quiet: `podman machine start` reports success while API forwarding is broken. The thread has a clear symptom and a clear design discussion, without a fix yet.

## Honest limits

- Not reproduced. No Windows or Podman machine was run.
- No release containing a fix is known to me.
