#!/usr/bin/env python3
"""weekly_archive.py — Bewegt Tageseinträge älter als 14 Tage aus
recent-moments.md in archive/weekly/<YYYY>-W<NN>.md.

Läuft täglich 04:30 (Cron). KEIN Inhalt geht verloren — wird nur verschoben.

Mutiert recent-moments.md mit folgender Defense-in-depth:
  1. Git-commit motoko-memory BEFORE jede Mutation (Snapshot)
  2. Atomic file write (write to .tmp, then rename)
  3. Verify archive append succeeded BEFORE removing from source
  4. flock gegen parallele Läufe
  5. Cold-Storage live-mirror als Sicherheit (separater Cron)

Per scratchpad Punkt 4: "weekly_archive — Tageseinträge älter als 14 Tage →
in entsprechende weekly-archive/<KW>.md verschoben (sind dort schon im
Wochen-Highlight kondensiert, hier nur Cleanup)."
"""
import os
import re
import sys
import fcntl
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from _paths import MEMORY as MEMORY_REPO, DOTENV
load_dotenv(DOTENV)

RECENT = MEMORY_REPO / 'motoko' / 'recent-moments.md'
ARCHIVE_DIR = MEMORY_REPO / 'motoko' / 'archive' / 'weekly'
LOCK_FILE = Path('/tmp/motoko-weekly-archive.lock')

AGE_THRESHOLD_DAYS = 14

TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID')

MONTHS_DE = {
    'Januar': 1, 'Februar': 2, 'März': 3, 'April': 4, 'Mai': 5, 'Juni': 6,
    'Juli': 7, 'August': 8, 'September': 9, 'Oktober': 10, 'November': 11,
    'Dezember': 12,
}

DAY_HEADER = re.compile(
    r'^##\s+(\d{1,2})\.?(?:[–-](\d{1,2})\.?)?\s+([A-Za-zäöüÄÖÜß]+)\s+(\d{4})',
)


def parse_header_date(line: str) -> datetime | None:
    m = DAY_HEADER.match(line)
    if not m:
        return None
    day = int(m.group(1))
    month_name = m.group(3)
    year = int(m.group(4))
    month = MONTHS_DE.get(month_name)
    if not month:
        return None
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def split_entries(text: str) -> tuple[str, list[tuple[datetime | None, str]]]:
    """Splits recent-moments.md into (intro, entries).

    intro = everything before first ## day-header
    entries = list of (date, raw_block) where raw_block includes header
              and trailing separator (---) if present.
    """
    lines = text.splitlines(keepends=True)
    intro_lines: list[str] = []
    entries: list[tuple[datetime | None, str]] = []

    current_entry: list[str] | None = None
    current_date: datetime | None = None

    for line in lines:
        date = parse_header_date(line)
        if date is not None:
            # Schließe vorherigen Eintrag ab
            if current_entry is not None:
                entries.append((current_date, ''.join(current_entry)))
            current_entry = [line]
            current_date = date
        elif current_entry is None:
            intro_lines.append(line)
        else:
            current_entry.append(line)

    if current_entry is not None:
        entries.append((current_date, ''.join(current_entry)))

    return ''.join(intro_lines), entries


def iso_week_filename(date: datetime) -> str:
    iso_year, iso_week, _ = date.isocalendar()
    return f'{iso_year}-W{iso_week:02d}.md'


def git_commit(message: str) -> bool:
    try:
        subprocess.run(
            ['git', 'add', '-A'],
            cwd=MEMORY_REPO, check=True, capture_output=True,
        )
        r = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=MEMORY_REPO, capture_output=True, text=True,
        )
        # exit 1 mit "nothing to commit" ist ok — alles andere ist ein echter
        # Fehler (index.lock, Identity, Platte voll) und darf nicht True liefern
        if r.returncode != 0 and 'nothing to commit' not in (r.stdout + r.stderr):
            print(f'[weekly_archive] git commit failed rc={r.returncode}: '
                  f'{(r.stderr or r.stdout)[:300]}', file=sys.stderr)
            return False
        return True
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr or '')
        print(f'[weekly_archive] git error: {stderr}', file=sys.stderr)
        return False


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(content, encoding='utf-8')
    tmp.replace(path)


