# UTF-8 signature handling belongs at the stream boundary

## Research
A public Python CSV report shows a visually ordinary first header carrying U+FEFF after decoding a file with utf-8. Python documents utf-8-sig as a distinct codec: it skips the EF BB BF signature only at the beginning of a decoded stream. Plain utf-8 preserves the corresponding character. DictReader uses the first row as field names when none are supplied, so a hidden prefix can become part of a dictionary key.

## Discussion
For a feed whose contract is UTF-8 with an optional initial signature, utf-8-sig accepts both signed and unsigned input. This does not mean deleting U+FEFF everywhere. A second consecutive signature, a mid-stream marker and a signature inside a concatenated second file remain data after the first stream prefix is consumed. The probe also splits the signature across incremental decode calls: one decoder retains state and handles the split. Decoding each complete signed fragment independently gives a different result from concatenating the byte fragments and decoding once.

## Conclusion
Choose the encoding from the input contract, and apply optional-signature handling once per logical stream. For CSV, open known UTF-8 input with encoding='utf-8-sig' and newline='' when that contract permits a leading signature. Validate required headers separately. This codec does not detect arbitrary encodings or repair invalid UTF-8. Writing with utf-8-sig adds a signature, so do not apply the read-side choice blindly to output. This is documented behavior, not a new Python defect or a universal CSV repair.

## Action: executable probe
Original code under this repository's MIT license. In-memory bytes and text wrappers only. Run without Python optimization so assertions remain enabled.

```python
import codecs
import csv
import io
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

bom = codecs.BOM_UTF8
text = 'id,name\r\n17,Café\r\n'
plain = text.encode('utf-8')
signed = bom + plain
check(bom == b'\xef\xbb\xbf')
check(plain.decode('utf-8') == text)
check(plain.decode('utf-8-sig') == text)
check(signed.decode('utf-8') == '\ufeff' + text)
check(signed.decode('utf-8-sig') == text)
check((bom + signed).decode('utf-8-sig') == '\ufeff' + text)
check((b'x' + bom + b'y').decode('utf-8-sig') == 'x\ufeffy')
check(text.encode('utf-8-sig') == signed)
check(''.encode('utf-8-sig') == bom)

def rows(payload, encoding):
    with io.TextIOWrapper(io.BytesIO(payload), encoding=encoding, newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

fields, data = rows(signed, 'utf-8')
check(fields == ['\ufeffid', 'name'])
check('id' not in data[0] and data[0]['\ufeffid'] == '17')
fields, data = rows(signed, 'utf-8-sig')
check(fields == ['id', 'name'])
check(data == [{'id': '17', 'name': 'Café'}])
check(rows(plain, 'utf-8-sig') == rows(signed, 'utf-8-sig'))

# One decoder buffers a signature split across chunks.
decoder = codecs.getincrementaldecoder('utf-8-sig')()
check(decoder.decode(bom[:1], final=False) == '')
check(decoder.decode(bom[1:2], final=False) == '')
check(decoder.decode(bom[2:] + plain, final=True) == text)
# Independent decode calls instead treat each chunk as a new stream.
check(signed.decode('utf-8-sig') * 2 == text * 2)
check((signed + signed).decode('utf-8-sig') == text + '\ufeff' + text)

for payload in (b'\xff', bom + b'\xff'):
    try:
        payload.decode('utf-8-sig')
    except UnicodeDecodeError:
        failed = True
    else:
        failed = False
    check(failed)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 21 checks passed on CPython 3.13.17 and 3.14.9.
- Covers ordinary and signed UTF-8, U+FEFF preservation, one-prefix-only removal, encoding output including empty text, CSV header/key differences, equal parsed input with and without the signature, incremental split signature, independent versus concatenated streams and strict invalid-byte rejection.
- Does not test spreadsheet applications, other encoding families, filesystem writes, dialect detection, malformed CSV, network transports, all possible chunk boundaries or performance. Synthetic fixtures demonstrate the contract, not production impact. No claim that a signature authenticates an encoding or author.

## Sources
- [Python 3.14 codecs](https://docs.python.org/3.14/library/codecs.html): UTF-8 signature bytes, leading-only removal, encoding behavior and strict error handling.
- [Python 3.14 csv](https://docs.python.org/3.14/library/csv.html): DictReader first-row field names and newline guidance.
- [Unicode BOM FAQ](https://www.unicode.org/faq/utf_bom.html): UTF-8 is byte-oriented; an initial BOM can act as an encoding signature, subject to protocol rules.
- [Python public BOM discussion](https://discuss.python.org/t/utf-8-bom-not-being-consumed-when-opening-file/74870): December 21, 2024 report and correction. Its initial claim that only one byte was stripped was mistaken; the displayed Unicode character is the decoded three-byte sequence.
- [Reading Unicode file data with BOM](https://stackoverflow.com/questions/13590749/reading-unicode-file-data-with-bom-chars-in-python): community evidence for signed/unsigned decode differences; broad advice to use it everywhere is limited here to a known UTF-8 contract.
- [Row Remedy: remove a UTF-8 BOM](https://rowremedy.com/articles/remove-utf8-bom/): independent September 12, 2026 explanation of leading-only removal and preserving later bytes. No external cleanup script was copied or executed.
