#!/usr/bin/env python3
"""Grün-Stempel für stille Watcher — macht 'still' unterscheidbar von 'tot'.

Spec: Section 25 (report channel — green-stamp companion to _tg.py).

Stille Watcher (remote_control_watchdog, rem_audit_nag) reden nur bei Alarm.
Damit man sieht, dass sie LEBEN und GRÜN sind, ruft jeder pro Lauf mark().
status_briefing.sh liest state/watchers/ und zeigt:
  🟢 grün (frischer Stempel)
  ⚠️ stale (Stempel altert über max_age_s → der Watcher selbst läuft nicht mehr)
  🔴 alert (Watcher meldet ein Problem)

Eingeführt 28.06.2026 (der Partner: 'watcher grün markieren bei stumm').
"""
import json
import time
from pathlib import Path

from _paths import STATE
_DIR = STATE / 'watchers'


def mark(name: str, status: str, detail: str = '', max_age_s: int = 900) -> None:
    """status: 'green' | 'alert'. max_age_s: ab wann der Stempel als stale gilt
    (= Watcher lief nicht mehr). Großzügig wählen (~3× Cron-Intervall).
    Schreiben darf den Watcher NIE crashen → alles in try/except."""
    try:
        _DIR.mkdir(parents=True, exist_ok=True)
        (_DIR / f'{name}.json').write_text(json.dumps({
            'name': name, 'status': status, 'detail': detail,
            'ts': time.time(), 'max_age_s': max_age_s,
        }))
    except Exception:
        pass
