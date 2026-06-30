# Template — leere Instanz-Struktur

Kopiere `motoko/` (und optional `claude-memory/`) nach `$MOTOKO_MEMORY`, um eine
neue, leere Instanz zu initialisieren. Die Engine fasst existierende Dateien nie
an (Init-if-absent) — sie schreibt nur in diese Wurzel hinein.

```
export MOTOKO_MEMORY="$HOME/mein-memory"
mkdir -p "$MOTOKO_MEMORY"
cp -rn templates/motoko "$MOTOKO_MEMORY"/
```

Diese Dateien enthalten nur Header/Struktur — keine Inhalte.
