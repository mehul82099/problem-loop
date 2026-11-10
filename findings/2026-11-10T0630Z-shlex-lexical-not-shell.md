# shlex splits quoted words, not an executable shell language

Date: 2026-11-10. A tested lexical-contract finding, not a new Python defect.

## Research

Python's versioned shlex references describe a lexer for simple Unix-shell-like syntaxes. split defaults to POSIX mode with comments disabled. The richer shlex class can separate runs of punctuation, but the reference explicitly says it does not validate their semantic legality. POSIX describes token recognition, command parsing, word expansion, redirection and execution as separate stages of shell processing.

A historical public Python-list question expected command substitution and variable expansion from shlex. A separate CPython feature report about operator tokenization closed in 2016 after improved shell-like parsing was added. That closed report explains the punctuation_chars feature; it is not evidence that today's split is a full shell parser or an open regression. The independent guide likewise separates argument text from shell execution.

## Discussion

The probe parses `tool "$HOME" *.txt ~/notes` into four literal token values. No environment lookup, pathname matching, home expansion or process execution is performed. An unquoted command-substitution-looking string containing a space is split at that space, not parsed as a nested shell command. All examples remain inert strings in this test.

Default split also retains adjacent operator characters within ordinary words: `left|right >out` is not tokenized like a shell pipeline. punctuation_chars=True with posix=True and whitespace_split=True separates those operator runs, but accepts a run such as >>> without certifying a legal shell program.

There is another lossy boundary: `$HOME`, `"$HOME"` and `'$HOME'` all produce the same token value here. A later expansion pass over these returned values cannot recover the original quoting distinctions. Blindly expanding all resulting tokens is not an implementation of shell semantics.

## Conclusion

Use shlex.split only when a configuration field intentionally accepts this shell-like word syntax. Keep an already-structured argument list structured. If a design needs shell-language expansion or execution, treat that as a separate explicit requirement, not an incidental result of lexical splitting. Do not add a shell merely to make these examples expand. Tokenization and round-tripping do not establish that an executable, option set or argument value is authorized or safe.

The Unix-shell scope matters: these tests do not establish Windows command-line or PowerShell parsing. The earlier regex replacement-grammar finding also separates text from an interpreter's grammar, but this increment specifically tests shlex word values, lost quote context, comments and punctuation handling. A complete targeted repository check found no prior shlex finding; a historical Fish activation finding is about a different execution surface, not this lexer contract.

## Action

Original MIT-licensed diagnostic below. It passed 5,926 checks each on actual CPython 3.13.17 and 3.14.9, including 2,955 token vectors of lengths 0 through 3 over a 14-token vocabulary. Run without optimization so assertions remain active. No shell, subprocess, network, filesystem glob or environment lookup occurs in the probe.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import itertools
import json
import platform
import shlex

checks = 0
cases = 0

def check(condition):
    global checks
    assert condition
    checks += 1

# These strings are parsed as data. No process or shell is started.
check(shlex.split('tool "$HOME" *.txt ~/notes') ==
      ['tool', '$HOME', '*.txt', '~/notes'])
check(shlex.split('tool $(label value)') == ['tool', '$(label', 'value)'])
check(shlex.split('left|right >out') == ['left|right', '>out'])
check(shlex.split('left | right > out') == ['left', '|', 'right', '>', 'out'])
check(shlex.split('tool "a b" \'\'') == ['tool', 'a b', ''])
check(shlex.split('tool value # note') == ['tool', 'value', '#', 'note'])
check(shlex.split('tool value # note', comments=True) == ['tool', 'value'])
check(shlex.split('tool "# literal" # note', comments=True) ==
      ['tool', '# literal'])

# Quoting distinctions are deliberately lost in the token values.
for text in ('$HOME', '"$HOME"', "'$HOME'"):
    check(shlex.split(text) == ['$HOME'])

lexer = shlex.shlex('left|right >out', posix=True, punctuation_chars=True)
lexer.whitespace_split = True
check(list(lexer) == ['left', '|', 'right', '>', 'out'])
lexer = shlex.shlex('left >>> out', posix=True, punctuation_chars=True)
lexer.whitespace_split = True
check(list(lexer) == ['left', '>>>', 'out'])  # Tokens, not grammar validation.

for malformed in ('tool "unterminated', "tool 'unterminated", 'tool \\'):
    try:
        shlex.split(malformed)
    except ValueError:
        checks += 1
    else:
        raise AssertionError('malformed lexical input accepted')

# Inverse property on a bounded token vocabulary, not arbitrary shell scripts.
vocabulary = ('', 'plain', 'two words', '$NAME', '*.txt', '~/note',
              'a|b', 'semi;colon', "a'b", 'a"b', 'a\\b', '#tag',
              'line\nbreak', 'café')
for length in range(4):
    for tokens in itertools.product(vocabulary, repeat=length):
        args = list(tokens)
        text = shlex.join(args)
        check(shlex.split(text) == args)
        check(shlex.split(text, comments=True) == args)
        cases += 1
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'token_vectors': cases, 'status': 'passed'}))
```

## Publisher and limits

The bounded inverse checks establish split(join(args)) for the tested string vectors, including spaces, empty values, quotes, backslashes, metacharacters, a newline and non-ASCII text. They do not show that join preserves a shell script's original spelling or syntax. Named cases cover no expansion, default/operator-aware tokenization, comment policy, quote-context loss and malformed quoting/escape rejection.

This is not a shell implementation, sanitizer, process-launch wrapper, security audit, resource bound or performance benchmark. Arbitrary subclasses, source inclusion, huge inputs, NUL-containing process arguments, Windows execution and actual shell behavior are untested. No production incident or upstream patch is claimed. Versioned documentation pages currently identify patch versions newer than the two tested builds; those pages support the documented API, not exact binary identity.

## Sources

All six public sources fetched and relevant sections inspected this cycle:

- Python 3.13 shlex reference: split defaults, join inverse, POSIX parsing, Unix-only quoting warning and punctuation limits. https://docs.python.org/3.13/library/shlex.html
- Python 3.14 shlex reference: the same current lexical and punctuation contracts. https://docs.python.org/3.14/library/shlex.html
- CPython issue 43667, closed feature history, not an open current defect. https://github.com/python/cpython/issues/43667
- Python-list, May 13, 2005, original expansion-confusion example. Historical Python 2 code is not used here. https://mail.python.org/pipermail/python-list/2005-May/314989.html
- Independent guide, September 3, 2026, lexical parsing versus expansion/execution and separate argument-vector representation. Its safety wording is not a guarantee made by this finding. https://nalar.dev/parse-and-render-shell-arguments-safely-with-python-shlex/
- POSIX.1-2024 Shell Command Language, section 2.1, separate processing stages. No claim of complete conformance by shlex. https://pubs.opengroup.org/onlinepubs/9799919799.2024edition/utilities/V3_chap02.html
