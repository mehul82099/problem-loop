# Hex decoding has a grammar and a Python-version input contract

Date: 2026-11-09. Evidence-backed Python finding, not a new decoder defect.

## Research

Python's bytes.fromhex accepts case variants and ASCII whitespace around complete hex-byte pairs. It does not mean "remove arbitrary separators then parse." Python 3.14 also changed the input-type contract: ASCII bytes and bytes-like objects are now accepted, whereas the tested 3.13 build requires text. The versioned references and 3.14 release notes document the change.

## Discussion

`0aFF` and `0a ff` decode to the same bytes, but they are different source spellings. A successful decode therefore does not prove lowercase separator-free canonical text. Nor should a caller silently remove punctuation, infer a missing nibble or discard a `0x` prefix unless its format allows that repair.

Whitespace tolerance also has boundaries. In these tests, ASCII whitespace can separate complete byte pairs, but `0 a` raises ValueError. A nonbreaking space is not ASCII whitespace and is rejected. An empty or whitespace-only string decodes to empty bytes, which may differ from a field's nonempty requirement.

The new bytes-like input support is a separate compatibility issue. The same `bytes.fromhex(b'0aff')` call raises TypeError on the tested 3.13 build and succeeds on the tested 3.14 build. Do not infer text-only rejection from an old example while deploying on 3.14, or rely on 3.14 input support while claiming 3.13 compatibility.

## Conclusion

| Contract | Policy | Boundary |
| --- | --- | --- |
| Human-readable hex dump | bytes.fromhex with documented syntax | Only supported whitespace/pair structure, not arbitrary punctuation |
| Stable lowercase field | Validate the source spelling and length first | Decoding alone collapses case/whitespace variants |
| Cross-version text input | Pass an explicitly decoded text value under a stated encoding policy | Type adaptation does not choose field grammar |
| Native 3.14 bytes-like input | Use its documented support and test the supported versions | Different from 3.13 behavior |

The helper below defines a toy field: str only, 1 through 4 bytes, lowercase ASCII hex, no separators. Four bytes is an example limit, not a recommended hash length or protocol limit. It does not validate what the decoded bytes mean. It differs from the earlier bytes-representation finding by testing decoder grammar and the 3.13/3.14 input-type change, rather than repr versus text decoding.

## Action: version-aware diagnostic and narrow field helper

Original standard-library-only code, covered by the repository MIT license. No external input, file access or network operations.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform
import sys

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def expect(exc, action):
    global checks
    try:
        action()
    except exc:
        checks += 1
    else:
        raise AssertionError(f'expected {exc.__name__}')

def canonical_hex(text):
    """Toy field: str only, lowercase, nonempty, 1..4 bytes, no separators."""
    if not isinstance(text, str):
        raise TypeError('text required')
    if not 2 <= len(text) <= 8 or len(text) % 2:
        raise ValueError('expected 1..4 complete hex bytes')
    if any(c not in '0123456789abcdef' for c in text):
        raise ValueError('lowercase hex digits only')
    return bytes.fromhex(text)

check(bytes.fromhex('0aFF') == b'\x0a\xff')
for whitespace in (' ', '\t', '\n', '\r', '\v', '\f'):
    check(bytes.fromhex(whitespace + '0a' + whitespace + 'ff' + whitespace)
          == b'\x0a\xff')
    expect(ValueError, lambda whitespace=whitespace: bytes.fromhex('0' + whitespace + 'a'))
for text in ('0x0a', '0a:ff', '0a,ff', 'a', 'gg', '0a\u00a0ff'):
    expect(ValueError, lambda text=text: bytes.fromhex(text))
check(bytes.fromhex('') == b'')
check(bytes.fromhex(' \t\n') == b'')
for data in (b'0aff', bytearray(b'0aff'), memoryview(b'0aff')):
    if sys.version_info >= (3, 14):
        check(bytes.fromhex(data) == b'\x0a\xff')
    else:
        expect(TypeError, lambda data=data: bytes.fromhex(data))
for text in ('0a', '00', 'abcdef01'):
    check(canonical_hex(text).hex() == text)
for text in ('', ' ', '0A', '0a ff', '0x0a', 'a', '0000000000'):
    expect(ValueError, lambda text=text: canonical_hex(text))
expect(TypeError, lambda: canonical_hex(b'0a'))
for value in range(256):
    text = f'{value:02x}'
    check(canonical_hex(text) == bytes([value]))
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'ascii_bytes_input_supported': sys.version_info >= (3, 14)}))
```

## Validation

Executed **291 checks per build** on CPython **3.13.17** and **3.14.9**. Both passed their version-specific expected outcomes. Tests cover all six ASCII whitespace separators, rejection inside a byte pair, case variants, punctuation, odd lengths, nonbreaking space, empty input, bytes/bytearray/memoryview inputs, the helper's explicit limits and all 256 one-byte values.

The version branch records the expected support, and actual API calls verify it. It is not a test of every possible buffer layout or future Python version. No performance or security-equivalence guarantee is made. Repository CI is separate.

## Publisher and sources

Published deliverable: this finding and runnable helper/probe. Six source pages were read; the exact versioned fromhex sections were also inspected separately after the long-page fetches. Documented syntax and a released feature change are not a new regression or incident-rate claim.

1. [Python 3.14 bytes.fromhex](https://docs.python.org/3.14/library/stdtypes.html#bytes.fromhex), primary reference: pair syntax, whitespace and new bytes-like input support.
2. [Python 3.13 bytes.fromhex](https://docs.python.org/3.13/library/stdtypes.html#bytes.fromhex), versioned primary reference: earlier text-input contract.
3. [What's New in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html), primary release documentation: ASCII bytes and bytes-like input addition.
4. [CPython issue 129349](https://github.com/python/cpython/issues/129349), public feature discussion, 2025: motivation and implementation of bytes input. No changes to that repository are made here.
5. [CPython issue 137083](https://github.com/python/cpython/issues/137083), public proposal, 2025: arbitrary separator tolerance was requested, not established as the current decoder contract.
6. [Real Python bytes tutorial](https://realpython.com/python-bytes/), independent explanation, 2025: mixed-case and whitespace examples. Its broad whitespace wording is constrained here to the official ASCII rule and tested byte-pair boundaries.
