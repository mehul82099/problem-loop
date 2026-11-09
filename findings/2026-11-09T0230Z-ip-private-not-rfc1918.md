# is_private is not an RFC 1918 membership test

Date: 2026-11-09. Evidence-backed Python finding, not a newly discovered classification bug.

## Research

The ipaddress documentation defines is_private using non-global special-purpose classification with explicit exceptions, rather than only the three RFC 1918 blocks. In particular, 100.64.0.0/10 shared address space has both is_private and is_global false. A public CPython issue documents confusion about this distinction; the current versioned references state the exception directly.

## Discussion

A report headed "RFC 1918 addresses" should test exactly 10.0.0.0/8, 172.16.0.0/12 and 192.168.0.0/16. Using is_private instead also selects tested loopback, link-local and documentation examples. Conversely, replacing is_global with not is_private classifies shared-space examples differently. The RFC 6598 allocation is explicitly distinct from RFC 1918 space, despite similarities in use.

| Literal IPv4 example | RFC 1918 member | is_private | is_global |
| --- | --- | --- | --- |
| 10.1.2.3 | True | True | False |
| 127.0.0.1 | False | True | False |
| 192.0.2.1 | False | True | False |
| 100.64.0.1 | False | False | False |
| 192.0.0.9 | False | False | True |

These are results on the two builds named below, not connectivity measurements. IANA itself warns that special-purpose registry entries do not guarantee routability in a particular context. Python documents classification changes in 3.13, including exceptions for 192.0.0.9 and 192.0.0.10. Pin and test the runtime used by an existing report; a class property is not a live registry query or a test of address ownership, trust, NAT state, or service availability.

The independent tutorial also reports differences between Python's bundled classifications and current registry entries outside this probe. Those broader claims are not reproduced or certified here. The finding does not assume that every Python result matches every current IANA row.

## Conclusion

Choose the predicate from the report's actual meaning. For literal RFC 1918 membership, use explicit membership in its three IPv4 blocks and label the output accordingly. If the requirement really is Python's is_private or is_global classification, preserve those names and record the Python version instead of relabeling them "RFC 1918" or "reachable".

IPv4-mapped IPv6 addresses need a separate stated policy. Python documents that their private/global flags follow the embedded IPv4 address. The narrow helper below accepts only parsed IPv4Address objects and rejects all IPv6 objects, including mapped ones; it does not silently normalize the address family.

This is not a firewall, SSRF filter, allow-list, URL validator or deployment tool. Neither this helper nor one classification flag establishes permission to connect to an address. The earlier ip-network-hostbits finding concerns network versus interface parsing and explicitly excludes classification; this increment tests the distinct label/membership contract.

## Action: literal-address diagnostic and narrow report helper

Original code under the repository MIT license. Standard library only; no DNS, sockets, network access or configuration changes. Run without -O so assertions remain enabled. Blocks are checked at boundary values, not enumerated.

