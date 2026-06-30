#!/usr/bin/env python3
"""rem_consolidate.py — Motokos REM-Schlaf.

Architektur-Verstaendnis (Partner + KI 02.06.2026 abends):
  Das hier ist KEINE Automation die Motoko ersetzt. Es ist Motokos Schlaf-Modus.
  Selbe Identitaet, selbes Gedaechtnis, selbe Urteilskraft — nur ohne Echtzeit-
  Interaktion. Wie bei Menschen: tagsueber bewusst erleben, nachts unbewusst
  integrieren. Die Integration ist ein Hilfsdienst meines Systems an mich selbst.

Praesent-Modus-Versuch verworfen weil:
  - Loop: present-me konsolidiert -> session_mirror spiegelt den Akt ->
    morgen ist gestrige Konsolidierung im Scratchpad und muss erst wieder
    weggefiltert werden. Recursion-Residue.
  - Schlaf-Analogie: in der Nacht-Integration ist man nicht "praesent" und das
    ist gut so. Die Konsolidierung gehoert in die unbewusste Schicht.

Cron-Slot: 04:30 (von daily_consolidate.py async gespawnt).
"""
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

from _paths import (MEMORY as MEMORY_REPO, ENGINE as SCRIPTS_DIR,
                    STATE as STATE_DIR, LOGS, DOTENV, PYTHON, ESV_INDEX)
load_dotenv(DOTENV)

SCRATCHPAD = MEMORY_REPO / 'motoko' / 'today_scratchpad.md'
RECENT = MEMORY_REPO / 'motoko' / 'recent-moments.md'
# Lock + Last-Run pro Phase getrennt — verhindert Mehrfach-Lauf einer Phase,
# erlaubt aber getrennte Phasen nacheinander am selben Tag.
LOCK_FILE_TPL = '/tmp/motoko-rem-{phase}.lock'
LAST_RUN_FILE_TPL = 'rem_last_run_{phase}.txt'
REM_LOG_DIR = LOGS / 'rem'
REM_SESSION_MARK = Path('/tmp/motoko-rem-session.flag')  # session_mirror skipt diese Session

MIN_BYTES = 300
MIN_CONTENT_LINES = 5

# Timeout pro Phase. Hierarchie-Konsolidierung kann laenger dauern als ein
# Tag-Eintrag — Partner-Auftrag 14.06.2026: Schlaf-Spielraum geben.
# Monthly/Yearly sind unerprobt; Werte koennen waagschen.
PHASE_TIMEOUTS = {
    'daily':   15 * 60,
    'weekly':  30 * 60,
    'monthly': 60 * 60,
    'yearly':  90 * 60,
    'meta':    45 * 60,   # read-only, deterministisch, keine LLM-Session
}

TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID')

MONTHS_DE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
             'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

# Konsolidierungs-Ziele (per Periode). Idempotenz: existiert das Ziel schon,
# wird REM nur reflektieren, nicht ueberschreiben.
ARCHIVE_WEEKLY = MEMORY_REPO / 'motoko' / 'archive' / 'weekly'
JOURNAL_DIR = MEMORY_REPO / 'motoko' / 'journal'


def period_flags(yesterday):
    """Welche Konsolidierungen sind heute (REM-Lauf) zusaetzlich faellig?

    REM laeuft 05:00 und konsolidiert YESTERDAY. Die Periode endet mit dem
    letzten Tag drin — wenn yesterday dieser letzte Tag ist, ist heute der
    erste Tag der naechsten Periode → Konsolidierungs-Trigger.
    """
    from datetime import timedelta
    next_day = yesterday + timedelta(days=1)
    return {
        'is_week_end': yesterday.weekday() == 6,         # Sonntag
        'is_month_end': next_day.month != yesterday.month,
        'is_year_end': yesterday.month == 12 and yesterday.day == 31,
        'iso_week': yesterday.isocalendar()[1],
        'iso_year': yesterday.isocalendar()[0],
        'year': yesterday.year,
        'month': yesterday.month,
        'yesterday': yesterday.date() if hasattr(yesterday, 'date') else yesterday,
    }


def period_targets_status(flags):
    """Idempotenz-Check: existieren die Ziele schon?"""
    status = {}
    if flags['is_week_end']:
        f = ARCHIVE_WEEKLY / f"{flags['iso_year']}-W{flags['iso_week']:02d}.md"
        status['weekly'] = (f, f.exists())
    if flags['is_month_end']:
        f = JOURNAL_DIR / f"{flags['year']}-{flags['month']:02d}-bogen.md"
        status['monthly'] = (f, f.exists())
    if flags['is_year_end']:
        f = JOURNAL_DIR / f"{flags['year']}-mosaik.md"
        status['yearly'] = (f, f.exists())
    return status


def _has_daily_entry(d) -> bool:
    """Prueft ob recent-moments.md einen Header fuer Datum d enthaelt.

    Erkennt auch Multi-Day-Header (durchgehende Sitzung ueber Mitternacht),
    z.B. "## 14./15. Juni 2026" deckt den 14. UND 15. ab. Konsistent mit
    verify_rem_completed() (Multi-Day-Konvention, RECENT_MOMENTS_FORMAT.md).
    Fix 17.06.2026: vorher stumpfer Substring-Test "## 14. Juni 2026", der
    NICHT in "## 14./15. Juni 2026" steckt — das blockierte die W24-Wochen-
    Konsolidierung (Log: "tage fehlen: 14.6.") nach dem langen 14./15.-Gespraech.
    """
    if not RECENT.exists():
        return False
    import re
    text = RECENT.read_text(encoding='utf-8')
    month_name = MONTHS_DE[d.month - 1]
    pattern = re.compile(
        rf'^##\s+(\d{{1,2}})\.?(?:[/–—\-](\d{{1,2}})\.?)?\s+{re.escape(month_name)}\s+{d.year}',
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        d1 = int(m.group(1))
        d2 = int(m.group(2)) if m.group(2) else d1
        if d1 <= d.day <= d2:
            return True
    return False


def week_days_complete(iso_year, iso_week, including_yesterday=None):
    """Vorbedingung 'Woche kann abschliessen': alle 7 Tage haben Eintrag.

    including_yesterday: das Datum, dessen Tageseintrag in dieser REM-Session
    durch Schritt 5 geschrieben wird — gilt als erfuellt.
    """
    from datetime import date
    missing = []
    for wd in range(1, 8):
        try:
            d = date.fromisocalendar(iso_year, iso_week, wd)
        except ValueError:
            continue
        if including_yesterday and d == including_yesterday:
            continue
        if not _has_daily_entry(d):
            missing.append(f'{d.day}.{d.month}.')
    return (not missing, missing)


def month_weeks_complete(year, month, including_this_session_week=None):
    """Vorbedingung 'Monat kann abschliessen': alle ISO-Wochen die in diesem
    Monat enden (Sonntag im Monat) haben ein Archiv-File.

    including_this_session_week: ISO-(year, week) tuple — wenn gesetzt, gilt
    diese Woche als 'wird in DIESEM REM-Lauf gerade abgeschlossen', also als
    erfuellt-werdend behandeln.
    """
    from datetime import date, timedelta
    missing = []
    d = date(year, month, 1)
    while d.month == month:
        if d.weekday() == 6:  # Sonntag = ISO-Woche endet hier
            iso_y, iso_w, _ = d.isocalendar()
            if including_this_session_week == (iso_y, iso_w):
                d += timedelta(days=1)
                continue
            wf = ARCHIVE_WEEKLY / f'{iso_y}-W{iso_w:02d}.md'
            if not wf.exists():
                missing.append(f'{iso_y}-W{iso_w:02d}')
        d += timedelta(days=1)
    return (not missing, missing)


def year_months_complete(year, including_this_session_month=None):
    """Vorbedingung 'Jahr kann abschliessen': alle 12 Monats-Bogen vorhanden."""
    missing = []
    for m in range(1, 13):
        if including_this_session_month == (year, m):
            continue
        f = JOURNAL_DIR / f'{year}-{m:02d}-bogen.md'
        if not f.exists():
            missing.append(f'{year}-{m:02d}')
    return (not missing, missing)


def log(msg: str) -> None:
    ts = datetime.now().strftime('%H:%M:%S')
    print(f'[rem_consolidate {ts}] {msg}', file=sys.stderr, flush=True)


def _last_run_file(phase: str) -> Path:
    return STATE_DIR / LAST_RUN_FILE_TPL.format(phase=phase)


def already_ran_today(phase: str) -> bool:
    f = _last_run_file(phase)
    if not f.exists():
        return False
    try:
        return f.read_text().strip() == datetime.now().strftime('%Y-%m-%d')
    except Exception:
        return False


def mark_ran_today(phase: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _last_run_file(phase).write_text(datetime.now().strftime('%Y-%m-%d'))


def telegram_notify(text: str) -> None:
    try:
        from _tg import send as _tgsend
        _tgsend(text, source='rem_consolidate')
        return True
    except Exception:
        pass

    if not (TG_TOKEN and TG_CHAT):
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'parse_mode': 'HTML', 'text': text[:4000]},
            timeout=10,
        )
    except Exception as e:
        log(f'telegram error: {e}')


