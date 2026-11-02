# Grafana: the AWS KMS encryption provider fails with the symmetric key the documentation tells you to create

**Source:** https://github.com/grafana/grafana/issues/136802 (opened 2026-11-02, open, no maintainer reply yet)

## The problem

Grafana's own documentation for envelope encryption with AWS KMS begins with "Create a symmetric API key" (the docs page uses "API key" where it means KMS key; the symmetric instruction is unambiguous). The reporter followed it: created a SYMMETRIC_DEFAULT / ENCRYPT_DECRYPT KMS key, configured the provider, restarted - and Grafana could not create its data key. The logged error is an AWS-side rejection: `InvalidKeyUsageException: Algorithm RSAES_OAEP_SHA_256 is incompatible with key spec SYMMETRIC_DEFAULT`, meaning Grafana's KMS Encrypt call specified an RSA-OAEP encryption algorithm that is only valid for asymmetric RSA keys.

The reporter ruled out the usual suspects from the same instance and role: `describe-key` shows the symmetric key correctly, and a plain `aws kms encrypt` (no algorithm specified) succeeds, so IAM and connectivity are fine. Switching to an asymmetric RSA_2048 key made the errors stop - but RSA keys are excluded from KMS automatic key rotation, so the workaround defeats the main reason to use KMS for this. The reporter later added context that may matter: the host is Ubuntu Pro with FIPS mode enabled, which could explain why an RSA-OAEP algorithm is being selected at all.

## Why it matters

Envelope encryption of database secrets is a security feature people enable precisely in regulated environments - the same environments that run FIPS mode. A documented setup that fails out of the box pushes operators toward an unrotatable key type, quietly degrading the security posture they were trying to improve. The documentation-vs-behavior gap is the actionable core: either the Encrypt call should omit the algorithm (or use SYMMETRIC_DEFAULT) for symmetric keys, or the docs must say an RSA key is required and explain how to rotate it manually.

## Verification and caveats

- Verified directly: the Grafana documentation page (and its source in the Grafana repo) instructs creating a symmetric key, exactly as the report says.
- Not verified: the Encrypt-call algorithm selection itself. The AWS KMS provider implementation is not present in the open-source Grafana tree (it appears to live in closed or enterprise code), so the RSAES_OAEP_SHA_256 behavior is the reporter's evidence (the AWS error message quotes it), not something this finding could confirm in source.
- Open with no maintainer response; reporter association NONE, but the report includes the exact logged error, the IAM/connectivity eliminations, and a tested workaround. The FIPS hypothesis is the reporter's follow-up note, unconfirmed.
- This finding does not propose a patch and does not advise switching key types; the rotation tradeoff noted above is the reporter's documented concern.
