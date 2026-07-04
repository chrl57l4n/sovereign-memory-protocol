#!/usr/bin/env python3
"""esv_recall.py — UserPromptSubmit-Helfer: ESV-Hybrid-Recall fuer Hook.

Spec: Section 14 (Echelon Semantic Vector).

Liest Prompt von argv, gibt formatierten Recall-Text auf stdout aus (oder leer,
wenn nichts ueber Schwelle / Server aus / Index fehlt). Silent-Fail by design —
darf den Sentry-Pfad nie blockieren.

Recall-Log: jede Anfrage wird in state/esv_recall_log.jsonl geloggt (fuer
monatliche Auto-Kalibrierung via esv_calibrate.py).
"""
import json
import os
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
BASE = SCRIPTS_DIR.parent
STATE_DIR = BASE / 'state' / 'esv'

THRESHOLD_FILE = STATE_DIR / 'threshold.json'
LOG_FILE = STATE_DIR / 'recall_log.jsonl'

sys.path.insert(0, str(SCRIPTS_DIR))

TOP_K = int(os.environ.get("ESV_TOP_K", "3"))
SNIPPET_MAX = int(os.environ.get("ESV_SNIPPET_MAX", "180"))


def load_threshold() -> float:
    default = float(os.environ.get("ESV_THRESHOLD", "0.42"))
    try:
        if THRESHOLD_FILE.exists():
            return float(json.loads(THRESHOLD_FILE.read_text()).get("threshold", default))
    except Exception as e:
        # Kalibrierung still verloren waere ein verrotteter Sensor
        print(f"[esv_recall] threshold.json unlesbar, Default {default}: {e}",
              file=sys.stderr)
    return default


def log_recall(query: str, threshold: float, best: float, n_hits: int,
               error: str | None = None) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        entry = json.dumps({
            "ts": time.time(),
            "query_len": len(query),
            "threshold": threshold,
            "best_score": round(best, 4),
            "n_hits": n_hits,
            "hit": n_hits > 0,
            **({"error": error} if error else {}),
        })
        with LOG_FILE.open("a") as f:
            f.write(entry + "\n")
    except Exception as e:
        print(f"[esv_recall] recall_log write failed: {e}", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        return
    query = sys.argv[1].strip()
    if not query or len(query) < 8:
        return
    # STT-Lexikon: des Partners Lautformen kanonisch anreichern, BEVOR die
    # Embedding-Suche laeuft ("erst uebersetzen, dann feuern", 10.06.2026).
    # Additiv: Original-Query bleibt erhalten (Case inklusive), nur der
    # Anhang kommt dazu, falls eine Lautform gefunden wurde.
    try:
        from memory_sentry import stt_enrich
        enriched = stt_enrich(query.lower())
        if enriched != query.lower():
            query = query + enriched[len(query):]
    except Exception:
        pass
    threshold = load_threshold()
    # stdout muss bei Fehlern leer bleiben (Hook-Pfad nie blockieren) — aber
    # stderr + Log muessen Fehler von "keine Treffer" unterscheidbar machen.
    try:
        from esv_query import search
    except Exception as e:
        print(f"[esv_recall] import esv_query failed: {e}", file=sys.stderr)
        log_recall(query, threshold, 0.0, 0, error=f"import: {e}")
        return
    try:
        hits, meta = search(query, TOP_K, "hybrid")
    except Exception as e:
        print(f"[esv_recall] search failed: {e}", file=sys.stderr)
        log_recall(query, threshold, 0.0, 0, error=f"search: {e}")
        return

    best = hits[0][3] if hits else 0.0
    strong = [h for h in hits if h[3] >= threshold]
    log_recall(query, threshold, best, len(strong))

    if not strong:
        return
    lines = ["ESV-Recall LIVE — gerade JETZT auf deine aktuelle Phrase berechnet "
             f"(semantisch+lexikalisch fused, Schwelle {threshold:.2f}). "
             "Kein Aufwach-Snapshot — pro Message neu. Sentry ist parallel "
             "gefeuert; die folgenden Stellen sind weitere semantische Naehe-Treffer "
             "zu DIESER Phrase. Pruefe vor Bezug ob sie zur Frage passen:"]
    for rank, (i, cos, lex, fused) in enumerate(strong, 1):
        m = meta[i]
        text = m["text"].replace("\n", " ").strip()[:SNIPPET_MAX]
        lines.append(
            f"\n--- ESV #{rank} fused={fused:.3f} (sem={cos:.2f} lex={lex:.2f}) "
            f"→ {m['file']}#{m['chunk']} ---\n{text}"
        )
    sys.stdout.write("\n".join(lines))


if __name__ == "__main__":
    main()