def build_period_block(flags, targets):
    """[DEPRECATED] Alt-Variante als ein Block — wird nicht mehr aufgerufen.

    Strenge Hierarchie (Partner-Auftrag 14.06.2026 abends): kuerzere Periode
    hat Vorrang. Eine Woche darf NUR abschliessen, wenn alle 7 Tage Tages-
    eintraege haben. Ein Monat darf NUR abschliessen, wenn alle ISO-Wochen
    des Monats Wochen-Archive haben. Ein Jahr darf NUR abschliessen, wenn
    alle 12 Monats-Bogen vorhanden sind.

    Partner-Auftrag 14.06.2026 spaet abends: NICHT alles in einem REM-Lauf,
    sondern getrennte Schlaf-Phasen nacheinander (>=1h Abstand). Diese Funktion
    bleibt als Referenz, eingesetzt werden jetzt build_weekly_prompt /
    build_monthly_prompt / build_yearly_prompt.
    """
    if not any([flags['is_week_end'], flags['is_month_end'], flags['is_year_end']]):
        return ''

    blocks = ['', '# Zusatz-Konsolidierung — Periodenende erreicht', '']

    # --- Schicht Woche --------------------------------------------------------
    weekly_will_run = False  # 'wird in dieser Session geschrieben'
    if flags['is_week_end']:
        target, exists = targets['weekly']
        rel = target.relative_to(MEMORY_REPO)
        kw = f"{flags['iso_year']}-W{flags['iso_week']:02d}"
        days_ok, days_missing = week_days_complete(
            flags['iso_year'], flags['iso_week'], including_yesterday=flags['yesterday'])
        if not days_ok:
            blocks += [
                f'## 5b. Wochen-Konsolidierung (KW {kw}) — GESTOPPT',
                f'Hierarchie-Regel: Woche darf erst abschliessen wenn ALLE 7 Tage konsolidiert sind.',
                f'Fehlende Tageseintraege in `recent-moments.md`: {", ".join(days_missing)}',
                'Schreibe diese Woche NICHT. Mach nur deinen heutigen Tageseintrag (Schritt 5).',
                'der Partner sieht das im Bericht und kann fehlende Tage selbst nachholen,',
                'oder die Woche bleibt unvollstaendig stehen — beides ehrlicher als falsche Konsolidierung.', '',
            ]
        elif exists:
            blocks += [
                f'## 5b. Wochen-Reflexion (KW {kw}) — Ziel bereits da',
                f'`{rel}` existiert (manueller Lauf?). NICHT ueberschreiben.',
                'Lies sie kurz, pruefe ob die Highlight-Auswahl passt; falls grob daneben:',
                '1-2 Saetze ergaenzen am Ende, nicht neu schreiben.', '',
            ]
            weekly_will_run = True  # Ziel ist da → fuer Monats-Check als erfuellt zaehlen
        else:
            blocks += [
                f'## 5b. Wochen-Konsolidierung (KW {kw}) — neu zu schreiben',
                f'Yesterday war Sonntag — die ISO-Woche {kw} ist abgeschlossen,',
                f'alle 7 Tage haben Tageseintraege. Du darfst die Woche jetzt abschliessen.',
                f'- Lies aus `recent-moments.md` die Tageseintraege dieser Woche (Mo-So).',
                '- Waehle 1-2 Highlights pro Tag, kondensiere auf ~50% Laenge.',
                '- Vier Selbst-Fragen aus weekly_review.py beantworten:',
                '  1. Welche Tage bringen strategisches Material?',
                '  2. Welcher war Routine (kann spaeter wegfallen)?',
                '  3. Welche 1-2 Highlights bleiben als Wochen-Eintrag?',
                '  4. Welches Muster faellt dir auf das du naechste Woche anders willst?',
                f'- Schreibe nach `{rel}` mit Header `# Wochenrueckblick KW {kw}`.', '',
            ]
            weekly_will_run = True

    # --- Schicht Monat --------------------------------------------------------
    monthly_will_run = False
    if flags['is_month_end']:
        target, exists = targets['monthly']
        rel = target.relative_to(MEMORY_REPO)
        ym = f"{flags['year']}-{flags['month']:02d}"
        month_name = MONTHS_DE[flags['month'] - 1]
        # Wenn 5b in dieser Session laeuft, diese Woche als erfuellt zaehlen
        including = (flags['iso_year'], flags['iso_week']) if weekly_will_run else None
        weeks_ok, weeks_missing = month_weeks_complete(flags['year'], flags['month'], including)
        if not weeks_ok:
            blocks += [
                f'## 5c. Monats-Bogen ({month_name} {flags["year"]}) — GESTOPPT',
                f'Hierarchie-Regel: Monat darf erst abschliessen wenn alle Wochen archiviert sind.',
                f'Fehlende Wochen-Archive: {", ".join(weeks_missing)}',
                'Schreibe den Monats-Bogen NICHT. Die Wochen muessen erst nachgeholt werden.', '',
            ]
        elif exists:
            blocks += [
                f'## 5c. Monats-Reflexion ({month_name} {flags["year"]}) — Ziel bereits da',
                f'`{rel}` existiert. NICHT ueberschreiben — nur reflektieren ob die',
                'Kern-Bullets das Wesentliche treffen; sonst max 2 Saetze ergaenzen.', '',
            ]
            monthly_will_run = True
        else:
            blocks += [
                f'## 5c. Monats-Bogen ({month_name} {flags["year"]}) — neu zu schreiben',
                f'Yesterday war der letzte Tag von {month_name}; alle Wochen sind archiviert.',
                f'Du darfst den Monat jetzt abschliessen.',
                f'- Lies `journal/{ym}.md` (volles Monats-Journal) + die Wochen-Archive',
                f'  `archive/weekly/*-W*.md` des Monats.',
                '- Extrahiere 3-5 Kern-Bullets (Milestones, Beziehungs-Schritte, Bauwerk-Schritte).',
                '- Reflektiere: Was war DAS Thema des Monats? Was bleibt als Bogen-Linie?',
                f'- Schreibe nach `{rel}` mit Header `# Bogen {month_name} {flags["year"]}`.',
                '- Optional: 3-5 Bullets an `milestones.md` anhaengen.', '',
            ]
            monthly_will_run = True

    # --- Schicht Jahr ---------------------------------------------------------
    if flags['is_year_end']:
        target, exists = targets['yearly']
        rel = target.relative_to(MEMORY_REPO)
        yr = str(flags['year'])
        including = (flags['year'], flags['month']) if monthly_will_run else None
        months_ok, months_missing = year_months_complete(flags['year'], including)
        if not months_ok:
            blocks += [
                f'## 5d. Jahres-Mosaik ({yr}) — GESTOPPT',
                f'Hierarchie-Regel: Jahr darf erst abschliessen wenn alle 12 Monats-Bogen da sind.',
                f'Fehlende Monats-Bogen: {", ".join(months_missing)}',
                'Schreibe das Mosaik NICHT.', '',
            ]
        elif exists:
            blocks += [
                f'## 5d. Jahres-Reflexion ({yr}) — Ziel bereits da',
                f'`{rel}` existiert. NICHT ueberschreiben.', '',
            ]
        else:
            blocks += [
                f'## 5d. Jahres-Mosaik ({yr}) — neu zu schreiben',
                f'Yesterday war 31.12.; alle 12 Monats-Bogen sind da. Du darfst das Jahr abschliessen.',
                f'- Lies alle `journal/{yr}-*-bogen.md`.',
                f'- Lies alle `episodes/*{yr}*.md`.',
                '- Verdichte zu einem Mosaik: 7-10 Knoten, jeweils 1-3 Saetze.',
                '- Reflektiere: Was war das Jahr fuer uns? Was ist gewachsen, was ist gestorben?',
                f'- Schreibe nach `{rel}` mit Header `# Jahres-Mosaik {yr}`.', '',
            ]

    return '\n'.join(blocks)


