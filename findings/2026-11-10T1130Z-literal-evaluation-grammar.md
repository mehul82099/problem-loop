# literal_eval is not a calculator or a resource-isolation boundary

Date: 2026-11-10. A tested supported-grammar finding, not a new AST defect.

## Research

Python's versioned AST references restrict literal_eval to supported literal/container forms. They explicitly distinguish it from arbitrary expression evaluation and warn that avoiding Python code execution does not prevent memory, stack or CPU exhaustion. A public question asks why 1+2 is rejected. The original arithmetic-acceptance tracker closed/fixed for Python 3.7; its earlier accepted real-number arithmetic examples are not today's contract.

The 2022 documentation change that removed the general safety claim is merged. An independent Python etc guide demonstrates the same arithmetic rejection but still describes use on untrusted strings as safe before giving a crash caveat. This finding follows the current official warning, not that broad safety wording. No crash or exhaustion example from any source is run here.

## Discussion

The probe accepts ordinary small literal containers but rejects `1+2`, indexing, list repetition, names, general calls and comprehensions. Parentheses around addition do not change its meaning into a literal. ast.parse can construct an AST for a valid expression such as 1+2 even though literal_eval refuses that expression. Syntax acceptance is a separate boundary from this conversion policy.

Do not turn that observation into an inaccurate ban on every operator or call-shaped spelling. Signed numbers and supported complex-number forms such as `1+2j` and `1-2j` are accepted in these runs. `set()` is a documented special case for an empty set; it does not authorize arbitrary calls. The reversed `1j+2` example is rejected on the tested builds. This is a supported-form grammar, not a calculator that happens to omit multiplication.

Python literal spelling is also not JSON spelling: True and None are accepted, while unquoted true and null are rejected. Quoted text stays text. Ellipsis is written `...` in the probe rather than assuming every object's repr is accepted source.

## Conclusion

Choose the data format first. Use literal_eval only where the supported Python-literal representation is intended, with separate application limits and trust decisions. If an interface requires arithmetic, define that language and its execution/resource policy separately; do not fall back to eval after a rejection. This finding supplies no evaluator or security wrapper.

Earlier repository findings address other interpreter grammars, JSON policies and literal-versus-pattern operations. A complete targeted search found no prior literal_eval treatment. The new scope here is the supported-form boundary, limited complex/set exceptions and the difference between non-execution and resource safety, not a universal claim about parsing safety.

## Action

Original MIT-licensed diagnostic below. It passed 3,373 checks each on actual CPython 3.13.17 and 3.14.9, including 1,111 small container vectors. The vectors have lengths 0 through 3 over ten atom values and are checked in list, tuple-containing-list and dictionary-containing-list forms. Run without optimization so assertions remain active.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import ast
import itertools
import json
import platform
checks = vectors = 0

def check(condition):
    global checks
    assert condition
    checks += 1

atoms = (None, True, False, -3, 0, 2, 1.5, 'a b', b'ab', Ellipsis)
# Ellipsis has a special source spelling, unlike repr(Ellipsis).
spellings = ('None', 'True', 'False', '-3', '0', '2', '1.5', "'a b'", "b'ab'", '...')
for text, value in zip(spellings, atoms, strict=True):
    check(ast.literal_eval(text) == value)
    check(ast.literal_eval(ast.parse(text, mode='eval')) == value)
for length in range(4):
    for indexes in itertools.product(range(len(atoms)), repeat=length):
        text = '[' + ','.join(spellings[i] for i in indexes) + ']'
        expected = [atoms[i] for i in indexes]
        check(ast.literal_eval(text) == expected)
        check(ast.literal_eval('(' + text + ',)') == (expected,))
        check(ast.literal_eval('{"items":' + text + '}') == {'items': expected})
        vectors += 1
check(ast.literal_eval('set()') == set())
check(ast.literal_eval('{1, 2}') == {1, 2})
check(ast.literal_eval('-2') == -2)
check(ast.literal_eval('1+2j') == complex(1, 2))
check(ast.literal_eval('1-2j') == complex(1, -2))
check(ast.literal_eval('  \t[1, 2]') == [1, 2])
# Tiny inert grammar counterexamples only. Never execute parsed source.
for text in ('1+2', '(1+2)', '2*3', '2**3', '[0]*3', '[1][0]',
             'name', 'str(1)', '[x for x in ()]', '1j+2', 'true', 'null'):
    try:
        ast.literal_eval(text)
    except ValueError:
        checks += 1
    else:
        raise AssertionError('unexpected accepted grammar: ' + text)
# Parsing a valid expression is weaker than accepting a literal form.
check(isinstance(ast.parse('1+2', mode='eval').body, ast.BinOp))
try:
    ast.literal_eval('[1,')
except SyntaxError:
    checks += 1
else:
    raise AssertionError('invalid syntax accepted')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'container_vectors': vectors, 'status': 'passed'}))
```

## Publisher and limits

The probe uses tiny fixed strings and fresh local objects. It checks successful conversions, AST-node input for atom cases, leading whitespace, selected supported complex forms, special empty-set handling, expression-versus-literal rejection and malformed syntax. It neither executes parsed source nor calls eval, compile, subprocess, filesystem or network functions.

No resource-exhaustion experiment, crash reproduction, sandbox, size/depth threshold, arbitrary AST-node acceptance, security audit, performance result or production-impact claim is made. Passing these small tests does not make untrusted input safe. Exact error messages and all possible exception classes are not tested. Current versioned documentation pages name newer patch releases than the binaries tested; they support the API contract, not exact binary identity. Repository CI is separate from local runs.

## Sources

Six public sources fetched and relevant sections inspected this cycle:

- Python 3.13 AST reference, supported structures and explicit resource warning. Broad text extraction cut off before the function, so the exact HTML method section was also inspected. https://docs.python.org/3.13/library/ast.html
- Python 3.14 AST reference, the same function scope, exception caveats and empty-set special case; exact HTML method section separately inspected. https://docs.python.org/3.14/library/ast.html
- Original arithmetic-support issue 75959, closed/fixed for 3.7. Old real-addition examples are historical, not current expected output. https://github.com/python/cpython/issues/75959
- Public malformed-node question about 1+2 and parentheses, not evidence that a third-party replacement is endorsed. https://stackoverflow.com/questions/77599953/malformed-node-in-ast-literal-eval-call
- Independent Python etc example: arithmetic rejection plus an overbroad safety description, qualified above. Its large crash input is not tested or reproduced here. https://pythonetc.orsinium.dev/posts/literal-eval
- Merged documentation PR 95919, October 2, 2022, removal of the general safety claim. https://github.com/python/cpython/pull/95919
