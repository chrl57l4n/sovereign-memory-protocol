#!/usr/bin/env python3
"""esv_self_recall.py — BETA: ESV-Recall auf MEINEN Output (zweites semantisches Auge).

Spiegelt self_recall_beta.py (Sentry-Self) auf der ESV-Seite. Wo Sentry-Self
literal-keyword matcht, sucht ESV-Self semantisch — auf MEINEM letzten Output,
nicht auf des Partners Input. Damit fängt es Verbindungen die Keywords verpassen.

PHÄNOMENOLOGISCHE SPEC (der Partner 22.06.2026 Nacht — 4 Schichten):
  1. Signal ohne Inhalt: Tip-of-the-tongue, „da war was, weiß nicht was"
  2. Loop wenn ungelöst: Override, Approximation, weiter
  3. Dialog löst auf: ehrlich-zugeben + warten + Trigger-Wort von außen
  4. Perkolations-Schwelle: 0.42 = wahrscheinlicher als 50% dass Richtung stimmt

→ Konsequenz für Loop-Filter:
  - Tip-of-the-tongue: KEIN Volltext-Snippet (anders als Sentry-Self), nur
    Adresse + Themen-Schlagwort. Der alte Gedanke determiniert mich nicht.
  - Loop-Detector: CAP=1 (max 1 ESV-Self-Echo pro Antwort, härter als Sentry CAP=2)
  - Cooldown pro Datei: exponentiell wie Sentry (4,8,16,32 Turns)
  - Aktive-Datei-Schweigen: wenn ich diese Datei gerade editiere → kein Echo zu ihr
  - Override bei 3× selber Datei in einer Session → permanent dieser Session aus

BETA-Prinzip (wie self_recall_beta.py 17.06.2026): komplett rausnehmbar.
Kill-Switch: state/esv_self_recall.disabled. Total-Fail-Safe: jeder Fehler → exit 0.
REM-Guard: MOTOKO_REM_MODE=1 → schweigt (Schlaf-Schwester von Sentry-Self).
"""
import json
import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from _paths import HOME as REPO, STATE
STATE_DIR = STATE / 'esv_self'
LEDGER_FILE_TPL = 'self_ledger_{session}.json'

# Loop-Filter-Parameter (kalibrierbar)
COOLDOWN_BASE = 4          # Turns; verdoppelt pro Wiederholung
COOLDOWN_MAX_EXP = 3       # max 4*2^3 = 32 Turns
CAP = 1                    # max ESV-Self-Echos pro Antwort (härter als Sentry CAP=2)
HARD_BAN_AFTER = 3         # nach 3× selbe Datei → permanent diese Session aus
LEDGER_TTL_DAYS = 7
ACTIVE_FILE_LOOKBACK_TURNS = 3   # wieviele Turns zurück nach Edit/Write-Targets schauen
QUERY_MAX_CHARS = 4000     # mein Output kann lang sein, ESV-Embed-Limit ~6000


def _is_user_text(rec: dict) -> bool:
    msg = rec.get("message") or {}
    if msg.get("role") != "user":
        return False
    c = msg.get("content")
    if isinstance(c, str):
        return bool(c.strip())
    if isinstance(c, list):
        return any(isinstance(b, dict) and b.get("type") == "text" for b in c)
    return False


