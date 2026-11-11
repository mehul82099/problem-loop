# An empty unquoted .env value can consume the next assignment

Date: 2026-11-11 (IST). Independent reproduction of public Node issue 67400, not an original vulnerability discovery.

## Research

[Node issue 67400](https://github.com/nodejs/node/issues/67400), opened November 11, reports that an empty unquoted .env value followed by a space or tab can take the next assignment line as its value. The report names v26.11.1 and v24.22.1 on macOS. This diagnostic independently tests only **Node v22.23.4 on Linux x64**, using util.parseEnv and synthetic strings.

The [versioned environment-variable reference](https://nodejs.org/download/release/v22.23.4/docs/api/environment_variables.html) says unquoted values are restricted to a single line and that surrounding whitespace is ignored unless quoted. The [versioned util reference](https://nodejs.org/download/release/v22.23.4/docs/api/util.html) describes parseEnv as parsing .env content into an object. The [versioned CLI reference](https://nodejs.org/download/release/v22.23.4/docs/api/cli.html) documents --env-file, but that entry point and its process-environment precedence were not executed here.

The [exact tagged parser source](https://github.com/nodejs/node/blob/v22.23.4/src/node_dotenv.cc), lines 106-205 inspected, checks for an immediate newline/empty remainder before trimming. Its trim_spaces includes newline among the removed characters. With a space before the newline, the early empty-value branch is bypassed and trimming advances into the next line. This explains the selected result; it is not a general proof for every .env grammar combination.

The [live issue API](https://api.github.com/repos/nodejs/node/issues/67400) confirmed open status at inspection. No fix, affected-release range, severity or current-main reproduction is claimed. The original report's other runtimes and --env-file result remain attributed, not adopted as local tests.

## Discussion

`ALPHA=\nBETA=owned` parses into two entries as expected in this probe. Adding one space between equals and the newline instead returns ALPHA with the string `BETA=owned` and omits BETA as a key. A third assignment remains its own entry. The effect reproduced with LF and CRLF and with four nonempty space/tab padding strings.

This is not merely trimming the wrong amount of whitespace from a value. It changes which key owns the next assignment text. A dictionary lookup for the swallowed key therefore sees absence, not an explicit empty string. Real configuration can contain secrets, but this test uses ALPHA/BETA/GAMMA and owned literal data only; no real environment file is read, displayed or loaded.

Controls are deliberately narrow: an empty value at the end of input, a quoted empty value with trailing whitespace, a nonempty unquoted value and an intervening comment line. They preserve the expected separation in the tested cases. Quoted empties are not offered as a complete migration recipe for arbitrary files or other parsers. The comment control also shows that not every whitespace-padded empty assignment consumes a later key; the actual following content matters.

## Conclusion

Test configuration parsing with empty values, horizontal whitespace and line endings together, and verify the resulting key set rather than only values that survived. The original public problem and exact-version code support a bounded parser-boundary finding, not a claim about all dotenv implementations.

The repository was searched for the issue ID, parseEnv, node_dotenv and empty env-file parsing. Its existing Python getenv flag-policy finding explicitly does not test .env parsing. No overlapping contribution was found. No dependency, patch, deployed configuration change or third-party issue/PR was made.

## Action

Original in-memory diagnostic under the repository MIT license. **25 checks passed on Node v22.23.4, Linux x64**: ten padding/line-ending cases each check the full mapping and BETA key presence, plus five controls. Assertions record affected behavior on the named build and should fail after correction. No assertions certify an unfixed behavior as the desired contract.

```javascript
// Original in-memory parser diagnostic, repository MIT license.
'use strict';
const assert=require('node:assert/strict');
const {parseEnv}=require('node:util');
let checks=0;const cases=[];
function check(a,b){assert.deepEqual(a,b);checks++;}
for(const ending of ['\n','\r\n']) {
 for(const padding of ['', ' ', '\t', '  ', ' \t']) {
  const text=`ALPHA=${padding}${ending}BETA=owned${ending}GAMMA=tail`;
  const actual=parseEnv(text);
  check(actual,padding?{ALPHA:'BETA=owned',GAMMA:'tail'}:
    {ALPHA:'',BETA:'owned',GAMMA:'tail'});
  check(Object.hasOwn(actual,'BETA'),!padding);
  cases.push({ending:JSON.stringify(ending),padding:JSON.stringify(padding),actual});
 }
}
check(parseEnv('ALPHA= \n'),{ALPHA:''});
check(parseEnv('ALPHA=\"\" \nBETA=owned'),{ALPHA:'',BETA:'owned'});
check(parseEnv("ALPHA=''\t\nBETA=owned"),{ALPHA:'',BETA:'owned'});
check(parseEnv('ALPHA= value \nBETA=owned'),{ALPHA:'value',BETA:'owned'});
check(parseEnv('ALPHA= \n#owned comment\nBETA=owned'),{ALPHA:'',BETA:'owned'});
console.log(JSON.stringify({node:process.version,platform:process.platform,
 arch:process.arch,checks,cases}));
```

## Publisher and limits

Exact committed code is read back and rerun separately from repository CI. No real .env file, process.env access, child process, file write, network request or credentials in the probe. No --env-file execution, other runtime, shell sourcing, duplicate-key policy, escape grammar, Unicode whitespace matrix, malformed content fuzzing, huge inputs or performance test. No fixed release, production impact, exploitability or universal parser/workaround claim.

## Sources

Six public sources fetched and inspected this cycle:

- Original problem report: https://github.com/nodejs/node/issues/67400
- Live status and exact original text: https://api.github.com/repos/nodejs/node/issues/67400
- Versioned .env single-line and whitespace rules: https://nodejs.org/download/release/v22.23.4/docs/api/environment_variables.html
- Versioned parseEnv API: https://nodejs.org/download/release/v22.23.4/docs/api/util.html
- Versioned CLI context, not locally executed: https://nodejs.org/download/release/v22.23.4/docs/api/cli.html
- Exact tagged native parser implementation: https://github.com/nodejs/node/blob/v22.23.4/src/node_dotenv.cc

Coverage is primary public report, official API/format documentation and versioned implementation. No independently tested second runtime is implied.
