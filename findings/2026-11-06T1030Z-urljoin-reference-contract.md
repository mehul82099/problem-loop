# urljoin resolves references, not API path prefixes

## Research
A long-running public Python question asks why urljoin drops the last base path segment or replaces the path when the second argument begins with a slash. A historical Locust pull request discusses why changing URL concatenation to urljoin could break a path-prefix contract. These are different operations, not interchangeable spellings.

## Discussion
Python documents urljoin as reference resolution: missing components come from the base. A trailing slash on the base changes which path is treated as a directory. A leading slash on the reference replaces the base path. A reference beginning with two slashes can replace the authority, and an absolute HTTPS URL can replace both scheme and authority. Dot segments can move outside a base path prefix while keeping the same host.

These are documented behaviors, not a new vulnerability report. A trailing slash on the base alone does not make arbitrary input stay under an API prefix. Likewise, checking only the resulting hostname does not establish path containment. The primary documentation warns against attacker-controlled references and states that parsing functions are not input validators.

## Conclusion
Decide what the second input means before selecting an operation. For a real URL reference, use reference resolution and apply the application's destination rules. For an identifier inserted into one route, define an identifier grammar and build that route rather than treating the identifier as a reference. The probe uses a deliberately narrow ASCII grammar to make that distinction visible; it is not a general URL validator or a network-access policy.

## Action: executable probe
Original code under this repository's MIT license. All addresses are inert example strings. No network requests are made.

```python
from urllib.parse import urljoin, urlsplit
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

base = 'https://example.test/api/v1/'
cases = [
    ('items', 'https://example.test/api/v1/items'),
    ('/items', 'https://example.test/items'),
    ('../items', 'https://example.test/api/items'),
    ('//other.test/items', 'https://other.test/items'),
    ('https://other.test/items', 'https://other.test/items'),
    ('?page=2', 'https://example.test/api/v1/?page=2'),
    ('#part', 'https://example.test/api/v1/#part'),
]
for reference, expected in cases:
    check(urljoin(base, reference) == expected)
check(urljoin(base.rstrip('/'), 'items') == 'https://example.test/api/items')
check(urljoin(base, '/items').startswith('https://example.test/'))
check(not urlsplit(urljoin(base, '/items')).path.startswith('/api/v1/'))

# A decoded identifier segment is not a URL reference.
# This deliberately narrow policy accepts only ASCII letters, digits, _ and -.
# It is not a general URL or hostname validator.
def item_url(identifier):
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
    if not identifier or any(char not in alphabet for char in identifier):
        raise ValueError('invalid identifier')
    return base + 'items/' + identifier

check(item_url('a_B-2') == 'https://example.test/api/v1/items/a_B-2')
for identifier in ('', '../x', '/x', '//other.test', 'https://other.test',
                   'x?y', 'x#y', 'two words', '%2f'):
    rejected = False
    try:
        item_url(identifier)
    except ValueError:
        rejected = True
    check(rejected)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9.
- Covers trailing/leading slashes, parent segments, authority/absolute replacement, query and fragment references, same-host/outside-prefix control, and narrow identifier acceptance/rejection.
- No live endpoint, redirects, DNS, browser parsing, proxy, percent-decoding pipeline, non-ASCII identifier or arbitrary scheme was tested. The fixed-base route helper is intentionally restrictive and does not accept general URL paths. Do not reuse it as an SSRF defense.
- Historical Python 3.14 alpha and file-URL differences were reviewed but are outside this probe; no relative-base or file-scheme compatibility claim is made.

## Sources
- [Python 3.14 urllib.parse](https://docs.python.org/3.14/library/urllib.parse.html): current urljoin semantics and parsing warnings.
- [RFC 3986, section 5.4](https://www.rfc-editor.org/rfc/rfc3986.html): reference-resolution examples, including rooted and parent paths.
- [Public urljoin question](https://stackoverflow.com/questions/10893374/python-confusions-with-urljoin): concrete slash and base-path confusion.
- [Locust PR 1217](https://github.com/locustio/locust/pull/1217): historical contract discussion, not a claim about current Locust behavior.
- [Joining URLs essay, July 2016](https://www.georgevreilly.com/blog/2016/07/12/PythonJoiningUrlsWithPosixpathJoin.html): path-building motivation; its custom join recipe is not adopted as a general solution.
- [CPython issue 125926](https://github.com/python/cpython/issues/125926): historical version differences that limit claims beyond the tested absolute HTTPS bases.
