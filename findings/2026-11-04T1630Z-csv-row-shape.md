# CSV strict parsing is not a row-shape or unique-header check

Date: 2026-11-04. A tested CSV import-contract finding and small opt-in validator.

## Research

The [csv reference](https://docs.python.org/3/library/csv.html) says DictReader stores extra fields under `restkey` (default None), fills missing fields with `restval` (default None), and passes other options to the underlying parser. Its dialect `strict` option raises on bad CSV input, but is not a table-schema validator. The [restval documentation issue](https://bugs.python.org/issue40013) closed after that missing-field behavior was clarified.

[CPython issue #112958](https://github.com/python/cpython/issues/112958) is a closed report where duplicate headers explained why the number of dictionary entries was smaller than the header count. This is historical evidence of confusion, not an unresolved current defect. [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180) describes consistent field counts as a CSV convention, while Python's parser supports a wider range of dialects. The [io reference](https://docs.python.org/3/library/io.html) documents StringIO, used below for in-memory tests rather than real import files.

## Discussion

In the measured examples, `DictReader(..., strict=True)` accepts both a short row and a long row. It returns None for a missing value or an extra list under the None key. Duplicate header strings are a separate problem: dictionary keys are unique, so the later field overwrites the earlier value. Counting dictionary entries after mapping cannot validate the original row width reliably.

An empty field and a missing field are different. `1,` has two fields; `1` has one. Quoted embedded newlines are also not extra records: parsing must happen before measuring width. Splitting text by commas or physical lines is not an adequate replacement for CSV parsing.

## Conclusion

For imports whose contract requires a unique header and equal-width records, validate parsed lists before converting them to dictionaries. The small helper below chooses an explicit policy: reject duplicate header strings, reject every width mismatch including blank records, allow empty field values, and accept a header-only file as zero data rows. It raises for a completely empty input. These policies are opt-in, not universal CSV requirements.

The helper is a generator. A later invalid row can raise after earlier rows were yielded. For a finite, small, effect-free input, collecting all rows before downstream changes provides a validation boundary; it is not transaction control and is not suitable for every file size. Applications must separately define encoding, field names, types, limits and handling of external spreadsheet consumers.

## Action: tested helper and regression probe

Ran 12 cases on each of CPython **3.13.17** and **3.14.9**, Linux x86_64, for 24 passing case executions. Seven assertions cover the permissive baseline and valid helper results; five rejection cases cover short/long rows, duplicate headers, empty input and a blank record. No file, network or database operations are used.

```python
import csv
import io
import json
import platform

def checked_rows(text):
    reader = csv.reader(io.StringIO(text, newline=''), strict=True)
    header = next(reader, None)
    if header is None:
        raise ValueError('missing header')
    if len(set(header)) != len(header):
        raise ValueError('duplicate header')
    for row in reader:
        if len(row) != len(header):
            raise ValueError('row width mismatch at physical line %s' % reader.line_num)
        yield dict(zip(header, row))

short = list(csv.DictReader(io.StringIO('a,b\n1\n'), strict=True))
assert short == [{'a': '1', 'b': None}]
long = list(csv.DictReader(io.StringIO('a,b\n1,2,3\n'), strict=True))
assert long == [{'a': '1', 'b': '2', None: ['3']}]
assert list(csv.DictReader(io.StringIO('a,a\n1,2\n'))) == [{'a': '2'}]
assert list(checked_rows('a,b\n1,2\n')) == [{'a': '1', 'b': '2'}]
assert list(checked_rows('a,b\n1,\n')) == [{'a': '1', 'b': ''}]
assert list(checked_rows('a,b\n"one\ntwo",2\n')) == [{'a': 'one\ntwo', 'b': '2'}]
assert list(checked_rows('a,b\n')) == []
for text in ('a,b\n1\n', 'a,b\n1,2,3\n', 'a,a\n1,2\n', '', 'a,b\n\n'):
    try:
        list(checked_rows(text))
    except ValueError:
        pass
    else:
        raise AssertionError('expected rejection')
print(json.dumps({'python': platform.python_version(), 'cases': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and helper are under the repository's MIT license. Linked upstream work retains its authorship.
- Validation is exact string-based header uniqueness and parsed field count only. No header trimming, normalization, BOM handling, alternate delimiter, malformed-quote matrix, resource limit, formula handling or application import was tested.
- The diagnostic uses the parser's physical line counter, not a logical record number. A quoted multiline record can span several physical lines.
- This is documented behavior and a narrow policy example, not a newly discovered defect or a complete CSV safety tool. The helper does not prevent semantic field misalignment when widths happen to match.
