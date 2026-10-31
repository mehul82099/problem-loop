# x/sys/unix `ParseUnixCredentials` still panics on a short SCM_CREDENTIALS payload - a check the standard library added ten years ago never made it across

**Source:** [golang/go#82750](https://github.com/golang/go/issues/82750) (open; both sides of the code verified on master)

## What happened

`golang.org/x/sys/unix.ParseUnixCredentials` validates the control message's level and type but never its payload length ([sockcmsg_linux.go#L27-L36](https://github.com/golang/sys/blob/master/unix/sockcmsg_linux.go#L27-L36), verified on master and present at the v0.49.0 tag). Hand it an `SCM_CREDENTIALS` message with no payload and `&m.Data[0]` panics with `index out of range [0] with length 0`; hand it a truncated one and the `unsafe.Pointer` cast reads a `Ucred` past the end of the buffer.

The telling part: the standard library's `syscall.ParseUnixCredentials` has had the missing guard since 2016. Issue [golang/go#16475](https://github.com/golang/go/issues/16475) ("syscall: ParseUnixCredentials is unsafe", closed) added exactly `if uintptr(len(m.Data)) < unsafe.Sizeof(Ucred{}) { return nil, EINVAL }` via CL 25154 - and that line is still there in stdlib master, verified. The x/sys copy of the same function never received it, so a decade later the "modern" import path is the unsafe one. Go's own gabyhelp bot independently surfaced #16475 as the top related issue (attributed to tooling).

The reporter is explicit about scope: the kernel always writes a full `ucred`, so this is a robustness gap, not a reachable attack - they found it while reviewing a caller, and a program would have to construct or forward a malformed control message itself. The repro is a 10-line `main` that panics on linux/amd64 with go1.27.3 and x/sys v0.49.0.

## Who this bites

- Any Go program calling `x/sys/unix.ParseUnixCredentials` on control messages that didn't come straight from the local kernel: test fixtures, fuzzers, message replay, or proxies that re-serialize ancillary data - one short buffer crashes the process.
- API-consistency expectations: x/sys is where new socket code is steered, and its version of this function is strictly less safe than the frozen stdlib original.
- Fuzzing Go's own ecosystem: this is exactly the class of panic that turns a corpus entry into a crash report in downstream projects.

## Limits

- Not a security vulnerability by the reporter's own assessment, and the finding repeats that: no unprivileged remote path is claimed - a kernel never sends a short ucred, so the panic needs a program that feeds the parser crafted input.
- The repro panic is the reporter's; I verified both code sites line-by-line on master, the stdlib fix and its source issue, and the v0.49.0 tag, but did not compile the repro (go repo ~139k stars).
- The same missing-check pattern may exist in sibling parsers in x/sys/unix (`PktInfo4` decoders and friends use similar casts); only `ParseUnixCredentials` is established here.
