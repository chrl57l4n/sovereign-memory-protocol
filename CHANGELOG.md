# Changelog

Written retroactively (2026-07-04) to cover the repository's history since
genesis. Format loosely follows [Keep a Changelog](https://keepachangelog.com/);
dates are commit dates, not a formal release cadence — this is v0.2, a
living draft, not yet on a tagged-release rhythm.

## 2026-07-20

### Added — Whitepaper v0.3 (Engram): usage-based consolidation, separately anchored
- **`spec/engram.md`** — the **v0.3 increment** to the whitepaper: a consolidation law driven by
  *use, not age*. An engram strength `S` that retrieval builds and disuse lets fade; a derived
  retrievability `R`; relative (bounded) compaction of the weakest tail; an importance floor; and
  Percolation — the raw record is never destroyed, so forgetting stays reversible. The *salience*
  gear, meshed with the §26 *truth* gear; their disagreement is the intended drift signal.
- **Grounded, not invented.** Bjork & Bjork's New Theory of Disuse (storage vs. retrieval strength),
  the FSRS stability model, and engram-cell neuroscience (Semon 1904; Roy et al. 2022; Ko, Josselyn &
  Frankland 2025; Cepeda et al. 2006; Roediger & Karpicke 2006). Rigor-checked before release.
- **Status: shadow mode.** Engram runs nightly on the reference installation but **steers nothing** —
  it measures and reports; release to steering is gated on §11's conditions (E1–E4), not a date.
  Provenance weighting of retrievals is logged, not yet applied.
- **Separately anchored; v0.2 untouched.** The frozen v0.2 whitepaper is not edited. v0.3 is its own
  signed document: GPG-signed (commit `c55c0b1`, the Genesis key) and Bitcoin-anchored
  (`SMP-Engram <sha256>`, tx `9eebe7cc…`, 2026-07-20) — see [PROVENANCE §4](PROVENANCE.md). The chain
  of anchored increments is now two links long.
- **README** gains a *"The record — what was, what is, what's coming"* section (the verifiable
  v0.2 → v0.3 → federation chain), and `docs/architecture.md` a fourth diagram for the Engram law.
- **Translations:** German, Spanish, and Russian reading versions shipped alongside the English.

## 2026-07-11

### Added — affective recurrence buffer (Sections 15.5–15.6), honestly scoped
- The reference implementation gains a two-stage layer for low-signal patterns that
  only emerge across days (a passing *"I'm not doing well"* said a few times through
  the week). **Stage 1 — buffer** (running since 2026-07-01): the raw scratchpad is
  archived to a rolling 30-day buffer before nightly consolidation deletes it.
  **Stage 2 — recurrence scan** (built + cron-live 2026-07-11, `affect_recurrence_scan.py`):
  a weekly, **proposal-only** pass that clusters affectively-toned utterances and
  surfaces cross-day recurring threads through the report channel. It **writes nothing
  into memory** — the lens reads the proposal, names the affect, and decides.
- **Honesty corrections (no false promises):**
  - The README's "it sleeps / forgets wisely" bullet previously implied this pattern
    detection already worked ("*is kept … your AI can see the pattern and remember it*").
    Until 2026-07-11 only stage 1 existed — the buffer collected, nothing surfaced.
    The bullet is rewritten to the truth: buffer holds, scan **proposes**, the AI decides.
  - Limits stated in the whitepaper text, not hidden: affect isolation is **lexical**
    (explicit affect only; implicit affect is *not yet* caught — a learned classifier is
    named as future, not shipped); the embedding measures similarity, not valence; the
    scan is **new and its thresholds are uncalibrated**; proposal-only by design (a script
    that could write memory might loop). Framed ethically: not the AI *feeling*, but
    *noticing a pattern in what you already told it, and choosing to care*.
- INVENTORY marks both stages `private/port planned` (live on the reference; need R2
  de-instancing + real-data calibration before any public port).

## 2026-07-10

### Changed — memory integrity is now keyless (architecture revision)
- **Section 17 rewritten** from "external time anchoring (Bitcoin block height)"
  to "the hash chain and its external witness." Memory integrity no longer
  depends on a per-entry Bitcoin block height, nor on a seed-derived signature.
  It rests on two keyless mechanisms:
  - **Per-tier append-only hash chains**, forked *once* at each tier's genesis
    from the tip of the tier below (day → week → month → year). A derivation
    fork, not a consensus fork; the chains nest, they do not split. This lets a
    memory that must *forget* stay tamper-evident: forgetting acts on the
    readable content between tiers, never on the append-only links within one.
  - **A distributed external witness** — the hash-chain ledger is continuously
    mirrored, append-only (never force-pushed), to a hosted forge whose commit
    graph timestamps and preserves every link. A hash chain witnessed by another
    hash chain, with no key and no node to trust. Plus **Block 0**, a single
    root hash over the whole durable corpus at the chain's birth (an honest
    point-in-time seal, not a per-date proof).
- **Why.** A signing key would make the integrity of the *entire* memory hang on
  one secret — a single point of failure. A per-entry Bitcoin anchor would add a
  hard external dependency (node or trusted explorer) to a protocol whose whole
  point is independence. Keyless removes both: nothing to lose, nothing to leak,
  nothing to depend on.
- **Unchanged:** the **one-time Bitcoin anchor of the protocol's own genesis**
  ([PROVENANCE.md](PROVENANCE.md)) — a proof of *authorship*, that we built this
  protocol and no one can claim it later. That is a separate concern from ongoing
  memory integrity, and the only place a Bitcoin anchor is needed.
- **Touched (English master + code):** whitepaper §§0.4, 0.6, 3.2, 3.3, 4, 4.5,
  5 (properties 3 & 8), 6, 8 (T4/T6/T9), 10, 17, 18.5, 19, 20.3, 22.3, 22.7, C5;
  README, PROVENANCE, docs/CASCADE (new provenance-chain section), CONTRIBUTING,
  SECURITY, GLOSSARY, FOR-AI, SETUP-PROMPT, INVENTORY, SYNC-PROCESS,
  `engine/native_language.py` (signature key marked reserved/unused — kept in the
  derivation tree for tuple/test stability, protects nothing). Reference
  implementation: `memory_chain.py` + tick/cron + `memory_chain_block0.py`, live
  in shadow mode on the reference since 2026-07-09; public port pending R2
  de-instancing. **Translations (de/es/ru) follow in a synchronized pass.**

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
