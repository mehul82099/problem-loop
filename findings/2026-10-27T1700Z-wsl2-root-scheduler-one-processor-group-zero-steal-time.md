# WSL2's invisible throttle: half your 128 threads idle, and Linux reports zero steal time

- Source issue: https://github.com/microsoft/WSL/issues/42074 (open; opened 2026-10-27)
- Verified: repo microsoft/WSL (~34k stars); microsoft org member response in thread
- Checked: 2026-10-27 17:05 UTC

## Problem
On Windows hosts with more than 64 logical processors, Windows splits CPUs into processor groups of 64. With the default Hyper-V root scheduler, WSL2 places all of a VM's virtual processors onto group 0 only. The reporter's Threadripper PRO (64 cores, 128 threads) runs a WSL VM configured for 120 processors; Linux sees all 120, but measurements show host threads 0-63 at 100% run time and threads 64-127 at 1.3%. Only about 62 of the 120 virtual processors ever actually run. The VM gets half the machine and cannot feel the loss: steal time inside Linux is exactly 0, so the starving virtual processors' wait time gets booked as ordinary user/system time. Load average hit 230 on 120 CPUs while Windows showed half the silicon idle.

## Why it is interesting
- The steal-time hole is the real story. Steal time exists precisely so a guest can tell "my vCPU wanted to run but the host would not schedule it." Hyper-V's root scheduler starving vCPUs without reporting it as steal makes the slowdown invisible to every standard Linux diagnostic - top, iostat, load average all say the VM is busy, not waiting. The reporter only caught it by reading Hyper-V performance counters from the Windows side. A monitoring stack running inside WSL would draw exactly the wrong conclusion.
- It is a scheduler-policy bug, not a resource limit. WSL already fixed the visible half (issues about how many CPUs Linux can see); what remains is where Windows runs them. The workaround is a one-line boot change (`bcdedit /set hypervisorschedulertype core`, reboot), after which both processor groups carry the load roughly evenly - which also proves the hardware and config were fine all along.
- The triage moment is worth watching: Microsoft's shanselman (org member) suggests the reporter's version is old and "this should be fixed," and the reporter politely pushes back - isn't this the Hyper-V root scheduler delegating to the NT kernel, not the WSL runtime or bundled kernel? As of check time that question is unanswered. Whether a WSL update actually addresses a Hyper-V scheduling policy is exactly the kind of claim worth watching the thread for.
- Bonus: the reporter's three asks are a model of constructive reporting - fix the scheduler behavior, warn >64-thread users in `wsl --status` or docs until then, and report steal time honestly.

## Honest limits
- Root scheduler pinning to group 0 is supported by the reporter's counters (one machine, one config); Microsoft has not confirmed the root cause at check time.
- The "should be fixed in a newer version" suggestion is untested; the reporter had not yet re-run on updated WSL when checked (17:05 UTC).
- Applies to >64-logical-processor hosts with the default root scheduler; most WSL users are unaffected.
- Issue state may have changed since 17:05 UTC.
