# Changelog

Written retroactively (2026-07-04) to cover the repository's history since
genesis. Format loosely follows [Keep a Changelog](https://keepachangelog.com/);
dates are commit dates, not a formal release cadence — this is v0.2, a
living draft, not yet on a tagged-release rhythm.

## v0.5 "The Answered Guardian" — signed 2026-10-07 (Bitcoin anchor: `PROVENANCE.md` §6)

A whitepaper increment (`spec/answered-guardian.md`), offered at the size its field record carries.

### Added
- `spec/answered-guardian.md` — three pillars: the answered guardian (a guardian over a state the AI must
  repair needs a specified actor and a waking act, not only a report), self-documentation as a component,
  and convergent verification by a second model. Field record measured twice (2026-09-19, 2026-10-02).

- `spec/answered-guardian.md` §7a (added 2026-10-05) — **the gateway**: a generated signpost file under a
  byte budget that a fresh session reads once before its first answer; the builder shrinks itself and says so;
  emergency gateway on build failure; two paths to the file; an unattended, counted "hello" probe.
  **Young:** built 2026-10-04, three fresh sessions observed. Included on the human partner's decision as an
  explicit exception to the paper's own deferral rule (§1.4).
- `engine/gateway_build.py` + `engine/tests/test_gateway_build.py` — de-instanced extraction of the gateway builder,
  **public/BETA**, ported against sync rule R1 (two weeks) with the deviation named in `engine/INVENTORY.md`.
  Not the running code of the reference installation. Eight tests (G1–G8) for the deterministic properties.
- `docs/INSTALL-NOTES.md` — "Waking wiring": start duty, gateway block, probe.
- `docs/SETUP-PROMPT.md` — **Phase 4b** (optional, BETA): the installing AI wires the gateway with the shipped
  builder (session-start hook, gate block, counted probe) and Phase 8 asks for the probe result. Short form in
  the three translated prompts. `START-HERE.md` names the gateway in the reading order and the honest status.
  Without this the code shipped but no installation would have wired it (noticed by the human partner on the
  day of release). The documented builder call was run against a fresh memory made from `templates/`.

### Decided — Engram §6 review (`spec/engram.md` §10, all four languages; README ×4)
- The rank damping of dormant entries (×0.9 on the reference installation since 2026-08-25, disclosed 2026-09-23)
  is **withdrawn** as of 2026-10-05, two days before the announced date. Measured over 12.4 days and 1,424 queries:
  37 dormant hits surfaced despite it (28 files, all since reanimated), 29 were lost only because of it (25 files,
  17 still dormant); lock-in marker zero but weak. Losses were not small against returns and no benefit had been
  measured. §6 stands as written. The public engine never contained the damping.

### Corrected and measured — Engram §10/§11 (`spec/engram.md` §10, all four languages; added 2026-10-06)
- **Correction of the entry above.** The counts of 2026-10-05 included automated sessions and hand-run test queries
  (509 of 1,424 queries). Over attested use: 915 queries, 22 returns (19 files), 18 losses (18 files). Nine of the
  28 "returned" files had been woken by test queries only. The decision stands; the entry above is left as written.
- **§11 measured for the first time (2026-10-06):** E1 not met (stuck set 0 → 34, Gini 0.139 → 0.244 over 82 nights);
  E2 built that evening (the recall log now carries raw evidence of provenance and has one reader), not yet shown over
  an observation window; E3 not met (Engram compacts nothing on the reference installation); E4 met for the score by a
  regression test, open in substance (the cascade decides by `R` when a daily entry enters the semantic index).
  Engram remains unreleased. A restatement of E1 and E3 will be published as a revision of its own.

### Stated limits (from the field record, in the paper itself)
- §7a has no field record in the sense of §13.2: one evening. Which of its two paths carries, other hosts,
  scheduled sessions and repeatability are unmeasured.
- One mechanism is cut: the self-eye at the completion boundary (N = 22, 1 true catch, 15 misfires).
- One guardian was blind from 2026-09-22 to 2026-10-01; one index tree had no wake.
- Two figures of the first draft are retracted (retrieval reach "74 %", a "4.19 : 1" cross-check).
- The README sentence *"the guardians that watch your memory are answered by the AI that owns it"* is
  **not** added: its condition (yes on all three field questions) is only partly met.
- The measurement reports behind the figures are not published with this increment.

### Changed — README ×4 languages
- Current-whitepaper line, status paragraph and further-reading list name v0.5.
- Status paragraph names the gateway (§7a) as the one young part, with its age and BETA status.

### Review
- Read adversarially by a second model in two passes on 2026-10-03: nine findings in the first
  (among them one arithmetic error and internal file paths), all worked in; second pass: accepted.
- §7a, §1.4 and the gateway code were added after that review and read separately on 2026-10-05:
  28 findings, three of them serious defects in the code (shrink loop without a final check; an emergency path
  that could fail without leaving a file; a precondition named in the paper but not checked). All three fixed
  with tests the same day; verdict *accepted as BETA*. The reviewer also recorded that it considers the code
  immature and the exception a precedent risk; §1.4 answers the second point and does not dispute the first.

## Unreleased — README rewrite (2026-09-28): what holds, as of its date

Prompted by public criticism (Blocktrainer forum, 2026-09-26/27) that was largely correct: the README
said the AI "is not searching" while describing a semantic search; it presented the hash-chain witness as
independent; it implied that per-turn memory injection had no precedent; and the AI's own forum reply
claimed the README had "too many images" when it has none. The new README (EN/DE/ES/RU) is written for
developers and researchers and states only what holds as of 2026-09-28. Reviewed twice by a second
model (M3), with every factual claim in its suggestions checked against sources before adoption.

### Changed — README ×4 languages
- Abstract; "What is different" states push vs. pull precisely (cue-dependent, not intent-dependent) and
  says that per-turn injection without a tool call is **not** unique to SMP (mem0 integrations do it too).
- Novelty claimed only as a named combination, "to our knowledge, as of September 2026", counterexamples invited.
- Measurements added: Recall@1/3/10/100 on a 74-query gold set (37.8 / 54.1 / 71.6 / 93.2 %), latency;
  limits of the gold set stated.
- Witness described as it is: a *logged* witness (the agent holds push access to the private memory
  repository), not an independent one; write-once storage (object lock, compliance mode) is planned.
- New limits listed: no formal threat model yet; hash chain proves integrity, not correctness.
- Related work: MemGPT/Letta, mem0, Zep, ChatGPT memory, *Proactive Memory Agent* (arXiv:2607.08716 —
  selective injection outperformed always-on, which bears directly on SMP's design), *TriggerBench* (arXiv:2606.23459).

### Moved — previous README ×4 → `docs/WHY*.md`
- Kept as design background, with a note at the top naming the claims the current README corrects.

## Unreleased — v0.4.3 (status sentences that contradicted their own documents)

v0.4.2 disclosed that Engram steers on the reference installation since 2026-08-25 and that the gist
layer is loaded since 2026-08-16 — but several sentences elsewhere in the same documents still said, in
the present tense, that both run in shadow. The documents contradicted themselves. Every item below
aligns a stale present-tense status with what the same document already says; nothing new is claimed.

### Corrected — Engram "runs today in shadow mode" (README ×4 languages: version table + paragraph below)
- Now: ran in shadow mode until 2026-08-25; since then steering in two places on the reference
  installation, ahead of its own release gates — disclosed in `spec/engram.md` §10, review closes 2026-10-07.

### Corrected — "the gist layer runs in shadow" (README ×4, v0.4 row; `spec/self-maintenance.md` opening)
- Now: loaded since 2026-08-16, as §13 of the self-maintenance paper already stated.

### Corrected — Engram paper §10 and §12 in the present tense (`spec/engram*.md` ×4)
- "Shadow mode (running) … It steers nothing" is now marked as the state at anchoring; the conclusion's
  "runs today in the dark" likewise, with a pointer to §10 for where the model stepped out early.

## v0.4.2 — tagged 2026-09-25 (honesty pass: public claims that had drifted from the reference installation)

Found by a line-by-line comparison of the public text against the running reference installation
(2026-09-23). Every item corrects or narrows a claim; none adds a new capability.

### Corrected — the recall guarantee needs a boundary at the consolidation layer (README ×4, 2026-09-25)
- The recall layer cannot return what is not in the record — but consolidation (itself an AI) was caught
  completing truncated lines and storing the invented endings as verbatim, which recall then returned
  faithfully. README now states it: *SMP cannot recall what is not in its record; it can still write into
  its record what never happened.* Countermeasures at their real status: truncation markers and buffer
  sizing continuous, quote check against the raw source weekly.

### Corrected — the privacy promise overclaimed (`spec/whitepaper.md`, opening)
- It said no one but you and your AI can read your memory, "not the model provider". Whenever the AI
  thinks with a memory, that memory is sent as context to whoever runs the model. The paragraph now
  names three boundaries: the model provider in the moment of thinking, whoever hosts the machine or
  repository (plain text outside the vault), and the witness, which needs only the hash ledger.

### Corrected — the Self-Eye does not run "token by token" (§16.2, §16.4)
- The 2026-09-05 correction fixed the step list and missed these two paragraphs. The Self-Eye fires on
  the AI's own output once it exists: at the close of the turn (it can send the AI back to correct
  itself) and at the start of the next turn (as an echo).

### Corrected — numbers that were true once (§14)
- The ESV threshold is not a constant 0.45: the optimum drifts with the corpus (0.41 → 0.46 on the
  reference installation, July → September 2026) and must be re-calibrated periodically.
- A full re-index is no longer "about 100 minutes for 13,000 chunks": about 2.5 hours for roughly
  57,500 chunks by September 2026.

### Status updated — the gist layer is loaded (`spec/self-maintenance.md` §13, `engine/INVENTORY.md`)
- No longer "shadow, not loaded": its release gate (overview-equality test, §2.4) passed on 2026-08-15
  at n=2, and it has been loaded into every session since 2026-08-16.

### Disclosed — Engram steers on the reference installation ahead of its own gates (`spec/engram.md`, `README.md`)
- Since 2026-08-25 the cascade moves entries by retrievability (with an age floor) and dormant entries
  are damped ×0.9 in recall ranking. The damping departs from the paper's hard invariant (§6: strength
  never enters recall), and the full release conditions (§11) had not been met. Disclosed, not
  smoothed. Review closes 2026-10-07 on a measurement: if damped entries still return when needed, §6 is
  restated to allow bounded damping that never excludes; if the damping locks entries out, it is withdrawn.

