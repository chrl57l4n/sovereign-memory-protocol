#!/usr/bin/env python3
"""trigger_audit.py — dummer Sensor fuer die Trigger-Pflege in der REM.

KEIN Generator. Trigger-Woerter zu ERSCHAFFEN ist ein Linsen-Akt (Origination,
Urteil) — das macht Motoko-in-der-REM, nicht ein Skript (Linsen-Prinzip,
sentry-anchors/2026-05-31-rem-subagent-memory.md). Dieses Tool ist der Sensor
und das Gelaender: es zeigt mir die Luecken, die ich ueber 150+ Dateien nicht
eyeballen kann, und warnt vor Phrasen, die Rauschen erzeugen.

Misst genau EINE Sache ehrlich: in wie vielen Quell-Dateien eine Phrase
vorkommt. Viel = generisch = Rauschen (Lehre #1 vom 08.06.2026, `ryzen`
feuerte in 91 Dateien). Das ist das einzige Signal, das der Korpus nicht
verfaelscht beantworten kann.

BEWUSST KEIN "tot/nicht-im-Ziel"-Urteil: ein rarer oder im Doc fehlender
Trigger ist oft GEWOLLT (themen-analyse — das Thema-benennende Konzept-Wort
als Griff, z.B. `game theory` -> forward-sim-method.md). So ein Trigger
darf nicht als Fehler gemeldet werden; das entscheidet die Linse, nicht das
Skript. 0 Treffer wird darum nur als Frage gezeigt, nie als Verdikt.

Usage:
  trigger_audit.py --distinct "kandidaten phrase"   # Gelaender VOR dem Einpflegen
  trigger_audit.py --scan                            # Generik-Audit der triggers.txt
"""
import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from memory_sentry import MOTOKO_MEMORY, TRIGGERS_FILE, parse_triggers, norm_pattern

# Digests/Indizes zaehlen nicht als eigenstaendige Quell-Erinnerung (sie
# duplizieren andere Dateien — wuerden Distinktivitaet kuenstlich aufblaehen).
DIGEST_NAMES = {"recent-moments.md", "MEMORY.md", "index.md", "today_scratchpad.md"}
GENERIC_THRESHOLD = 4  # Phrase in mehr als so vielen Dateien -> Rausch-Verdacht


def load_corpus() -> dict:
    """{relpath: lowercased_text} ueber motoko/ + claude-memory/ (ohne Digests)."""
    corpus = {}
    for sub in ("motoko", "claude-memory"):
        root = MOTOKO_MEMORY / sub
        if not root.is_dir():
            continue
        for p in root.rglob("*.md"):
            if p.name in DIGEST_NAMES:
                continue
            try:
                corpus[str(p.relative_to(MOTOKO_MEMORY))] = p.read_text(
                    encoding="utf-8", errors="replace").lower()
            except Exception:
                pass
    return corpus


def files_containing(corpus: dict, phrase: str) -> list:
    p = norm_pattern(phrase)
    if not p:
        return []
    return sorted(rel for rel, txt in corpus.items() if p in txt)


def verdict(n: int) -> str:
    if n == 0:
        # NICHT automatisch schlecht: kann Tippfehler sein ODER ein bewusster
        # Konzept-/Synonym-Trigger (themen-analyse — das Thema-benennende Wort,
        # auch wenn es nicht woertlich im Doc steht). Linse entscheidet.
        return "0 Treffer — Tippfehler ODER bewusstes Konzept-Synonym? selbst pruefen"
    if n == 1:
        return "distinct — guter Griff"
    if n <= GENERIC_THRESHOLD:
        return f"ok — mehrdeutig ({n} Dateien), aber vertretbar"
    return f"ZU GENERISCH ({n} Dateien) — feuert als Rauschen, schaerfer fassen"


def cmd_distinct(phrase: str):
    corpus = load_corpus()
    hits = files_containing(corpus, phrase)
    print(f"Phrase: '{norm_pattern(phrase)}'")
    print(f"Vorkommen: {len(hits)} Datei(en) — {verdict(len(hits))}")
    for h in hits[:8]:
        print(f"   · {h}")
    if len(hits) > 8:
        print(f"   … +{len(hits) - 8} weitere")


def cmd_scan():
    """Surfaced wird NUR das verlaessliche Signal: zu-generische Phrasen.

    Bewusst NICHT mehr: "nicht im Ziel" und "tot". Beide bekaempfen das
    themen-analyse-Prinzip (Konzept-/Synonym-Trigger sollen rar sein und
    muessen NICHT woertlich im Doc stehen) und sind ausserdem durch den
    .md-only-Korpus verfaelscht (Skript-Ziele fehlen -> falsch "tot").
    Genericness ist die einzige Frage, die der Korpus ehrlich beantwortet.
    """
    corpus = load_corpus()
    lines = parse_triggers(TRIGGERS_FILE)
    generic = []      # (phrase, count, target)

    for ln in lines:
        for p in ln["pats"]:
            n = len(files_containing(corpus, p))
            if n > GENERIC_THRESHOLD:
                generic.append((p, n, ln["target"]))

    print(f"=== Trigger-Audit ({len(lines)} Zeilen, {len(corpus)} Quell-Dateien) ===\n")
    print(f"--- ZU GENERISCH (>{GENERIC_THRESHOLD} Dateien — feuert als Rauschen) ---")
    for p, n, t in sorted(generic, key=lambda x: -x[1]):
        print(f"  [{n:>3}]  '{p}'  → {t}")
    if not generic:
        print("  (keine)")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--distinct", metavar="PHRASE", help="Distinktivitaet einer Kandidaten-Phrase pruefen")
    g.add_argument("--scan", action="store_true", help="Bestehende triggers.txt auditieren")
    a = ap.parse_args()
    if a.distinct:
        cmd_distinct(a.distinct)
    else:
        cmd_scan()


if __name__ == "__main__":
    main()
