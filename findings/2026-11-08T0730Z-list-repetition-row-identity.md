# List repetition repeats references, not independent rows

Date: 2026-11-08. Scope: ordinary nested lists and one tuple containing a mutable list.

## Research

The official Python FAQ documents why [[0] * 2] * 3 does not create three independent rows. Sequence repetition references the existing elements multiple times; it does not copy those elements. A public tracker report was closed as not a bug and points to that FAQ. A community question also asks why deepcopy does not remove the aliasing already built into such a grid.

## Discussion

The repeated grid looks rectangular, but grid[0], grid[1] and grid[2] are the same row. Assigning grid[0][1] changes that row and is therefore visible through every alias. Replacing grid[0] itself with a new row is different: it replaces just that outer slot. Equal printed values are not enough to prove independent mutable state; the probe checks identity and the effect of mutation.

Constructing a new row inside each comprehension iteration gives separate rows for a scalar-filled grid. Merely writing [row for _ in range(3)] still reuses the named row. Fresh rows also do not imply fresh mutable cells: [[shared_cell] * 2 for _ in range(3)] has separate rows containing the same cell object. Construct the mutable cell at the level where independence is required.

Copying is not a generic de-aliasing operation. An outer list.copy() retains the original row references. A single deepcopy of the whole grid isolates it from the original but preserves its internal shared-row relationship, using the copy operation's memo. That is consistent with the earlier graph-alias finding; here the practical consequence is that copying a malformed independent-row assumption does not repair it.

An independent article gives useful row-construction examples, but its blanket suggestion of deepcopy for full independence is too broad for this grid. Its statement that tuple repetition is always safe regardless of the contained object is also too broad: a tuple can reference a mutable list, and that list can be mutated through either repeated reference. Both counterexamples are tested below. Immutable outer structure does not make reachable mutable contents independent.

## Conclusion

Choose the intended sharing graph, then create fresh mutable objects at each level that should be independent. Repetition is suitable when sharing the element is intended, including scalar-filled rows whose slots will later be replaced. Do not infer row independence from shape, use deepcopy as automatic alias removal or treat a comprehension as a guarantee when it only repeats an existing object.

## Action

The original MIT-licensed probe passed 26 checks each on CPython 3.13.17 and 3.14.9. It covers repeated rows, shallow/whole-graph deep copying, fresh rows, reused names, shared mutable cells, fresh cells, slot replacement, nonpositive repetition and mutable contents inside a tuple. It is not a numerical-array comparison, performance benchmark or exhaustive custom-copy-hook test.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import copy
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

grid = [[0] * 2] * 3
check(grid[0] is grid[1] is grid[2])
grid[0][1] = 7
check(grid == [[0, 7], [0, 7], [0, 7]])
outer_copy = grid.copy()
check(outer_copy is not grid)
check(outer_copy[0] is grid[0])
whole_deep = copy.deepcopy(grid)
check(whole_deep is not grid)
check(whole_deep[0] is not grid[0])
check(whole_deep[0] is whole_deep[1])
whole_deep[0][0] = 8
check(whole_deep == [[8, 7], [8, 7], [8, 7]])
check(grid == [[0, 7], [0, 7], [0, 7]])

fresh = [[0] * 2 for _ in range(3)]
check(fresh[0] is not fresh[1])
fresh[0][1] = 7
check(fresh == [[0, 7], [0, 0], [0, 0]])

# Reusing a named mutable object still aliases inside a comprehension.
row = [0, 0]
reused = [row for _ in range(3)]
check(reused[0] is reused[1] is row)
reused[1][0] = 5
check(reused == [[5, 0], [5, 0], [5, 0]])

# Fresh rows do not imply fresh mutable cells.
shared_cell = []
rows = [[shared_cell] * 2 for _ in range(3)]
check(rows[0] is not rows[1])
check(rows[0][0] is rows[2][1])
rows[0][0].append('x')
check(rows[2][1] == ['x'])
cells = [[[] for _ in range(2)] for _ in range(3)]
check(cells[0][0] is not cells[0][1])
check(cells[0][0] is not cells[1][0])
cells[0][0].append('x')
check(cells == [[['x'], []], [[], []], [[], []]])

# Slot replacement differs from mutating the shared object.
a = [[0]] * 2
a[0] = [9]
check(a == [[9], [0]])
check(a[0] is not a[1])
check([row] * 0 == [])
check([row] * -1 == [])
t = ([],) * 2
check(t[0] is t[1])
t[0].append('nested')
check(t[1] == ['nested'])
check(len(t) == 2)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding and deterministic diagnostic. Documented behavior, not a new runtime defect. The probe uses no private data, third-party packages or network calls. Run without optimization so assertions remain enabled.

## Sources

All six public sources fetched and inspected during this cycle:

- Python 3.14 FAQ, multidimensional-list construction: https://docs.python.org/3.14/faq/programming.html#how-do-i-create-a-multidimensional-list
- Python 3.14 sequence reference, repetition does not copy items: https://docs.python.org/3.14/library/stdtypes.html
- Python 3.14 copy reference, shallow/deep distinction and memo: https://docs.python.org/3.14/library/copy.html
- Historical tracker report, not-a-bug resolution: https://bugs.python.org/issue27135
- Community deepcopy question: https://stackoverflow.com/questions/4865821/deepcopy-on-nested-referenced-lists-created-by-list-multiplication-does-not-work
- Independent explanation; deepcopy and tuple blanket claims qualified above: https://hackernoon.com/why-doesnt-create-independent-nested-lists-in-python-the-hidden-list-multiplication-trap