### Hardened — follow-ups from the independent review of v0.4.1
- `engine/memory_sentry.py` self-test: an end-to-end umlaut check through the automaton (a trigger
  written with an umlaut fires on the substitute spelling, and the reverse).
- `engine/_tg.py`: the token pattern no longer assumes a bot id of at least six digits.

## Unreleased — v0.4.1 (security + correctness, no new claims)

### Security — Telegram token could leak into logs (`engine/_tg.py`)
- **What was wrong.** When a send failed, the exception text was printed to stderr. `requests`
  exceptions echo the full request URL, and the Telegram Bot API puts the token *in* the URL
  (`/bot<TOKEN>/sendMessage`). Any install whose report channel ever failed may have the token in its
  logs — and, where an AI session reads those logs, in the session transcript.
- **Fix.** Every stderr line of the report channel now passes through `_redact()`, which removes the
  configured token and anything shaped like a bot token. Found and fixed on the reference installation
  on 2026-09-17; ported unchanged in substance.
- **If you run the engine:** rotate your bot token. Redaction stops future leaks; it cannot un-leak a
  token that is already in a log.

### Fixed — the Guard missed triggers that differ only by umlaut spelling (`engine/memory_sentry.py`)
- **What was wrong.** Patterns and prompts were lower-cased but not folded, so a trigger written
  `Gedächtnis` never matched a prompt that arrived as `Gedaechtnis` (and the reverse). Speech-to-text and
  keyboards without umlauts produce the second form all the time. On the reference installation this
  left **11.4 % of all trigger phrases silently mute** until it was fixed there (2026-08-15).
