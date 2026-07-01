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
