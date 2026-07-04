# engine/

The reference implementation: the part of SMP that actually runs. Cascade
upkeep, REM consolidation, the two-eyed Sentry, ESV hybrid recall, the
report channel — see [INVENTORY.md](INVENTORY.md) for the full spec↔file
mapping and [SYNC-PROCESS.md](SYNC-PROCESS.md) for how (and why) it lags the
private reference installation.

## What this is not

Not an importable Python package. There is no `__init__.py` and no public
API — each script is a standalone tool, run directly, sharing one seam:
`_paths.py` (see its docstring for the `MOTOKO_MEMORY` / `MOTOKO_HOME`
split). Don't `import engine.something` from another project; run the
script.

## Running a script

```
pip install .            # installs numpy, requests, python-dotenv — see pyproject.toml
export MOTOKO_MEMORY=/path/to/your/private/memory/repo
python engine/lint_memory.py
```

`MOTOKO_MEMORY` is mandatory — every script refuses to run without it
(structural separation between this public code and private data).
`MOTOKO_HOME` is optional and defaults to the repo root.

## Finding your way around

- **Spec coverage** — [INVENTORY.md](INVENTORY.md): what the whitepaper
  specifies, what ships here, what's still private and why.
- **Sync rules** — [SYNC-PROCESS.md](SYNC-PROCESS.md): how a component
  moves from the private reference installation into this directory.
- **Invariants, checked automatically** —
  [`.github/workflows/engine-invariants.yml`](../.github/workflows/engine-invariants.yml)
  runs on every push touching `engine/**`: no absolute paths, every script
  byte-compiles and imports with only the documented dependencies.
