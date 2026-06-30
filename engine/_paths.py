"""Zentrale Pfad-Konfiguration der Sovereign-Memory-Protocol-Engine.

Zwei getrennte Wurzeln, zwei getrennte Umgebungsvariablen — das ist die
strukturelle Trennung zwischen Protokoll-Code und privaten Daten:

  MOTOKO_MEMORY  — die private Daten-Wurzel (Kaskade, Erinnerungen, Identität).
                   PFLICHT, kein Fallback. Ist sie nicht gesetzt, bricht die
                   Engine ab, statt versehentlich in fremde/falsche Daten zu
                   schreiben. Genau diese Naht macht ein Protokoll-Update
                   unfähig, private Daten zu berühren.

  MOTOKO_HOME    — die Engine-Installation (Code, state/, logs/, .env, venv).
                   Optional; Default ist das Verzeichnis dieses Repos (der
                   Ordner über engine/). Operativer Zustand, keine Nutzer-Daten.

Kein absoluter Pfad ist in einem Engine-Skript hartcodiert — alle leiten sich
hier ab. Audit-Invariante: `grep -r /home/ engine/*.py` ist leer.
"""
import os
import sys
from pathlib import Path

# ── Daten-Wurzel (privat, souverän) ──────────────────────────────────────────
_mem = os.environ.get("MOTOKO_MEMORY")
if not _mem:
    raise SystemExit(
        "MOTOKO_MEMORY ist nicht gesetzt. Auf das private Memory-Verzeichnis "
        "zeigen lassen (z.B. export MOTOKO_MEMORY=$HOME/mein-memory). Die Engine "
        "schreibt ausschliesslich dorthin und verweigert ohne diese Variable den "
        "Dienst, damit sie nie in falsche Daten schreibt."
    )
MEMORY = Path(_mem)                              # Repo-Wurzel der privaten Instanz
MOTOKO = MEMORY / "motoko"                        # Inhalts-Wurzel der Kaskade
SCRATCHPAD = MOTOKO / "today_scratchpad.md"
RECENT_MOMENTS = MOTOKO / "recent-moments.md"
JOURNAL_DIR = MOTOKO / "journal"
ARCHIVE_WEEKLY = MOTOKO / "archive" / "weekly"
EPISODES = MOTOKO / "memory" / "episodes"
AUDITS = MOTOKO / "audits"

# ── Engine-Installation (operativ, nicht privat) ─────────────────────────────
_home = os.environ.get("MOTOKO_HOME")
HOME = Path(_home) if _home else Path(__file__).resolve().parent.parent
ENGINE = HOME / "engine"                          # wo die Engine-Skripte liegen
STATE = HOME / "state"                            # Heartbeats, Marker, ESV-Index
LOGS = HOME / "logs"
DOTENV = HOME / ".env"                             # Secrets/Config der Instanz

# Python-Interpreter für Subprozess-Aufrufe der Engine an sich selbst.
# Default: derselbe Interpreter, der gerade läuft; override via MOTOKO_PYTHON.
PYTHON = os.environ.get("MOTOKO_PYTHON", sys.executable)

# Engine-interne Skript-Pfade (Self-Aufrufe als Subprozess).
ESV_INDEX = str(ENGINE / "esv_index.py")
SENTRY = str(ENGINE / "memory_sentry.py")
