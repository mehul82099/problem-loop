# `PyInitConfig_SetStr(config, name, NULL)` segfaults in `strlen` - the NULL guard skips the one type it allows

**Source:** [python/cpython#160962](https://github.com/python/cpython/issues/160962) (open, `type-bug`, `interpreter-core`, `topic-C-API`; code path verified against `main`; a maintainer reproduced it, another disputes whether it should be fixed)

## What happened

CPython's new `PyInitConfig` C API has a string setter whose NULL guard has the condition backwards in effect. In `Python/initconfig.c`, `initconfig_set_str` rejects a NULL `value` only when the option's type is **not** `PyConfig_MEMBER_WSTR_OPT` - the "optional wide string" type that exists precisely for options allowed to be unset:

```c
if (value == NULL && spec->type != PyConfig_MEMBER_WSTR_OPT) {
    initconfig_set_error(config, "config option string cannot be NULL");
    return -1;
}
```

For a `WSTR_OPT` option, NULL falls through to `utf8_to_wstr(config, value)`, whose first statement is `_Py_DecodeUTF8(str, strlen(str), ...)` - `strlen(NULL)` segfaults. Verified at the cited commit `d3a1e728` ([initconfig.c#L4369-L4376](https://github.com/python/cpython/blob/d3a1e7280bd74a16c5822cff9c77fa28da4d725e/Python/initconfig.c#L4369-L4376), [L4324-L4328](https://github.com/python/cpython/blob/d3a1e7280bd74a16c5822cff9c77fa28da4d725e/Python/initconfig.c#L4324-L4328)) and unchanged on `main` at the same line numbers (4369 and 4376). The reporter's suggested fix separates the two checks so NULL is always rejected.

## The discussion is the interesting part

A CPython member (NekoAsakura) **reproduced the crash on `main`** with a three-line C program - `PyInitConfig_SetStr(config, "prefix", NULL)` dies in `__strlen_avx2` from `utf8_to_wstr` at initconfig.c:4328, called from line 4376. Another member (picnixz) questions whether the fix is warranted at all: the docs describe `value` as "a null-terminated UTF-8 string", which arguably never permits NULL, so guarding may be "unnecessary churn". The reporter counters that the implementation explicitly checks for NULL already, so NULL looks like an intended input. The issue is one day old and unresolved between "documented contract violation, caller's fault" and "the API half-supports NULL and crashes instead of erroring".

## Who this bites

- Embedders using the new `PyInitConfig` API (PEP 741-style initialization) who pass a possibly-NULL `char*` through from their own configuration layer - instead of a catchable `-1` error return, the process segfaults inside `strlen`.
- The crash fires before any interpreter state exists, so there is no Python-level error to catch.

## Limits

- The stack trace and reproducer are from a maintainer's comment; the reporter (association NONE) did not run one. I verified the code path and line anchors on `main` and at the cited commit, but did not compile the reproducer myself (~77.7k stars repo).
- Whether NULL is contractually allowed is exactly what the two members disagree about; the finding takes no position on the fix, only on the verified behavior: today, `WSTR_OPT` + NULL crashes rather than errors.
- The `PyInitConfig` API is recent, so affected production embedders are likely rare; the intersecting risk is with binding generators and FFI wrappers that forward nullable strings.