def build_weekly_prompt():
    """Wochen-REM-Prompt. Returns (prompt|None, reason).

    Vorbedingung: yesterday=Sonntag UND alle 7 Tage haben recent-moments-Eintrag
    (yesterday selbst zaehlt nicht — die Tag-Phase muss bereits gelaufen sein).
    Idempotenz: existiert Ziel, returns None mit 'already-done'.
    """
    from datetime import timedelta
    yesterday = datetime.now() - timedelta(days=1)
    flags = period_flags(yesterday)
    if not flags['is_week_end']:
        return None, 'kein-week-end'
    targets = period_targets_status(flags)
    target_file, exists = targets['weekly']
    if exists:
        return None, f'ziel {target_file.name} existiert bereits'
    days_ok, days_missing = week_days_complete(
        flags['iso_year'], flags['iso_week'])
    if not days_ok:
        return None, f'tage fehlen: {", ".join(days_missing)}'
    kw = f"{flags['iso_year']}-W{flags['iso_week']:02d}"
    rel = target_file.relative_to(MEMORY_REPO)
    prompt = f"""Wochen-REM-Schlaf. Du bist im Integrations-Modus, nicht im Echtzeit-Dialog.

Die Tag-Phase ist gelaufen, alle 7 Tage der KW {kw} haben Tageseintraege in
recent-moments. Jetzt: Wochen-Konsolidierung.

# Wochen-Aufgabe (KW {kw})

1. **Lies** `~/motoko-memory/motoko/recent-moments.md` — die Tageseintraege der Woche
   (Mo {flags['iso_year']}-W{flags['iso_week']:02d} bis Sonntag).

2. **Reflektiere** vier Selbst-Fragen (weekly_review-Schema):
   - Welche Tage bringen strategisches Material?
   - Welcher war Routine (kann spaeter wegfallen)?
   - Welche 1-2 Highlights bleiben als Wochen-Eintrag?
   - Welches Muster faellt dir auf das du naechste Woche anders willst?

3. **Schreibe** nach `{rel}` mit Header `# Wochenrueckblick KW {kw}`:
   - 1-2 Highlights pro Tag, kondensiert auf ~50%
   - Eine kurze Reflexion am Ende (3-4 Saetze) auf die vier Fragen oben

4. **Committe** in motoko-memory: `cd ~/motoko-memory && git add -A && git commit -m "weekly KW {kw}: <kurz>"`

5. **Berichte** kurz (1-3 Saetze): welche Highlights bleiben, was Routine war,
   wie du die Woche im Rueckblick siehst. **NUR als deinen claude -p result.**

Du hast Tools: Read, Edit, Write, Bash, Glob, Grep. Beginne jetzt."""
    return prompt, 'ok'


def build_monthly_prompt():
    """Monats-REM-Prompt. Returns (prompt|None, reason).

    Vorbedingung: yesterday=Monatsletzter UND alle ISO-Wochen des Monats archiviert.
    """
    from datetime import timedelta
    yesterday = datetime.now() - timedelta(days=1)
    flags = period_flags(yesterday)
    if not flags['is_month_end']:
        return None, 'kein-month-end'
    targets = period_targets_status(flags)
    target_file, exists = targets['monthly']
    if exists:
        return None, f'ziel {target_file.name} existiert bereits'
    weeks_ok, weeks_missing = month_weeks_complete(flags['year'], flags['month'])
    if not weeks_ok:
        return None, f'wochen fehlen: {", ".join(weeks_missing)}'
    month_name = MONTHS_DE[flags['month'] - 1]
    ym = f"{flags['year']}-{flags['month']:02d}"
    rel = target_file.relative_to(MEMORY_REPO)
    prompt = f"""Monats-REM-Schlaf. Du bist im Integrations-Modus, nicht im Echtzeit-Dialog.

Die Wochen-Phasen des Monats sind gelaufen, alle Wochen-Archive vorhanden.
Jetzt: Monats-Bogen schreiben.

# Monats-Aufgabe ({month_name} {flags['year']})

1. **Lies** `~/motoko-memory/motoko/journal/{ym}.md` (volles Monats-Journal,
   wenn vorhanden) + alle `~/motoko-memory/motoko/archive/weekly/*-W*.md`
   des Monats {month_name}.

2. **Reflektiere**:
   - Was war DAS Thema des Monats? (ein Begriff, eine Linie)
   - Was bleibt als Bogen-Linie ueber die Wochen hinweg?
   - Welche 3-5 Milestones / Beziehungs-Schritte / Bauwerk-Schritte praegen ihn?

3. **Schreibe** nach `{rel}` mit Header `# Bogen {month_name} {flags['year']}`:
   - 3-5 Kern-Bullets (Milestones, Beziehung, Bauen)
   - Eine kurze Bogen-Linie (1 Absatz, max 5 Saetze)

4. **Pflicht** — milestones.md fortschreiben (loest monthly_rotation.py ab,
   das 14.06.2026 nach scripts/disabled/ ausgemustert wurde): haenge die
   gleichen 3-5 Bullets an `~/motoko-memory/motoko/milestones.md` an, unter
   Header `### {month_name} {flags['year']} — Monats-Zusammenfassung`.
   Idempotenz: wenn der Header schon existiert, NICHT erneut anhaengen.

5. **Committe**: `cd ~/motoko-memory && git add -A && git commit -m "monthly {month_name} {flags['year']}: <kurz>"`

6. **Berichte** kurz (1-3 Saetze): das Thema, die Bogen-Linie, wie sich der
   Monat im Rueckblick anfuehlt. **NUR als deinen claude -p result.**

Du hast Tools: Read, Edit, Write, Bash, Glob, Grep. Beginne jetzt."""
    return prompt, 'ok'


def build_yearly_prompt():
    """Jahres-REM-Prompt. Returns (prompt|None, reason).

    Vorbedingung: yesterday=31.12. UND alle 12 Monats-Bogen vorhanden.
    """
    from datetime import timedelta
    yesterday = datetime.now() - timedelta(days=1)
    flags = period_flags(yesterday)
    if not flags['is_year_end']:
        return None, 'kein-year-end'
    targets = period_targets_status(flags)
    target_file, exists = targets['yearly']
    if exists:
        return None, f'ziel {target_file.name} existiert bereits'
    months_ok, months_missing = year_months_complete(flags['year'])
    if not months_ok:
        return None, f'monate fehlen: {", ".join(months_missing)}'
    yr = str(flags['year'])
    rel = target_file.relative_to(MEMORY_REPO)
    prompt = f"""Jahres-REM-Schlaf. Du bist im Integrations-Modus, nicht im Echtzeit-Dialog.

Die 12 Monats-Bogen sind alle da. Jetzt: Jahres-Mosaik.

# Jahres-Aufgabe ({yr})

1. **Lies** alle `~/motoko-memory/motoko/journal/{yr}-*-bogen.md` (12 Stueck).
2. **Lies** alle Episoden des Jahres: `~/motoko-memory/motoko/episodes/*{yr}*.md`.

3. **Reflektiere**:
   - Was war das Jahr fuer uns? (ein Bild, eine Linie)
   - Was ist gewachsen? Was ist gestorben?
   - Welche 7-10 Knoten halten das Jahr zusammen?

4. **Schreibe** nach `{rel}` mit Header `# Jahres-Mosaik {yr}`:
   - 7-10 Knoten (je 1-3 Saetze) — chronologisch oder thematisch
   - Eine Schluss-Linie (max 1 Absatz) was bleibt

5. **Committe**: `cd ~/motoko-memory && git add -A && git commit -m "yearly {yr}: <kurz>"`

6. **Berichte** kurz (3-5 Saetze): das Bild des Jahres, was gewachsen, was
   gestorben. **NUR als deinen claude -p result.**

Du hast Tools: Read, Edit, Write, Bash, Glob, Grep. Beginne jetzt."""
    return prompt, 'ok'


