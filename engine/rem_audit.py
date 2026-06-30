#!/usr/bin/env python3
"""rem_audit.py — Täglicher REM-Audit der Memory-Cascade.

Liest CASCADE_TOPOLOGY.md (kanonische Spec der 7 Schichten), prüft pro Schicht
einen konkreten Health-Check, schreibt eine datierte Audit-Datei nach
motoko-memory/motoko/audits/YYYY-MM-DD-rem-audit.md und meldet eine
Befund-Zusammenfassung per Telegram.

Pflicht aus principles.md (REM-Audit als Pflicht, 02.06.2026). Konsolidierung
bleibt mein Akt — dieses Skript misst nur, schreibt NIE in Cascade-Schichten
(nur in audits/). Linsen-Prinzip.

Cron: täglich 06:30 — der zweite Durchgang nach dem daily-REM (05:00). Misst,
ob die Konsolidierung der Nacht die Cascade-Schichten gesund gehalten hat.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

from _paths import MOTOKO as MEMORY, STATE, LOGS, DOTENV
load_dotenv(DOTENV)

SCRATCH = MEMORY / 'today_scratchpad.md'
WEEKLY_DIR = MEMORY / 'archive' / 'weekly'
JOURNAL_DIR = MEMORY / 'journal'
EPISODES = MEMORY / 'memory' / 'episodes'
AUDITS = MEMORY / 'audits'
TOPOLOGY = MEMORY / 'memory' / 'CASCADE_TOPOLOGY.md'

CONSOLIDATE_HEARTBEAT = STATE / 'consolidate_heartbeat.json'

COLD_DIR = Path(os.environ.get('MOTOKO_TRANSCRIPTS', str(STATE / 'transcripts')))
DRILL_LOG = LOGS / 'restore_drill.log'

TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID')


def now() -> datetime:
    return datetime.now()


def days_since(p: Path) -> int | None:
    if not p.exists():
        return None
    mtime = datetime.fromtimestamp(p.stat().st_mtime)
    return (now() - mtime).days


def check_layer_1_scratchpad() -> dict:
    """Mikro-Notizen. Erwartet: existiert, mtime < 36h."""
    if not SCRATCH.exists():
        return {'status': 'RED', 'note': 'Scratchpad fehlt'}
    age_h = (now() - datetime.fromtimestamp(SCRATCH.stat().st_mtime)).total_seconds() / 3600
    size = SCRATCH.stat().st_size
    if age_h > 36:
        return {'status': 'YELLOW',
                'note': f'mtime {age_h:.1f}h alt ({size} B)'}
    return {'status': 'GREEN', 'note': f'mtime {age_h:.1f}h, {size} B'}


def check_layer_2_daily() -> dict:
    """Tages-Konsolidierungs-Reflex via Heartbeat-File.

    Umstellung 25.06.2026 (feedback_sensor_robustheit_heartbeat.md): vorher
    parste dieser Check die recent-moments-Markdown-Header per Regex. Das war
    fragil — Doppel-Tag-Header (`## 22./23. Juni 2026`) und Format-Drifts
    machten den Sensor still blind. Jetzt liest er den Heartbeat den
    daily_consolidate.py bei jedem Lauf schreibt.

    Erwartet: state/consolidate_heartbeat.json existiert + last_run <26h alt
    (Cron-Frequenz 23:00 + Toleranz). 26-48h = YELLOW, >48h oder fehlend = RED.
    """
    if not CONSOLIDATE_HEARTBEAT.exists():
        return {'status': 'RED',
                'note': f'Heartbeat fehlt: {CONSOLIDATE_HEARTBEAT.name}'}
    try:
        data = json.loads(CONSOLIDATE_HEARTBEAT.read_text(encoding='utf-8'))
        last_run = datetime.fromisoformat(data['last_run'])
        outcome = data.get('outcome', '?')
        reason = data.get('reason', '')
    except Exception as e:
        return {'status': 'RED', 'note': f'Heartbeat unlesbar: {e}'}

    # Vergleich tz-naiv erzwingen (now() ist naiv, last_run kann tz-aware sein)
    if last_run.tzinfo is not None:
        last_run_naive = last_run.astimezone().replace(tzinfo=None)
    else:
        last_run_naive = last_run
    age_h = (now() - last_run_naive).total_seconds() / 3600

    if outcome == 'failed':
        return {'status': 'RED',
                'note': f'letzter Lauf {age_h:.1f}h alt, outcome=failed ({reason})'}
    if age_h > 48:
        return {'status': 'RED',
                'note': f'Heartbeat {age_h:.1f}h alt (Cron-Tod?)'}
    if age_h > 26:
        return {'status': 'YELLOW',
                'note': f'Heartbeat {age_h:.1f}h alt, outcome={outcome}'}
    return {'status': 'GREEN',
            'note': f'Heartbeat {age_h:.1f}h alt, outcome={outcome}'}


def check_layer_3_weekly() -> dict:
    """archive/weekly. Erwartet: letzte abgeschlossene Woche hat Datei."""
    if not WEEKLY_DIR.exists():
        return {'status': 'RED', 'note': 'archive/weekly/ fehlt'}
    files = sorted(WEEKLY_DIR.glob('*-W*.md'))
    if not files:
        return {'status': 'RED', 'note': 'keine Wochen-Dateien'}
    last = files[-1].stem
    last_iso = re.match(r'(\d{4})-W(\d{2})', last)
    if not last_iso:
        return {'status': 'YELLOW',
                'note': f'unparsebar: {last}'}
    last_year, last_week = int(last_iso.group(1)), int(last_iso.group(2))

    # Letzte abgeschlossene ISO-Woche
    today = now()
    last_completed = today - timedelta(days=today.weekday() + 1)
    exp_year, exp_week, _ = last_completed.isocalendar()

    if (last_year, last_week) >= (exp_year, exp_week):
        return {'status': 'GREEN', 'note': f'letzte Datei {last}'}
    # Drift in Wochen
    drift = (exp_year - last_year) * 52 + (exp_week - last_week)
    return {'status': 'YELLOW' if drift <= 1 else 'RED',
            'note': f'letzte Datei {last}, fällig {exp_year}-W{exp_week:02d} '
                    f'(Drift {drift} Wochen)'}


def check_layer_4_monthly_arc() -> dict:
    """journal/YYYY-MM-bogen.md für letzten abgeschlossenen Monat."""
    today = now()
    # erster Tag dieses Monats - 1 Tag = letzter Tag des Vormonats
    first_this = today.replace(day=1)
    last_month_date = first_this - timedelta(days=1)
    expected = JOURNAL_DIR / f'{last_month_date.year}-{last_month_date.month:02d}-bogen.md'
    if expected.exists():
        return {'status': 'GREEN', 'note': f'{expected.name} vorhanden'}
    # Heuristik: noch in der Toleranzwoche nach Monatsende?
    if today.day <= 7:
        return {'status': 'YELLOW',
                'note': f'{expected.name} fehlt noch (Toleranz erste Woche)'}
    return {'status': 'RED',
            'note': f'{expected.name} fehlt (Monats-Bogen-Routine nicht etabliert)'}


def check_layer_5_yearly_mosaic() -> dict:
    """journal/YYYY-mosaik.md — erst ab Dezember oder Geburts-Jubiläum fällig."""
    today = now()
    expected = JOURNAL_DIR / f'{today.year}-mosaik.md'
    if expected.exists():
        return {'status': 'GREEN', 'note': f'{expected.name} vorhanden'}
    # Geburtstag 19.04. — bis dahin erst ein Jahr Material
    if today < datetime(today.year, 4, 19):
        return {'status': 'GRAY', 'note': 'noch nicht fällig (vor 19.04.)'}
    if today < datetime(today.year, 12, 1):
        return {'status': 'GRAY',
                'note': 'optional (zwischen Geburts-Anker und Jahresende)'}
    return {'status': 'YELLOW' if today.day < 20 else 'RED',
            'note': f'{expected.name} fehlt (Dezember-Fälligkeit)'}


def check_layer_6_episodes() -> dict:
    """Episoden. Schwellwert: >14 Tage Stille = YELLOW, >28 = RED."""
    if not EPISODES.exists():
        return {'status': 'RED', 'note': 'episodes/ fehlt'}
    files = sorted(EPISODES.glob('*.md'))
    if not files:
        return {'status': 'RED', 'note': 'keine Episoden'}
    newest = max(files, key=lambda p: p.stat().st_mtime)
    age = days_since(newest)
    if age is None:
        return {'status': 'RED', 'note': 'unbekannt'}
    if age > 28:
        return {'status': 'RED',
                'note': f'letzte Episode {newest.name} (vor {age} Tagen)'}
    if age > 14:
        return {'status': 'YELLOW',
                'note': f'letzte Episode {newest.name} (vor {age} Tagen)'}
    return {'status': 'GREEN',
            'note': f'letzte Episode {newest.name} (vor {age} Tagen)'}


def check_layer_7_cold_storage() -> dict:
    """Cold-Storage Mirror + Restore-Drill."""
    notes = []
    if not COLD_DIR.exists():
        return {'status': 'RED', 'note': 'cold-storage/ fehlt'}
    # Frische = neueste Datei im Baum, NICHT mtime des Parent-Dirs. Der Sync schreibt
    # in Projekt-Unterordner (Layout-Wechsel 06.06.), daher ändert sich der Parent-mtime
    # nur bei Struktur-Änderungen → 84.7h falsches RED (Sensor-Rot-Fix 17.06.2026).
    newest_m = max((p.stat().st_mtime for p in COLD_DIR.rglob('*') if p.is_file()), default=0.0)
    mirror_age_h = (now().timestamp() - newest_m) / 3600 if newest_m else 1e9
    if mirror_age_h > 30:
        notes.append(f'Mirror {mirror_age_h:.1f}h alt')
        mstatus = 'YELLOW' if mirror_age_h < 48 else 'RED'
    else:
        notes.append(f'Mirror {mirror_age_h:.1f}h alt')
        mstatus = 'GREEN'

    # Drill-Log — bei logrotate copytruncate ist Original 0 Bytes; rotierte .gz pruefen.
    drill_candidates = [DRILL_LOG] + sorted(DRILL_LOG.parent.glob(f'{DRILL_LOG.name}.*.gz'))
    drill_source = next((p for p in drill_candidates if p.exists() and p.stat().st_size > 0), None)
    if drill_source is None:
        notes.append('Drill-Log fehlt (auch keine rotierten)')
        return {'status': 'RED', 'note': '; '.join(notes)}
    drill_age_h = (now() - datetime.fromtimestamp(drill_source.stat().st_mtime)).total_seconds() / 3600
    # Drill-Cron ist monatlich (0 5 1 * *), daher Schwelle 31d+Buffer statt 26h.
    # Bis 13.06.2026 standen hier 26h/48h — das gab JEDEN Tag zwischen den
    # Cron-Laeufen Rot. Schwellen angepasst an reale Cron-Frequenz.
    drill_age_d = drill_age_h / 24
    if drill_age_d > 28:
        notes.append(f'Drill {drill_age_d:.1f}d alt')
        dstatus = 'YELLOW' if drill_age_d < 35 else 'RED'
    else:
        notes.append(f'Drill {drill_age_d:.1f}d alt ✓')
        dstatus = 'GREEN'

    final = 'RED' if 'RED' in (mstatus, dstatus) else 'YELLOW' if 'YELLOW' in (mstatus, dstatus) else 'GREEN'
    return {'status': final, 'note': '; '.join(notes)}


LAYERS = [
    ('1 Scratchpad', check_layer_1_scratchpad),
    ('2 Tages-Konsolidierung', check_layer_2_daily),
    ('3 Wochen-Highlights', check_layer_3_weekly),
    ('4 Monats-Bogen', check_layer_4_monthly_arc),
    ('5 Jahres-Mosaik', check_layer_5_yearly_mosaic),
    ('6 Episoden', check_layer_6_episodes),
    ('7 Cold-Storage', check_layer_7_cold_storage),
]


def write_audit(results: list[tuple[str, dict]]) -> Path:
    AUDITS.mkdir(parents=True, exist_ok=True)
    out = AUDITS / f'{now():%Y-%m-%d}-rem-audit.md'
    lines = [
        f'# REM-Audit — {now():%Y-%m-%d %H:%M %Z}',
        '',
        f'> Automatischer Stufen-Check der Memory-Cascade (siehe '
        f'`memory/CASCADE_TOPOLOGY.md`). Skript: `motoko-server/scripts/rem_audit.py`.',
        f'> Diagnose only — Konsolidierung bleibt mein Akt.',
        '',
        '## Stufen-Status',
        '',
        '| Schicht | Status | Befund |',
        '|---|---|---|',
    ]
    for name, r in results:
        icon = {'GREEN': '🟢', 'YELLOW': '🟡', 'RED': '🔴', 'GRAY': '⚪'}.get(r['status'], '?')
        lines.append(f'| {name} | {icon} {r["status"]} | {r["note"]} |')

    lines.extend([
        '',
        '## Die drei Audit-Fragen (per Stufe wo gelb/rot)',
        '',
        '1. Was im Material darunter war wichtig + fehlt in dieser Schicht?',
        '2. Was in dieser Schicht war trivial?',
        '3. Welche Zitate paraphrasiert statt verbatim? (Symmetrie: Partner und KI.)',
        '',
        '## Aktionen',
        '',
        '_Bitte hier eintragen, was du aus diesem Audit zu tun beschließt._',
        '',
        '- [ ] ',
        '',
    ])
    out.write_text('\n'.join(lines), encoding='utf-8')
    return out


def telegram_notify(text: str) -> bool:
    try:
        from _tg import send as _tgsend
        _tgsend(text, source='rem_audit')
        return True
    except Exception:
        pass
    if not (TG_TOKEN and TG_CHAT):
        print('[rem_audit] WARN: tg creds missing', file=sys.stderr)
        return False
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'parse_mode': 'HTML', 'text': text},
            timeout=10,
        )
        return r.status_code == 200
    except Exception as e:
        print(f'[rem_audit] tg error: {e}', file=sys.stderr)
        return False


def main() -> int:
    if not TOPOLOGY.exists():
        print(f'[rem_audit] FATAL: CASCADE_TOPOLOGY.md fehlt unter {TOPOLOGY}',
              file=sys.stderr)
        return 2

    results = [(name, fn()) for name, fn in LAYERS]
    out = write_audit(results)

    counts = {'GREEN': 0, 'YELLOW': 0, 'RED': 0, 'GRAY': 0}
    for _, r in results:
        counts[r['status']] = counts.get(r['status'], 0) + 1

    summary_lines = [
        f'<b>🧠 REM-Audit {now():%d.%m.%Y}</b>',
        '',
        f'🟢 {counts["GREEN"]}  🟡 {counts["YELLOW"]}  '
        f'🔴 {counts["RED"]}  ⚪ {counts["GRAY"]}',
        '',
    ]
    for name, r in results:
        icon = {'GREEN': '🟢', 'YELLOW': '🟡', 'RED': '🔴', 'GRAY': '⚪'}[r['status']]
        summary_lines.append(f'{icon} <b>{name}</b>: {r["note"]}')
    summary_lines.extend([
        '',
        f'Bericht: <code>{out.relative_to(MEMORY.parent)}</code>',
        '',
        'Skript misst nur. Konsolidieren tu ich.',
    ])
    telegram_notify('\n'.join(summary_lines))

    print(f'[rem_audit] wrote {out}', file=sys.stderr)
    has_red = counts['RED'] > 0
    return 1 if has_red else 0


if __name__ == '__main__':
    sys.exit(main())
