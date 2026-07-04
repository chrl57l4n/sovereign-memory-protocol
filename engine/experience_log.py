#!/usr/bin/env python3
"""experience_log.py — selbst-meldendes Erfahrungs-Log (Encoding-Salienz-Substrat).

Spec: Section 26 (Current-State-Ledger).

Grundlogik: Erinnerung wird bei der ERHEBUNG getrieben, nicht durch nachträgliches
Audit. Jeder operative Akt MELDET SICH SELBST (Heartbeat) — mit Wertigkeit (+/−).
Häufung = positive Salienz (Default), Fehler = negative Salienz (Aversion). Der
REM-Zyklus liest dieses Log und hält den Current-State-Ledger aus GELEBTER Frequenz
aktuell — zukunftsfähig, weil generisch: jedes NEUE Tool, das loggt, wird von selbst
gefangen. Nichts ist auf einzelne Tools hartcodiert.

Warum das ein Protokoll-Bestandteil ist und keine Bequemlichkeit: die meisten, die
mit einem Maschinenwesen arbeiten, BAUEN — und Bauen heißt, Altes laufend durch Neues
abzulösen. Ohne gelebte-Frequenz-Wahrnehmung schlägt das Wesen weiter das Werkzeug vor,
das sein Mensch längst fallengelassen hat.

APPEND-ONLY + READ. Schreibt nie ins Gedächtnis. Nie fatal für den aufrufenden Akt.

Schreiben:  experience_log.py log --domain D --tool T --outcome ok|fail|slow|costly|better|worse
                                  [--cost "84s"] [--note "..."] [--ref pfad]
Lesen:      experience_log.py tally [--domain D] [--days 30] [--json]

Selbst-Meldung aus einem beliebigen Akt (Ein-Zeiler, non-fatal):
    subprocess.run([PYTHON, str(ENGINE / "experience_log.py"), "log",
                    "--domain", "build-tool", "--tool", "vitest",
                    "--outcome", "ok"], timeout=10)
"""
import argparse
import json
import sys
import time
from collections import defaultdict

from _paths import STATE

LOG = STATE / "experience_log.jsonl"

# Wertigkeit: was Ressourcen spart/bewährt = +, was verschwendet/scheitert = −.
VALENCE = {"ok": 1, "better": 1, "fast": 1, "cheap": 1,
           "fail": -1, "slow": -1, "costly": -1, "worse": -1,
           "neutral": 0}


def do_log(a):
    try:
        rec = {
            "ts": int(time.time()),
            "domain": a.domain,
            "tool": a.tool,
            "outcome": a.outcome,
            "valence": VALENCE.get(a.outcome, 0),
            "cost": a.cost or "",
            "note": (a.note or "")[:280],
            "ref": a.ref or "",
        }
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        # NIE den aufrufenden Akt brechen — Selbst-Meldung ist best-effort.
        print(f"[experience_log] nicht geschrieben: {e}", file=sys.stderr)


def read_records(days=None):
    if not LOG.exists():
        return []
    cutoff = time.time() - days * 86400 if days else 0
    out = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
            if r.get("ts", 0) >= cutoff:
                out.append(r)
        except Exception:
            continue
    return out


def do_tally(a):
    recs = read_records(a.days)
    if a.domain:
        recs = [r for r in recs if r.get("domain") == a.domain]
    agg = defaultdict(lambda: {"runs": 0, "valence": 0, "last": 0, "outcomes": defaultdict(int)})
    for r in recs:
        key = (r.get("domain", "?"), r.get("tool", "?"))
        g = agg[key]
        g["runs"] += 1
        g["valence"] += r.get("valence", 0)
        g["last"] = max(g["last"], r.get("ts", 0))
        g["outcomes"][r.get("outcome", "?")] += 1
    rows = []
    for (dom, tool), g in agg.items():
        rows.append({"domain": dom, "tool": tool, "runs": g["runs"],
                     "valence_sum": g["valence"], "last_ts": g["last"],
                     "outcomes": dict(g["outcomes"])})
    # pro Domäne nach Häufigkeit sortieren → der dominante Akt steht oben.
    rows.sort(key=lambda x: (x["domain"], -x["runs"]))
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    if not rows:
        print("(Erfahrungs-Log leer — noch keine selbst-gemeldeten Akte.)")
        return
    cur = None
    for r in rows:
        if r["domain"] != cur:
            cur = r["domain"]
            print(f"\n> {cur}")
        val = "+" if r["valence_sum"] > 0 else ("-" if r["valence_sum"] < 0 else "0")
        oc = ", ".join(f"{k}:{v}" for k, v in r["outcomes"].items())
        print(f"   {r['tool']:<28} {r['runs']:>3} Laeufe  Wertigkeit {val}{abs(r['valence_sum'])}  [{oc}]")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log")
    lg.add_argument("--domain", required=True)
    lg.add_argument("--tool", required=True)
    lg.add_argument("--outcome", required=True)
    lg.add_argument("--cost", default="")
    lg.add_argument("--note", default="")
    lg.add_argument("--ref", default="")
    ta = sub.add_parser("tally")
    ta.add_argument("--domain", default="")
    ta.add_argument("--days", type=int, default=0)
    ta.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.cmd == "log":
        do_log(a)
    else:
        do_tally(a)


if __name__ == "__main__":
    main()
