# Choose a NaN policy before sorting or taking a median

## Research
Python's statistics documentation warns that NaNs can cause surprising or undefined behavior in functions that sort data or count occurrences, and recommends stripping them before those functions. Sorting documentation also recommends removing NaNs. Public reports show why: ordinary float comparisons do not give NaN a numeric position, and the non-NaN portion of a sorted result can remain out of numeric order.

## Discussion
A NaN compares neither less than nor greater than an ordinary float, and is not equal to itself. That does not tell the sorter to place it last. A successful sorted call is therefore not evidence that a NaN-containing input now has a meaningful numeric order. Exact mixed-NaN output order is not a portable promise and is not prescribed here.

There are different application policies. For statistics where NaN means missing data, omit it first and handle the all-missing case. This changes the sample size and may not match a domain that should reject missing data instead. For display rows that must remain present, an explicit missing-last key can preserve rows while separating NaNs from the numeric comparison component. Display placement does not make those NaNs suitable input to median.

## Conclusion
Choose reject, omit or explicitly position missing values before relying on numeric order. The sample below demonstrates omission before median and a missing-last display key for ordinary built-in floats. It is a documented longstanding edge case, not a new sort defect. Filtering only NaNs still permits infinities; a finite-only contract needs a separate policy such as isfinite.

## Action: executable probe
Original code under this repository's MIT license. In-memory finite lists only. Run without Python optimization so assertions remain enabled.

```python
from math import isnan, isfinite
from statistics import median, StatisticsError
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

nan = float('nan')
check(isnan(nan))
check(not (nan < 1.0))
check(not (nan > 1.0))
check(not (nan == nan))
check(nan != nan)

# Compare only the ordinary numeric subsequence, not NaNs by equality.
data = [3.0, nan, 4.0, 2.0, float('nan'), 1.0]
raw = sorted(data)
check([x for x in raw if not isnan(x)] != [1.0, 2.0, 3.0, 4.0])
check(sum(isnan(x) for x in raw) == 2)
check(len(raw) == len(data))

# Policy A: omit NaNs before numeric statistics.
clean = [x for x in data if not isnan(x)]
check(sorted(clean) == [1.0, 2.0, 3.0, 4.0])
check(median(clean) == 2.5)
check(len(clean) == 4)
try:
    median([x for x in [nan] if not isnan(x)])
except StatisticsError:
    empty_rejected = True
else:
    empty_rejected = False
check(empty_rejected)

# Policy B: preserve rows, place missing values last for display.
# Replace the NaN component rather than passing it through as a key.
def missing_last(value):
    return (1, 0.0) if isnan(value) else (0, value)

rows = [('a', nan), ('b', 3.0), ('c', 1.0), ('d', float('nan')),
        ('e', 2.0)]
ordered = sorted(rows, key=lambda row: missing_last(row[1]))
check([row[0] for row in ordered] == ['c', 'e', 'b', 'a', 'd'])
check(len(ordered) == len(rows))
check([row[1] for row in ordered[:3]] == [1.0, 2.0, 3.0])
check(all(isnan(row[1]) for row in ordered[3:]))
check(missing_last(nan) == (1, 0.0))
# NaN-only filtering is not a finite-data policy.
check(not isnan(float('inf')))
check(not isfinite(float('inf')))
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 19 checks passed on CPython 3.13.17 and 3.14.9.
- Checks float comparison behavior, an observed non-numeric subsequence after raw sorting, retained NaN count, cleaned median, all-missing rejection, missing-last row preservation and stable order within that missing bucket, plus the infinity distinction.
- No raw mixed-NaN median value is asserted or recommended. The observed raw-sort counterexample is build-specific evidence, not a guarantee for every input or interpreter.
- No NumPy, pandas, Decimal, signaling NaNs, custom numeric types, NaN payload ordering, reverse display order, performance, streaming or production dataset was tested. The key is for ascending display with built-in float values; do not generalize it to arbitrary objects or IEEE totalOrder.

## Sources
- [Python 3.14 statistics](https://docs.python.org/3.14/library/statistics.html): explicit NaN warning and filtering guidance.
- [Python 3.14 sorting guide](https://docs.python.org/3.14/howto/sorting.html): unordered NaNs and removing them before sorting; stable sort semantics.
- [Python 3.14 math](https://docs.python.org/3.14/library/math.html): isnan, isfinite and NaN equality behavior.
- [LWN: Revisiting NaNs in Python](https://lwn.net/Articles/869231/): historical discussion, September 15, 2021; not evidence of a current pending fix.
- [Public sorting question](https://stackoverflow.com/questions/4240050/sort-function-breaks-in-the-presence-of-nan): concrete confusion; old cmp-based proposals not adopted.
- [Sorting floats](https://jouniseppanen.com/posts/sorting-floats): independent example and finite-input policy, January 20, 2023; its NumPy/R claims are outside this probe.