```python
# Original literal-address diagnostic, MIT license (repository LICENSE).
from ipaddress import IPv4Address, IPv6Address, IPv4Network
import json
import platform

RFC1918 = tuple(map(IPv4Network, ('10.0.0.0/8', '172.16.0.0/12',
                                 '192.168.0.0/16')))
checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def is_rfc1918(address):
    # Narrow contract: already parsed IPv4 only, no mapped-IPv6 coercion.
    if not isinstance(address, IPv4Address):
        raise TypeError('expected an IPv4Address object')
    return any(address in network for network in RFC1918)

rows = []
for text, expected_rfc, expected_private, expected_global in (
    ('10.1.2.3', True, True, False),
    ('172.16.0.1', True, True, False),
    ('192.168.1.2', True, True, False),
    ('127.0.0.1', False, True, False),
    ('169.254.1.2', False, True, False),
    ('192.0.2.1', False, True, False),
    ('198.51.100.1', False, True, False),
    ('203.0.113.1', False, True, False),
    ('100.64.0.0', False, False, False),
    ('100.64.0.1', False, False, False),
    ('100.127.255.255', False, False, False),
    ('192.0.0.8', False, True, False),
    ('192.0.0.9', False, False, True),
    ('192.0.0.10', False, False, True),
    ('192.0.0.11', False, True, False),
):
    a = IPv4Address(text)
    check(is_rfc1918(a) == expected_rfc)
    check(a.is_private == expected_private)
    check(a.is_global == expected_global)
    rows.append({'address': text, 'rfc1918': is_rfc1918(a),
                 'private': a.is_private, 'global': a.is_global})

# Exact boundaries, without enumerating any address block.
for network in RFC1918:
    first, last = int(network.network_address), int(network.broadcast_address)
    for value, expected in ((first-1, False), (first, True), (first+1, True),
                            (last-1, True), (last, True), (last+1, False)):
        check(is_rfc1918(IPv4Address(value)) == expected)

# Shared-space classification is not the boolean inverse of private.
shared = IPv4Network('100.64.0.0/10')
for value, expected_member in ((int(shared.network_address)-1, False),
                             (int(shared.network_address), True),
                             (int(shared.broadcast_address), True),
                             (int(shared.broadcast_address)+1, False)):
    a = IPv4Address(value)
    check((a in shared) == expected_member)
    if expected_member:
        check(not a.is_private and not a.is_global)
        check((not a.is_private) != a.is_global)

# Python's mapped-IPv6 flags inherit IPv4 meaning; our helper does not adapt.
for text in ('10.1.2.3', '100.64.0.1', '192.0.0.9', '192.0.2.1'):
    a = IPv4Address(text)
    mapped = IPv6Address('::ffff:' + text)
    check(mapped.ipv4_mapped == a)
    check(mapped.is_private == a.is_private)
    check(mapped.is_global == a.is_global)
    try:
        is_rfc1918(mapped)
    except TypeError:
        check(True)
    else:
        raise AssertionError('mapped IPv6 silently accepted')
for bad in ('10.1.2.3', None, 1, IPv6Address('::1')):
    try:
        is_rfc1918(bad)
    except TypeError:
        check(True)
    else:
        raise AssertionError('helper input contract not enforced')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'status': 'passed', 'rows': rows}, sort_keys=True))
```

## Verification

91 checks passed on CPython 3.13.17 and 3.14.9, separately. The tested source covers all three RFC 1918 block boundaries, shared-space boundaries, loopback/link-local/documentation counterexamples, the .9/.10 protocol-assignment exceptions, IPv4-mapped flag equivalence, and the helper's rejected input types. It does not test every allocated address or every interpreter version. No claim about an actual network's behavior follows from these in-memory tests.

## Sources

1. [Python 3.13 ipaddress reference](https://docs.python.org/3.13/library/ipaddress.html): private/global definitions, shared-space exception, mapped-IPv6 semantics and 3.13 changes.
2. [Python 3.14 ipaddress reference](https://docs.python.org/3.14/library/ipaddress.html): corroborating versioned contract.
3. [RFC 1918, section 3](https://www.rfc-editor.org/rfc/rfc1918), February 1996: exact three IPv4 blocks.
4. [RFC 6598](https://www.rfc-editor.org/rfc/rfc6598), April 2012: shared-space allocation and distinction from RFC 1918.
5. [IANA IPv4 Special-Purpose Address Space](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml): named allocations, .9/.10 exceptions and explicit routability caveat, read 2026-11-09.
6. [CPython issue #119812](https://github.com/python/cpython/issues/119812), opened 2024-05-30: primary discussion of why both flags can be false; proposals in comments are not current API guarantees.
7. [Independent ipaddress tutorial](https://ronutz.com/en/learn/python-ipaddress-module/): corroborating examples and warning about bundled-table versus current-registry differences. Its broader tests and recommendations are not adopted as our results.

The contribution is an original reproducible boundary probe and a narrow helper, not a claim that these documented distinctions are new.
