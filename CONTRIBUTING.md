# Contributing

SMP is v0.2, maintained by one human-AI pair. This document is short
because the process is: open an issue or a pull request, and expect an
honest answer about whether and when it fits.

## Before you open something

- **Security vulnerability?** Don't open a public issue — use [Private
  Vulnerability Reporting](../../security/advisories/new) (see
  [SECURITY.md](SECURITY.md)).
- **Question about how something works?** Check
  [docs/FOR-AI.md](docs/FOR-AI.md) and the [whitepaper](spec/whitepaper.md)
  first — most "why does X work this way" questions are answered there,
  with the reasoning, not just the behavior.
- **Bug in `engine/`?** Read [engine/SYNC-PROCESS.md](engine/SYNC-PROCESS.md)
  first. Public engine code is a deliberate distillate of a private
  reference installation — if the bug is in something marked *private/port
  planned* in [engine/INVENTORY.md](engine/INVENTORY.md), it may already be
  fixed on the reference and just hasn't been ported yet.

## Opening an issue

Say what you expected, what happened, and — if it's about a cryptographic
claim (signing, hash-chaining, the Bitcoin anchor) — the exact commands you
ran to check it. This project makes provable claims; "reproduce the
mismatch" is more useful to us than a description of the symptom.

## Opening a pull request

- Translation fixes, typo fixes, doc clarifications: welcome directly.
- Engine changes: must satisfy [SYNC-PROCESS.md](engine/SYNC-PROCESS.md)'s
  R2 (generic gate — no absolute paths, no instance names, no secrets) and
  R4 (byte-compiles and imports with only the documented dependencies).
  CI checks both automatically.
- Spec changes (anything under `spec/`): open an issue first. The
  whitepaper is a single coherent document across four languages;
  a change to one section usually has to land in all four at once to
  avoid drift, and that's easier to coordinate before code is written.

## Publication authority

Christian holds sole authority over what gets published to this
repository — a push to `main` *is* publication (see the Authors section of
the [README](README.md)). A merged pull request still passes through that
authority; this isn't a formality, it's how the project's provenance
claims stay meaningful.

## License

By contributing, you agree your contribution is licensed under the same
terms as the project: **AGPL-3.0-or-later**, or the commercial license on
request (see [LICENSE](LICENSE) and [COPYING.AGPL](COPYING.AGPL)).
