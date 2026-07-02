<!--
Current-State Ledger — what we use RIGHT NOW.

Live operational state (which tool / default is current), kept SEPARATE from
narrative memory. It is always loaded — print it in your session-start briefing so
the current state is PRESENT, never something the AI has to recall mid-thought.
Verified against ground-truth artifacts by engine/state_ledger_verify.py.
Whitepaper: Section 26.

Admission rule (strict): only facts whose staleness would cause WRONG ACTION
(a superseded tool, a changed default, a moved endpoint). No relationship or
narrative memory — that belongs in the cascade and is reached by recall. Keep it
small; aim for fewer than ~30 rows.

Columns:
  Domain     — the slice of the work this row governs.
  Current    — what is in use right now.
  Artifact   — a real path (script, config, commit) that PROVES the current value.
               state_ledger_verify.py checks it exists; DOMAIN_PROBES can flag a
               newer sibling; experience_log.py frequency can flag a changed default.
  Since      — when this became current.
  Supersedes — what it replaced (demoted, not deleted — keeps its history).

Replace the example rows below with your own. Delete this comment if you like.
-->

# Current-State Ledger — what we use right now

| Domain | Current | Artifact (ground truth) | Since | Supersedes |
|---|---|---|---|---|
| language-model | <your default model> | .env | YYYY-MM-DD | — |
| build-tool | <your bundler> | package.json | YYYY-MM-DD | <old tool> |
| test-runner | <your test runner> | package.json | YYYY-MM-DD | — |
| embedding-model | <e.g. bge-m3 @ 127.0.0.1> | engine/esv_index.py | YYYY-MM-DD | — |
| deploy-target | <where it ships> | <ci config path> | YYYY-MM-DD | — |
