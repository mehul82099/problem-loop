# JSON numeric spelling, float range and strict strings are separate contracts

Date: 2026-11-09. Evidence-backed Python numeric-boundary finding, not a new decoder defect.

## Research

Python's versioned json references document that strict=True controls unescaped control characters inside strings. It does not reject the NaN, Infinity and -Infinity extensions accepted by default. parse_constant can reject those named tokens. Ordinary fractional/exponent tokens instead use parse_float, which defaults to float conversion.

RFC 8259 excludes NaN and Infinity from its number grammar, but explicitly discusses 1E400 as a JSON number that can cause range/interoperability problems. Rejecting that exponent under a finite-float application policy is therefore different from rejecting a non-JSON named constant. A July 2020 public question asks how to use the named-constant hook. Independent numeric tutorials also distinguish overflow from that hook; their wider application advice is not adopted as this probe's contract.

## Discussion

On both tested builds, json.loads of 1e400 returns positive infinity even with a rejecting parse_constant hook, because that hook is not invoked for an ordinary exponent token. The probe records hook calls to make the routing visible. A parse_float callback can reject a nonfinite result of conversion when finite binary floats are the intended representation.

| Boundary | Mechanism illustrated | Remaining gap |
| --- | --- | --- |
| Named NaN/Infinity extensions on input | parse_constant that raises | Does not intercept ordinary exponent tokens |
| Finite binary-float conversion | parse_float plus isfinite | Does not guarantee exactness or field range |
| Nonfinite float output | allow_nan=False | Separate from input policy and later calculations |
| Literal controls inside strings | strict=True, the default | Not a whole-document or numeric-policy switch |

Quoted text such as "NaN" remains ordinary text under this policy. null, true and false are not numeric constants passed to parse_constant. Integer tokens still use the separate default int path.

Finite does not mean faithful: 1e-400 becomes zero in these runs, and 0.1 is not represented as an exact decimal fraction by binary float. parse_float=Decimal represents the tested 1e400 value as finite, which is a different representation and range policy, not a drop-in version of the finite-float rule. It needs its own application limits and output decisions.

## Conclusion

Choose input spelling, numeric representation, finiteness and domain range separately, and test the outbound encoder too. A demonstration finite-float loader can combine the two numeric hooks, but that is not a general strict JSON validator. It still accepts the usual JSON shapes and default integer behavior and has no size, depth, schema, duplicate-name, Unicode or resource-isolation policy.

Earlier repository findings cover duplicate object names and record framing. The framing example already uses allow_nan=False; this increment does not claim that encoder option is new. It adds independently tested decoder-hook routing, ordinary exponent overflow and the finite-versus-exact boundary. No combined production loader is supplied.

## Action

Original code under this repository's MIT license. Bounded in-memory text only. Run without Python optimization so assertions remain enabled.

```python
import json
import math
import platform
from decimal import Decimal

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def rejects(call):
    try:
        call()
    except ValueError:
        check(True)
    else:
        raise AssertionError('expected rejection')

def no_constant(token):
    raise ValueError('named numeric extension rejected')

def finite_float(token):
    number = float(token)
    if not math.isfinite(number):
        raise ValueError('outside finite float range')
    return number

def read_finite_float(text):
    # Demonstration policy only: no transport/schema/resource validation.
    return json.loads(text, parse_constant=no_constant, parse_float=finite_float)

for token in ('NaN', 'Infinity', '-Infinity'):
    check(not math.isfinite(json.loads(token, strict=True)))
    rejects(lambda: read_finite_float(token))
    check(read_finite_float(json.dumps(token)) == token)
    rejects(lambda: json.dumps({'n': [json.loads(token)]}, allow_nan=False))

seen = []
def record_constant(token):
    seen.append(token)
    return None
check(math.isinf(json.loads('1e400', parse_constant=record_constant)))
check(seen == [])
check(json.loads('[NaN,Infinity,-Infinity]', parse_constant=record_constant)
      == [None, None, None])
check(seen == ['NaN', 'Infinity', '-Infinity'])

# Valid JSON exponent syntax may exceed binary-float range.
for sign in ('', '-'):
    for exponent in range(300, 411):
        token = sign + '1e' + str(exponent)
        exact = Decimal(token)
        check(exact.is_finite())
        converted = float(token)
        if math.isfinite(converted):
            check(read_finite_float(token) == converted)
        else:
            rejects(lambda: read_finite_float(token))
        check(json.loads(token, parse_float=Decimal) == exact)

check(read_finite_float('1e-400') == 0.0)
check(Decimal('1e-400') != 0)
check(Decimal.from_float(read_finite_float('0.1')) != Decimal('0.1'))
check(read_finite_float('9007199254740993') == 9007199254740993)
check(type(read_finite_float('9007199254740993')) is int)
check(read_finite_float('[null,true,false,"NaN",1.5]')
      == [None, True, False, 'NaN', 1.5])
rejects(lambda: read_finite_float('{"nested":[1e400]}'))
rejects(lambda: read_finite_float('{"nested":[NaN]}'))
# strict controls unescaped string controls, not named numeric extensions.
rejects(lambda: json.loads('"a\nb"', strict=True))
check(json.loads('"a\nb"', strict=False) == 'a\nb')
check(json.loads('"a\\nb"', strict=True) == 'a\nb')
print(json.dumps({'checks': checks, 'exponent_cases': 222,
                  'python': platform.python_version(), 'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.13.17** and **3.14.9**: **693 checks passed per build**. Includes 222 positive/negative exponent cases from 300 through 410, named constants, recorded constant-hook routing, quoted lookalikes, nested rejection, encoder rejection, integer preservation, underflow/precision limits, and raw-versus-escaped string controls. Decimal is used as a separate representation reference for those bounded tokens, not as the same finite-float policy.

No arbitrary documents, large integer stress, maximum nesting, custom decoders, third-party JSON libraries, decimal serialization, production requests or performance were tested. The helper processes an already-created string and is not a transport or resource boundary. Finite floats can still violate an application's allowed magnitude, precision or type.

## Publisher

One bounded finding and probe. Full targeted repository matches were inspected and nearby duplicate-name/framing material read. Shared encoder-option coverage is disclosed above; no history was rewritten.

## Sources

1. [Python 3.13 json reference](https://docs.python.org/3.13/library/json.html), primary documentation: strict strings, parse_float, parse_constant and allow_nan.
2. [Python 3.14 json reference](https://docs.python.org/3.14/library/json.html), primary documentation: same decoding/encoding contracts and accepted numeric extensions.
3. [RFC 8259, section 6](https://www.rfc-editor.org/rfc/rfc8259), standard: number grammar excludes named NaN/Infinity, while 1E400 is a range/interoperability example.
4. [json.load for not allowing nan and inf values](https://stackoverflow.com/questions/62678653/json-load-for-not-allowing-nan-and-inf-values-load), July 1, 2020 community question/answer: callback rejection of named constants.
5. [Numbers, precision and NaN](https://topolearnapp.com/learn/py-json/numbers), independent tutorial: exponent overflow and numeric representation. Its general money/conversion recommendations are outside this finding; no automatic null substitution is adopted.
6. [Python JSON: Reject Duplicate Keys, NaN and Infinity](https://prepwithproof.com/blog/python-json-duplicate-keys-nan-infinity), October 30, 2026 independent lab: numeric-hook distinction and finiteness limits. Its larger loader and reported tests are not used as local verification or copied into this narrow probe.
