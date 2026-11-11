# CSV header detection is a guess, not an import contract

Date: 2026-11-11 (IST). A bounded diagnostic of documented heuristic behavior, not a new csv defect.

## Research

[Issue 131043](https://github.com/python/cpython/issues/131043) reports a clear-to-the-author header that has_header rejects; that issue is closed. [Issue 104380](https://github.com/python/cpython/issues/104380) discusses possible improvements and ambiguity. These reports supply motivation, not the expected answer for every CSV file.

The [Python 3.10 CSV reference](https://docs.python.org/3.10/library/csv.html) describes has_header as a rough heuristic that can produce false positives and negatives. The [exact v3.10.12 implementation](https://github.com/python/cpython/blob/v3.10.12/Lib/csv.py) votes using inferred numeric types and consistent string lengths, dropping inconsistent columns. The [current 3.14 reference](https://docs.python.org/3.14/library/csv.html) retains the heuristic warning.

The [merged dialect-detection rewrite PR 153694](https://github.com/python/cpython/pull/153694) is later work and describes changes to sniff plus some has_header error cases. It is not pending, and its merge is not evidence that this installed older runtime has changed. No newer-runtime result or claim that the rewrite fixes semantic header ambiguity is made here.

## Discussion

On the actual installed **CPython 3.10.12, Linux**, name/code followed by equal-length string values is classified as no header. Declaring the first row to be column names makes that a false negative. A headerless dataset whose first string values are longer than later constant-length values is classified as a header, which would drop a data row if the caller blindly sliced it off. A name/count numeric control is classified as having a header.

The declaration in this diagnostic is an external test-fixture contract. It is not information magically recoverable from the CSV bytes. The same first row can legitimately be labels or data in different applications. Correct delimiter parsing and correct header intent are separate questions.

## Conclusion

For a known import format, specify whether a header is required and validate the expected schema separately. For an unknown format, treat has_header as a suggestion for review rather than permission to discard the first record. This report supplies no universal detector or production importer; it demonstrates the cost of turning a heuristic Boolean into a row-selection rule.

## Action

**65 assertions passed across 16 in-memory cases**: four datasets crossed with comma/semicolon delimiters and LF/CRLF endings. Each case checks the observed guess, exact explicit-dialect parse, declared data-row count, and whether guess-based slicing changes the data rows. One aggregate check confirms twelve mismatches with the declared policy. This finite matrix is deliberately selected to expose failure shapes; twelve of sixteen is not an accuracy estimate on real CSV files.

| Synthetic case | Declared header | Observed guess | Declared data rows | Guess-based data rows |
| --- | --- | --- | --- | --- |
| same-length-header | yes | false | 2 | 3 |
| headerless-length-change | no | true | 3 | 2 |
| numeric-control | yes | true | 2 | 2 |
| variable-length-header | yes | false | 2 | 3 |

All four delimiter/line-ending combinations gave the same table. No sample truncation, escaped-field guessing or performance measurement is involved. Run original MIT diagnostic below as `python csv-header-policy.py` without -O so assertions remain active. It uses StringIO and fixed synthetic values only; no files, private data, network or package installs.

```python
# Original diagnostic, MIT licensed. In-memory synthetic CSV only.
import csv
import io
import json
import platform

cases = [
    ('same-length-header', [['name', 'code'], ['anna', 'west'], ['beth', 'east']], False, True),
    ('headerless-length-change', [['anna', 'west'], ['b', 'e'], ['c', 'f']], True, False),
    ('numeric-control', [['name', 'count'], ['alpha', '1'], ['beta', '2']], True, True),
    ('variable-length-header', [['filename', 'path'], ['a.txt', '/tmp/a.txt'], ['longer.txt', '/tmp/longer.txt']], False, True),
]
checks = 0
results = []
for delimiter in (',', ';'):
    for ending in ('\n', '\r\n'):
        for name, rows, expected_guess, declared_header in cases:
            stream = io.StringIO(newline='')
            csv.writer(stream, delimiter=delimiter, lineterminator=ending).writerows(rows)
            text = stream.getvalue()
            guess = csv.Sniffer().has_header(text)
            assert guess is expected_guess
            checks += 1
            parsed = list(csv.reader(io.StringIO(text, newline=''), delimiter=delimiter))
            assert parsed == rows
            checks += 1
            # Declared policy, not inferred from CSV bytes.
            declared_data = parsed[1:] if declared_header else parsed
            guessed_data = parsed[1:] if guess else parsed
            assert len(declared_data) == (2 if declared_header else 3)
            checks += 1
            assert (guessed_data != declared_data) is (guess != declared_header)
            checks += 1
            results.append({'case': name, 'delimiter': delimiter, 'line_ending': repr(ending),
                            'guess': guess, 'declared_header': declared_header,
                            'declared_data_rows': len(declared_data), 'guessed_data_rows': len(guessed_data)})
assert sum(r['guess'] != r['declared_header'] for r in results) == 12
checks += 1
print(json.dumps({'python': platform.python_version(), 'platform': platform.system(),
                  'checks': checks, 'cases': len(results), 'results': results}, indent=2))
```

## Publisher and limits

Only CPython 3.10.12 on Linux was executed in this cycle. The version is stated rather than treating current documentation as proof of installed behavior. Other Python versions, arbitrary encodings, preambles, malformed records, multiline quoted fields, escape dialects, partial samples and schema validation are outside this probe. The repository's earlier CSV row-shape report concerns DictReader width, not Sniffer header intent.
