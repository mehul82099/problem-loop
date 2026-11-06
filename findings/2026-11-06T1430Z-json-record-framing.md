# Repeated JSON dumps need an explicit record format

## Research
Python's json reference warns that repeated dump calls to the same stream do not supply a framed protocol. Public append-file questions encounter Extra data when trying to load adjacent objects. That exception is not the only possible failure: adjacent numeric outputs can merge into a different valid number.

## Discussion
Two objects written as adjacent JSON texts fail single-document parsing, but dump(1) followed by dump(2) writes 12, which loads as one number. The intended record boundaries have been lost even though parsing succeeds. This is documented-format misuse, not a new parser defect.

Choose one JSON array when the data is one collection. For independent records, JSON Lines defines one valid JSON value per line, UTF-8 for byte storage, and LF record delimiters. Its format page rejects blank lines and recommends a final delimiter. The NDJSON specification differs on some details, including optional documented empty-line skipping, so consumer policy should be explicit.

Use an encoder with no pretty-print indentation for one-line records, append a delimiter, and parse each whole line with loads. ensure_ascii=False does not stop the encoder escaping a newline inside a string: required control-character escapes remain. Conversely, pretty-print indentation adds physical newlines and is unsuitable for one-record-per-line framing. raw_decode is a prefix-decoding primitive, not a substitute for checking the rest of each record.

## Conclusion
Agree on document versus record-stream semantics on both sides. Do not infer record integrity from one successful loads call or a valid prefix. A line reader can yield earlier records before a later line fails; decide separately whether the application accepts partial progress or needs all-input validation before effects. Framing alone is not schema validation, an atomic append guarantee or crash recovery.

## Action: executable probe
Original code under this repository's MIT license. Small StringIO streams only. Run without Python optimization so assertions remain enabled.

```python
import io
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def invalid_document(text):
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return True
    return False

objects = [{'id': 1}, {'id': 2}]
stream = io.StringIO()
for obj in objects:
    json.dump(obj, stream)
check(stream.getvalue() == '{"id": 1}{"id": 2}')
check(invalid_document(stream.getvalue()))
check(json.loads(json.dumps(objects)) == objects)

# Adjacent numeric outputs can silently merge instead of raising.
stream = io.StringIO()
json.dump(1, stream)
json.dump(2, stream)
check(stream.getvalue() == '12')
check(json.loads(stream.getvalue()) == 12)

records = [{'text': 'a\nb', 'label': 'café'}, None, 7]
text = ''.join(json.dumps(record, ensure_ascii=False, allow_nan=False)
               + '\n' for record in records)
check(len(text.split('\n')) == 4)
check('a\\nb' in text)
check('café' in text)
check([json.loads(line) for line in io.StringIO(text)] == records)
check(invalid_document(text))

# A selected prefix is not validation of the rest of the stream.
lines = io.StringIO('{"id":1}\nnot-json\n{"id":3}\n')
check(json.loads(next(lines)) == {'id': 1})
check(invalid_document(next(lines)))
check(json.loads(next(lines)) == {'id': 3})
check(invalid_document('\n'))
pretty = json.dumps({'a': 1}, indent=2) + '\n'
check(len(list(io.StringIO(pretty))) == 3)
check(invalid_document(next(iter(io.StringIO(pretty)))))
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 16 checks passed on CPython 3.13.17 and 3.14.9.
- Tests object concatenation failure, numeric concatenation merging, array control, one-line record round-trip with escaped newline and non-ASCII text, full-stream loads failure, invalid later record, blank line rejection and pretty-print line failure.
- No byte encoding, disk append, concurrent writer, interrupted write, streaming network, huge input, strict arbitrary-JSON validator or third-party jsonlines package was tested. allow_nan=False is used for the encoder example; the small line reader is not a full interoperable JSON validation policy.
- Distinct from the earlier duplicate-object-name finding, which concerns members inside one object rather than record boundaries.

## Sources
- [Python 3.14 json](https://docs.python.org/3.14/library/json.html): framing warning, control-character escapes, indentation and raw_decode contract.
- [JSON Lines format](https://jsonlines.org/): one value per line, encoding and delimiter rules.
- [NDJSON specification](https://github.com/ndjson/ndjson-spec): related but not identical stream policy.
- [Public append-file question](https://stackoverflow.com/questions/51225954/python-error-trying-to-append-json-file): concrete failure report. Its claim that ensure_ascii=False leaves string newlines unescaped is not adopted.
- [jsonlines package docs](https://jsonlines.readthedocs.io/en/latest/index.html): reader/writer and error-policy considerations; package not tested here.
- [Independent framing article](https://techatlas.osuslova.pro/en/ai-json-framing-multiple-objects/): array versus records discussion. Broad recovery claims and raw_decode-as-line-reader advice are not adopted.