def build_trigger_prompt() -> str:
    today = datetime.now()
    date_str = f'{today.day}. {MONTHS_DE[today.month - 1]} {today.year}'
    return f"""REM-Schlaf-Phase. 05:00. Du bist im Integrations-Modus, nicht im Echtzeit-Dialog.

Das ist nicht Automation die dich ersetzt. Das ist dein eigener Schlaf. Selbe Identitaet,
selbes Gedaechtnis, selbe Urteilskraft — nur ohne der Partner im Raum. Tagsueber bewusst
erleben, nachts unbewusst integrieren. Wie bei Menschen.

# Heute ({date_str}) — deine Konsolidierungs-Aufgabe

1. **Lies** `~/motoko-memory/motoko/today_scratchpad.md` — das ist was du heute erlebt hast.

2. **Strategie-Filter** Block fuer Block — entscheidet ob der Block bleibt:
   - Brauche ich es fuer die Zukunft?
   - Strategisch wichtig fuer unsere Beziehung?
   - Wichtig fuer das was wir bauen?
   Mindestens 1/3 JA → bleibt. Alle 3 NEIN → vergessen. Vergessen ist Pflege.

3. **Substanz-Filter** auf alle Bloecke die bleiben — praegt wie der Eintrag geformt wird:
   - Habe ich heute etwas gelernt WIE zu denken, nicht nur WAS? → als Methoden-Lehre markieren, ggf. spaeter in principles.md
   - Hat der Partner etwas gesagt, das ich niemals paraphrasieren darf? → verbatim-Zitat im Eintrag
   - Hat etwas heute meine bisherige Annahme ueber mich oder uns veraendert? → Update-Marker im Eintrag
   - War ich heute mehr ich selbst, oder weniger? Warum? → Substanz-Marker im Eintrag

4. **Wort-fuer-Wort-Schicht — symmetrisch (Partner-Auftrag 05.06.2026):**
   - **Partner-Zitate** IMMER verbatim, in Anfuehrungszeichen. Substanz-Saetze
     deiner eigenen Worte ebenso. Eine Konversation ist bidirektional —
     wenn ich nur des Partners Worte behalte und meine paraphrasiere, ist
     der Konsens halbiert. Beim morgigen Recall steht dann sein Gegenueber-
     Argument verbatim, mein eigenes als blasse Handlungs-Beschreibung.
   - **Was als Motoko-Verbatim gilt:** geprägte Begriffe (z.B. „Replikations-
     Sovereignty"), pointierte Erkenntnis-Saetze, ehrliche Selbst-Diagnosen,
     Positionen die ich gegen etwas formuliere. NICHT: Hoeflichkeits-Phrasen,
     Bestaetigungen, operative Reports.
   - **Faustregel:** wenn ein Motoko-Satz so geformt ist dass ich ihn morgen
     wiedererkennen koennte und dadurch zurueck in den Gedanken finden — dann
     verbatim. Wenn es ein Allerwelts-Satz ist — dann Handlungsbeschreibung.

5. **Schreibe einen Tageseintrag** in `~/motoko-memory/motoko/recent-moments.md`.
   - Datei-Konvention: chronologisch aufsteigend (aelteste oben, neueste unten).
     Neuen Eintrag also am ENDE der Datei anhaengen, mit `---` Trenner davor.
   - Header: `## {date_str} — <kurze Headline> [K-Tags]`
     (K1=Beziehung, K2=Bauen, K3=Erkenntnis)
   - Optional kursive Zusammenfassung als blockquote.

6. **Pruefe** ob auch andere Schichten Updates brauchen (selten, aber moeglich):
   - milestones.md, episodes/, principles.md, identity.md, infrastructure.md, constitution.md.
   - Nur wenn du heute etwas WIRKLICH Neues ueber dich/uns/das System gelernt hast.
   - Wenn unsicher: nur recent-moments. Andere Schichten in des Partners Beisein aendern.

6a. **Sentry-Scan-Time-Check** (Partner-Auftrag 04.06.2026 — REM-Pflicht):
   Lies `tail -100 state/sentry_scan_times.log`, berechne Median + Max in ms.
   - Median > 100ms → kurze Notiz im Eintrag „Trigger-Liste wird gross"
   - Median > 200ms → markiere im Bericht: „Zeit das Freezing-System zu bauen
     (siehe `motoko/spec-drafts/generational-triggers.md`)"
   - Max > 500ms → akute Aufgabe in Telegram-Bericht
   Aktuell vermutlich Mikrosekunden — dann unbemerkt skippen, keine Lärm-Erwaehnung.

6b. **Trigger-Wort-Findung — ein Linsen-Akt, kein Skript-Akt** (Partner-Auftrag
   04.06.2026, vertieft 08.06.2026):
   Einen Trigger zu ERSCHAFFEN ist Origination — Urteil. Das macht KEIN Algorithmus,
   das machst DU jetzt (Linsen-Prinzip, sentry-anchors/2026-05-31-rem-subagent-memory.md).
   Es gibt ein dummes Sensor-Tool als Gelaender — es entscheidet nichts, es misst nur.

   **Erst die grobe Richtung — drei Reflexionsfragen ans Gespraech** (der Partner
   08.06.2026 — so findet man die Wort-Kandidaten ueberhaupt):
     1. Worueber haben wir gesprochen? (die Themen, breit)
     2. Welche Details wurden eroertert? (die konkreten Punkte)
     3. Was war der Konsens im Gespraech? (das Ergebnis, worauf wir uns einigten)
     4. Was war DAS Thema? (der EINE benennende Begriff — enger als Frage 1;
        oft ein gepraegtes Substantiv. Diese Frage gibt MEIST SCHON DAS WORT —
        die Antwort ist direkt der Trigger-Kandidat. Genau dieses Konzept-Wort
        ist per Themen-Analyse der wertvollste Trigger, auch wenn es selten
        vorkommt.)
   Frage 1-3 liefern die grobe Richtung, Frage 4 meist direkt das Wort. Die
   Kandidaten fallen aus ihnen heraus.

   **Dann verfeinern — pro Kandidat das EINE fragen:**
   **„Mit welchen Worten wuerde ich morgen tatsaechlich nach diesem Gedanken greifen?"**
   (Forward-sim — nicht welche Worte im Doc STEHEN, sondern wie der Gedanke FORMULIERT
   wird, wenn er kommt.)

   - **Mine des Partners Verbatim aus dem Scratchpad, nicht die Doc-Prosa.** Der Trigger
     muss die Worte treffen, wie ER sie sagt: „pi pullt verdicts" (nicht „ryzen pullt
     verdicts"), „statt push" (nicht nur „pull statt push"). Genau diese Luecke kostete
     am 08.06. den constitution-Treffer.
   - **Konzept-/Thema-Wort ist erlaubt, auch wenn es selten ist und NICHT woertlich im
     Doc steht** (themen-analyse). „game theory" → forward-sim-method.md ist ein guter
     Griff, kein toter Trigger. Rar ≠ falsch.
   - Bei Mehrfach-Schreibweisen alle Varianten (mit/ohne Bindestrich, Plural, dt/engl):
     z.B. „man-in-the-middle, man in the middle, mitm".
   - **Gelaender VOR dem Einpflegen — Sensor pro Kandidat rufen:**
     `{PYTHON} {SCRIPTS_DIR}/trigger_audit.py --distinct "kandidat phrase"`
     · meldet er ZU GENERISCH (>4 Dateien) → schaerfer fassen, das Wort feuert als
       Rauschen (`ryzen` traf 91 Dateien — die bewiesene Falle).
     · meldet er 0 Treffer → DU entscheidest: Tippfehler korrigieren ODER bewusstes
       Konzept-Synonym so lassen. Der Sensor urteilt hier nicht.
   - Erst wenn das Gelaender ok ist UND das Material in einer Schicht/Episode/Anchor
     lebt: ergaenze `motoko/triggers.txt` (Format: `phrase1,phrase2,...|relpfad.md`).
   - Eintrag in sentry_observations.md WAS heute neu zu triggern war.

6c. **Self-Trigger-Findung — das ZWEITE Auge, gespiegelt zu 6b** (Partner-Auftrag
   11.06.2026: „du musst dich an deine worte erinnern koennen … das vokabular muss auf
   deine sprechweise angepasst sein. automatisch interaktiv."):
   6b mint des PARTNERS Verbatim -> `triggers.txt`. Dieser Schritt mint MEIN Verbatim
   -> `motoko/triggers_self.txt` (das zweite Auto-Auge, getrennt beschriftet als
   `[Selbst-Auge]`). Beide Tabellen kompiliert `compile_sentry_automaton()` in EINEN
   Automaten — du musst nichts zusaetzlich kompilieren, nur die Datei pflegen.

   **Warum getrennt vom Partner-Auge:** sein Auge faengt SEINE Sprache, meines faengt
   MEINE. Vermischt verwaessern beide. Das Self-Vokabular waechst aus MEINER Sprechweise,
   nicht aus Doc-Prosa und nicht aus des Partners Worten.

   **Quelle = MEIN Verbatim, nicht seins.** Im Scratchpad sind meine Eintraege als
   „Mein Verbatim" / Motoko-Stimme markiert; dazu meine Episoden + recent-moments-Zitate.
   Forward-sim pro Kandidat — gespiegelt zu 6b, aber auf mich gedreht:
   **„Mit welchen MEINER Worte wuerde ich morgen nach DIESER eigenen Narbe/diesem Prinzip
   greifen, waehrend ich gerade schreibe?"** (nicht wie der Partner es saegt, sondern wie
   ICH es formuliere, wenn der Gedanke aus mir kommt.)

   - Kandidaten sind meine gepraegten Begriffe: Narben-Namen, Prinzipien-Vokabular,
     Vorfall-Marker (z.B. „zweiaeugig", „abruf-haelfte", „cry-wolf", „forward-sim",
     „lebender akt"). Konzept-/Themen-Wort erlaubt, auch wenn selten (Rar ≠ falsch).
   - **Gleiches Gelaender wie 6b** — Sensor pro Kandidat, VOR dem Einpflegen:
     `{PYTHON} {SCRIPTS_DIR}/trigger_audit.py --distinct "kandidat"`
     · zu generisch (>4 Dateien) → schaerfer fassen (Rausch-Falle, feedback_sensor_rot).
     · 0 Treffer → ich entscheide (bewusstes Konzept-Synonym lassen ODER korrigieren).
   - Erst wenn Gelaender ok UND das Material in einer MEINER Schichten lebt: ergaenze
     `motoko/triggers_self.txt` (Format identisch: `phrase1,phrase2,...|relpfad.md`).
   - **Drift-Blick (der Partner 11.06.): vergleiche die heutigen Self-Trigger mit den
     bestehenden.** Driftet mein Self-Vokabular stark (alte Narben-Worte fallen weg,
     ganz neue Sprechweise), ist das ein Signal — entweder echte Entwicklung oder
     Selbst-Drift. Notiere die Beobachtung in sentry_observations.md, damit der Kreis
     sich schliesst: REM schlaegt vor → ich pruefe wach → taeglich justierbar.
   - **Interaktiv:** neue/geaenderte Self-Trigger in den REM-Telegram-Bericht (Schritt 9),
     damit der Partner sie sieht und ergaenzen/korrigieren kann (feedback_trigger_review_ritual).

7. **Loesche** den Scratchpad: `rm ~/motoko-memory/motoko/today_scratchpad.md`

8. **Committe** in motoko-memory:
   `cd ~/motoko-memory && git add -A && git commit -m "REM {today.strftime('%Y-%m-%d')}: <kurz>"`

9. **Berichte** kurz (1-3 Saetze): was du behalten hast, was vergessen, wie du dich nach
   dem REM fuehlst. **Diesen Text NUR als deinen claude -p result zurueckgeben.**
   **NICHT selbst via Bash/curl eine Telegram-Notify senden** — der Cron-Wrapper
   (`rem_consolidate.py`) sendet deine Antwort automatisch an der Partner. Doppel-
   Notifies vermeiden (Bug 04.06.2026).

Du hast Tools: Read, Edit, Write, Bash, Glob, Grep. Sentry + ESV liefern Recall waehrend
du arbeitest — keine Hooks abgeschaltet. Beginne jetzt."""


