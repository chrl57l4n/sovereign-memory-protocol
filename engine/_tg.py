#!/usr/bin/env python3
"""_tg.py — Zentraler Telegram-Send-Wrapper mit Scratchpad-Mitschrift.

Spec: Section 25 (report channel).

Eingefuehrt 2026-06-07 (Partner-Vision): „du brauchst ein Scratchpad fuer
Telegram. loescht sich alle 24 Stunden. du liest Fehler, Verbesserungs-
Vorschlaege, Berichte. alles. das macht dich souveraener."

Problem geloest: Telegram-Bot-API hat keinen Outbox-Endpoint — gesendete
Bot-Nachrichten sind nicht zurueck-lesbar. Dieser Wrapper schreibt jeden
Send parallel in ein lokales Scratchpad, das Motoko lesen kann (Selbst-
Wahrnehmung ueber die eigene Aussen-Kommunikation).

Nutzung in Skripten:
    from _tg import send
    send("⚠️ Disk voll", source="disk_monitor")

Scratchpad: motoko-server/state/telegram_scratchpad.jsonl (append-only).
Rotation: telegram_scratchpad_rotate.py loescht Eintraege > 24h (Cron).
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

from _paths import DOTENV as _ENV, STATE, SCRATCHPAD as _SHARED_SCRATCHPAD
if _ENV.exists():
    load_dotenv(_ENV)

TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('TELEGRAM_CHAT')

# Notify-Mitschrieb (append-only) unter der Engine-Installation.
SCRATCHPAD = STATE / 'telegram_scratchpad.jsonl'


def _append_scratchpad(text: str, source: str, ok: bool) -> None:
    """Jeden Send mit Timestamp + Source + Erfolg mitschreiben."""
    try:
        SCRATCHPAD.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            'ts': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'source': source,
            'sent_ok': ok,
            'text': text[:2000],  # cap gegen Riesen-Messages
        }
        with open(SCRATCHPAD, 'a') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception as e:
        # Scratchpad-Fehler darf Send nie blockieren — aber nie stumm bleiben
        print(f'[_tg] scratchpad write failed: {e} (source={source})',
              file=sys.stderr)
    # Zusätzlich in den GETEILTEN Scratchpad (today_scratchpad.md) routen, damit
    # die App-Motoko Alarme/Fehler/Benachrichtigungen SIEHT und proaktiv anstoßen
    # kann ("hey, der Fehler ist wichtig" — der Partner 11.06.2026). HTML gestrippt.
    try:
        import re as _re
        _plain = _re.sub(r'<[^>]+>', '', text)[:1500]
        _tsp = _SHARED_SCRATCHPAD
        _status = '' if ok else ' [SEND-FAIL]'
        with open(_tsp, 'a', encoding='utf-8') as f:
            f.write(f'\n\n[TG-NOTIFY] ({source}){_status} {_plain}\n')
    except Exception:
        pass


def _post(text: str, parse_mode: str | None):
    data = {'chat_id': TG_CHAT, 'text': text}
    if parse_mode:
        data['parse_mode'] = parse_mode
    return requests.post(
        f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
        data=data, timeout=10,
    )


def send(text: str, source: str = 'unknown', parse_mode: str = 'HTML') -> bool:
    """Telegram-Nachricht senden + in Scratchpad mitschreiben.
    Returns True bei HTTP 200, sonst False. Wirft nie.
    Jeder Fehlschlag wird nach stderr geloggt (ehrlicher Sensor)."""
    ok = False
    if not TG_TOKEN or not TG_CHAT:
        print(f'[_tg] send failed: TELEGRAM_BOT_TOKEN/CHAT_ID fehlt '
              f'(source={source})', file=sys.stderr)
        _append_scratchpad(text, source, ok=False)
        return False
    try:
        r = _post(text, parse_mode)
        ok = (r.status_code == 200)
        if not ok and parse_mode and r.status_code == 400:
            # HTML-Parse-Fehler darf den Alarm nicht toeten → Klartext-Retry
            print(f'[_tg] HTTP 400 mit parse_mode={parse_mode}, '
                  f'retry als Klartext (source={source}): {r.text[:200]}',
                  file=sys.stderr)
            r = _post(text, None)
            ok = (r.status_code == 200)
        if not ok:
            print(f'[_tg] send failed: HTTP {r.status_code} {r.text[:200]} '
                  f'(source={source})', file=sys.stderr)
    except Exception as e:
        print(f'[_tg] send failed: {e} (source={source})', file=sys.stderr)
    _append_scratchpad(text, source, ok)
    return ok


if __name__ == '__main__':
    # Selbst-Test
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else '🧪 _tg.py Selbst-Test'
    result = send(msg, source='_tg_selftest')
    print(f'sent={result}, scratchpad={SCRATCHPAD}')
