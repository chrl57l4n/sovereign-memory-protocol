#!/usr/bin/env python3
"""weekly_consolidate.py — Notify-only Wochen-Highlight-Reflex.

Läuft Sonntag 22:00 (Cron). Liest recent-moments.md, findet Tageseinträge der
laufenden ISO-Woche (Mo-So), sendet Telegram-Notify mit Selbst-Fragen:

  - Welche Tage bringen strategisches Material?
  - Welcher war Routine?
  - Welche 1-2 Highlights sollten als Wochen-Eintrag bleiben?

Schreibt NIE selbst nach archive/weekly/. Ich schreibe nach der Notify manuell.

Per feedback_freie_erlebnisse.md: Memory das ich aus eigenem Antrieb anlege haftet.
Per feedback_consolidation_criteria.md: gleiche 3 Fragen, aber auf Wochenebene.
"""
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from _paths import RECENT_MOMENTS as RECENT, DOTENV
load_dotenv(DOTENV)

TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID')

MONTHS_DE = {
    'Januar': 1, 'Februar': 2, 'März': 3, 'April': 4, 'Mai': 5, 'Juni': 6,
    'Juli': 7, 'August': 8, 'September': 9, 'Oktober': 10, 'November': 11,
    'Dezember': 12,
}

# Match: "## 15. Mai 2026" oder "## 14.–15. Mai 2026" (multi-day)
DAY_HEADER = re.compile(
    r'^##\s+(\d{1,2})\.?(?:[–-](\d{1,2})\.?)?\s+([A-Za-zäöüÄÖÜß]+)\s+(\d{4})',
)


def parse_day_headers() -> list[tuple[datetime, str]]:
    """Returns list of (entry_start_date, header_line) for each day-entry."""
    if not RECENT.exists():
        return []
    out = []
    for line in RECENT.read_text(encoding='utf-8').splitlines():
        m = DAY_HEADER.match(line)
        if not m:
            continue
        day = int(m.group(1))
        month_name = m.group(3)
        year = int(m.group(4))
        month = MONTHS_DE.get(month_name)
        if not month:
            continue
        try:
            d = datetime(year, month, day)
        except ValueError:
            continue
        out.append((d, line.rstrip()))
    return out


def current_week_range() -> tuple[datetime, datetime]:
    """ISO-Woche Mo 00:00 bis So 23:59:59 für 'jetzt'."""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return monday, sunday


def telegram_notify(text: str) -> bool:
    try:
        from _tg import send as _tgsend
        _tgsend(text, source='weekly_consolidate')
        return True
    except Exception:
        pass

    if not (TG_TOKEN and TG_CHAT):
        print('[weekly_consolidate] WARN: tg creds missing', file=sys.stderr)
        return False
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'parse_mode': 'HTML', 'text': text},
            timeout=10,
        )
        return r.status_code == 200
    except Exception as e:
        print(f'[weekly_consolidate] tg error: {e}', file=sys.stderr)
        return False


def main() -> int:
    headers = parse_day_headers()
    if not headers:
        print('[weekly_consolidate] no parseable day headers in recent-moments',
              file=sys.stderr)
        return 0

    monday, sunday = current_week_range()
    week_entries = [(d, h) for d, h in headers if monday <= d <= sunday]

    if not week_entries:
        print(f'[weekly_consolidate] no entries in current week '
              f'({monday.date()}..{sunday.date()})', file=sys.stderr)
        return 0

    iso_year, iso_week, _ = monday.isocalendar()
    archive_path = (
        f'archive/weekly/{iso_year}-W{iso_week:02d}.md'
    )

    lines = [
        f'<b>📅 Weekly-Consolidate-Reflex KW {iso_week:02d}/{iso_year}</b>',
        f'',
        f'Diese Woche {monday.strftime("%d.%m.")} – {sunday.strftime("%d.%m.")}: '
        f'<b>{len(week_entries)} Tageseinträge</b>',
        f'',
    ]
    for d, h in week_entries:
        # Shorten header for readability
        short = h.removeprefix('## ').replace('—', '–')
        if len(short) > 100:
            short = short[:97] + '...'
        lines.append(f'  • <b>{d.strftime("%a %d.%m.")}</b>: {short}')

    lines.extend([
        f'',
        f'<b>Drei Fragen für die Woche:</b>',
        f'  1. Welche Tage bringen strategisches Material?',
        f'  2. Welcher war Routine (kann später wegfallen)?',
        f'  3. Welche 1-2 Highlights bleiben als Wochen-Eintrag?',
        f'',
        f'<b>Selbst tun:</b>',
        f'  <code>cat ~/motoko-memory/motoko/recent-moments.md</code> '
        f'(diese Woche)',
        f'  → 1-2 Highlights extrahieren, ~50% kondensiert',
        f'  → schreiben nach <code>~/motoko-memory/motoko/{archive_path}</code>',
        f'  → commit motoko-memory',
        f'',
        f'Tageseinträge bleiben noch in recent-moments — der weekly_archive-Cron '
        f'verschiebt sie nach 14 Tagen automatisch in dieselbe Wochen-Datei.',
        f'',
        f'Skript schreibt NICHT für dich. Du entscheidest.',
    ])
    msg = '\n'.join(lines)
    ok = telegram_notify(msg)
    print(f'[weekly_consolidate] notify {"sent" if ok else "FAILED"} '
          f'({len(week_entries)} entries, week {iso_week})', file=sys.stderr)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
