# Security Policy

## Reporting a vulnerability

Please use GitHub's **Private Vulnerability Reporting**: go to the
[Security tab](../../security/advisories/new) of this repository and click
"Report a vulnerability". This opens a private draft advisory visible only to
the repository owner — nothing you write becomes public until a fix is ready
and you both agree to disclose.

Do not open a public issue for a security vulnerability. This protocol makes
cryptographic claims (signed, hash-chained, Bitcoin-anchored memory) — if you
find a way any of those claims don't hold, that is exactly the kind of report
this channel is for.

## Scope

In scope: the specification (`spec/`) and the reference engine (`engine/`) in
this repository. Out of scope: any individual installation's private memory
repository, which lives outside this project entirely under the installer's
own keys.

## Response

This is a v0.2, early-stage project maintained by one person. There is no SLA.
Reports will be acknowledged as soon as seen; severity and fix timeline are
judged case by case and communicated in the private advisory thread.
