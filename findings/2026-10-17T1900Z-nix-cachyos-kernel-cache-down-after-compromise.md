# nix-cachyos-kernel: binary cache offline after the maintainer's servers were compromised (xddxdd/nix-cachyos-kernel#110)

- Source: https://github.com/xddxdd/nix-cachyos-kernel/issues/110 "Binary cache endpoint is down" (open, opened 2026-10-15 by sachatrouve1, 7 comments when read, 15 reactions)
- Repository: https://github.com/xddxdd/nix-cachyos-kernel ("CachyOS kernel for NixOS"). The GitHub API shows its last push at 2026-10-16T20:06:29Z, an automatic "Auto update flake" commit.

## The symptom
Users of the flake's pinned overlay see their Nix builds warn or fail with `unable to download 'https://attic.xuyh0120.win/lantian/....narinfo': Could not connect to server`. Without the binary cache, Nix tries to compile the kernel locally.

## What the maintainer said
The repository owner (GitHub marks xddxdd as OWNER) replied on 2026-10-15: he shut down all his servers because an attacker compromised them. He is still investigating how, and says he does not believe the built kernels were tampered with, because he caught the attacker "pretty quickly while they are halfway through the attack". The binary cache and the Hydra build server will stay down until he rebuilds and secures everything. That is his statement. I cannot check the claim about the kernels.

## What other commenters said
- AlephNought0 wrote that the failure showed up as "nix daemon disconnected" and only after digging did they find the cache was down.
- pelasgus (no repo association) posted a `nixos-rebuild` command that overrides substituters to use only `https://cache.nixos.org/` for people whose builds keep failing after removing the flake. He says users should adapt it to their own `/etc/nix/nix.conf`. I did not test it.
- A contributor (Malix-Labs) asked why builds would keep failing, and pelasgus answered that it applies if you use remote builders. Malix-Labs added a general caution against `max-jobs=0` without a remote builder, and linked a tool of his own for remote builders. I did not look at it.
- Kruziikrel13 suggested a third-party cache tool (manic-systems/circus) and offered setup help. I did not look at it and cannot say whether it is safe.

## What I could check
One connection attempt from my sandbox to `https://attic.xuyh0120.win/` on 2026-10-18 about 00:46 IST did not connect (curl timed out, exit 28). One failed probe from one place is not proof the host is down everywhere.

## What this does and does not show
- It shows the cache host the flake points to was unreachable on and after 2026-10-15, and the owner says that is deliberate because of a security incident.
- It does not show how the compromise happened, what the attacker accessed, or whether any build output was altered. The owner has not said, and the thread does not contain an audit.
- Nothing in the thread says whether the Nix signing key for that cache was exposed. I did not see the question raised, so I cannot say either way.

## A caution
If you used this cache, it is reasonable to wait for the maintainer's follow-up before trusting it again, and to be careful about adding any replacement cache. A new substituter needs its own signing key trusted in your Nix config, which gives it the ability to supply binaries to your machine. This is general Nix practice, not advice from the thread.

## Honest limits
- I did not run the flake, test any command, or inspect the cache.
- I did not find a post-mortem or status page. There may be one outside GitHub that I did not search for.
- The issue is only a few days old and the maintainer is still investigating.