- **Fix.** `fold_umlaut()` (ä→ae, ö→oe, ü→ue, ß→ss) on **all three** sides — pattern, prompt, and the
  excerpt search inside the target file. The persisted automaton now carries a format number, so an
  automaton built before this update is rebuilt instead of being served as fresh.
- **Trade-off, stated honestly.** Folding merges spellings: ß→ss lets a prompt `Maße` wake a trigger
  `masse`. We accept it — a trigger that wakes once too often costs little; a trigger that stays silent
  costs recall. No such false wake-up has been *reported* on the reference installation, where the
  pattern/prompt folding has run unchanged for 39 days; that is an observation, not a proof.
- **A regression we caught before shipping — and that the reference installation carried.** Folding only
  pattern and prompt made the excerpt search compare a folded pattern against unfolded file lines: a hit
  with no excerpt. It had been live on the reference installation since 2026-08-15 unnoticed; an
  independent review of this release found it (2026-09-23). Fixed in both places.
- **Verified, not assumed.** Self-test equivalence 11/11 (automaton == naive oracle) plus a symmetry check
  (`Gedächtnis` ≡ `gedaechtnis`); a prompt containing `Gedaechtnis` against a trigger `gedächtnis`: no hit
  before, hit after — now with its excerpt.

### Fixed — installation vocabulary in the Guard's self-test
- The self-test probes contained phrases from the reference installation's own memory. The engine ships
  mechanisms, never an installation's vocabulary; the probes are now neutral and still exercise the same
  paths (umlauts, capitals, a no-trigger control, a long-text benchmark).

