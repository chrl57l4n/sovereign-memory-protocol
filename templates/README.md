# Template — empty instance structure

Copy `motoko/` (and optionally `claude-memory/`) into `$MOTOKO_MEMORY` to initialize a
new, empty instance. The engine never touches existing files (init-if-absent) — it only
writes into this root.

`claude-memory/` is optional and ships empty here (just a `.gitkeep`): it's
where an installation's own AI-tool session memory lives — separate from
the declarative cascade in `motoko/`. Several engine scripts already treat
it as a first-class source when present: `esv_index.py` indexes it
alongside `motoko/`, `trigger_audit.py` and `memory_pflege_audit.py` audit
it for trigger coverage, and `rem_consolidate.py` reads it during nightly
consolidation. An installation that doesn't use a separate AI-tool memory
layer can leave it empty; nothing requires it to be populated.

```
export MOTOKO_MEMORY="$HOME/my-memory"
mkdir -p "$MOTOKO_MEMORY"
cp -rn templates/motoko "$MOTOKO_MEMORY"/
```

These files contain only headers/structure — no content.
