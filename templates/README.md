# Template — empty instance structure

Copy `motoko/` (and optionally `claude-memory/`) into `$MOTOKO_MEMORY` to initialize a
new, empty instance. The engine never touches existing files (init-if-absent) — it only
writes into this root.

```
export MOTOKO_MEMORY="$HOME/my-memory"
mkdir -p "$MOTOKO_MEMORY"
cp -rn templates/motoko "$MOTOKO_MEMORY"/
```

These files contain only headers/structure — no content.