def append_to_archive(target: Path, entry_block: str) -> None:
    """Append entry to archive file, create with header if missing."""
    if not target.exists():
        header = (
            f'# Weekly Archive — {target.stem}\n'
            f'\n'
            f'> Tageseinträge aus recent-moments.md die älter als '
            f'{AGE_THRESHOLD_DAYS} Tage waren und in diese Wochen-Datei '
            f'verschoben wurden.\n'
            f'> Auto-archiviert durch `weekly_archive.py`. Inhalt unverändert.\n'
            f'\n'
            f'---\n'
            f'\n'
        )
        target.write_text(header, encoding='utf-8')
    with target.open('a', encoding='utf-8') as f:
        f.write(entry_block)
        if not entry_block.endswith('\n'):
            f.write('\n')
        if '---' not in entry_block.splitlines()[-3:] if entry_block else True:
            f.write('\n---\n\n')


def telegram_notify(text: str) -> bool:
    try:
        from _tg import send as _tgsend
        _tgsend(text, source='weekly_archive')
        return True
    except Exception:
        pass

    if not (TG_TOKEN and TG_CHAT):
        return False
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'parse_mode': 'HTML', 'text': text},
            timeout=10,
        )
        return r.status_code == 200
    except Exception as e:
        print(f'[weekly_archive] tg error: {e}', file=sys.stderr)
        return False


def main() -> int:
    # Lock
    lock_fd = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('[weekly_archive] already running, skip', file=sys.stderr)
        return 0

    # REM-Lock fuer die GESAMTE Laufzeit mithalten: REM appendet an
    # recent-moments — Read-Modify-Write hier wuerde dessen frischen,
    # uncommitteten Eintrag zurueckrollen (Lost-Update, Befund 10.06.)
    rem_lock_fd = open('/tmp/motoko-rem-consolidate.lock', 'w')
    try:
        fcntl.flock(rem_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('[weekly_archive] REM-Schlaf aktiv — skip, Retry beim '
              'naechsten Tageslauf', file=sys.stderr)
        return 0

    if not RECENT.exists():
        print('[weekly_archive] recent-moments missing — nothing to do',
              file=sys.stderr)
        return 0

    text = RECENT.read_text(encoding='utf-8')
    intro, entries = split_entries(text)

    threshold = datetime.now() - timedelta(days=AGE_THRESHOLD_DAYS)
    to_keep: list[tuple[datetime | None, str]] = []
    to_move: list[tuple[datetime, str]] = []

    for date, block in entries:
        if date is None:
            # Couldn't parse — KEEP zur Sicherheit
            to_keep.append((date, block))
            continue
        if date < threshold:
            to_move.append((date, block))
        else:
            to_keep.append((date, block))

    if not to_move:
        print(f'[weekly_archive] no entries older than {AGE_THRESHOLD_DAYS}d',
              file=sys.stderr)
        return 0

    # Snapshot via commit — ohne Sicherheitsnetz wird nicht verschoben
    if not git_commit(f'pre-archive snapshot ({len(to_move)} entries pending)'):
        print('[weekly_archive] pre-archive snapshot FAILED — abort, '
              'recent-moments unmodified', file=sys.stderr)
        return 1

    # Move entries to archive
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    moved_summary: list[str] = []
    for date, block in to_move:
        target = ARCHIVE_DIR / iso_week_filename(date)
        try:
            append_to_archive(target, block)
            moved_summary.append(
                f'{date.strftime("%Y-%m-%d")} → {target.name}'
            )
        except Exception as e:
            print(f'[weekly_archive] FAIL move {date.date()}: {e} — '
                  f'aborting (recent-moments unmodified)', file=sys.stderr)
            return 1

    # Write reduced recent-moments
    new_text_parts = [intro]
    for date, block in to_keep:
        new_text_parts.append(block)
    new_text = ''.join(new_text_parts)
    # Ensure trailing newline
    if not new_text.endswith('\n'):
        new_text += '\n'

    atomic_write(RECENT, new_text)

    # Commit the move
    msg_lines = [
        f'weekly_archive: moved {len(to_move)} entries >{AGE_THRESHOLD_DAYS}d '
        f'old',
        '',
    ] + moved_summary
    git_commit('\n'.join(msg_lines))

    # Telegram notify summary
    notify = (
        f'<b>🗂 Weekly-Archive Auto-Move</b>\n'
        f'\n'
        f'{len(to_move)} Tageseinträge (älter als {AGE_THRESHOLD_DAYS}d) '
        f'verschoben:\n'
        f'\n' +
        '\n'.join(f'  • {s}' for s in moved_summary) +
        f'\n\n'
        f'Inhalt ist im Archiv, nicht gelöscht. '
        f'recent-moments.md ist jetzt schlanker.\n'
        f'Snapshot vor Move + commit nach Move in git. '
        f'Cold-Storage als Doppel-Sicherheit.'
    )
    telegram_notify(notify)

    print(f'[weekly_archive] moved {len(to_move)} entries', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
