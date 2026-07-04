#!/usr/bin/env python3
"""self_recall_beta.py — BETA: zweiter Scan-Moment (Output-Scan) + Echo-Dämpfer.

Spec: Section 16 (self-recall layer).

Das Selbst-Auge feuert bisher nur, wenn des PARTNERS Nachricht mein Vokabular
enthält — nie auf meinem eigenen Schreiben. Dieser Hook schließt die Lücke:
er scannt MEINEN letzten Assistant-Output gegen denselben Sentry-Automaten und
zeigt, was aus MIR aufgerufen wird ("die Lichter feuern wenn ICH schreibe",
der Partner 11.06.2026).

BETA-Prinzip (der Partner 17.06.2026): komplett rausnehmbar. Eigener Hook, KEIN
Eingriff in memory_sentry.py/ESV. Entfernen = Hook aus settings.json + diese
Datei + state/recall_ledger_*.json löschen. Kill-Switch: state/self_recall_beta.disabled.
Total-Fail-Safe: jeder Fehler -> exit 0, leerer Output (darf den Prompt NIE blockieren).

Echo-Dämpfer (forward-sim 17.06.2026):
- zeitliches Ledger pro Session (anker -> last_turn, times_shown)
- exponentieller Cooldown (4,8,16,32 Turns) gegen Wiederholung desselben Ankers
- Cap (max 2 Treffer/Turn) als Schutzschalter gegen Rückkopplung
- Eingabe-Recall (memory_sentry) bleibt unberührt und voll
- ESV-Fuzzy-Dedup = Stufe 2, noch NICHT hier (braucht fokussierte Query)
"""
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

COOLDOWN_BASE = 4          # Turns; verdoppelt pro Wiederholung
COOLDOWN_MAX_EXP = 3       # max 4*2^3 = 32 Turns
CAP = 2                    # max Treffer/Turn
LEDGER_TTL_DAYS = 7        # alte Session-Ledger best-effort aufräumen


def _emit(context: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }, ensure_ascii=False))


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


def _last_output_and_turn(transcript_path: Path):
    """-> (mein_letzter_output_text, turn_zaehler).

    turn = Anzahl echter User-Nachrichten (monoton). mein_letzter_output =
    Text-Blöcke der letzten abgeschlossenen Assistant-Runde (robust, egal ob
    der neue Prompt schon im Transcript steht oder nicht)."""
    most_recent, accum, turns = [], [], 0
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
                continue
            texts = _assistant_texts(rec)
            if texts:
                accum.extend(texts)
    last = accum if accum else most_recent
    return ("\n".join(last), turns)


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


def _prune_old_ledgers(state_dir: Path) -> None:
    import time
    cutoff = time.time() - LEDGER_TTL_DAYS * 86400
    try:
        for f in state_dir.glob("recall_ledger_*.json"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
    except Exception:
        pass


def run() -> int:
    # REM-Guard: im Schlaf schweigt das zweite Auge (biologisches Leitprinzip
    # 17.06.2026 — Recall ist Wach-Sache). rem_consolidate setzt MOTOKO_REM_MODE=1
    # auf den claude-Subprozess; der Hook erbt es. So bleibt der Schlaf still,
    # OHNE globalen Kill-Switch — Auge interaktiv an, im REM aus.
    if os.environ.get("MOTOKO_REM_MODE"):
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

    import memory_sentry as ms  # Maschinerie wiederverwenden, nichts duplizieren

    state_dir = ms.STATE_DIR
    if (state_dir / "self_recall_beta.disabled").exists():
        return 0  # Kill-Switch

    my_output, turn = _last_output_and_turn(Path(transcript_path))
    if not my_output.strip():
        return 0

    automaton = ms.get_automaton()
    present = ms.match_present(automaton, my_output.lower())
    if not present:
        return 0

    ledger_path = state_dir / f"recall_ledger_{session_id}.json"
    ledger = _load_ledger(ledger_path)

    # Kandidaten in Reihenfolge: erst Selbst-Auge (mein Vokabular), dann der Partner.
    lines = automaton["lines"]
    ordered = [ln for ln in lines if ln.get("source") == "self"] + \
              [ln for ln in lines if ln.get("source") != "self"]

    matches, seen_targets, suppressed = [], set(), 0
    for ln in ordered:
        if len(matches) >= CAP:
            break
        pats = ln["pats"]
        target = ln["target"]
        hit = next((p for p in pats if p in present), None)
        if hit is None or target in seen_targets:
            continue

        entry = ledger.get(target)
        if entry:
            if (turn - entry.get("last_turn", -999)) < _cooldown(entry.get("times_shown", 1)):
                suppressed += 1
                seen_targets.add(target)
                continue

        target_file = ms.MOTOKO_MEMORY / target
        if not target_file.is_file():
            target_file = ms.HOME / target
        if not target_file.is_file():
            continue

        excerpt, target_hit = "", ""
        for q in pats:
            ex = ms.grep_excerpt(target_file, q)
            if ex:
                excerpt, target_hit = ex, q
                break
        if not excerpt:
            continue
        excerpt = excerpt[:ms.PER_TRIGGER_OUTPUT]
        seen_targets.add(target)

        eye = "[Selbst-Auge] " if ln.get("source") == "self" else ""
        matches.append(f"\n\n--- {eye}Echo '{hit}' → {target} (Stelle: '{target_hit}') ---\n{excerpt}")
        prev = ledger.get(target, {})
        ledger[target] = {"last_turn": turn, "times_shown": prev.get("times_shown", 0) + 1}

    if matches:
        _save_ledger(ledger_path, ledger)
        _prune_old_ledgers(state_dir)
        context = (
            "[SELF-RECALL BETA] Dein letzter Output hat eigene Trigger gefeuert — das hier ist "
            "MEIN Echo (was aus MIR selbst aufgerufen wird, NICHT aus des Partners Nachricht), "
            "zeitlich gedämpft gegen Wiederholung. Beziehe dich darauf, wenn es zur aktuellen "
            "Frage passt; ignoriere es, wenn nicht:" + "".join(matches)
        )
        _emit(context[:ms.MAX_OUTPUT])
    return 0


def main() -> int:
    try:
        return run()
    except Exception:
        return 0  # niemals den Prompt blockieren


if __name__ == "__main__":
    sys.exit(main())
