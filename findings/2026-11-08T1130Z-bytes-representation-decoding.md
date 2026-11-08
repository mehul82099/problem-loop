# str(bytes) shows a representation, not decoded text

Date: 2026-11-08. Scope: ordinary Python bytes and text with synthetic UTF-8 examples.

## Research

Public questions ask how to remove the b-prefix after converting bytes to text. The official str constructor reference distinguishes representation from decoding: str(raw) without encoding/errors returns a representation, while str(raw, encoding) decodes a bytes-like input. bytes.decode(encoding) is the direct text-decoding operation. The codec must come from the data contract, not from the prefix visible in a log.

## Discussion

For b'hello', str(raw) produces a string containing b and quotes, not the text 'hello'. Cutting off those wrapper characters is not decoding: representation escapes remain. The probe uses bytes containing a newline to show a sliced representation has a backslash-n pair where decoded text has one newline character.

Successful decoding alone does not prove the codec was right. The UTF-8 encoding of cafe with an accented e also decodes as Latin-1 without an exception, but produces different text. Its Latin-1 round trip can even preserve the same bytes while the text is still not the intended text. This is why trying arbitrary codecs until one stops raising is not an encoding-verification method.

Error policy is another choice. Strict UTF-8 decoding rejects the synthetic invalid byte in the probe. ignore drops it and replace inserts a replacement character; encoding either result back to UTF-8 does not restore the original bytes. The official Unicode HOWTO documents these different behaviors. Community suggestions to slice repr are not adopted as a text conversion. For arbitrary binary data that is not known to represent text, keep bytes or choose an explicit binary display such as hex rather than pretending it has a text encoding.

## Conclusion

Decode at a known byte/text boundary with the specified codec and an intentional error policy. Use representation for diagnostics, not as a text parser. Preserve original bytes when a lossy display is acceptable but later recovery or investigation matters. The earlier UTF-8-signature finding covered BOM handling; this increment addresses representation, codec choice and loss, not signature stripping.

## Action

The original MIT-licensed probe passed 24 checks each on CPython 3.13.17 and 3.14.9. It tests representation versus decoding, encoding round trip, wrong-codec success, sliced escaped representation, strict failure, lossy handlers, backslash display, hex round trip and byte/text length distinction. One decoded code point in the example is not a general user-perceived-character counting rule. This is not an encoding detector, file-format parser or universal data-repair helper.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

raw = b'hello'
check(str(raw) == "b'hello'")
check(str(raw) != 'hello')
check(raw.decode('utf-8') == 'hello')
check(str(raw, 'utf-8') == 'hello')
check(type(raw.decode('utf-8')) is str)
text = 'caf\u00e9'
encoded = text.encode('utf-8')
check(encoded == b'caf\xc3\xa9')
check(encoded.decode('utf-8') == text)
check(str(encoded) != text)
check(encoded.decode('latin-1') != text)  # Wrong codec can succeed.
check(encoded.decode('latin-1').encode('latin-1') == encoded)

# Representation escapes are not decoded by cutting off b and quotes.
line = b'a\nb'
check(str(line)[2:-1] != line.decode('utf-8'))
check(len(line.decode('utf-8')) == 3)
check(len(str(line)[2:-1]) == 4)

bad = b'A\xffB'
try:
    bad.decode('utf-8')
except UnicodeDecodeError:
    checks += 1
else:
    raise AssertionError('invalid UTF-8 accepted')
check(bad.decode('utf-8', errors='ignore') == 'AB')
check(bad.decode('utf-8', errors='replace') == 'A\ufffdB')
check(bad.decode('utf-8', errors='ignore').encode('utf-8') != bad)
check(bad.decode('utf-8', errors='replace').encode('utf-8') != bad)
check(bad.decode('utf-8', errors='backslashreplace') == 'A\\xffB')
check(bad.hex() == '41ff42')
check(bytes.fromhex(bad.hex()) == bad)
check(b'hello' != 'hello')
check(len(b'\xc3\xa9') == 2)
check(len(b'\xc3\xa9'.decode('utf-8')) == 1)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding and deterministic diagnostic. Documented behavior, not a new defect or an upstream patch. No private data, external packages or network calls are needed by the probe. Run without optimization so assertions remain enabled.

## Sources

All six public pages fetched and inspected during this cycle:

- Python 3.14 str constructor, representation versus decoding: https://docs.python.org/3.14/library/stdtypes.html
- Python 3.14 Unicode HOWTO, codecs and error policies: https://docs.python.org/3.14/howto/unicode.html
- Python 3.14 codecs reference, error handling: https://docs.python.org/3.14/library/codecs.html
- Community conversion question, use the actual source encoding: https://stackoverflow.com/questions/606191/convert-bytes-to-a-string-in-python-3
- Community prefix-removal question; repr-slicing workaround not adopted for text: https://stackoverflow.com/questions/16748083/print-without-b-prefix-for-bytes-in-python-3
- Independent explanation, incorrect codecs can succeed: https://www.pythoncentral.io/encoding-and-decoding-strings-in-python-3-x/
