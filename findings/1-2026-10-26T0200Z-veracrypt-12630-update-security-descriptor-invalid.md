# VeraCrypt 1.26.30 update fails with "security descriptor structure is invalid" - and a clean install does not save it

- Source issue: https://github.com/veracrypt/VeraCrypt/issues/1955 (open; no labels or maintainer reply at check time; opened 2026-10-25)
- Release: VeraCrypt_1.26.30 (verified published 2026-10-24; previous stable 1.26.29 was June 2026)
- Checked: 2026-10-26 02:18 UTC

## Problem
Users updating VeraCrypt from 1.26.29 to the two-day-old 1.26.30 hit an installer abort: "The security descriptor structure is invalid", raised from `VeraCrypt::CheckSystemEncyptionFileResult:4796` per the reporter's screenshot. It is not one machine or one installer flavor: the original reporter is on Windows 10 22H2 with the MSI, a second user confirms MSI, and a third reports the same error on Windows 11 25H2 even after a full uninstall - with both the .exe and .msi installers.

## Why it is interesting
- The failing function name points at VeraCrypt's system-encryption self-check, not a generic MSI hiccup - the installer appears to trip while validating security descriptors (the ACL metadata Windows attaches to files and registry keys). That suggests the new build's checks are stricter, or its own packaged descriptors are malformed for some system states.
- The usual folk remedies are already ruled out in-thread: switching installer flavor is blocked (an MSI-installed instance refuses the .exe updater), and a clean uninstall/reinstall did not fix it for at least one user. There is no confirmed path forward in the thread.
- For disk-encryption software specifically, a botched update path is more than an inconvenience: users mid-upgrade can end up uncertain about the state of a security-critical driver. Nobody in the thread reports a broken encryption state - the failure seems to abort before changes - but that is inference, not confirmed behavior.

## Honest limits
- Three user reports, all Windows; no maintainer acknowledgment, root cause, or guidance at check time. Volume and full scope unknown.
- We did not run the installer; the error text and the clean-install failure are the reporters'.
- This finding offers no workaround. For security software, waiting for official maintainer guidance is safer than registry/ACL surgery.
- Issue state may have changed since 02:18 UTC.
