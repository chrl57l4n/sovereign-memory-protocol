#!/usr/bin/env python3
"""rem_audit_nag.py — Telegram-Nag wenn der substanzielle REM-Audit überfällig ist.

Eingeführt 2026-06-28. Anlass: der substanzielle (manuelle) REM-Audit fiel 23 Tage
aus, weil ihn NICHTS erzwingt — der tägliche `rem_audit.py` ist grün und maskiert
die Lücke. Der Marker `state/rem_last_audit.txt` rückt nur vor, wenn die wache Motoko
den Audit von Hand macht. Dieser Nag schließt die Schleife: er macht das Unerzwungene
sichtbar, statt es meiner Initiative zu überlassen (die vom Bauen aufgefressen wird).

Logik:
- Liest state/rem_last_audit.txt (Datum des letzten substanziellen Audits).
- Alter > THRESHOLD_DAYS → Telegram-Nag mit Anleitung.
- Cooldown RE_NAG_DAYS gegen tägliches Spam; bei frischem Audit Reset.
- Marker fehlt → als sehr überfällig behandeln.

Cron: täglich 09:00. Kadenz des Audits ist wöchentlich/monatlich, ein täglicher Check
reicht. Spiegelt das Pattern von remote_control_watchdog.py / service_health.py.
"""
import json
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))  # für _tg/_watch unter cron

try:
    from _watch import mark as _mark
except Exception:
    def _mark(*a, **k):  # Status-Stempel optional, darf nie crashen
        pass

from _paths import STATE as STATE_DIR, DOTENV
load_dotenv(DOTENV)
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID')

MARKER = STATE_DIR / 'rem_last_audit.txt'
STATE = STATE_DIR / 'rem_audit_nag.json'
THRESHOLD_DAYS = 10   # ab hier überfällig (Audit-Soll: wöchentlich)
RE_NAG_DAYS = 2       # frühestens alle 2 Tage erneut nagen


def notify(msg: str) -> None:
    try:
        from _tg import send
        send(msg, source='rem_audit_nag')
        return
    except Exception:
        pass
    try:
        import requests
        requests.post(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': TG_CHAT, 'parse_mode': 'HTML', 'text': msg},
            timeout=10,
        )
    except Exception:
        pass


def marker_age_days() -> int | None:
    """Tage seit letztem substanziellen Audit. None wenn Marker fehlt/unparsbar."""
    if not MARKER.exists():
        return None
    raw = MARKER.read_text().strip()
    try:
        d = datetime.strptime(raw, '%Y-%m-%d').date()
    except ValueError:
        return None
    return (date.today() - d).days


def main() -> None:
    age = marker_age_days()
    stamp = time.strftime('%Y-%m-%d %H:%M:%S')

    st = {'last_nag_ts': 0.0}
    if STATE.exists():
        try:
            st.update(json.loads(STATE.read_text()))
        except Exception:
            pass

    overdue = (age is None) or (age > THRESHOLD_DAYS)
    if not overdue:
        print(f'{stamp} OK: REM-Audit vor {age} Tagen (≤ {THRESHOLD_DAYS}) — kein Nag')
        _mark('rem-audit-nag', 'green', f'Audit vor {age}d (≤{THRESHOLD_DAYS})', max_age_s=93600)
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(st, indent=2))
        return

    _mark('rem-audit-nag', 'alert', f'überfällig: {age}d', max_age_s=93600)
    now = time.time()
    cooled = (now - float(st.get('last_nag_ts', 0))) >= RE_NAG_DAYS * 86400
    if not cooled:
        print(f'{stamp} überfällig (age={age}), aber Cooldown aktiv — kein Nag')
        return

    if age is None:
        age_txt = 'unbekannt (Marker fehlt)'
    else:
        age_txt = f'<b>{age} Tagen</b>'
    msg = (
        "🧠 <b>REM-Audit überfällig</b>\n\n"
        f"Letzter substanzieller Audit vor {age_txt}. Soll: wöchentlich "
        "(Kalibrierungs-Phase) gegen die Roh-Transkripte.\n\n"
        "Der tägliche Automat misst nur — das <i>Urteilen</i> bin ich: war das "
        "Vergessen gut? Halten die Empfehlungen? Wurde ein Zitat paraphrasiert?\n\n"
        "So läuft er: sag mir in einer Session einfach <code>mach den REM-Audit</code>.\n\n"
        f"(Nächster Nag frühestens in {RE_NAG_DAYS} Tagen.)"
    )
    notify(msg)
    st['last_nag_ts'] = now
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=2))
    print(f'{stamp} NAG gesendet (age={age})')


if __name__ == '__main__':
    main()
