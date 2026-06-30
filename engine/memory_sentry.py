#!/usr/bin/env python3
"""memory_sentry.py — UserPromptSubmit-Hook: SIGINT-Style Phrase-Trigger, ein Pass.

Loest die Bash-Version (memory_sentry.sh, O(N) Fork-Schleife: ~1000-2500 Prozess-
Spawns/Nachricht, 5-6s/Scan bei 283 Triggern) durch einen In-Prozess-Aho-Corasick-
Automaten ab. Architektur (project_recall_struktur_rem_build.md): REM kompiliert den
Automaten nachts + persistiert ihn (state/sentry_automaton.json), die Laufzeit laedt
nur und macht EINEN Pass ueber den Prompt — O(Textlaenge+Treffer), unabhaengig von
der Pattern-Zahl. Symmetrie mit ESV (Reindex teuer im REM, Query billig zur Laufzeit).

Modi:
  memory_sentry.py            Hook-Laufzeit: JSON-Prompt von stdin -> additionalContext-JSON
  memory_sentry.py --compile  Automat aus triggers.txt bauen + nach state/ persistieren (REM ruft das)
  memory_sentry.py --selftest AC-Treffermenge == naive Substring-Orakel beweisen + Benchmark

Match-Semantik IDENTISCH zur Bash-Version: literales, case-insensitives Substring-
Matching (wie grep -qF/-inF). Pattern-Normalisierung: lowercase + Whitespace-Collapse
(awk '{$1=$1;print}'). Prompt: nur lowercase (kein Collapse) — exakt wie tr im Original.
"""
import json
import os
import sys
import time
from collections import deque
from pathlib import Path

from _paths import MEMORY as MOTOKO_MEMORY, MOTOKO, STATE as STATE_DIR
TRIGGERS_FILE = Path(os.environ.get("MOTOKO_TRIGGERS_FILE", MOTOKO / "triggers.txt"))
# Zweites Auge: meine EIGENEN Self-Trigger (mein Vokabular: Narben/Prinzipien/Vorfall-
# Marker -> meine Schichten). der Partner 2026-06-11: "du musst dich an deine worte
# erinnern koennen." Gleicher Automat, gleicher Pass, nur getrennt beschriftet.
# Fehlt die Datei -> no-op (Sentry laeuft unveraendert einaeugig weiter).
SELF_TRIGGERS_FILE = Path(os.environ.get(
    "MOTOKO_SELF_TRIGGERS_FILE", MOTOKO / "triggers_self.txt"))
AUTOMATON_FILE = STATE_DIR / "sentry_automaton.json"
SCAN_LOG = STATE_DIR / "sentry_scan_times.log"

MAX_OUTPUT = 9500
PER_TRIGGER_OUTPUT = 2000
CTX_BEFORE = 1   # grep -B 1
CTX_AFTER = 5    # grep -A 5
EXCERPT_MAX_LINES = 25  # head -25


def norm_pattern(p: str) -> str:
    """lowercase + Whitespace-Collapse — repliziert awk '{$1=$1;print}' | tr upper lower."""
    return " ".join(p.split()).lower()


# ---------------------------------------------------------------------------
# STT-Lexikon — des Partners Lautformen -> kanonische Begriffe (10.06.2026)
# Prinzip: "erst uebersetzen, dann auf sentry feuern lassen". Anreicherung ist
# ADDITIV (Original + Uebersetzungen angehaengt) — kein Ersetzungs-Risiko,
# die Trigger-Wortliste bleibt frei von Lautform-Duplikaten.
# ---------------------------------------------------------------------------
STT_LEXIKON_FILE = Path(os.environ.get(
    "MOTOKO_STT_LEXIKON", MOTOKO_MEMORY / "motoko" / "stt_lexikon.txt"))


def stt_enrich(prompt_lc: str) -> str:
    """Haengt fuer jede im Prompt gefundene Lautform die kanonische Form an.
    Lexikon fehlt oder leer -> no-op (Prompt unveraendert zurueck)."""
    if not STT_LEXIKON_FILE.exists():
        return prompt_lc
    additions = []
    try:
        for raw in STT_LEXIKON_FILE.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            lautform, kanonisch = line.split("|", 1)
            lautform = norm_pattern(lautform)
            kanonisch = norm_pattern(kanonisch)
            if lautform and kanonisch and lautform in prompt_lc:
                additions.append(kanonisch)
    except Exception:
        return prompt_lc
    if not additions:
        return prompt_lc
    return prompt_lc + " §stt: " + " ".join(dict.fromkeys(additions))


