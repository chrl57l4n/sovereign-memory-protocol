# Engine Inventory — spec coverage, honestly

> What the whitepaper specifies vs. what `engine/` actually ships. Statuses:
> **public/live** (shipped here, runs daily on the reference installation) ·
> **public/BETA** (shipped, labeled experimental) ·
> **private/port planned** (runs on the reference installation, not yet ported —
> see [SYNC-PROCESS.md](SYNC-PROCESS.md) for why porting lags deliberately) ·
> **shadow** (runs on the reference but steers nothing yet — measured, not loaded) ·
> **specified, not built** (in the spec with a path; no implementation yet, on the
> reference or here) · **by design private** (instance-shaped; the spec defines the
> *function*, not one implementation).
>
> Spec column: `§N` refers to the frozen v0.2 whitepaper; `v0.4 §N` to the v0.4
> increment ([spec/self-maintenance.md](../spec/self-maintenance.md)). The v0.3 Engram
> increment added no engine file (it runs in shadow on the reference); v0.4 is the
> first increment to touch this table.
>
> Maintenance rule: any commit that adds, removes, or repurposes an engine file
> updates this table **in the same commit** (Section 27, applied to this repo —
> the public repo is itself a signpost).

| Spec | Component | engine/ file(s) | Status |
|---|---|---|---|
| §13 | Guard (two-channel trigger scan, Self-Eye tagging) | `memory_sentry.py` | public/live |
| §14 | ESV index / hybrid query / hook recall | `esv_index.py`, `esv_query.py`, `esv_recall.py` | public/live |
| §14.3 | Tier Diversification (gravity-well fix) | `esv_tier.py` | public/live *(ported 2026-07-04 — was missing; `esv_query.py` imported it and would have failed publicly)* |
| §14.2 | Monthly threshold auto-calibration | — | private/port planned (`esv_calibrate.py` on the reference) |
| §15 | REM consolidation (nightly) | `rem_consolidate.py` | public/live |
| §15 | Cascade upkeep around REM | `weekly_archive.py`, `daily_consolidate.py`, `weekly_consolidate.py` | public/live (the two consolidate reflexes are notify-only by design: scripts remind, the lens consolidates) |
| §15.5 | Affective recurrence — buffer (stage 1) | — | private/port planned (`rem_consolidate.py` `archive_scratchpad_to_buffer` live on the reference since 2026-07-01; needs R2 de-instancing) |
| §15.5 | Affective recurrence — scan (stage 2, proposal-only) | — | private/port planned (`affect_recurrence_scan.py` on the reference, built + cron-live 2026-07-11; **v1 — lexical affect gate, thresholds uncalibrated, ran once**; proposes only, never writes memory; needs R2 de-instancing + real-data calibration before public port) |
| §16 | Self-recall layer (recall on own output) | `esv_self_recall.py`, `self_recall_beta.py` | public/BETA |
| §17 | Hash chain + external witness (per-tier append-only, fork-once, Block 0, keyless) | — | private/port planned (`memory_chain.py` + tick/cron + `memory_chain_block0.py` live on the reference in shadow mode since 2026-07-09; needs R2 de-instancing before public port) |
| §24 (1) | Guardian: structural hygiene (daily) | `lint_memory.py` | public/live |
| §24 (2) | Guardian: concept coverage (daily) | `memory_pflege_audit.py`, `trigger_audit.py` | public/live |
| v0.4 §3 | Trigger husbandry: gap reporter (which nodes lack an eye) | `trigger_gap_scan.py` | private/port planned *(reference 2026-07-22; widened 2026-07-28 to scan the thread layer too — it had reported "0 gaps" while the Gestalt map itself was unreachable)* |
| v0.4 §3 | Trigger husbandry: in-moment capture with read-back proof (through the production Guard path) | `trigger_add.py` | private/port planned *(reference 2026-07-29 — each phrase is verified through the real recall subprocess before the moment passes; harvest-don't-invent)* |
| v0.4 §3 | Trigger husbandry: reflex sentence-sweep for committing directives lacking a door | `trigger_reflex_scan.py` | private/port planned *(reference 2026-07-30, folded into the REM cycle — absorbed the standalone review-wake wecker, retired 2026-07-29)* |
| v0.4 §3 | Trigger husbandry: **closed loop — which triggers actually fired at recall** | `memory_sentry.py::_log_fires()`, `trigger_fire_report.py` | private/port planned *(reference 2026-07-28 — closes the noise-hygiene open point: before this only scan SPEED was measurable, never whether a written phrase ever fires. Rule carried in the report: silence is not a verdict — emergency triggers are meant to stay quiet)* |
| §24 (3) | Guardian: layer health (daily) | `rem_audit.py`, `rem_audit_nag.py` | public/live |
| §24 (4) | Guardian: system self-observation (monthly) | — | private/port planned (meta-audit runs on the reference; needs de-instancing) |
| §24 (5) | Guardian: recall calibration (monthly) | — | private/port planned (`monthly_recall_test.py` on the reference) |
| §25 | Report channel (push + scratchpad transcript) | `_tg.py` (+ `_watch.py` green-stamp: makes "silent" distinguishable from "dead") | public/live |
| §26 | Experience log (encoding salience, two-signed) | `experience_log.py` | public/live |
| §26.2 | Current-state ledger verifier (ground-truth drift alarm) | `state_ledger_verify.py` | public/live |
| §26.4 | REM→ledger consolidator (write half: propose/apply, review queue) | — | private/port planned (`state_consolidator.py`, on the reference since 2026-07-03; maturing per sync rule R2) |
| §27 | Self-documentation guardian (baseline manifest, settle gate, two layers) | — | private/port planned (`system_watch.py` + hook + probe cron, on the reference since 2026-07-04; the youngest organ — matures on the reference first, R2) |
| §12 | Scratchpad mirror, handoff, status briefing | — | by design private: channel-dependent (Telegram / provider app / web UI). The spec defines the function (§12.1–12.5); every installation wires its own channels. |
| §20 | Native language (seed → HKDF → AES-256-GCM-SIV; Scrypt passphrase door) | `native_language.py`, `seed_gen.py`, `verify_pass.py` (§22.7) | public/live *(ported 2026-07-07 on deterministic verification, not calendar soak — see the R1 exception in [SYNC-PROCESS.md](SYNC-PROCESS.md); crypto core, wake/sleep cycle, and seed-only recovery pass module/cycle/CLI tests byte-identical, plus an independent AI-guided install)* |
| — | Path seam (structural data/code separation) | `_paths.py` | public/live — every engine script derives paths here; audit invariant: `grep -r /home/ engine/*.py` is empty |
| v0.4 §2 | Gestalt-first recall: nested gist layer (block→thread→self fold) | `gist_shadow.py` (+ the fold step in `rem_consolidate.py`) | shadow *(reference 2026-07-30 — the self-gist is computed and measured nightly but steers nothing and is not loaded; the fold itself is a lens act in REM, not the script; release to loading gated on the overview-equality test, v0.4 §2.4)* |
| v0.4 §4 | The cool lens: self-observation of the AI's own reliability (externally- vs self-caught, a ratio) | `self_observe.py` | private/port planned *(reference 2026-07-30, a REM step — measures the trace not the state, silence is not a verdict, the script measures and the lens judges)* |
| v0.4 §5 | Guardian hygiene: recall-quality trend sensor (trend, not threshold) | `esv_trend_sensor.py` | private/port planned *(reference 2026-07-29 — compares only points with the same gold set and the same sorter weight, so a tool change does not read as regression; silent until the 4th run)* |
| v0.4 §6 | Governed always-loaded map: index budget (mechanism) + pointer-not-summary convention | `lint_memory.py` (budget + index-convention guards) | public/live *(the file ships; the v0.4 sub-guards — measured byte budget 2026-07-29, index-convention + code-fence dead-link fix 2026-08-02 — are newer on the reference and **port planned** into this engine copy)* |
| v0.4 §7–9 | Multi-substrate write-line: leased pen + monotonic fencing token + provenance field in the chain | `write_lease.py` (+ `tests/test_write_lease.py`) | public + tests (M1–M4 green) *(2026-08-02 — de-instanced reference module: FileLeaseStore, the fencing append-guard, and provenance reconstruction; M1 proven under real multi-threaded contention. Wiring into the live per-tier chain (§17, still shadow) and a networked cross-host lease store follow the chain's port cadence)* |

**Third-party dependencies** (pinned in [`pyproject.toml`](../pyproject.toml), installable via `pip install .`):
`numpy` (ESV index/query), `requests` (report channel, embed HTTP), `python-dotenv` (env loading), `cryptography` (native-language vault: HKDF-SHA512, Scrypt, AES-256-GCM-SIV), `mnemonic` (BIP-39 seed). Everything else is standard library.