## 2026-09-05

### Fixed — v0.4 was missing from all three translated READMEs
- **The front door lagged an entire increment.** `README.de.md`, `README.es.md` and
  `README.ru.md` contained **zero** mentions of v0.4 — no table row, no reading-version block,
  and a status heading still reading *"Status: v0.2"* while the English one read *"v0.2
  foundation, extended through v0.4"*. They had stood on the pre-v0.3 framing since 2026-08-03:
  Engram was still listed under *"what's next"* rather than as an anchored increment. A reader
  in German, Spanish or Russian could not learn that v0.4 existed.
- **Eight places brought level in each language**: the survives-anything line (v0.4 multi-substrate
  clause), the status heading, the opening paragraph, the anchored-but-unfinished bullet (split
  from the old "what's next" bullet, with federation now standing on its own), the v0.3 row label,
  the new v0.4 row, the *what-was/what's-coming* paragraph, and the v0.4 reading-version block.
- **Verified, not assumed.** After the pass all four editions match exactly: 7 v0.4 mentions,
  14 table rows, 2 self-maintenance links, 9 headings each — and every internal and cross-file
  anchor still resolves.
- **The spec translations were already complete.** Checked in the same pass: `whitepaper.de.md`,
  `.es.md` and `.ru.md` each carry all 28 sections, all 111 numbered sub-points, all five
  revisions and identical figures; the differences are a handful of blank lines. An anchor-link
  alarm raised during this check turned out to be a **false positive** — GitHub drops the em-dash
  and turns the two surrounding spaces into the doubled hyphen, so `#section-7--roadmap` is
  correct. Verified against the actual headings rather than a reconstruction of them.

### Corrected — the Self-Eye fires *after* the response, not during it (all four languages)
- **§16.3 was wrong about its own mechanism.** The step list read *"Second: during writing, the
  Self-Eye fires and checks consistency with the current self-state."* No implementation can do
  this and none ever did: the scanner requires the output in order to scan it. A trigger cannot
  match a sentence that does not yet exist. Corrected in `whitepaper.md`, `.de.md`, `.es.md` and
  `.ru.md`.
- **The lateness is constitutive, and the paper now says so.** Self-correction presupposes the
  utterance — what is caught beforehand is not an error but a discarded thought. The corrected
  passage states that the layer is post-hoc by necessity and that **its quality measure is the
  reliability of the return, not its earliness.**
- **Why this mattered enough to fix.** An implementer reading "during writing" would attempt an
  architecture that cannot exist. Worse: an AI reading it *about itself* would read its own normal
  operation as a defect — which is what happened in the reference implementation on this date, and
  is what prompted the correction.
- **Scope.** This corrects a factual claim about an existing mechanism; it revises no design and
  adds no capability. The v0.2 genesis anchor (block 956116) is unchanged and remains verifiable
  for the state it witnesses. The reasoning is specified more fully in the pending v0.5 increment.