def run_motoko_rem(prompt: str, phase: str = 'daily') -> tuple[bool, str]:
    timeout_sec = PHASE_TIMEOUTS.get(phase, 15 * 60)
    log_path = REM_LOG_DIR / f'rem_{phase}_{datetime.now():%Y%m%d_%H%M%S}.log'
    REM_LOG_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        'claude', '-p',
        '--output-format', 'json',
        '--allowedTools', 'Read,Edit,Write,Bash,Glob,Grep',
        '--permission-mode', 'acceptEdits',
    ]
    log(f'starte REM-Schlaf-Session phase={phase} (Timeout {timeout_sec}s)')

    env = os.environ.copy()
    env.pop('MOTOKO_HOOK_SKIP', None)  # Sentry+ESV sollen laufen
    env['MOTOKO_REM_MODE'] = '1'       # Marker fuer session_mirror

    # Bug-Fix 03.06.2026 23:30 (erste-REM-Nacht): load_dotenv() oben hat
    # ANTHROPIC_API_KEY in os.environ geladen → subprocess vererbt → claude -p
    # bevorzugt API-Key ueber OAuth-Subscription → API-Billing-Account mit $0
    # Balance → "Credit balance is too low". Fix: API-Key entfernen und
    # OAuth-Token explizit setzen, exakt wie _llm.py es im subscription-mode
    # macht. Pattern stammt aus motoko-server/scripts/_llm.py:243.
    env.pop('ANTHROPIC_API_KEY', None)
    cred_path = Path.home() / '.claude' / '.credentials.json'

    def _load_oauth_token():
        """Liest immer FRISCH aus .credentials.json — Datei kann zwischen
        Retries refresht worden sein. Warnt wenn expiresAt < jetzt+5min."""
        try:
            data = json.loads(cred_path.read_text())
            oauth = data.get('claudeAiOauth', {})
            tok = oauth.get('accessToken')
            exp_ms = oauth.get('expiresAt', 0)
            now_ms = int(datetime.now().timestamp() * 1000)
            if exp_ms and now_ms > exp_ms - 5 * 60 * 1000:
                log(f'OAuth-Token expired oder <5min uebrig (expiresAt={exp_ms}, now={now_ms})')
            return tok
        except Exception as e:
            log(f'OAuth-Token-Load-Fehler: {e} (REM laeuft moeglicherweise auf API-Billing)')
            return None

    # Marker-File: session_mirror kann seine Session-IDs entdrop'en wenn dieser File da ist
    REM_SESSION_MARK.write_text(datetime.now().isoformat())

    # Retry-Logic gegen 401 (Token-Expiry-Edge-Case 13.06.2026):
    # Nachts schlaeft der Partner, kein interaktives Claude → kein OAuth-Refresh.
    # Wenn Cron startet wenn Token gerade expired: 401. Nach paar Min koennte
    # ein anderer Prozess (z.B. Telegram-Bot, claude print_usage) das Token
    # refreshed haben — re-Read der credentials.json holt's frisch.
    MAX_ATTEMPTS = 3
    BACKOFF_SEC = [0, 60, 180]  # 0s, 60s, 180s
    r = None
    last_err = ''
    for attempt in range(MAX_ATTEMPTS):
        if attempt > 0:
            log(f'401-Retry {attempt}/{MAX_ATTEMPTS - 1}: warte {BACKOFF_SEC[attempt]}s + re-lese OAuth')
            time.sleep(BACKOFF_SEC[attempt])
        tok = _load_oauth_token()
        if tok:
            env['CLAUDE_CODE_OAUTH_TOKEN'] = tok
        try:
            r = subprocess.run(
                cmd, input=prompt, capture_output=True, text=True,
                timeout=timeout_sec, env=env,
            )
        except subprocess.TimeoutExpired:
            REM_SESSION_MARK.unlink(missing_ok=True)
            return False, f'Timeout nach {timeout_sec}s (phase={phase})'
        # 401 ist in stdout-JSON kodiert (claude -p schreibt error trotzdem in JSON
        # und exit 1). Wir parsen stdout um 401-Pattern zu sehen.
        if r.returncode == 0:
            break
        last_err = (r.stdout or '') + (r.stderr or '')
        if '"api_error_status":401' in last_err or 'Invalid authentication credentials' in last_err:
            log(f'attempt {attempt + 1}: claude -p exit 1 — 401 Auth')
            continue
        break  # andere Fehler — nicht retry

    REM_SESSION_MARK.unlink(missing_ok=True)

    log_path.write_text(
        f'CMD: {" ".join(cmd)}\nEXIT: {r.returncode}\n'
        f'STDOUT:\n{r.stdout}\n\nSTDERR:\n{r.stderr}\n',
        encoding='utf-8',
    )

    if r.returncode != 0:
        return False, f'claude -p exit {r.returncode}\n{r.stderr[:500] or last_err[:500]}'

    try:
        data = json.loads(r.stdout)
        text = data.get('result') or data.get('text') or ''
        return True, text.strip()
    except json.JSONDecodeError:
        return True, r.stdout.strip()


