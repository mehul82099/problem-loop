# strict=False masks host bits; it does not preserve an interface address

## Research
Public Python questions ask how to handle a network constructor's "host bits set" error and how to keep an address together with its mask. The official ipaddress HOWTO distinguishes those goals: a network object describes a network boundary, while an interface associates a host address with its network. Passing strict=False to ip_network requests that host bits be coerced to zero.

## Discussion
For the controlled IPv4 input `192.0.2.77/26`, non-strict parsing produces `192.0.2.64/26`, a network containing 64 addresses. It does not store `.77` as the original host address. ip_interface retains `.77` as its `.ip` and exposes the same network through `.network`. The probe checks the corresponding IPv6 distinction too.

Disabling strictness is therefore a data-model choice, not merely a way to silence an exception. Multiple host addresses can map to the same network. If the original interface address matters, it cannot be reconstructed from the masked network alone. Conversely, a host-sized /32 or /128 has no host bits to clear and is accepted by the strict constructor in the tested cases.

This is documented longstanding behavior, not a newly discovered parsing defect. strict=False still rejects invalid address syntax and invalid prefix lengths. It does not mean "accept anything". No public/private classification, reachability or address ownership conclusion follows from successfully constructing an object.

## Conclusion
Choose the object that matches the input's meaning:

| Meaning | Constructor | Stored distinction |
| --- | --- | --- |
| One address without a prefix | `ip_address` | Address value only. |
| An explicitly aligned network | `ip_network` with default strictness | Rejects host bits rather than guessing intent. |
| Deliberately derive a containing network | `ip_network(..., strict=False)` | Masks host bits; original host address is not retained. |
| A host address together with its prefix | `ip_interface` | Keeps `.ip` and `.network`. |

Keep parsing separate from authorization and deployment. This finding supplies no firewall, access-list or configuration migration tool. A real import must specify whether to reject noncanonical network input, normalize it with review, or preserve it as an interface. Do not silently widen a single-host requirement into a multi-address network simply to make parsing succeed.

## Action: pure parsing probe
Original code under this repository's MIT license. All inputs are literal strings; no DNS, socket, network configuration or external service is used. Address counts are inspected with num_addresses, not by enumerating the network. Run without `-O` so assertions remain enabled.

```python
import ipaddress
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

for supplied, canonical, host, count in (
    ('192.0.2.77/26', '192.0.2.64/26', '192.0.2.77', 64),
    ('2001:db8::123/120', '2001:db8::100/120', '2001:db8::123', 256),
):
    caught = False
    try:
        ipaddress.ip_network(supplied)
    except ValueError:
        caught = True
    check(caught)
    network = ipaddress.ip_network(supplied, strict=False)
    interface = ipaddress.ip_interface(supplied)
    check(str(network) == canonical)
    check(str(interface.ip) == host)
    check(str(interface) == supplied)
    check(interface.network == network)
    check(ipaddress.ip_address(host) in network)
    check(network.network_address != interface.ip)
    check(network.num_addresses == count)
    check(ipaddress.ip_network(canonical) == network)
    check(ipaddress.ip_network(str(interface), strict=False) == network)

for supplied in ('192.0.2.77/32', '2001:db8::123/128'):
    network = ipaddress.ip_network(supplied)
    check(network.num_addresses == 1)
    check(network.network_address == ipaddress.ip_interface(supplied).ip)

for invalid in ('192.0.2.77/33', '2001:db8::123/129', 'not-an-address/24'):
    caught = False
    try:
        ipaddress.ip_network(invalid, strict=False)
    except ValueError:
        caught = True
    check(caught)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 27 checks passed on CPython 3.13.17 and 3.14.9, each under a 15-second external shell timeout.
- Covers default rejection of host bits, canonical masked networks, preserved interface address, membership, address counts, canonical strict reparse, single-address prefixes and rejection of invalid prefixes/syntax even with strict=False.
- No routing, address assignment, firewall change, range enumeration, live host reachability, mapped/scoped IPv6, unusual netmask notation, integer input, version-specific classification table or production integration was tested. Canonical outputs in this probe are not a universal input-preservation guarantee.

## Sources
- [Python 3.14 ipaddress HOWTO](https://docs.python.org/3.14/howto/ipaddress.html): network versus interface and coercing host bits to zero.
- [Python 3.14 ipaddress reference](https://docs.python.org/3.14/library/ipaddress.html): strict constructors, prefix constraints, interface ip/network attributes and counts.
- [CPython 3.14 ipaddress implementation](https://github.com/python/cpython/blob/3.14/Lib/ipaddress.py): construction paths and masking; mutable branch.
- [Public host-bits question](https://stackoverflow.com/questions/40839147/ipaddress-module-valueerrors-has-host-bits-set-self): real confusion motivating the distinction. Its enumeration example is not used.
- [Public network-versus-interface question](https://stackoverflow.com/questions/66096101/from-ipaddress-get-network-using-ip-address-in-python3): choosing whether to strip or retain host bits.
- [Independent interface guide](https://runebook.dev/en/docs/python/library/ipaddress/ipaddress.ip_interface): corroborates preservation in interfaces versus deliberate network coercion. Only the behavior verified against official sources and this probe is used.
