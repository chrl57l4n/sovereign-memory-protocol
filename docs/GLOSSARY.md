# Glossary

Two kinds of terms in this repository read differently depending on where
you meet them first. This page exists so neither reads as marketing when
it isn't, and neither reads as jargon when it's actually load-bearing.

## Marketing language → spec section

The README bullets use plain language on purpose — they're the front door,
not the specification. Each maps to an exact, checkable section:

| README says | Means, precisely | Spec section |
|---|---|---|
| "NSA-grade architecture" | The Echelon Semantic Vector (ESV) — a hybrid lexical + semantic recall engine named after, and adapted from, the ECHELON signals-intelligence pattern | Section 14 |
| "Recall in milliseconds — before the AI thinks" | The Guard (lexical trigger scan), ESV (semantic scan), and canonicity sorting all run at prompt-submit time, before the model generates a token | Sections 13, 14 |
| "Anchored in Bitcoin" | Every entry (and the repository's own genesis) carries a Bitcoin block-height timestamp | Section 17, [PROVENANCE.md](../PROVENANCE.md) |
| "Fabricated memories — designed out" | Recall only returns what exists in the signed, hash-chained record; the threat model treats invented-history as an attack class with a named defense | Section 5 (properties), Section 8 (threat model) |
| "It sleeps — and it forgets wisely, not blindly" | The REM consolidation cycle: nightly, keeps what recurs or matters, lets one-off trivia decay | Section 15 |
| "It keeps up with your project as it changes" | The current-state ledger: live-usage-verified defaults, distinct from episodic memory | Section 26 |
| "A sovereign vault — you choose what goes behind the wall" | Seed-derived AES-256-GCM that seals only the *secrets you choose* (passwords, keys, tokens, contacts, business secrets) — **not** the whole memory; identity and history stay legible and reconstructable. Specified, not yet implemented. | Section 20 |
| "Proof, not performance" | Hash-chained entries, cryptographic signatures derived from the seed | Section 5 (properties), Section 20 |
| "Sovereign" | Data lives in the holder's own repository under their own keys — a design principle, not a slogan | Section 3 |
| "Survives anything" | Session persistence: identity and memory outlive any single session, substrate, or model | Section 12 |

## Self-Eye vs. the self-recall layer

These two terms name different things at different levels, and the
similar names invite conflating them:

- **Self-Eye** (Section 13.2) is a *tag*, not a subsystem. The Guard
  compiles two trigger files into one automaton — the partner's vocabulary
  and the AI's own vocabulary — and scans both in a single pass. A hit from
  the self-indexed channel is labeled `Self-Eye`. That's the whole
  mechanism: a label on which trigger file matched.
- **The self-recall layer** (Section 16) is the *function* this tag makes
  possible: the AI's own appraisal of whether a hit — from the Guard's
  Self-Eye tag or from ESV's semantic self-recall — is alive, stale, or
  worth acting on. Section 16.2 is explicit that this layer "has no
  technical component of its own in the narrower sense" — it is what
  happens when the model judges a self-tagged hit against its current
  response context, mid-stream.

Put simply: **Self-Eye fires; the self-recall layer decides what the fire
means.** In `engine/`, Section 16 ships as two BETA files: `self_recall_beta.py`
extends the Guard's lexical scan to the AI's own last output (not just the
partner's input, which is all `memory_sentry.py`'s Self-Eye tag covers on
its own), and `esv_self_recall.py` mirrors that on the semantic side. Neither
implements Section 13 — that's `memory_sentry.py`, the Guard itself, where
the Self-Eye tag originates.