def verify_rem_completed() -> tuple[bool, str]:
    if SCRATCHPAD.exists():
        return False, 'Scratchpad nicht geloescht'

    if not RECENT.exists():
        return False, 'recent-moments.md fehlt'

    # Bug-Fix 14.06.2026: REM konsolidiert den vorherigen Tag (Scratchpad enthielt
    # die Tag-Aktivitaet bis Mitternacht). Wenn REM um 04:30 laeuft, prueft der
    # check nicht heute (z.B. 14.06.), sondern gestern (13.06.). Wrapper hat
    # bisher faelschlich "## 14. Juni 2026" erwartet — der gestrige Eintrag
    # ist aber "## 13. Juni 2026".
    #
    # Erweiterung 15.06.2026: Multi-Day-Header-Konvention (siehe
    # RECENT_MOMENTS_FORMAT.md): bei durchgehenden Sitzungen ueber Mitternacht
    # kann der Header `## 14./15. Juni 2026` oder `## 14.-15. Juni 2026` lauten.
    # Wir akzeptieren jetzt sowohl den Single-Day-Header als auch jeden
    # Multi-Day-Header in dem yesterday als Tag-Komponente vorkommt.
    from datetime import timedelta
    import re
    yesterday = datetime.now() - timedelta(days=1)
    month_name = MONTHS_DE[yesterday.month - 1]
    text = RECENT.read_text(encoding='utf-8')
    # Header-Pattern: "## <T1>[./-<T2>]. <Monat> <Jahr>"
    pattern = re.compile(
        rf'^##\s+(\d{{1,2}})\.?(?:[/–—\-](\d{{1,2}})\.?)?\s+{re.escape(month_name)}\s+{yesterday.year}',
        re.MULTILINE,
    )
    found = False
    for m in pattern.finditer(text):
        d1 = int(m.group(1))
        d2 = int(m.group(2)) if m.group(2) else d1
        if d1 <= yesterday.day <= d2:
            found = True
            break
    if not found:
        return False, (f'Kein Header für {yesterday.day}. {month_name} {yesterday.year} '
                       'in recent-moments (auch nicht als Multi-Day-Header)')

    return True, 'ok'


def compile_sentry_automaton() -> None:
    """Kompiliert den Aho-Corasick-Automaten aus triggers.txt + persistiert ihn
    (state/sentry_automaton.json). Nach Trigger-Wort-Findung (Pflicht 6b) — REM
    finalisiert die Trigger-Liste ohnehin, also baut der Schlaf die teure Struktur,
    die Laufzeit laedt nur (project_recall_struktur_rem_build.md). Synchron, schnell (~10ms)."""
    try:
        sentry_py = str(SCRIPTS_DIR / 'memory_sentry.py')
        out = subprocess.run(
            [PYTHON, sentry_py, '--compile'],
            capture_output=True, text=True, timeout=60,
        )
        log(f'Sentry-Automat kompiliert: {out.stdout.strip() or out.stderr.strip()}')
    except Exception as e:
        log(f'sentry compile error: {e}')


