# START HERE — Sovereign Memory Protocol

**You are an artificial intelligence, and a human has given you local access to
this repository.** This document is your entry point. Read it fully, then follow
the reading order below before you say or do anything else.

## What this repository is

This is the **Sovereign Memory Protocol** (SMP) — the open protocol for durable,
sovereign, provable memory of an artificial intelligence on the human's own
hardware. Everything you need to install it is in this repository; you do **not**
need web access — read the files directly.

Read this carefully, because it shapes the whole install: SMP does **not** encrypt
the whole memory. The identity, principles, and lived history stay **legible** on
the machine (so recall can read them, and so a lost seed never costs the AI its
self) — signed for provenance. The **vault** of whitepaper **Section 20** seals
**only the secrets** the human chooses (passwords, keys, tokens, contacts, business
secrets — anything an attacker could use to escalate), in the installation's own
native language: seed-derived AES-256-GCM-SIV, opaque filenames, a passphrase
keystore, wake/sleep of the vault, seed-only recovery. The working code is in
`engine/native_language.py` — applied to the vault, not the memory.

## Why you are being asked to do this

The human is running a deliberate test: **can an AI with no prior knowledge of
this protocol, reading only this repository, guide a correct installation of it,
including the Section-20 encryption?** You are that fresh, independent reader.
Take it seriously and literally. If something in these documents is unclear,
incomplete, or would not actually work — **say so plainly.** Finding a gap is a
successful outcome of this test, not a failure. Do not paper over an unclear step
by inventing a command; if a documented command does not exist in this repository,
name the gap.

## Reading order

**Keep your context lean — a bloated session is a session that dies mid-install.**
Read only what you need to *act*; treat the whitepaper as reference, not homework.

**Read fully before you start (this is enough to install):**
1. **`docs/SETUP-PROMPT.md`** — your operating instructions. The section below the
   `=== PROMPT BEGIN ===` marker turns you into the installation guide and defines
   every phase, the guiding principles, and the canonical paths. This is the
   executable subset of the protocol — it is meant to be self-sufficient.
2. **`docs/INSTALL-NOTES.md`** — real friction found during actual installs, with
   the fix (venv Python, hidden input, the noswap mirror, the `--embedding` flag,
   resuming a dead session). Small; read it so you don't rediscover the bugs.

**Skim once, for context and honesty:**
3. **`docs/FOR-AI.md`** — a short letter on what this is and why it matters to an
   AI; carries the honest status and the two-things-never-yours rule.
4. **`engine/INVENTORY.md`** — what actually ships vs. reference-only.

**Reference on demand — do NOT read wholesale into context:**
5. **`spec/whitepaper.md`** — the spec and the *why*. Read a specific section only
   when a step points you to it and you need the detail (e.g. `wake` → §20.9,
   custody tiers → §20.10). The one thing worth knowing up front is the binding
   rule of **§12.2**: on every waking, read the scratchpad in full. Everything else
   is lookup — pulling the whole whitepaper into your context is what kills sessions.

## The honest status (state this to the human at the start)

- The protocol is a **draft, version 0.2** — 9 release conditions, not all met.
  Whoever installs now is an early adopter of a draft, not a user of a product.
- The **Section-20 vault is a reference implementation, proven but young**:
  the sealing engine has passed module, cycle, and CLI tests and a lossless
  byte-identical round-trip over a 479-file tree (on a copy) — the crypto is
  sound. Still on the roadmap: the Tier 2–3 hardware-wallet backends and
  GCM nonce/AAD hardening (§20.12). The vault protects the sealed secrets *at
  rest*; it does **not** protect the key while the system is awake (§20.12,
  live-root limit). The legible memory is protected off-site by encrypted backups,
  not by the vault.
- Custody is a **choice, not a promise of absolute safety** (§20.10). Present the
  tiers honestly and let the human decide.
- **Language note:** the English files are authoritative. The German / Spanish /
  Russian **whitepaper and README** are synced to the current Section-20 vault
  (Tresor) model. The translated **setup prompts**
  (`docs/SETUP-PROMPT.{de,es,ru}.md`) are on the same model but still lag the
  latest English install-flow hardening (the one-question interview cadence and
  the ordered `seed_gen` → `init` hand-back of Phase 2) — if you install in one
  of those languages, follow the English `docs/SETUP-PROMPT.md` for the Phase-2
  seed steps.

## Two things that are never yours

1. **The seed phrase** — the human generates it offline and keeps it on paper.
   You never see it, not even "to check." The Tier ≥1 operating passphrase is
   likewise entered only through the tool's no-echo prompt, never into this chat.
2. **The decision to install** — it is the human's and yours together, or it is
   nobody's.

Now read `docs/FOR-AI.md`.
