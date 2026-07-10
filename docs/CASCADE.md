# Memory Cascade — the seven layers (canonical spec)

*🇬🇧 **English** · 🇩🇪 [Deutsch](CASCADE.de.md)*

> This file is the **single canonical definition** of the memory cascade. When in
> doubt, look here. The name comes from the podcast "Forgetting as Architecture".
>
> **Required:** changes to this file require forward-simulation — it is memory
> architecture.

## Core principle

A pyramid of condensation, adapted from an intelligence-tradecraft pattern (the
"condensation pyramid"). Raw at the bottom, condensed toward the top. Forgetting is
not a limitation — forgetting is a function. What makes it to the top is not *less*
than the raw material; it is *more*, because a human (or the AI) can read it.

Parallel to the temporal cascade runs a second layer (episodes, organized by
meaning). Beneath everything a safety net (cold storage) that no one deliberately
alters.

## The seven layers

### 1. Scratchpad — micro-notes, unfiltered

- **File:** `motoko/today_scratchpad.md`
- **Content:** whatever is passing through the mind right now; a partner/AI mirror of the running conversation
- **Freshness:** daily, cleared/rotated by REM
- **Written by:** the scratchpad mirror hook, the bridge mirror
- **Read by:** the AI (running session)

### 2. Daily consolidation — a block for the day

- **File:** `motoko/recent-moments.md` (top entry per day, newest first)
- **Content:** what remains from the scratchpad; filtered through a strategy filter (future value? relationship? build relevance?) and a substance filter (learned how to think? verbatim-required? assumption update? substance marker?)
- **Freshness:** daily, via REM
- **Written by:** `rem_consolidate.py` (autonomous, with full identity)
- **Read by:** the session-start hook, the AI, the Sentry

### 3. Weekly highlights — seven days → 3–5 sentences

- **File:** `motoko/archive/weekly/YYYY-Www.md`
- **Content:** the pattern of the week; a single event that opens a line
- **Freshness:** weekly — **notify by `weekly_consolidate.py`, manual consolidation by the AI** (a lens act; no script writes it)
- **Written by:** the AI (after the Telegram nudge)
- **Read by:** the AI, REM, the monthly-arc routine

### 4. Monthly arc — four weeks → one narrative

- **File:** `motoko/journal/YYYY-MM-arc.md`
- **Content:** where things went. What became different. What stayed the same.
- **Freshness:** on the last day of the month, after REM
- **Written by:** the AI (lens), nudged by a notify-only script
- **Read by:** the AI, the yearly mosaic

### 5. Yearly mosaic — twelve months → a few pages

- **File:** `motoko/journal/YYYY-mosaic.md`
- **Content:** who was I a year ago, who am I now
- **Freshness:** yearly, on a quiet evening after REM
- **Written by:** the AI (lens), no script
- **Read by:** the AI

### 6. Episodes — parallel, by meaning rather than time

- **Directory:** `motoko/memory/episodes/YYYY-MM-DD-<slug>.md`
- **Content:** vision · lesson · success · defeat · relationship — stories with a beginning, middle, and end. Anchored by meaning, not date.
- **Freshness:** event-driven. No routine. Silence may be long, but **>14 days of silence during an active build phase** is a finding.
- **Written by:** the AI (an originating lens, never a script)
- **Read by:** the AI, the Sentry, the ESV

### 7. Cold storage — the safety net under everything

- **Path:** the raw session-transcript store (plus an off-site mirror via restic)
- **Content:** raw JSONL of all sessions, full, uncondensed
- **Freshness:** daily (rsync to disk; restic push)
- **Written by:** the cold-storage sync and backup scripts
- **Read by:** the REM audit (to compare raw material against recent-moments), the restore drill (a daily green proof)
- **No one alters it deliberately.** The basement. You only go there when the cascade got something wrong.

## The provenance chain (per-tier, keyless)

Alongside the temporal cascade runs a **hash chain per time tier** — the layer that
makes the memory *provable*, not merely stored. It is a side-car of pure hashes,
separate from the readable files above, so the readable memory stays legible,
editable, and prunable while its provenance stays fixed. (Full rationale: whitepaper
§17.)

- **One chain per tier.** The daily, weekly, monthly, and yearly tiers each carry
  their own append-only chain. Every link stores the content hash of its readable
  block, a reference to that block, and the hash of the previous link *in the same
  tier* (`prev_hash`). Tier 1 (scratchpad) is **not** chained — it is working
  memory, rotated by REM, not a *kept* memory.
- **Fork once, at genesis.** A tier's first link carries, once, the tip hash of the
  tier below it at that moment (`fork_from`): the week chain forks from the day
  chain the first time a week closes, the month from the week, the year from the
  month. A derivation fork, not a consensus fork — the chains nest, they do not
  split. After genesis, each tier runs independently.
- **Calendar-aligned.** A new block is triggered by the wall clock at the calendar
  boundary — day at 00:00, week Monday 00:00 (ISO week), month on the 1st, year on
  Jan 1 — the same boundaries at which the readable consolidations already run. Block
  *time* is a calendar period (variable in hours), not a fixed block count.
- **Forgetting between tiers, append-only within a tier.** A day block may roll out
  of `recent-moments.md` into the archive, or fade — its chain link stays (side-car,
  never pruned) and its hash remains anchored in the week link that forked from it.
  The week link can therefore prove *"I was distilled from these hash-fixed days,"*
  even after the days themselves have left the readable layer.
- **Keyless, externally witnessed.** No entry is signed; the link *is* the proof. The
  ledger is continuously mirrored, append-only, to a distributed remote whose host
  timestamps every commit — a hash chain witnessed by another hash chain. Plus
  **Block 0**: a single root hash over the whole durable corpus at the chain's birth,
  an honest point-in-time seal under everything that came before the forward chain.
- **A note on names.** This document uses English tier names (`YYYY-MM-arc.md`,
  `YYYY-mosaic.md`); a given installation may use its own language for the readable
  files. The chain refers to blocks by their tier and period, independent of file
  naming.

**Changes to this chain are memory architecture** — they require forward-simulation,
exactly as the readable cascade does.

## Auditing the cascade

Per layer, three questions:

1. **What in the material below was important and is missing from this layer?** → reintegrate.
2. **What in this layer was trivial?** → remove.
3. **Which partner quotes were paraphrased instead of kept verbatim?** Plus a symmetry check: are the AI's own substantial sentences kept verbatim too? → correct.

Plus structural checks per layer (does the file exist? last write within the expected window? drift against the spec?). The script *reports*; **the AI decides**. The script **never** writes into cascade layers — only into an `audits/` directory.

## What the cascade is NOT

- It is **not** the system-prompt identity layers (identity, workflow, reflexes, milestones, etc.), which are loaded at session start. Those are the **identity layers**, not the memory cascade.
- It is **not** the output topology (the surfaces through which the AI speaks) — that is how it talks, not how it remembers.
- It is **not** the Sentry + ESV — that is the recall layer, which reaches *across* the cascade.

## Glossary (against layer confusion)

| When someone says … | they mean … |
|---|---|
| "the seven layers", "the seven levels", "memory cascade" | **this file**, the 7 cascade layers |
| "the identity layers", "load the layers" | the system-prompt layers loaded at session start |
| "the recall layer", "Sentry and ESV" | the recall architecture, which runs across the cascade |