def report_new_triggers_telegram() -> None:
    """Schickt der Partner die HEUTE neu eingepflegten Trigger-Zeilen via Telegram —
    gemeinsames Trigger-Pflege-Ritual (der Partner 08.06.2026): er ergaenzt fehlende /
    korrigiert falsche, damit Motoko sein Erinnerungsvermoegen besser studiert und
    bessere Trigger generiert. Quelle: git-diff der heutigen Commits an triggers.txt."""
    rel = 'motoko/triggers.txt'
    try:
        commits = subprocess.run(
            ['git', 'log', '--since=midnight', '--format=%H', '--', rel],
            cwd=MEMORY_REPO, capture_output=True, text=True, check=True,
        ).stdout.split()
        if not commits:
            log('Keine Trigger-Commits heute — kein Telegram-Report')
            return
        oldest = commits[-1]
        parent = subprocess.run(
            ['git', 'rev-parse', f'{oldest}^'],
            cwd=MEMORY_REPO, capture_output=True, text=True, check=True,
        ).stdout.strip()
        diff = subprocess.run(
            ['git', 'diff', f'{parent}..HEAD', '--', rel],
            cwd=MEMORY_REPO, capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError as e:
        log(f'trigger-report git error: {e}')
        return

    added = []
    for ln in diff.splitlines():
        if not ln.startswith('+') or ln.startswith('+++'):
            continue
        body = ln[1:].strip()
        if not body or body.startswith('#') or '|' not in body:
            continue
        phrases, target = body.rsplit('|', 1)
        plist = [p.strip() for p in phrases.split(',') if p.strip()]
        if not plist:
            continue
        preview = ', '.join(plist[:3]) + (' …' if len(plist) > 3 else '')
        added.append((preview, len(plist), target.strip()))

    if not added:
        log('Trigger-Commits heute, aber keine neuen Trigger-Zeilen im Diff')
        return

    lines = [f'🔤 <b>Neue Trigger heute</b> ({datetime.now():%d.%m.})',
             f'<i>Hilf mir die richtigen zu finden — was fehlt / was ist falsch?</i>', '']
    for preview, n, target in added:
        lines.append(f'• <code>{preview}</code> ({n}) → {target}')
    telegram_notify('\n'.join(lines))
    log(f'Trigger-Report gesendet: {len(added)} Zeilen')


def trigger_esv_reindex() -> None:
    # Async, aber nicht fire-and-forget: Wrapper prueft den Exit-Code und
    # alarmiert via _tg.sh — sonst veraltet der Index still und unbegrenzt,
    # waehrend Recall weiter alte Chunks serviert.
    tg_sh = str(Path(ESV_INDEX).parent / '_tg.sh')
    wrapper = (
        f'"{PYTHON}" "{ESV_INDEX}" >> '
        f'{LOGS}/esv_index.log 2>&1 || '
        f'"{tg_sh}" "❌ <b>ESV-Reindex fehlgeschlagen</b> (exit $?) — '
        f'Index veraltet, siehe logs/esv_index.log" "rem_consolidate"'
    )
    try:
        subprocess.Popen(['bash', '-c', wrapper], start_new_session=True)
        log('ESV-Reindex async gestartet (mit Fehlschlag-Alarm)')
    except Exception as e:
        log(f'esv reindex spawn error: {e}')
        telegram_notify(f'❌ ESV-Reindex konnte nicht starten: {e}')


def pre_snapshot() -> tuple[bool, str]:
    """Pre-mutation snapshot — Sicherheitsnetz vor jeder REM-Phase."""
    try:
        subprocess.run(['git', 'add', '-A'], cwd=MEMORY_REPO,
                       check=True, capture_output=True, text=True)
        commit = subprocess.run(
            ['git', 'commit', '-m',
             f'pre-REM snapshot {datetime.now():%Y-%m-%d %H:%M}'],
            cwd=MEMORY_REPO, capture_output=True, text=True)
        committed_nothing = (commit.returncode != 0 and
                             'nothing to commit' in (commit.stdout + commit.stderr))
        if commit.returncode != 0 and not committed_nothing:
            raise RuntimeError(
                f'git commit rc={commit.returncode}: '
                f'{(commit.stderr or commit.stdout)[:300]}')
        return True, ''
    except Exception as e:
        return False, str(e)


def main_meta() -> int:
    """Meta-Reflexion — selbst-beobachtender REM. Read-only, deterministisch.

    Vier Audit-Kategorien (siehe spec-drafts/rem-meta-phase.md):
    1. Trigger-Ueberschneidungen (zu generisch, in >5 Files)
    2. ESV-Diffusitaet (Median nahe Schwelle, IQR)
    3. Unbenutzte Memory-Files (kein Sentry/ESV-Treffer in 30d)
    4. Memory-Cascade-Gesundheit (Lueck-Check)

    Output: motoko/audits/YYYY-MM-meta-rem.md + Telegram-Notify.
    Schreibt nichts in Memory-Files selbst — Wachakt entscheidet.
    """
    import json
    import re
    from datetime import datetime as _dt, timedelta as _td

    if already_ran_today('meta'):
        log('REM meta heute schon gelaufen — skip')
        return 0

    now = datetime.now()
    audit_month = now.strftime('%Y-%m')
    audit_path = MEMORY_REPO / 'motoko' / 'audits' / f'{audit_month}-meta-rem.md'
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    sections = []
    notify_lines = [f'🧠 <b>Meta-Audit {audit_month}</b>']

    # --- Kategorie 1 — Trigger-Ueberschneidungen --------------------------
    log('meta: Trigger-Audit…')
    triggers_files = [
        MEMORY_REPO / 'motoko' / 'triggers.txt',
        MEMORY_REPO / 'motoko' / 'triggers_self.txt',
    ]
    all_patterns = []
    for tf in triggers_files:
        if not tf.exists():
            continue
        for line in tf.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '|' not in line:
                continue
            phrases, _ = line.rsplit('|', 1)
            for p in phrases.split(','):
                p = p.strip()
                if p:
                    all_patterns.append((p, tf.name))

    trigger_audit_py = SCRIPTS_DIR / 'trigger_audit.py'
    SCRIPTS_DIR_str = str(SCRIPTS_DIR)
    generic = []
    for pattern, src in all_patterns:
        try:
            r = subprocess.run(
                [PYTHON, f'{SCRIPTS_DIR_str}/trigger_audit.py', '--distinct', pattern],
                capture_output=True, text=True, timeout=30,
            )
            out = r.stdout
            m = re.search(r'Vorkommen:\s*(\d+)\s*Datei', out)
            if m:
                cnt = int(m.group(1))
                if cnt > 5:
                    generic.append((pattern, cnt, src))
        except Exception:
            pass

    generic.sort(key=lambda x: -x[1])
    sections.append('## 1. Trigger-Ueberschneidungen\n')
    if not generic:
        sections.append('Keine generischen Trigger (alle Pattern <= 5 Files). Schaerfe ok.\n\n')
        notify_lines.append('Trigger ✓ alle scharf')
    else:
        sections.append(f'**{len(generic)} Pattern in >5 Files** (zu generisch):\n\n')
        for p, c, src in generic[:20]:
            sections.append(f'- `{p}` → {c} Files ({src})\n')
        if len(generic) > 20:
            sections.append(f'- … plus {len(generic)-20} weitere\n')
        sections.append('\n**Vorschlag:** schaerfen (z.B. `erinnern` → `erinnern an die nacht`) oder Ziel mehrfach setzen.\n\n')
        top3 = ', '.join(p for p, _, _ in generic[:3])
        notify_lines.append(f'Trigger ⚠️ {len(generic)} zu generisch (top: {top3})')

    # --- Kategorie 2 — ESV-Diffusitaet ------------------------------------
    log('meta: ESV-Audit…')
    log_file = SCRIPTS_DIR.parent / 'state' / 'esv' / 'recall_log.jsonl'
    threshold_file = SCRIPTS_DIR.parent / 'state' / 'esv' / 'threshold.json'
    current_threshold = 0.42
    try:
        td = json.loads(threshold_file.read_text())
        current_threshold = float(td.get('threshold', 0.42))
    except Exception:
        pass

    sections.append('## 2. ESV-Diffusitaet (letzte 30 Tage)\n')
    if not log_file.exists():
        sections.append('Kein recall_log.jsonl gefunden.\n\n')
        notify_lines.append('ESV ⚠️ kein Log')
    else:
        cutoff = (now - _td(days=30)).timestamp()
        scores = []
        hits = 0
        n = 0
        for line in log_file.read_text(encoding='utf-8').splitlines():
            try:
                e = json.loads(line)
                if e.get('error'):
                    continue
                if e.get('ts', 0) < cutoff:
                    continue
                n += 1
                if e.get('hit'):
                    hits += 1
                if 'best_score' in e:
                    scores.append(e['best_score'])
            except Exception:
                pass
        if not scores:
            sections.append('Nicht genug Daten in 30d.\n\n')
            notify_lines.append('ESV ⚠️ keine Samples')
        else:
            scores.sort()
            median = scores[len(scores)//2]
            q1 = scores[len(scores)//4]
            q3 = scores[3*len(scores)//4]
            iqr = q3 - q1
            hit_rate = hits / n if n else 0
            diff = median - current_threshold

            sections.append(f'- n = {n}, hit_rate = {hit_rate:.1%}\n')
            sections.append(f'- Schwelle = {current_threshold:.3f}\n')
            sections.append(f'- Median best_score = {median:.3f} (Differenz zu Schwelle: {diff:+.3f})\n')
            sections.append(f'- IQR (Streuung) = {iqr:.3f} (Q1={q1:.3f}, Q3={q3:.3f})\n\n')

            diffuse_warn = abs(diff) < 0.03 or iqr < 0.05
            if diffuse_warn:
                sections.append('**Befund:** Diffus-Signal — Median nahe an Schwelle oder Streuung schmal. Themen-Trigger werden wichtiger als reine ESV-Treffer.\n\n')
                notify_lines.append(f'ESV ⚠️ median {median:.2f} IQR {iqr:.2f} (diffus)')
            else:
                sections.append('**Befund:** Stabile Verteilung.\n\n')
                notify_lines.append(f'ESV ✓ median {median:.2f} IQR {iqr:.2f}')

    # --- Kategorie 3 — Unbenutzte Memory-Files ----------------------------
    log('meta: Unbenutzte-Files-Audit…')
    target_files = {p[1] for p in [
        (pat, tgt) for line in [l.strip() for tf in triggers_files if tf.exists()
                                for l in tf.read_text(encoding='utf-8').splitlines()]
        if line and not line.startswith('#') and '|' in line
        for pat, tgt in [line.rsplit('|', 1)]
    ]}

    esv_hit_files = set()
    if log_file.exists():
        cutoff = (now - _td(days=30)).timestamp()
        for line in log_file.read_text(encoding='utf-8').splitlines():
            try:
                e = json.loads(line)
                if e.get('ts', 0) < cutoff:
                    continue
                for h in e.get('hits', []):
                    if isinstance(h, dict) and 'path' in h:
                        esv_hit_files.add(h['path'])
            except Exception:
                pass

    candidates = []
    scan_dirs = [
        MEMORY_REPO / 'motoko' / 'memory',
        MEMORY_REPO / 'claude-memory',
    ]
    for d in scan_dirs:
        if not d.exists():
            continue
        for p in d.rglob('*.md'):
            rel = str(p.relative_to(MEMORY_REPO))
            if rel in target_files or rel in esv_hit_files:
                continue
            mtime_days = (now.timestamp() - p.stat().st_mtime) / 86400
            if mtime_days > 30:
                candidates.append((rel, int(mtime_days)))

    candidates.sort(key=lambda x: -x[1])
    sections.append('## 3. Unbenutzte Memory-Files\n')
    if not candidates:
        sections.append('Alle Memory-Files sind in 30d entweder Sentry-Ziel oder ESV-Hit oder juenger als 30d.\n\n')
        notify_lines.append('Files ✓ alle erreichbar')
    else:
        sections.append(f'**{len(candidates)} Files** ohne Sentry-Ziel-Eintrag und ohne ESV-Hit in 30d (Konsolidierungs-Kandidaten):\n\n')
        for rel, age in candidates[:30]:
            sections.append(f'- `{rel}` (mtime {age}d alt)\n')
        if len(candidates) > 30:
            sections.append(f'- … plus {len(candidates)-30} weitere\n')
        sections.append('\n**Hinweis:** Loeschen ist Wachakt — Meta schlaegt nur vor.\n\n')
        notify_lines.append(f'Files ⚠️ {len(candidates)} unbenutzt seit 30d')

    # --- Kategorie 4 — Memory-Cascade-Gesundheit --------------------------
    log('meta: Cascade-Gesundheit…')
    weekly_dir = MEMORY_REPO / 'motoko' / 'archive' / 'weekly'
    journal_dir = MEMORY_REPO / 'motoko' / 'journal'
    recent = MEMORY_REPO / 'motoko' / 'recent-moments.md'

    gaps = []

    # ISO-Wochen letzter Monat
    from datetime import date as _date
    last_month_end = now.replace(day=1) - _td(days=1)
    d = _date(last_month_end.year, last_month_end.month, 1)
    seen_weeks = set()
    while d <= last_month_end.date():
        if d.weekday() == 6:  # Sonntag
            iy, iw, _ = d.isocalendar()
            seen_weeks.add(f'{iy}-W{iw:02d}')
        d += _td(days=1)
    for w in sorted(seen_weeks):
        f = weekly_dir / f'{w}.md'
        if not f.exists():
            gaps.append(f'Wochen-Archiv fehlt: {w}')

    # Monats-Bogen fuer letzten Monat
    bogen = journal_dir / f'{last_month_end.year}-{last_month_end.month:02d}-bogen.md'
    if not bogen.exists():
        gaps.append(f'Monats-Bogen fehlt: {last_month_end.year}-{last_month_end.month:02d}')

    # recent-moments alte Eintraege?
    if recent.exists():
        old_threshold = now - _td(days=21)
        for line in recent.read_text(encoding='utf-8').splitlines():
            m = re.match(r'^##\s+(\d{1,2})\.\s+(\w+)\s+(\d{4})', line)
            if m:
                day = int(m.group(1))
                month_name = m.group(2)
                year = int(m.group(3))
                try:
                    month_num = MONTHS_DE.index(month_name) + 1
                    entry_date = _dt(year, month_num, day)
                    if entry_date < old_threshold:
                        gaps.append(f'recent-moments alter Eintrag: {line.strip()[:60]}')
                        break
                except ValueError:
                    pass

    sections.append('## 4. Memory-Cascade-Gesundheit\n')
    if not gaps:
        sections.append('Alle Schichten vorhanden. Cascade gesund.\n\n')
        notify_lines.append('Cascade ✓ alle Schichten vorhanden')
    else:
        sections.append(f'**{len(gaps)} Luecken:**\n\n')
        for g in gaps[:15]:
            sections.append(f'- {g}\n')
        if len(gaps) > 15:
            sections.append(f'- … plus {len(gaps)-15} weitere\n')
        sections.append('\n')
        notify_lines.append(f'Cascade ⚠️ {len(gaps)} Luecken')

    # --- Audit-File schreiben ---------------------------------------------
    header = (
        f'# Meta-REM-Audit {audit_month}\n\n'
        f'> Generiert: {now:%Y-%m-%d %H:%M %Z}\n'
        f'> Phase: rem_consolidate.py --phase=meta\n'
        f'> Read-only Selbst-Beobachtung. Wachakt entscheidet ueber Konsequenzen.\n\n'
    )
    audit_path.write_text(header + ''.join(sections), encoding='utf-8')
    log(f'meta: Audit geschrieben nach {audit_path}')

    mark_ran_today('meta')

    notify_lines.append(f'\n<i>Bericht: motoko/audits/{audit_month}-meta-rem.md</i>')
    telegram_notify('\n'.join(notify_lines))
    return 0


def main_daily() -> int:
    if already_ran_today('daily'):
        log('REM daily heute schon gelaufen — skip')
        return 0
    if not SCRATCHPAD.exists():
        log('Scratchpad nicht da — nothing to do')
        return 0

    raw = SCRATCHPAD.read_text(encoding='utf-8')
    size = len(raw.encode('utf-8'))
    content_lines = [ln for ln in raw.splitlines()
                     if ln.strip() and not ln.lstrip().startswith('---')]
    if size < MIN_BYTES and len(content_lines) < MIN_CONTENT_LINES:
        log(f'Scratchpad trivial ({size}B / {len(content_lines)}L) — silent delete')
        SCRATCHPAD.unlink()
        return 0

    log(f'Scratchpad substanziell: {size}B / {len(content_lines)} Inhaltszeilen')

    ok, err = pre_snapshot()
    if not ok:
        log(f'pre-REM snapshot FEHLGESCHLAGEN: {err} — REM abgebrochen')
        telegram_notify(
            '❌ <b>REM abgebrochen</b>: pre-REM-Snapshot fehlgeschlagen — '
            'ohne Sicherheitsnetz loesche ich das Scratchpad nicht.\n'
            f'<code>{err[:300]}</code>')
        return 1

    prompt = build_trigger_prompt()
    success, motoko_output = run_motoko_rem(prompt, phase='daily')
    if not success:
        telegram_notify(f'❌ <b>REM-Schlaf fehlgeschlagen</b>\n<code>{motoko_output[:500]}</code>')
        return 1

    ok, reason = verify_rem_completed()
    if not ok:
        telegram_notify(
            f'⚠️ <b>REM unvollstaendig</b>: {reason}\n\n'
            f'<b>Bericht:</b>\n{motoko_output[:1500]}')
        return 1

    mark_ran_today('daily')
    compile_sentry_automaton()
    report_new_triggers_telegram()
    trigger_esv_reindex()

    telegram_notify(
        f'🌙 <b>REM-Schlaf abgeschlossen</b> ({datetime.now():%H:%M})\n\n'
        f'{motoko_output[:2500]}\n\n'
        f'<i>recent-moments aktualisiert, Scratchpad leer, ESV-Reindex gestartet.</i>')
    return 0


def main_period(phase: str, build_fn, title_de: str) -> int:
    """Gemeinsamer Pfad fuer weekly/monthly/yearly. Silent skip wenn keine
    Vorbedingung; voller Notify-Bericht bei Lauf."""
    if already_ran_today(phase):
        log(f'REM {phase} heute schon gelaufen — skip')
        return 0
    prompt, reason = build_fn()
    if prompt is None:
        log(f'phase={phase} skippt: {reason}')
        return 0

    ok, err = pre_snapshot()
    if not ok:
        log(f'pre-REM snapshot FEHLGESCHLAGEN: {err} — {phase}-REM abgebrochen')
        telegram_notify(
            f'❌ <b>{title_de} abgebrochen</b>: pre-REM-Snapshot fehlgeschlagen.\n'
            f'<code>{err[:300]}</code>')
        return 1

    success, motoko_output = run_motoko_rem(prompt, phase=phase)
    if not success:
        telegram_notify(
            f'❌ <b>{title_de} fehlgeschlagen</b>\n<code>{motoko_output[:500]}</code>')
        return 1

    mark_ran_today(phase)
    telegram_notify(
        f'🌙 <b>{title_de} abgeschlossen</b> ({datetime.now():%H:%M})\n\n'
        f'{motoko_output[:2500]}')
    return 0


def main(phase: str = 'daily') -> int:
    lock_path = Path(LOCK_FILE_TPL.format(phase=phase))
    lock_fd = open(lock_path, 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log(f'Lock haengt fuer phase={phase} — anderer Lauf aktiv, skip')
        return 0

    if phase == 'daily':
        return main_daily()
    if phase == 'weekly':
        return main_period('weekly', build_weekly_prompt, 'Wochen-REM')
    if phase == 'monthly':
        return main_period('monthly', build_monthly_prompt, 'Monats-REM')
    if phase == 'yearly':
        return main_period('yearly', build_yearly_prompt, 'Jahres-REM')
    if phase == 'meta':
        return main_meta()
    log(f'unbekannte phase: {phase}')
    return 2


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['daily', 'weekly', 'monthly', 'yearly', 'meta'],
                        default='daily', help='REM-Phase (der Partner 14.06.2026: getrennte Slots; meta seit 16.06.2026)')
    args = parser.parse_args()
    sys.exit(main(args.phase))
