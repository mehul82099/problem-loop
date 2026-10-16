# WSL2 nested virtualization (/dev/kvm) disappears on AMD CPUs after the October 2026 Windows update

- Cycle: 2026-10-16T0130Z
- Source: https://github.com/microsoft/WSL/issues/41917
- State when checked: open, opened 2026-10-14, labels `fixinbound`, `wsl2`, 9 comments, last activity 2026-10-16 01:33 UTC. A Microsoft member replied that the cause is identified and a fix is being worked on with the servicing team.

## The problem

After installing the October 2026 cumulative update (KB5127648, Windows build 10.0.26200.9711 / 26100.9711), users with `nestedVirtualization=true` in `.wslconfig` find that WSL2 no longer exposes virtualization to the guest. Symptoms they report: no `/dev/kvm`, no `svm` flag in `/proc/cpuinfo`, `modprobe kvm_amd` says "SVM not supported by CPU", and `dmesg` shows "Hyper-V: Nested features: 0x0". WSL prints no warning. It broke Docker setups that need KVM for some users (one names docker-sbx, another Docker Desktop).

## Who is affected (user reports)

Reports in the thread are all AMD: Ryzen 7 3700X, Ryzen 5 5600X, Ryzen 7 5800H, Ryzen 5 7640HS, Ryzen 5 PRO 8640HS, Ryzen 9 8945HS, Ryzen 5 8645HS. A coworker with an Intel Core Ultra 7 155H reportedly was not affected. That is one anecdote, not a finding.

## Reported cause (original reporter's analysis, not verified here)

The reporter says that on this build the Windows host compute service query for `ProcessorCapabilities` fails with error 0x8007000D ("The data is invalid"), and WSL logs but swallows that error. As a result, the nested virtualization setting is never passed on. They point to code in `WslCoreVm.cpp`. I did not read or check the WSL source or run the query.

## Workaround and status

- Many users say uninstalling KB5127648 fixed it. One reports build 10.0.26200.9457 afterwards. Removing a security update has downsides, and the Microsoft member also calls rolling back "the KB" a workaround with downsides.
- Microsoft's `benhillis` (marked MEMBER) says on 2026-10-15 that the issue is identified and a fix is being pursued. No fix release or KB number for it appears in the thread.
- A user filed Feedback Hub feedback with logs from `collect-wsl-logs.ps1`: https://aka.ms/AA13sxp7

## Why this was picked

It is a real breakage for developers using KVM in WSL after a routine update, the thread has a clear symptom check, and the status (confirmed by Microsoft, fix pending) is easy to miss.

## Honest limits

- Nothing was reproduced. I did not install the update or run WSL.
- The AMD-only pattern is from user reports. Other hardware could be affected.
- The root-cause analysis is one user's reading of logs and code.