# ---------------------------------------------------------------------------
# triggers.txt parsen -> Zeilen-Metadaten (Reihenfolge = Datei-Reihenfolge)
# ---------------------------------------------------------------------------
def parse_triggers(path: Path):
    """-> list[{'pats': [norm_pattern,...], 'target': relpath}], Datei-Reihenfolge erhalten."""
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            continue
        patterns, target = line.split("|", 1)
        target = target.strip()
        pats = [norm_pattern(p) for p in patterns.split(",")]
        pats = [p for p in pats if p]
        if not pats or not target:
            continue
        lines.append({"pats": pats, "target": target})
    return lines


def load_all_lines():
    """Beide Augen in EINE Zeilenliste: erst des Partners Trigger (source='partner'),
    dann meine Self-Trigger (source='self'). Self-Datei fehlt -> nur des Partners.
    Reihenfolge erhalten (der Partner zuerst), damit der seen_targets-Dedup das
    kanonische Ziel bevorzugt; mein Self-Auge ergaenzt, ueberschreibt nicht."""
    combined = []
    for ln in parse_triggers(TRIGGERS_FILE):
        ln["source"] = "partner"
        combined.append(ln)
    if SELF_TRIGGERS_FILE.exists():
        for ln in parse_triggers(SELF_TRIGGERS_FILE):
            ln["source"] = "self"
            combined.append(ln)
    return combined


# ---------------------------------------------------------------------------
# Aho-Corasick (rein Python, JSON-serialisierbar — keine C-Abhaengigkeit,
# ueberlebt Body-Wechsel ryzen/pi/thinkpad). Findet die Menge aller Pattern,
# die als Substring im Text vorkommen.
# ---------------------------------------------------------------------------
def build_automaton(lines):
    """Baut Goto/Fail/Output-Tabellen. Output speichert Pattern-IDs (Index in `patterns`)."""
    # Eindeutige Pattern -> ID
    patterns = []
    pat_id = {}
    for ln in lines:
        for p in ln["pats"]:
            if p not in pat_id:
                pat_id[p] = len(patterns)
                patterns.append(p)

    goto = [{}]          # goto[state][char] = next_state
    out = [[]]           # out[state] = list[pattern_id]
    # Trie
    for pid, p in enumerate(patterns):
        s = 0
        for ch in p:
            nxt = goto[s].get(ch)
            if nxt is None:
                nxt = len(goto)
                goto.append({})
                out.append([])
                goto[s][ch] = nxt
            s = nxt
        out[s].append(pid)

    # Failure-Links via BFS, Outputs entlang Fail-Kette mergen (Standard-AC)
    fail = [0] * len(goto)
    q = deque()
    for ch, nxt in goto[0].items():
        fail[nxt] = 0
        q.append(nxt)
    while q:
        s = q.popleft()
        for ch, nxt in goto[s].items():
            q.append(nxt)
            f = fail[s]
            while f and ch not in goto[f]:
                f = fail[f]
            cand = goto[f].get(ch, 0)
            fail[nxt] = cand if cand != nxt else 0
            out[nxt] = out[nxt] + out[fail[nxt]]

    return {"patterns": patterns, "goto": goto, "fail": fail, "out": out, "lines": lines}


def match_present(automaton, text_lc):
    """EIN Pass: -> set[str] der im Text vorkommenden Pattern."""
    goto = automaton["goto"]
    fail = automaton["fail"]
    out = automaton["out"]
    patterns = automaton["patterns"]
    present = set()
    s = 0
    for ch in text_lc:
        while s and ch not in goto[s]:
            s = fail[s]
        s = goto[s].get(ch, 0)
        if out[s]:
            for pid in out[s]:
                present.add(patterns[pid])
    return present


def naive_present(lines, text_lc):
    """Orakel: triviales literales Substring-Matching = Ground Truth fuer Aequivalenz-Test."""
    present = set()
    for ln in lines:
        for p in ln["pats"]:
            if p in text_lc:
                present.add(p)
    return present


