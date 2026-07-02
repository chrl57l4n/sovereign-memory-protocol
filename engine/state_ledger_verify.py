#!/usr/bin/env python3
"""state_ledger_verify.py — Ground-Truth-Verifier für den Current-State-Ledger.

Referenz-Implementierung zu Whitepaper Section 26.

Der Ledger (MOTOKO/current_state.md) deklariert den Live-Operativ-Zustand ("was
benutzen wir JETZT"). DIESER Checker hält ihn gegen Ground-Truth ehrlich — sonst
verrottet er wie jede handgepflegte Liste (dann wäre er ein Pflaster statt Grundlogik).

READ-ONLY. Schreibt nie in den Ledger. Meldet nur. Exit immer 0 (Reporting).

Vier Checks:
  1. EXISTENZ   — jedes Artefakt (Spalte 3) existiert auf der Platte?
  2. DRIFT      — gibt es in einer Domäne ein STRIKT NEUERES Geschwister-Artefakt
                  (git-Commit), auf das der Ledger NICHT zeigt? (opt-in via DOMAIN_PROBES)
  3. KONKURRENZ — taucht ein "löst ab"-Wert (Spalte 5) im Always-Loaded-Index noch
                  als aktuell-klingender Claim OHNE Supersession-Marker auf?
                  (Index optional via Umgebungsvariable MOTOKO_INDEX)
  4. FREQUENZ   — zeigt die GELEBTE Nutzung (experience_log) ein anderes, positiv
                  bewertetes Tool als der Ledger? Generisch, ohne Hartcodieren.

Usage: state_ledger_verify.py [--ledger PFAD] [--json]
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from _paths import MOTOKO, HOME, MEMORY, STATE

LEDGER_DEFAULT = MOTOKO / "current_state.md"
EXP_LOG = STATE / "experience_log.jsonl"
# Optionaler Always-Loaded-Index für den Konkurrenz-Check (z.B. der Datei, die die
# Installation bei jedem Session-Start lädt). Nicht gesetzt → Check übersprungen.
_idx = os.environ.get("MOTOKO_INDEX")
INDEX = Path(_idx) if _idx else None

# Domänen mit "jüngeres-Geschwister"-Check (Glob relativ HOME). Pro Installation
# selbst befüllen — Beispiel:  {"build-tool": "engine/build_*.py"}
DOMAIN_PROBES: dict[str, str] = {}

SUPERSEDE_MARKERS = ("überholt", "ueberholt", "löst ab", "loest ab", "ersetzt",
                     "abgelöst", "abgeloest", "deprecated", "veraltet", "s.u.", "s. u.")
CURRENCY_WORDS = ("aktuell", "default", "ist der", "ist die", "current",
                  "adoptiert", "kanonische", "standard")
GENERIC_SUPERSEDED = {"fixwert", "manuell", "—", "-", "none", "keine"}


def fold(s): return s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")


def _resolve(tok: str) -> Path | None:
    """Artefakt-Pfad relativ zur Engine-Installation ODER zur Daten-Wurzel."""
    for base in (HOME, MEMORY):
        p = base / tok
        if p.exists():
            return p
    return None


def git_commit_ts(path: Path) -> int:
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", str(path)],
                           cwd=path.parent, capture_output=True, text=True, timeout=10)
        s = r.stdout.strip()
        return int(s) if s else int(path.stat().st_mtime)
    except Exception:
        try: return int(path.stat().st_mtime)
        except Exception: return 0


def parse_ledger(ledger: Path):
    rows = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        if cells[0].lower() in ("domäne", "domaene", "domain", "") or set(cells[0]) <= set("-: "):
            continue
        rows.append({"domain": cells[0], "current": cells[1], "artifact": cells[2],
                     "since": cells[3], "supersedes": cells[4]})
    return rows


def check_existence(rows):
    out = []
    for r in rows:
        for tok in re.split(r"[,\s]+", r["artifact"]):
            if "/" in tok and tok.endswith((".py", ".sh", ".json", ".md", ".txt", ".toml", ".yaml", ".yml")):
                if _resolve(tok) is None:
                    out.append(f"[EXISTENZ] {r['domain']}: Artefakt fehlt -> {tok}")
    return out


def check_drift(rows):
    out = []
    by_domain = {r["domain"]: r for r in rows}
    for domain, glob in DOMAIN_PROBES.items():
        r = by_domain.get(domain)
        if not r:
            continue
        art = next((t for t in re.split(r"[,\s]+", r["artifact"]) if "/" in t), None)
        if not art:
            continue
        art_path = _resolve(art)
        art_ts = git_commit_ts(art_path) if art_path else 0
        for sib in sorted(HOME.glob(glob)):
            rel = str(sib.relative_to(HOME))
            if rel == art:
                continue
            if git_commit_ts(sib) > art_ts:
                out.append(f"[DRIFT] {domain}: jüngeres Artefakt als Ledger-Ziel "
                           f"({art}) -> {rel} — prüfen ob Default gewechselt hat")
    return out


def check_competing(rows):
    out = []
    if INDEX is None or not INDEX.exists():
        return out
    lines = INDEX.read_text(encoding="utf-8").splitlines()
    for r in rows:
        cur_tokens = {t for t in re.split(r"[^a-z0-9]+", fold(r["current"])) if len(t) >= 4}
        for term in re.split(r"[,\s]+", fold(r["supersedes"])):
            if len(term) < 4 or term in GENERIC_SUPERSEDED:
                continue
            for ln in lines:
                lf = fold(ln)
                if term not in lf or not any(c in lf for c in CURRENCY_WORDS):
                    continue
                if any(m in lf for m in SUPERSEDE_MARKERS):
                    continue
                if any(tok in lf for tok in cur_tokens):
                    continue
                out.append(f"[KONKURRENZ] '{term}' (überholt laut Ledger:{r['domain']}) "
                           f"klingt im Index noch aktuell, ohne Marker:\n     \"{ln.strip()[:150]}\"")
    return out


def experience_tally():
    agg = {}
    if not EXP_LOG.exists():
        return agg
    for line in EXP_LOG.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        dom, tool = r.get("domain", "?"), r.get("tool", "?")
        g = agg.setdefault(dom, {}).setdefault(tool, {"runs": 0, "valence": 0})
        g["runs"] += 1
        g["valence"] += r.get("valence", 0)
    return agg


def check_frequency(rows):
    """Zukunfts-Kern: zeigt die GELEBTE Nutzung ein anderes (positives) Tool als
    der Ledger, ist der Ledger veraltet — generisch, ohne Hartcodieren."""
    out = []
    tally = experience_tally()
    by_domain = {r["domain"]: r for r in rows}
    for dom, tools in tally.items():
        pos = {t: g for t, g in tools.items() if g["valence"] > 0}
        if not pos:
            continue
        dom_tool = max(pos, key=lambda t: pos[t]["runs"])
        runs = pos[dom_tool]["runs"]
        r = by_domain.get(dom)
        if not r:
            out.append(f"[FREQUENZ] Domäne '{dom}' wird gelebt ({dom_tool}, {runs} Läufe), "
                       f"fehlt aber im Ledger — aufnehmen?")
            continue
        if fold(dom_tool) not in fold(r["current"]):
            out.append(f"[FREQUENZ] {dom}: gelebte Nutzung zeigt '{dom_tool}' ({runs} Läufe), "
                       f"Ledger sagt '{r['current']}' — Default gewechselt?")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=str(LEDGER_DEFAULT))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    ledger = Path(a.ledger)
    if not ledger.exists():
        print(f"[FATAL] Ledger fehlt: {ledger}"); sys.exit(0)
    rows = parse_ledger(ledger)
    findings = (check_existence(rows) + check_drift(rows)
                + check_competing(rows) + check_frequency(rows))
    if a.json:
        print(json.dumps({"rows": len(rows), "findings": findings}, ensure_ascii=False, indent=2))
        return
    print(f"Current-State-Ledger: {len(rows)} Domänen geprüft.")
    if not findings:
        print("OK — alle Artefakte da, keine Drift, keine veralteten Konkurrenz-Claims.")
    else:
        print(f"{len(findings)} Befund(e):\n")
        for f in findings:
            print(" - " + f)


if __name__ == "__main__":
    main()
