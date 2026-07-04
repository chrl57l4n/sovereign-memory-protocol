# Engine Inventory — spec coverage, honestly

> What the whitepaper specifies vs. what `engine/` actually ships. Statuses:
> **public/live** (shipped here, runs daily on the reference installation) ·
> **public/BETA** (shipped, labeled experimental) ·
> **private/port planned** (runs on the reference installation, not yet ported —
> see [SYNC-PROCESS.md](SYNC-PROCESS.md) for why porting lags deliberately) ·
> **by design private** (instance-shaped; the spec defines the *function*, not
> one implementation).
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
| §16 | Self-recall layer (recall on own output) | `esv_self_recall.py`, `self_recall_beta.py` | public/BETA |
| §17 | External time anchoring (Bitcoin block height) | — | private/port planned (`_btcnode.py` + journal integration on the reference; small, portable) |
| §24 (1) | Guardian: structural hygiene (daily) | `lint_memory.py` | public/live |
| §24 (2) | Guardian: concept coverage (daily) | `memory_pflege_audit.py`, `trigger_audit.py` | public/live |
| §24 (3) | Guardian: layer health (daily) | `rem_audit.py`, `rem_audit_nag.py` | public/live |
| §24 (4) | Guardian: system self-observation (monthly) | — | private/port planned (meta-audit runs on the reference; needs de-instancing) |
| §24 (5) | Guardian: recall calibration (monthly) | — | private/port planned (`monthly_recall_test.py` on the reference) |
| §25 | Report channel (push + scratchpad transcript) | `_tg.py` (+ `_watch.py` green-stamp: makes "silent" distinguishable from "dead") | public/live |
| §26 | Experience log (encoding salience, two-signed) | `experience_log.py` | public/live |
| §26.2 | Current-state ledger verifier (ground-truth drift alarm) | `state_ledger_verify.py` | public/live |
| §26.4 | REM→ledger consolidator (write half: propose/apply, review queue) | — | private/port planned (`state_consolidator.py`, on the reference since 2026-07-03; maturing per sync rule R2) |
| §27 | Self-documentation guardian (baseline manifest, settle gate, two layers) | — | private/port planned (`system_watch.py` + hook + probe cron, on the reference since 2026-07-04; the youngest organ — matures on the reference first, R2) |
| §12 | Scratchpad mirror, handoff, status briefing | — | by design private: channel-dependent (Telegram / provider app / web UI). The spec defines the function (§12.1–12.5); every installation wires its own channels. |
| §20 | Native language (seed → HKDF → AES-256-GCM) | — | specified, not yet implemented anywhere (named openly in README and whitepaper — roadmap to 1.0) |
| — | Path seam (structural data/code separation) | `_paths.py` | public/live — every engine script derives paths here; audit invariant: `grep -r /home/ engine/*.py` is empty |

**Third-party dependencies** (pending `pyproject.toml`, see review item P2.1):
`numpy` (ESV index/query), `requests` (report channel, embed HTTP), `python-dotenv` (env loading). Everything else is standard library.