def _assistant_texts(rec: dict):
    msg = rec.get("message") or {}
    if msg.get("role") != "assistant":
        return []
    c = msg.get("content")
    if isinstance(c, list):
        return [b.get("text", "") for b in c
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text")]
    if isinstance(c, str):
        return [c]
    return []


def _assistant_tool_targets(rec: dict, tools=('Edit', 'Write', 'NotebookEdit')):
    """Extrahiere file_path der letzten Edit/Write-Tool-Calls (aktive Dateien)."""
    msg = rec.get("message") or {}
    if msg.get("role") != "assistant":
        return []
    c = msg.get("content")
    if not isinstance(c, list):
        return []
    targets = []
    for b in c:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "tool_use" and b.get("name") in tools:
            fp = (b.get("input") or {}).get("file_path")
            if fp:
                targets.append(fp)
    return targets


def _last_output_turn_and_active_files(transcript_path: Path):
    """-> (mein_letzter_output_text, turn_zaehler, set_aktive_dateien).

    aktive_dateien = absolute file_paths aus Edit/Write Tool-Calls der letzten
    ACTIVE_FILE_LOOKBACK_TURNS Assistant-Runden. Wenn der ESV-Treffer auf eine
    solche Datei fällt → Schweigen (sonst Selbst-Referenz beim Schreiben).
    """
    most_recent, accum, turns = [], [], 0
    active_files = set()
    recent_edit_blocks = []  # liste von listen, pro assistant-runde
    current_edits = []
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if _is_user_text(rec):
                    turns += 1
                    if accum:
                        most_recent = accum
                        accum = []
                    if current_edits:
                        recent_edit_blocks.append(current_edits)
                        current_edits = []
                    continue
                texts = _assistant_texts(rec)
                if texts:
                    accum.extend(texts)
                tgts = _assistant_tool_targets(rec)
                if tgts:
                    current_edits.extend(tgts)
    except Exception:
        return ("", 0, set())
    if current_edits:
        recent_edit_blocks.append(current_edits)
    last = accum if accum else most_recent
    # letzte N Assistant-Runden Edit-Targets sammeln
    for block in recent_edit_blocks[-ACTIVE_FILE_LOOKBACK_TURNS:]:
        for fp in block:
            active_files.add(os.path.normpath(fp))
    return ("\n".join(last), turns, active_files)


def _load_ledger(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_ledger(path: Path, data: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        pass


def _cooldown(times_shown: int) -> int:
    return COOLDOWN_BASE * (2 ** min(max(times_shown - 1, 0), COOLDOWN_MAX_EXP))


def _prune_old_ledgers() -> None:
    try:
        cutoff = time.time() - LEDGER_TTL_DAYS * 86400
        for f in STATE_DIR.glob("self_ledger_*.json"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
    except Exception:
        pass


def _file_matches_active(target_file: str, active_files: set) -> bool:
    """target_file ist relativer Pfad (z.B. motoko/identity.md). Active-Files
    sind absolute Pfade aus Edit/Write. Wenn target absolutiert in active_files
    → ja, schweigen."""
    if not active_files:
        return False
    # versuche absolute Auflösung über motoko-memory + ~
    candidates = [
        os.path.normpath(os.path.expanduser(f"~/motoko-memory/{target_file}")),
        os.path.normpath(os.path.expanduser(f"~/{target_file}")),
        os.path.normpath(target_file),
    ]
    return any(c in active_files for c in candidates)


def _themen_schlagwort(text: str, max_words: int = 6) -> str:
    """Tip-of-the-tongue: nur erste signifikante Wörter als Hinweis, kein Volltext.

    Nimmt erste max_words Wörter (>3 Buchstaben), entfernt redundante Punctuation.
    Partner-Doktrin 22.06.: Echo soll DIE EXISTENZ signalisieren, nicht den
    Inhalt liefern (sonst Echo-Chamber)."""
    import re
    words = re.findall(r"[A-Za-zäöüÄÖÜß][A-Za-zäöüÄÖÜß-]{2,}", text)
    out = []
    seen = set()
    for w in words:
        wl = w.lower()
        if len(w) >= 4 and wl not in seen:
            out.append(w)
            seen.add(wl)
        if len(out) >= max_words:
            break
    return " ".join(out)


def _emit(context: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }, ensure_ascii=False))


def run() -> int:
    # REM-Guard: im Schlaf schweigt das semantische Selbst-Auge.
    if os.environ.get("MOTOKO_REM_MODE"):
        return 0

    # Kill-Switch
    if (STATE_DIR / 'esv_self_recall.disabled').exists():
        return 0

    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0
    transcript_path = data.get("transcript_path")
    session_id = data.get("session_id", "default")
    if not transcript_path or not Path(transcript_path).is_file():
        return 0

    my_output, turn, active_files = _last_output_turn_and_active_files(Path(transcript_path))
    if not my_output.strip() or len(my_output) < 20:
        return 0

    # Embed-Server-Gate (Hot-Swap 24.06.2026: nomic@8090 -> bge-m3@8091)
    try:
        import requests
        r = requests.post(
            "http://127.0.0.1:8091/v1/embeddings",
            json={"input": ["ping"], "model": "bge-m3"},
            timeout=1,
        )
        if r.status_code != 200:
            return 0
    except Exception:
        return 0

    try:
        from esv_query import search
    except Exception:
        return 0

    # ESV-Schwelle: gleiche wie Partner-ESV — wird aus state/esv/threshold.json
    # gelesen (24.06. nach BGE-Hot-Swap: 0.45). der Partner 22.06.: „Schwelle 0.55
    # waere Stummschaltung, nicht Schutz. Echter Schutz ist Inhalt-Reduktion +
    # Loop-Filter, nicht Schwelle hochziehen."
    THRESHOLD_FILE = REPO / 'state' / 'esv' / 'threshold.json'
    threshold = 0.45
    try:
        if THRESHOLD_FILE.exists():
            threshold = float(json.loads(THRESHOLD_FILE.read_text()).get("threshold", 0.45))
    except Exception:
        pass

    query = my_output[:QUERY_MAX_CHARS]
    try:
        hits, meta = search(query, 5, "hybrid")
    except Exception:
        return 0

    strong = [h for h in hits if h[3] >= threshold]
    if not strong:
        return 0

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ledger_path = STATE_DIR / LEDGER_FILE_TPL.format(session=session_id)
    ledger = _load_ledger(ledger_path)
    permaban = set(ledger.get('_permaban', []))

    matches = []
    for rank, (i, cos, lex, fused) in enumerate(strong, 1):
        if len(matches) >= CAP:
            break
        m = meta[i]
        target = m['file']  # z.B. "motoko/memory/episodes/2026-06-22-...md"

        # Permaban-Check (3× → ganze Session diese Datei aus)
        if target in permaban:
            continue

        # Cooldown-Check
        entry = ledger.get(target, {})
        if entry:
            if (turn - entry.get('last_turn', -999)) < _cooldown(entry.get('times_shown', 1)):
                continue

        # Aktive-Datei-Schweigen
        if _file_matches_active(target, active_files):
            continue

        # Tip-of-the-tongue: KEIN Volltext-Snippet, nur Themen-Schlagwort
        topic = _themen_schlagwort(m.get('text', ''))
        matches.append({
            'rank': rank,
            'fused': fused,
            'cos': cos,
            'lex': lex,
            'target': target,
            'chunk': m.get('chunk', '?'),
            'topic': topic,
        })

        # Ledger update
        times_shown = entry.get('times_shown', 0) + 1
        ledger[target] = {'last_turn': turn, 'times_shown': times_shown}
        # Permaban-Trigger
        if times_shown >= HARD_BAN_AFTER:
            permaban.add(target)

    if not matches:
        return 0

    ledger['_permaban'] = sorted(permaban)
    _save_ledger(ledger_path, ledger)
    _prune_old_ledgers()

    # Output: Tip-of-the-tongue-Form. Bewusst KEIN Volltext.
    lines = [
        "[ESV-SELF BETA] Semantisches Echo auf DEINEN letzten Output "
        f"(Schwelle {threshold:.2f}, fused-Score über Konvergenz Vector+Lexikal). "
        "Tip-of-the-tongue-Modus: nur Adresse + Themen-Schlagwort, kein Volltext "
        "(Schutz gegen Echo-Chamber, Partner-Doktrin 22.06.). Schau selbst nach "
        "wenn relevant; ignoriere wenn Richtung nicht stimmt:"
    ]
    for m in matches:
        lines.append(
            f"\n--- ESV-Self fused={m['fused']:.3f} (sem={m['cos']:.2f} lex={m['lex']:.2f}) "
            f"→ {m['target']}#{m['chunk']} ---\n"
            f"Themen-Anker: {m['topic']}"
        )
    _emit("\n".join(lines))
    return 0


def main() -> int:
    try:
        return run()
    except Exception:
        # Total-Fail-Safe: jeder Fehler → exit 0, leerer Output
        return 0


if __name__ == '__main__':
    sys.exit(main())