# ---------------------------------------------------------------------------
# Persistenz
# ---------------------------------------------------------------------------
def save_automaton(automaton, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(automaton, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def load_automaton(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def get_automaton():
    """Laedt persistierten Automaten; baut inline neu bei fehlend ODER stale (mtime-Guard).
    Stale = triggers.txt neuer als Automat -> nie veralteten Index ausliefern."""
    newest_src = 0.0
    if TRIGGERS_FILE.exists():
        newest_src = TRIGGERS_FILE.stat().st_mtime
    if SELF_TRIGGERS_FILE.exists():
        newest_src = max(newest_src, SELF_TRIGGERS_FILE.stat().st_mtime)
    fresh = (
        AUTOMATON_FILE.exists()
        and newest_src > 0.0
        and AUTOMATON_FILE.stat().st_mtime >= newest_src
    )
    if fresh:
        try:
            return load_automaton(AUTOMATON_FILE)
        except Exception:
            pass
    lines = load_all_lines()
    automaton = build_automaton(lines)
    try:
        save_automaton(automaton, AUTOMATON_FILE)
    except Exception:
        pass  # write best-effort; Hook darf nie wegen Persistenz scheitern
    return automaton


# ---------------------------------------------------------------------------
# Excerpt-Extraktion (Port von grep -inF -B1 -A5 | head -25)
# ---------------------------------------------------------------------------
def grep_excerpt(target_file: Path, pattern: str):
    """Case-insensitive Substring-Suche mit -B1/-A5-Kontext, Zeilennummern, head -25.
    Format nah an grep: 'N:zeile' fuer Treffer, 'N-zeile' fuer Kontext, '--' zwischen Gruppen."""
    try:
        lines = target_file.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return ""
    pl = pattern.lower()
    hit_idx = [i for i, ln in enumerate(lines) if pl in ln.lower()]
    if not hit_idx:
        return ""
    # Kontext-Bereiche bilden + ueberlappende mergen
    ranges = []
    for i in hit_idx:
        lo, hi = max(0, i - CTX_BEFORE), min(len(lines) - 1, i + CTX_AFTER)
        if ranges and lo <= ranges[-1][1] + 1:
            ranges[-1] = (ranges[-1][0], max(ranges[-1][1], hi))
        else:
            ranges.append((lo, hi))
    hits = set(hit_idx)
    out_lines = []
    for ridx, (lo, hi) in enumerate(ranges):
        if ridx > 0:
            out_lines.append("--")
        for i in range(lo, hi + 1):
            sep = ":" if i in hits else "-"
            out_lines.append(f"{i + 1}{sep}{lines[i]}")
    return "\n".join(out_lines[:EXCERPT_MAX_LINES])


def cascade_excerpt(pats):
    """Fallback fuer recent-moments: archive/weekly -> monthly -> milestones, neueste zuerst."""
    for cdir in [MOTOKO_MEMORY / "motoko" / "archive" / "weekly",
                 MOTOKO_MEMORY / "motoko" / "archive" / "monthly"]:
        if not cdir.is_dir():
            continue
        for cfile in sorted(cdir.glob("*.md"), reverse=True):
            for q in pats:
                ex = grep_excerpt(cfile, q)
                if ex:
                    return ex, f"{q} (cascade: {cfile.name})"
    ms = MOTOKO_MEMORY / "motoko" / "milestones.md"
    if ms.is_file():
        for q in pats:
            ex = grep_excerpt(ms, q)
            if ex:
                return ex, f"{q} (cascade: milestones)"
    return "", ""


# ---------------------------------------------------------------------------
# Laufzeit-Hook
# ---------------------------------------------------------------------------
def run_hook():
    t0 = time.perf_counter_ns()
    if not TRIGGERS_FILE.exists():
        return 0
    raw = sys.stdin.read()
    try:
        prompt = json.loads(raw).get("prompt", "") if raw.strip() else ""
    except Exception:
        prompt = ""
    if not prompt:
        return 0
    prompt_lc = stt_enrich(prompt.lower())

    automaton = get_automaton()
    lines = automaton["lines"]
    present = match_present(automaton, prompt_lc)

    matches = []
    seen_targets = set()
    for ln in lines:
        pats = ln["pats"]
        target_trim = ln["target"]
        # Phase 1: erster Pattern der Zeile (in Deklarations-Reihenfolge) der im Prompt vorkommt
        prompt_hit = next((p for p in pats if p in present), None)
        if prompt_hit is None:
            continue
        if target_trim in seen_targets:
            continue
        # Ziel-Aufloesung: erst motoko-memory, dann HOME (fuer Code-Ziele wie
        # motoko-server/scripts/*.py — waren vorher stille Tote, Fix 10.06.2026)
        target_file = MOTOKO_MEMORY / target_trim
        if not target_file.is_file():
            target_file = HOME / target_trim
        if not target_file.is_file():
            continue

        # Phase 2: erste Wort-fuer-Wort-Stelle im Target ueber alle Pattern der Zeile
        excerpt, target_hit = "", ""
        for q in pats:
            ex = grep_excerpt(target_file, q)
            if ex:
                excerpt, target_hit = ex, q
                break

        # Phase 3: Cascade fuer recent-moments
        if not excerpt and "recent-moments" in target_trim:
            excerpt, target_hit = cascade_excerpt(pats)

        # Fallback: Datei-Anfang
        if not excerpt:
            head = "\n".join(target_file.read_text(encoding="utf-8", errors="replace").splitlines()[:10])
            excerpt = (f"(Pattern '{prompt_hit}' matched im Prompt; keine Wort-fuer-Wort-Stelle "
                       f"im Target gefunden — Datei trotzdem relevant. Anfang:)\n{head}")
            target_hit = "(Datei-Anfang)"

        excerpt = excerpt[:PER_TRIGGER_OUTPUT]
        seen_targets.add(target_trim)
        eye = "[Selbst-Auge] " if ln.get("source") == "self" else ""
        matches.append(
            f"\n\n--- {eye}Trigger '{prompt_hit}' → {target_trim} (Stelle: '{target_hit}') ---\n{excerpt}"
        )

    _log_scan(t0)

    if not matches:
        return 0
    additional = ("Memory-Sentry (zweiaeugig): Phrasen aus dem Prompt matchen auf Memory-Eintraege. "
                  "Treffer ohne Marker = des Partners Trigger; '[Selbst-Auge]' = MEINE eigenen "
                  "Self-Trigger (was aus MIR aufgerufen wird). Lese diese BEVOR du antwortest "
                  "und beziehe dich darauf:" + "".join(matches))
    additional = additional[:MAX_OUTPUT]
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional,
        }
    }, ensure_ascii=False))
    return 0


