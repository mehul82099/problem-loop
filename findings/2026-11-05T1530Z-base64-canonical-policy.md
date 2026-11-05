# Base64 decoding, strict character checks and canonical spelling are separate policies

Date: 2026-11-05. A documented decoding-policy distinction, not a new Python defect.

## Research

The [base64 reference](https://docs.python.org/3/library/base64.html) documents that b64decode discards non-alphabet characters by default and validate=True rejects them. It separately lists canonical padding-bit checks among Python 3.15 additions. [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648), sections 3.3 and 3.5, distinguishes non-alphabet handling from canonical encoding and zero pad bits. A [public CPython proposal](https://github.com/python/cpython/issues/148204) discusses changing the permissive default. It is context for the policy choice, not a claim that the default changed in either tested build.

## Discussion

On the tested 3.13 and 3.14 builds, `b64decode(b'Z!g==')` returns `b'f'`, while validate=True rejects the punctuation. A trailing newline likewise decodes under the default and fails strict validation. Whether line wrapping is allowed is a protocol decision; blindly enabling strict mode can reject intentionally wrapped input.

Strict character validation is not the same as one canonical spelling. In both tested builds, `b'Zh=='` passes validate=True and decodes to `b'f'`, whose standard encoder output is `b'Zg=='`. The example below chooses an exact padded standard-alphabet bytes representation by decoding strictly and comparing the re-encoded bytes. It rejects the alias rather than silently normalizing it.

## Conclusion

Choose alphabet, padding, whitespace and canonical-text policy explicitly. Use validate=True when rejecting non-alphabet characters matches the protocol, but do not infer canonical text from that flag alone on these builds. The round-trip helper is deliberately narrow. Base64 decoding is not encryption, authentication or authorization, and canonical spelling does not make the decoded payload trustworthy.

## Action: fixed standard-alphabet bytes probe

Ran 17 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Tests cover ignored punctuation/whitespace under the default, strict rejection, a nonzero-pad-bit alias, standard round trips and exact-policy rejections. Only fixed non-secret sample bytes are used.

```python
import base64
import binascii
import json
import platform

# Exact padded standard-alphabet bytes policy, not authentication.
def canonical_standard(text):
    decoded = base64.b64decode(text, validate=True)
    if base64.b64encode(decoded) != text:
        raise ValueError('not the selected canonical spelling')
    return decoded

checks = 0
for dirty in [b'Z!g==', b'Zg==\n', b' Zg==']:
    assert base64.b64decode(dirty) == b'f'
    checks += 1
    try:
        base64.b64decode(dirty, validate=True)
    except binascii.Error:
        checks += 1
    else:
        raise AssertionError('expected non-alphabet rejection')
assert base64.b64decode(b'Zh==', validate=True) == b'f'
checks += 1
assert base64.b64encode(b'f') == b'Zg=='
checks += 1
for raw in [b'', b'f', b'fo', b'foo', b'\x00\xff']:
    assert canonical_standard(base64.b64encode(raw)) == raw
    checks += 1
for text in [b'Zh==', b'Zg', b'Z!g==', b'Zg==\n']:
    try:
        canonical_standard(text)
    except (ValueError, binascii.Error):
        checks += 1
    else:
        raise AssertionError('expected exact-policy rejection')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe use the repository's MIT license. Linked sources retain their authorship.
- The helper expects bytes and selects padded standard Base64. It is not a URL-safe decoder, MIME parser, general protocol validator or streaming implementation.
- Newer Python 3.15 options are documentation context only and are not used or tested. No change of defaults or proposal outcome is claimed.
- No untrusted large-input limit, payload validation, cryptographic property, exploit, production change or performance result is claimed.
