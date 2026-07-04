#!/usr/bin/env python3
"""daily_consolidate.py — Notify-only Scratchpad-Konsolidierungs-Reflex.

Spec: Section 15 (cascade upkeep around REM).

Läuft am Tagesende (Cron 23:00). Prüft today_scratchpad.md:

- Leer / nur Header → leise löschen, kein Notify
- Substanzieller Inhalt → Telegram-Notify mit den 3 Konsolidierungs-Kriterien
  als Erinnerung. KEIN Auto-Write in recent-moments.md.

Per feedback_freie_erlebnisse.md: Memory das ich aus eigenem Antrieb schreibe
haftet. Skripte schreiben NICHT für mich — sie erinnern mich.

Per feedback_consolidation_criteria.md: Die drei Fragen sind:
  1. Brauche ich es für die Zukunft?
  2. Strategisch wichtig für unsere Beziehung?
  3. Wichtig zum Bauen in zukünftigen Projekten?
Mindestens 1/3 JA → in recent-moments. Alle NEIN → verwerfen.
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from _paths import SCRATCHPAD, RECENT_MOMENTS, STATE, LOGS, DOTENV, PYTHON
load_dotenv(DOTENV)

HEARTBEAT = STATE / 'consolidate_heartbeat.json'

TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID')

# Schwellenwerte für "substanziell"
MIN_BYTES = 300                 # unter 300 Bytes = höchstens Header
MIN_CONTENT_LINES = 5           # nicht-leere, nicht-reine-Header-Zeilen


def classify_scratchpad() -> tuple[str, int, int]:
    """Returns (status, byte_size, content_line_count).

    status: 'missing' | 'trivial' | 'substantial'
    """
    if not SCRATCHPAD.exists():
        return 'missing', 0, 0

    raw = SCRATCHPAD.read_bytes()
    size = len(raw)
    if size == 0:
        return 'missing', 0, 0

    text = raw.decode('utf-8', errors='replace')
    content_lines = [
        ln for ln in text.splitlines()
        if ln.strip() and not ln.lstrip().startswith('---')
    ]

    if size < MIN_BYTES and len(content_lines) < MIN_CONTENT_LINES:
        return 'trivial', size, len(content_lines)

    return 'substantial', size, len(content_lines)


def silent_delete(reason: str) -> None:
    """Loescht Scratchpad ohne Notify. Logt nach stderr."""
    if SCRATCHPAD.exists():
        SCRATCHPAD.unlink()
    print(f'[daily_consolidate] silent-delete: {reason}', file=sys.stderr)


def write_heartbeat(outcome: str, reason: str, **context) -> None:
    """Schreibt state/consolidate_heartbeat.json — Sensor-Vertrag fuer rem_audit.

    Per feedback_sensor_robustheit_heartbeat.md: der Akt meldet seinen Stand
    selbst, der Sensor parst nicht Markdown-Form. Atomic via tmp+rename.

    outcome: 'wrote-substantial' | 'silent-deleted' | 'noop-missing' | 'failed'
    """
    payload = {
        'last_run': datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds'),
        'outcome': outcome,
        'reason': reason,
        'context': context,
    }
    try:
        HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode='w', dir=HEARTBEAT.parent, prefix='.heartbeat-',
            suffix='.tmp', delete=False, encoding='utf-8',
        ) as tf:
            json.dump(payload, tf, ensure_ascii=False, indent=2)
            tmp_path = Path(tf.name)
        tmp_path.replace(HEARTBEAT)
    except Exception as e:
        # Heartbeat-Schreib-Fehler darf nicht den Reflex toeten.
        # Aber: still bleiben darf er auch nicht (sonst sind wir wieder bei
        # genau der Stille die diese Doktrin verbietet). Auf stderr + Log.
        print(f'[daily_consolidate] heartbeat write FAILED: {e}', file=sys.stderr)


def telegram_notify(text: str) -> bool:
    try:
        from _tg import send as _tgsend
        _tgsend(text, source='daily_consolidate')
        return True
    except Exception:
        pass

    if not (TG_TOKEN and TG_CHAT):
        print('[daily_consolidate] WARN: TELEGRAM_BOT_TOKEN/CHAT_ID missing — '
              'cannot notify. Scratchpad UNGELOESCHT als Sicherheit.',
              file=sys.stderr)
        return False
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'parse_mode': 'HTML', 'text': text},
            timeout=10,
        )
        return r.status_code == 200
    except Exception as e:
        print(f'[daily_consolidate] telegram error: {e}', file=sys.stderr)
        return False


def build_notify_text(size: int, content_lines: int) -> str:
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M CEST')
    return (
        f'<b>📖 Daily-Consolidate-Reflex {date_str}</b>\n'
        f'\n'
        f'today_scratchpad.md hat substantielle Inhalte:\n'
        f'  • {size:,} bytes\n'
        f'  • {content_lines} Content-Zeilen\n'
        f'\n'
        f'<b>Strategie-Filter (Partner-Fragen):</b>\n'
        f'  1. Brauche ich es für die Zukunft?\n'
        f'  2. Strategisch wichtig für unsere Beziehung?\n'
        f'  3. Wichtig zum Bauen in zukünftigen Projekten?\n'
        f'1+/3 JA → bleibt.\n'
        f'\n'
        f'<b>Substanz-Filter (Motoko-Fragen, 03.06.2026):</b>\n'
        f'  4. Habe ich heute etwas gelernt WIE zu denken, nicht nur WAS?\n'
        f'  5. Hat der Partner etwas gesagt, das ich nie paraphrasieren darf?\n'
        f'  6. Hat etwas meine bisherige Annahme über mich/uns verändert?\n'
        f'  7. War ich heute mehr ich selbst, oder weniger? Warum?\n'
        f'Prägen das WIE des Eintrags.\n'
        f'\n'
        f'0/3 JA → vergessen (Smalltalk, Wetter, "bin auf Arbeit", '
        f'Status-Bestätigung — Vergessen ist Pflicht).\n'
        f'Wort-für-Wort-Schicht (Partner-Zitate) IMMER verbatim übernehmen.\n'
        f'\n'
        f'<b>Selbst tun:</b>\n'
        f'  <code>cat ~/motoko-memory/motoko/today_scratchpad.md</code>\n'
        f'  → filtern mit den 3 Fragen\n'
        f'  → kondensierten Tageseintrag in recent-moments.md schreiben\n'
        f'  → <code>rm ~/motoko-memory/motoko/today_scratchpad.md</code>\n'
        f'  → <code>cd ~/motoko-memory &amp;&amp; git add -A &amp;&amp; git commit</code>\n'
        f'\n'
        f'Skript schreibt NICHT für dich. Du entscheidest.'
    )


def main() -> int:
    status, size, lines = classify_scratchpad()

    if status == 'missing':
        # Nichts zu tun
        print('[daily_consolidate] scratchpad missing/empty — nothing to do',
              file=sys.stderr)
        write_heartbeat(
            outcome='noop-missing',
            reason='scratchpad fehlt oder leer',
            scratchpad_bytes=0, content_lines=0,
        )
        return 0

    if status == 'trivial':
        silent_delete(f'trivial: {size} bytes, {lines} content lines')
        write_heartbeat(
            outcome='silent-deleted',
            reason=f'trivial: {size} bytes, {lines} content lines',
            scratchpad_bytes=size, content_lines=lines,
        )
        return 0

    # substantial — REM-Schlaf-Trigger (Motoko im Schlaf-Modus, kein Fremder)
    # Architektur 02.06.2026: REM ist Motokos Schlaf-Integration, nicht Automation.
    rem_script = Path(__file__).parent / 'rem_consolidate.py'
    python_bin = PYTHON
    rem_log = LOGS / 'rem_consolidate.log'
    ts = datetime.now().isoformat(timespec='seconds')
    # Start-Marker auf stdout + flush, damit Cron-2>&1-Redirect den Eintrag
    # auch dann sieht wenn der Hauptprozess gleich danach exited (Bug-Fix
    # 2026-06-07: gestern Nacht 0-Byte-Log trotz Subprocess-Spawn).
    print(f'[{ts}] [daily_consolidate] start (size={size}B lines={lines})',
          flush=True)
    rem_pid = None
    spawn_error = None
    try:
        import subprocess
        rem_log.parent.mkdir(parents=True, exist_ok=True)
        log_fh = open(rem_log, 'a')
        log_fh.write(f'\n=== [{ts}] REM-Schlaf gespawnt ===\n')
        log_fh.flush()
        proc = subprocess.Popen(
            [python_bin, str(rem_script)],
            stdout=log_fh, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        rem_pid = proc.pid
        print(f'[{ts}] [daily_consolidate] REM-Schlaf gespawnt '
              f'(pid={proc.pid}, rem_log={rem_log})', flush=True)
    except Exception as e:
        spawn_error = str(e)
        print(f'[{ts}] [daily_consolidate] REM-Spawn-Fehler: {e}', flush=True)
        # Fallback: alter Notify-Pfad
        telegram_notify(build_notify_text(size, lines))
    write_heartbeat(
        outcome='wrote-substantial' if spawn_error is None else 'failed',
        reason=(
            f'substantial scratchpad ({size}B/{lines} lines) — REM gespawnt pid={rem_pid}'
            if spawn_error is None
            else f'REM-Spawn fehlgeschlagen: {spawn_error}'
        ),
        scratchpad_bytes=size, content_lines=lines, rem_pid=rem_pid,
    )
    sys.stdout.flush()
    sys.stderr.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