def _log_scan(t0):
    try:
        scan_ms = (time.perf_counter_ns() - t0) // 1_000_000
        n_lines = sum(1 for _ in TRIGGERS_FILE.read_text(encoding="utf-8").splitlines())
        SCAN_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(SCAN_LOG, "a", encoding="utf-8") as fh:
            fh.write(f"{int(time.time())} {scan_ms}ms triggers={n_lines}\n")
        # Ring auf 100 Eintraege
        kept = SCAN_LOG.read_text(encoding="utf-8").splitlines()[-100:]
        SCAN_LOG.write_text("\n".join(kept) + "\n", encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# --compile (REM ruft das)
# ---------------------------------------------------------------------------
def run_compile():
    lines = load_all_lines()
    automaton = build_automaton(lines)
    save_automaton(automaton, AUTOMATON_FILE)
    n_pat = len(automaton["patterns"])
    n_states = len(automaton["goto"])
    n_self = sum(1 for ln in lines if ln.get("source") == "self")
    print(f"OK: {len(lines)} Trigger-Zeilen ({n_self} Selbst-Auge), {n_pat} Pattern, "
          f"{n_states} Automat-Zustaende -> {AUTOMATON_FILE}")
    return 0


# ---------------------------------------------------------------------------
# --selftest (don't-trust-verify: AC == naive Orakel + Benchmark)
# ---------------------------------------------------------------------------
def run_selftest():
    lines = load_all_lines()
    automaton = build_automaton(lines)
    probes = [
        "wann hatten wir ueber perkolation gesprochen",
        "lass uns den sentry umbau und esv neukalibrierung machen",
        "sohee stimme und die tts config mit fixed seed",
        "llama qwen gemma nobara lokales llm modell",
        "auto-memory migration claude-memory recall coverage blindspot",
        "notebooklm deep dive externe ki perspektive",
        "don't trust verify",
        "voellig zusammenhangsloser text ohne jeden trigger 12345",
        "PERKOLATION in GROSSBUCHSTABEN und Sohee gemischt",
        "pairing remote-control fernsteuer anthropic-app",
    ]
    all_text = " ".join(probes) + " " + "x" * 5000
    probes.append(all_text)

    failures = 0
    for pr in probes:
        plc = pr.lower()
        ac = match_present(automaton, plc)
        nv = naive_present(lines, plc)
        if ac != nv:
            failures += 1
            only_ac = sorted(ac - nv)
            only_nv = sorted(nv - ac)
            print(f"  MISMATCH bei {pr[:50]!r}: nur-AC={only_ac} nur-naiv={only_nv}")
    print(f"Aequivalenz: {len(probes) - failures}/{len(probes)} Prompts AC==naiv")

    # Benchmark: Automat-Bau + 1000 Match-Passes
    t = time.perf_counter()
    for _ in range(50):
        build_automaton(lines)
    build_ms = (time.perf_counter() - t) / 50 * 1000
    bench_prompt = probes[1].lower()
    t = time.perf_counter()
    for _ in range(1000):
        match_present(automaton, bench_prompt)
    match_us = (time.perf_counter() - t) / 1000 * 1_000_000
    print(f"Benchmark: Automat-Bau {build_ms:.1f}ms | Match-Pass {match_us:.1f}us "
          f"({len(automaton['patterns'])} Pattern, {len(automaton['goto'])} Zustaende)")
    return 1 if failures else 0


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--compile":
        return run_compile()
    if arg == "--selftest":
        return run_selftest()
    return run_hook()


if __name__ == "__main__":
    sys.exit(main())