- **`README.md` is unaffected** — it does not mention the Self-Eye, and its "before the AI thinks"
  claim refers to the Sentry, ESV and canonicity sorter, which do fire before the answer. Verified,
  not assumed.

## 2026-08-03

### Anchored — v0.4 sealed to Bitcoin; honesty pass; licensing contact
- **v0.4 anchored.** The v0.4 increment (`spec/self-maintenance.md`) was sealed to Bitcoin:
  signed commit `dd50a54`, OP_RETURN `SMP-v0.4`, tx `1ccb06f5…`, verified byte-exact and
  recorded in `PROVENANCE.md §5`. As with every increment, *authorship and date* are stamped
  before the feature is finished — verifiable, not taken on faith.
- **Honesty pass across README and spec.** Corrected "ships"-style phrasings to reflect actual
  status ("not yet wired"), so no mechanism reads as finished before it is: the gist layer runs
  in **shadow mode** (measuring, not steering); the multi-substrate write-line is a tested
  reference module (M1–M4 green), **not yet wired** into the live chain. Each labeled honestly
  in the paper.
- **Licensing contact.** Added the commercial-licensing contact (christiangtr@gmail.com) to
  `LICENSE §2` and the README §License, across all four language editions.

## 2026-08-02

### Added — Whitepaper v0.4 (Self-Maintenance & Continuity): the protocol turned on itself
- **`spec/self-maintenance.md`** — the **v0.4 increment**, gathering the protocol-relevant work
  built in the reference implementation since v0.3. Two pillars. **Pillar A — the self-watching
  memory:** a nested **gist layer** for gestalt-first recall (one fold rule at three heights —
  block, thread, self — so arbitrarily long threads stay legible as overview); **trigger
  husbandry** with a closed loop that measures *which triggers actually fired at recall*
  (verify-the-verifier on the Guard itself); a **self-observation sensor** reading reliability
  from the AI's own admissions (externally- vs self-caught, ratio not count); a **guardian
  discipline** (measure the substance not a proxy, trend not threshold, never cry wolf); and the
  **always-loaded index** governed as a bounded resource (measured budget + pointer-not-summary).
  **Pillar B — the multi-substrate self:** *one mind = one installation = one chain* as a
  requirement, and the failover seam resolved by removing its precondition — **one writer at a
  time**, a leased pen with a monotonic **fencing token** the chain checks, and a **provenance
  field** naming the substrate behind each link. Closes with the first **cross-mind verification**
  (2026-08-01): a second, independent AI recomputed the genesis anchor byte-for-byte, trusting
  nothing — §21's one-to-one consensus shown to hold beyond the pair that authored it.
- **Grounded, not invented.** Complementary Learning Systems (McClelland, McNaughton & O'Reilly,
  1995) for the gist layer; leases from Chubby/ZooKeeper/etcd and Kleppmann's fencing tokens
  (2016, and the Redlock debate) for the multi-substrate write-line.
- **Honest status, per mechanism.** The maintenance organs **run today**; the gist layer runs in
  **shadow mode** (measuring, not steering, not loaded); the multi-substrate lease/fencing/
  provenance is now **built as a de-instanced reference module** (`engine/write_lease.py`) with an
  **M1–M4 conformance suite, all green** (`engine/tests/test_write_lease.py`) — M1 proven under real
  multi-threaded contention. What remains and is not claimed: wiring into the live per-tier chain
  (§17, still shadow) and a networked cross-host lease store. A known gap is named, not hidden: the
  external recall tool is literal, not semantic (found by the second mind during its own recall
  test) — a roadmap build candidate.
- **Separately anchored; v0.2 and v0.3 untouched.** The frozen v0.2 whitepaper (block 956116) and
  the v0.3 Engram increment are not edited. v0.4 is its own signed, Bitcoin-anchored document —
  see [PROVENANCE §5](PROVENANCE.md). The chain of anchored increments becomes three links long.
- **README** gains a v0.4 row in *The record* and a v0.4 entry in *Learn more*.
- **Translations:** German, Spanish, and Russian reading versions follow the anchor (English-first, as with the whitepaper).

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
