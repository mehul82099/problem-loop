# Default CSV output loses the difference between None and empty text

Date: 2026-11-06. A documented representation boundary, not a new CSV defect.

## Research

The [Python 3.14 csv reference](https://docs.python.org/3.14/library/csv.html) explicitly says the writer's None-to-empty-string transformation is not reversible. It documents QUOTE_NOTNULL: writers quote non-None fields, while matching readers interpret an unquoted empty field as None. The [3.13 reference](https://docs.python.org/3.13/library/csv.html) documents the same mode. This finding validates actual 3.13 and 3.14 builds, not every release since the constant was added.

A [community None/empty-string question](https://stackoverflow.com/questions/11379300/csv-reader-behavior-with-none-and-empty-string), a [database-export question](https://stackoverflow.com/questions/54816169/how-to-keep-null-values-when-writing-to-csv), and the [historical quoting-rules discussion](https://bugs.python.org/issue23041) record the practical need to distinguish these values. An [independent CSV guide](https://nalar.dev/read-and-write-csv-reliably-in-python/) notes the default loss and cautions about sentinel collisions. Database-specific import advice in older answers is not tested here.

## Discussion

With the default writer, None and empty text in the same row become indistinguishable empty fields. QUOTE_ALL quotes both and still loses the distinction. Once the representation is ambiguous, a reader cannot infer which original value was present.

QUOTE_NOTNULL preserves this particular distinction when both ends agree on the mode: None is unquoted empty, while empty text is quoted empty. A reader using the ordinary mode still returns empty text for both. The mode does not restore arbitrary Python types: the integer 7 returns as the string '7' in the probe. CSV dialect and application schema remain separate agreements.

## Conclusion

Choose a null representation before exporting data that must round-trip. Use matching reader and writer settings when QUOTE_NOTNULL fits both sides, or define a collision-safe representation accepted by the actual consumer. Do not assume spreadsheets, database importers or every CSV library share Python's null convention. Neither quoting everything nor replacing empty strings after reading can recover already-lost distinctions.

## Action

Original MIT-licensed probe using small in-memory rows only. It checks default and all-quoted ambiguity, matching versus mismatched QUOTE_NOTNULL reads, stringification of a number, and fields containing commas, quotes and a newline.

```python
import csv
import io
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def encode(row, quoting):
    stream = io.StringIO(newline='')
    csv.writer(stream, quoting=quoting, lineterminator='\n').writerow(row)
    return stream.getvalue()

def decode(text, quoting):
    return next(csv.reader(io.StringIO(text, newline=''), quoting=quoting))

row = [None, '', 'text', 7]
ordinary = encode(row, csv.QUOTE_MINIMAL)
check(ordinary == ',,text,7\n')
check(decode(ordinary, csv.QUOTE_MINIMAL) == ['', '', 'text', '7'])
check(encode([None, 'x'], csv.QUOTE_MINIMAL) ==
      encode(['', 'x'], csv.QUOTE_MINIMAL))

quoted = encode(row, csv.QUOTE_ALL)
check(quoted == '"","","text","7"\n')
check(decode(quoted, csv.QUOTE_ALL) == ['', '', 'text', '7'])

nullable = encode(row, csv.QUOTE_NOTNULL)
check(nullable == ',"","text","7"\n')
restored = decode(nullable, csv.QUOTE_NOTNULL)
check(restored == [None, '', 'text', '7'])
check(restored[0] is None)
check(restored[1] == '')
check(restored[3] == '7' and type(restored[3]) is str)
check(decode(nullable, csv.QUOTE_MINIMAL) == ['', '', 'text', '7'])

special = [None, '', 'a,b', 'say "yes"', 'line\nbreak']
check(decode(encode(special, csv.QUOTE_NOTNULL), csv.QUOTE_NOTNULL) == special)

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 12 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. No external CSV consumer, Python 3.12 build, database import, spreadsheet formula handling, file newline policy or schema inference was tested. Repository CI is separate.

## Publisher

One evidence-backed finding and bounded executable probe. No general serializer or production export changes.
