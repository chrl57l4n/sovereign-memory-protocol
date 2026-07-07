# Changelog

Written retroactively (2026-07-04) to cover the repository's history since
genesis. Format loosely follows [Keep a Changelog](https://keepachangelog.com/);
dates are commit dates, not a formal release cadence — this is v0.2, a
living draft, not yet on a tagged-release rhythm.

## 2026-07-07

### Milestone — end-to-end verified on independent hardware
- An independent AI (Claude Code), reading **only this public repository**,
  installed SMP autonomously on separate hardware and demonstrated every
  headline claim of the README and whitepaper:
  - **Vault crypto** — T5 backup/restore, T6 wake→edit→sleep→wake, and T6b
    **cold recovery from the seed alone** (12 words), all green.
  - **Recall reflex** — the freshly installed instance answered a question
    from its installed memory, not the base model's guess.
  - **All three recall layers** — the literal Sentry (word → memory pointer),
    the semantic ESV (a cross-language hit with **zero** lexical overlap still
    ranked the meaning-equivalent chunk first), and the canonicity sorter
    (`ESV_CANON_WEIGHT` lifting source chunks above their retellings, visibly
    reordering results). On the empty template memory the ESV honestly returns
    "nothing strong" below threshold — the intended behaviour, not a defect.
- This is the verification behind the vault's move from *specified* to
  *shipped* (below): the protocol was installed and exercised by someone who
  did not write it.

### Added
- The Section-20 **native-language vault** as a shipped, verified feature:
  `engine/native_language.py`, `engine/seed_gen.py`, `engine/verify_pass.py`
  (seed-derived AES-256-GCM-SIV, scrypt passphrase door, opaque filenames,
  wake/sleep, seed-only recovery). Test suite `engine/tests/` — 7/7 green.
- 12-or-24-word seed choice throughout (was fixed 24).
- `START-HERE.md`, `docs/INSTALL-NOTES.md` — AI entry point and real-friction
  install notes.
- `integrations/open-webui/recall_filter.py` — reflex recall (Sentry + ESV +
  sorter) as an Open WebUI inlet filter behind any served model.

### Changed
- Vault status flipped from "specified — on the way to 1.0 / not yet
  implemented" to "new in v0.2 — shipped and verified" across `README.md`,
  `docs/GLOSSARY.md`, and `spec/whitepaper.md` §20.4 (GCM-SIV + scrypt door
  noted) — mirrored in all four languages. Federation between installations
  (v0.3) remains the one labelled roadmap item.

### Fixed
- `engine/verify_pass.py` spawned its `wake`/`sleep` subprocesses with a bare
  `"python3"`, which on a venv-based system resolves to the interpreter
  without `cryptography`/`mnemonic` and fails with `ModuleNotFoundError` —
  the single hole the acceptance install hit. Root-fixed: subprocesses now
  use `sys.executable`; `docs/SETUP-PROMPT.md` generalizes the venv-python
  convention to every engine command. Independently confirmed by the
  installing agent, which proposed the same fix.

## 2026-07-04

### Added
- Section 27 — self-documentation guardian (baseline manifest, per-delta
  settle gate, two enforcement layers).
- Section 12.2 — scratchpad-read-in-full-at-every-waking obligation.
- `spec/whitepaper.es.md`, `spec/whitepaper.ru.md` — full Spanish and
  Russian reading versions of the whitepaper.
- `README.es.md`, `README.ru.md`; `docs/FOR-AI.es.md`, `docs/FOR-AI.ru.md`;
  `docs/SETUP-PROMPT.es.md`, `docs/SETUP-PROMPT.ru.md` — all four
  installation-path documents now exist in all four languages.
- `engine/esv_tier.py` — ported from the reference installation; fixes a
  real broken import in `engine/esv_query.py`.
- `engine/INVENTORY.md`, `engine/SYNC-PROCESS.md` — full spec↔engine
  coverage table and the six rules governing how a component moves from
  the private reference installation into this public repository.
- `SECURITY.md` — private vulnerability reporting via GitHub's built-in
  feature, no maintainer inbox required.
- `.github/workflows/engine-invariants.yml` — CI: every push touching
  `engine/**` is checked for the R2 (no absolute paths) and R4
  (byte-compile + import) invariants.
- `pyproject.toml`, `engine/README.md` — reproducible dependency pinning
  and an entry point for newcomers to `engine/`.
- Anchor links from all four READMEs to the specific whitepaper sections
  they mention (previously named a section number with nothing to click).
- `docs/GLOSSARY.md` — marketing-language-to-spec-section table, and the
  Self-Eye vs. self-recall-layer terminology distinction.
- Docstring convention: every `engine/*.py` module now names its spec
  section directly in the module docstring.
- This file.

### Fixed
- All of the above originated from an independent full-repository review
  (a second model, MiniMax, acting as external verifier — see
  `motoko-memory/motoko/audits/2026-07-04-m3-repo-review.md` for the
  private working notes). Translation fixes across the new Spanish and
  Russian documents from the same review pass.
- `README.de.md` was missing an entire bullet ("available now:
  installation via dialogue") that English, Spanish, and Russian already
  had — added and linked.
- `_paths.py`'s own docstring contained the literal path pattern the R2
  audit invariant forbids, so the invariant was never actually satisfiable
  as stated — corrected.

## 2026-07-03

### Added
- Section 26 — implementation of the current-state ledger (living
  defaults): the protocol's answer to an AI recommending a tool or
  approach its partner has already moved on from.
- Reference implementation for Section 26 (`experience_log.py`,
  `state_ledger_verify.py` in the private reference installation; ported
  the same day).

## 2026-07-02

### Added
- Section 24 — the Guardians (self-maintenance across five classes:
  structural hygiene, concept coverage, layer health, system
  self-observation, recall calibration).
- Section 25 — the report channel (push notification + scratchpad
  transcript, so a "silent" channel is distinguishable from a "dead" one).
- Release condition C9.
- `docs/FOR-AI.md` — the appendix written for an AI reading this repo.
- The normative setup prompt (Section 22.2), given a prominent install
  entry point in both READMEs.

## 2026-07-01

### Added
- Full English whitepaper (v0.2 reading version) — faithful translation
  from the v0.1 working draft, digits and terminology normalized.

### Changed
- English became the default language throughout the repository; German
  moved to `.de.md` companion files (license, cascade docs, templates).
- README language selector; several passes clarifying the "forgets
  wisely, not blindly" sleep bullet with concrete examples.

## 2026-06-30 — Genesis

### Added
- Sovereign Memory Protocol v0.2: initial public repository.
- `PUBKEY.asc` — public key for genesis signature verification.
- `PROVENANCE.md` — the repository's own genesis anchored in **Bitcoin
  block 956116**, GPG-signed. The first thing this protocol proves is its
  own claim to prove things.
- README with the v0.2 status section and the honest-features framing
  (running today / demonstrated / specified-not-yet-implemented).
