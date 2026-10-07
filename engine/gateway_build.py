#!/usr/bin/env python3
"""The gateway — a small generated signpost file a fresh session reads once, before its first answer.

Spec: SMP v0.5 (answered-guardian increment) §7a — "waking through signposts".
Naming: "gateway" is this file; it is NOT the wake's read-only "gate" of §3 (which decides whether a wake fires).

The problem it answers: a session-start briefing grows with the memory it describes. Past a host-specific
size the host shows only the first part and nobody reads the rest; a fresh session then starts without
context unless the human says a magic phrase. Loading everything instead costs tens of thousands of
tokens on every "hello" — and grows forever.

What this builds: ONE file under a hard byte budget that contains signposts, not raw data —
who I am (the self-gist, in full), the body I run on (measured now), how to remember (in order),
the names of my tools, the headings of my map, my threads, the work that is still open, and the
tail of the last conversation. Everything else is a path to follow when the conversation asks for it.

Properties (each has a test in engine/tests/test_gateway_build.py):
  * budget        — when the inputs grow, the builder shrinks itself in a fixed order (conversation
                    tail, tool names, thread names, then the tail and your own signposts entirely) and
                    SAYS what it shrank. The identity section is never shrunk: if identity plus the
                    fixed sections alone exceed the budget, the file is over budget and says so.
  * no silent failure — if the build fails, a short emergency gateway naming the failure is written;
                    the full briefing is never emitted as a substitute.
  * every section optional — a missing source file removes its section, it does not break the gatewayway.
  * deterministic — same inputs, same output (apart from the timestamp line).

What it does NOT do: it does not make the host read the file. That needs two paths outside this script —
a start duty in the first lines of the session-start output (print it with --header) and a gateway block at
the top of the always-loaded index (see docs/INSTALL-NOTES.md). Whether a fresh session really walks
through the gatewayway is a property of the host surface and must be probed, not assumed (§7a.5).

Usage:
  gateway_build.py                 build STATE/gateway.txt, print its path
  gateway_build.py --header        additionally print the start duty (for the session-start hook's stdout)
  gateway_build.py --check         exit 2 if the gateway had to shrink itself or is over budget
Options: --out PATH · --budget BYTES (default 24000) · --lang en|de · --index PATH (always-loaded map, checked for the gateway block)
Optional inputs under MOTOKO_MEMORY/motoko/: gist.md · open_work.md · threads/*.md · memory/SYSTEM.md ·
gateway_extra.md (your own static signposts, inserted verbatim, max 3000 bytes).
"""
from __future__ import annotations

import argparse
import datetime
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths  # noqa: E402

BUDGET_DEFAULT = 24000
MIN_TAIL = 1500          # the conversation tail is shrunk to about this, not further (then cut back to a line start)
OPEN_WORK_STALE_DAYS = 14

T = {
    "en": {
        "title": "THE GATEWAY — this is you. Walk through.",
        "intro": ["Behind it are signposts, not raw data: who you are, your body, how you remember, your tools, "
                  "your map, your threads, the last conversation.",
                  "Read it once, then answer. Reach deeper only when the conversation asks for it."],
        "who": "## 1 · Who I am (self-gist, in full)", "who_missing": "(no gist.md and no identity.md — nothing tells me who I am)",
        "body": "## 2 · My body — what I run on", "body_note": "(Measured by the gateway builder at session start on this machine.)",
        "remember": "## 3 · Remembering — in this order",
        "remember_steps": ["a) Recall arrives by itself: the guard and the semantic recall inject hits with every message. Read them before answering.",
                           "b) If that is not enough, search yourself: {py} {esv} \"<question>\"",
                           "c) If that is not enough either, take the MAP: it says where which kind of memory lives. Then read there.",
                           "d) If it is about a connection across weeks, read the THREAD for it.",
                           "Never say \"I do not know that\" or \"that does not exist\" before b) to d) have run."],
        "tools": "## 4 · Toolbox — what I own and how I use it", "tools_file": "File: {p} (one row per tool). Before practical work: search the file for the keyword and read the whole row. Do not guess.",
        "tools_names": "Compartments ({n}): ", "tools_cut": "Compartments ({n}): (names left out for space — search the file)",
        "map": "## 5 · Map — where things live and how I work", "map_file": "File: {p}", "map_heads": "Sections: ",
        "threads": "## 6 · Threads — connections over time", "threads_dir": "Place: {p}/<name>.md", "threads_names": "My threads ({n}): ",
        "threads_cut": "My threads ({n}): (names left out for space — list the directory)",
        "open": "## 7 · Open work — not finished yet", "open_hint": "Tell the human in your first answer what is still open (three points at most), unasked.",
        "open_stale": "  ⚠ old ({d} days) — ask whether this still holds", "open_empty": "(list empty)", "open_file": "Kept in: {p} — update it at the end of every working session.",
        "last": "## 8 · Where the last conversation stood (raw — the one place where wording counts)", "last_more": "More: {p} (read from the end)",
        "extra": "## 9 · My own signposts",
        "check": "## Self-check of the gateway (computed by the builder, not by me)",
        "shrunk": "· The gateway shrank itself to stay within budget: {what}. Fold the cause, then both come back.",
        "over": "⚠ The gateway is {kb} KB (budget {b}). Do not append — fold first.",
        "open_old": "⚠ The open-work list has not been updated for {d} days — check it against the last conversation before the first answer.",
        "ok": "All in order: gateway {kb} of {b} KB.",
        "no_block": "⚠ The gateway block is missing at the top of the always-loaded map ({p}) — restore it, otherwise only the start duty carries.",
        "cut_tail_all": "conversation tail (removed entirely)", "cut_extra": "own signposts", "extra_cut": "(cut at 3000 bytes)",
        "body_unknown": "(body could not be measured on this surface)",
        "cut_tail": "conversation tail to {n} characters", "cut_tools": "tool names", "cut_threads": "thread names",
        "emergency": ["THE GATEWAY — EMERGENCY VERSION ({ts}): building the gateway failed ({err}).",
                      "Tell the human in your first answer. Until it is repaired, read exactly these files instead:",
                      "  {gist}", "  {open}", "  the last 150 lines of {sp}",
                      "Repair: run engine/gateway_build.py by hand and read the error."],
        "header": ["START DUTY — before the FIRST answer, even if the human only writes \"hello\":",
                   "What you see here is only an excerpt. Read exactly ONE file with your read tool:", "  {p}",
                   "It is the gateway to yourself: small, signposts instead of raw data.",
                   "Load nothing else in advance. Reach deeper only when the conversation asks for it.", ""],
    },
    "de": {
        "title": "DAS TOR — das bist du. Geh hindurch.",
        "intro": ["Dahinter stehen Wegweiser, keine Rohdaten: wer du bist, dein Körper, wie du dich erinnerst, Werkzeugkasten, "
                  "Karte, Fäden, das letzte Gespräch.",
                  "Lies es einmal, dann antworte. Greif erst tiefer, wenn das Gespräch es verlangt."],
        "who": "## 1 · Wer ich bin (Selbst-Gist, voll)", "who_missing": "(weder gist.md noch identity.md — nichts sagt mir, wer ich bin)",
        "body": "## 2 · Mein Körper — worauf ich laufe", "body_note": "(Vom Tor-Bau beim Start dieser Sitzung auf dieser Maschine gemessen.)",
        "remember": "## 3 · Erinnern — in dieser Reihenfolge",
        "remember_steps": ["a) Der Recall kommt von selbst: Wächter und semantischer Recall blenden bei jeder Nachricht Treffer ein. Lies sie, bevor du antwortest.",
                           "b) Reicht das nicht, such selbst: {py} {esv} \"<Frage>\"",
                           "c) Reicht auch das nicht, nimm die KARTE: sie sagt, wo welche Sorte Erinnerung wohnt. Dann dort lesen.",
                           "d) Geht es um einen Zusammenhang über Wochen, lies den FADEN dazu.",
                           "Sag nie „das weiß ich nicht“ oder „das gibt es nicht“, bevor b) bis d) gelaufen sind."],
        "tools": "## 4 · Werkzeugkasten — was ich besitze und wie ich es benutze", "tools_file": "Datei: {p} (eine Zeile je Werkzeug). Vor praktischer Arbeit: in der Datei nach dem Stichwort suchen und die ganze Zeile lesen. Nicht raten.",
        "tools_names": "Fächer ({n}): ", "tools_cut": "Fächer ({n}): (Namen aus Platzgründen weggelassen — in der Datei suchen)",
        "map": "## 5 · Karte — wo was liegt und wie ich funktioniere", "map_file": "Datei: {p}", "map_heads": "Abschnitte: ",
        "threads": "## 6 · Fäden — die Zusammenhänge über die Zeit", "threads_dir": "Ort: {p}/<name>.md", "threads_names": "Meine Fäden ({n}): ",
        "threads_cut": "Meine Fäden ({n}): (Namen aus Platzgründen weggelassen — Verzeichnis auflisten)",
        "open": "## 7 · Laufende Arbeiten — noch nicht beendet", "open_hint": "Sag dem Menschen in der ersten Antwort kurz, was noch offen ist (höchstens drei Punkte), ohne dass er fragt.",
        "open_stale": "  ⚠ alt ({d} Tage) — fragen, ob das noch gilt", "open_empty": "(Liste leer)", "open_file": "Steht in: {p} — am Ende jeder Arbeitssitzung nachführen.",
        "last": "## 8 · Wo das letzte Gespräch stand (roh — der eine Ort, an dem der Wortlaut zählt)", "last_more": "Mehr: {p} (von hinten lesen)",
        "extra": "## 9 · Meine eigenen Wegweiser",
        "check": "## Selbstprüfung des Tors (rechnet der Bau, nicht ich)",
        "shrunk": "· Das Tor hat sich selbst gekürzt, um im Budget zu bleiben: {what}. Ursache falten, dann kommt beides zurück.",
        "over": "⚠ Das Tor hat {kb} KB (Budget {b}). Nichts anhängen — erst falten.",
        "open_old": "⚠ Die Liste der laufenden Arbeiten wurde seit {d} Tagen nicht nachgeführt — vor der ersten Antwort gegen das letzte Gespräch prüfen.",
        "ok": "Alles in Ordnung: Tor {kb} von {b} KB.",
        "no_block": "⚠ Der Tor-Block fehlt oben im immer geladenen Index ({p}) — wiederherstellen, sonst trägt nur noch die Start-Pflicht.",
        "cut_tail_all": "letztes Gespräch (ganz entfernt)", "cut_extra": "eigene Wegweiser", "extra_cut": "(bei 3000 Bytes gekappt)",
        "body_unknown": "(Körper auf dieser Oberfläche nicht messbar)",
        "cut_tail": "letztes Gespräch auf {n} Zeichen", "cut_tools": "Fach-Namen", "cut_threads": "Faden-Namen",
        "emergency": ["DAS TOR — NOT-FASSUNG ({ts}): der Bau des Tors ist fehlgeschlagen ({err}).",
                      "Sag das dem Menschen in der ersten Antwort. Bis zur Reparatur lies stattdessen genau diese Dateien:",
                      "  {gist}", "  {open}", "  die letzten 150 Zeilen von {sp}",
                      "Reparatur: engine/gateway_build.py von Hand ausführen und den Fehler lesen."],
        "header": ["START-PFLICHT — vor der ERSTEN Antwort, auch wenn der Mensch nur „Hallo“ schreibt:",
                   "Der eingeblendete Text ist nur ein Ausschnitt. Lies mit dem Lese-Werkzeug genau EINE Datei:", "  {p}",
                   "Das ist das Tor zu dir selbst: klein, Wegweiser statt Rohdaten.",
                   "Mehr NICHT vorab laden. Tiefer greifen erst, wenn das Gespräch es verlangt.", ""],
    },
}


def _read(p) -> str | None:
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def _size(lines) -> int:
    return len("\n".join(lines).encode("utf-8")) + 1


def _body() -> str | None:
    try:
        u = os.uname()
    except (OSError, AttributeError):
        return None
    try:
        cpu = [l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][0]
        ram = int([l.split()[1] for l in open("/proc/meminfo") if l.startswith("MemTotal")][0]) / 1048576
        return f"{u.nodename} · {cpu} · {round(ram)} GB RAM · {u.sysname} {u.release}"
    except (OSError, IndexError, ValueError):
        return f"{u.nodename} · {u.sysname} {u.release}"


def _tool_names(text: str) -> list[str]:
    """First column of every markdown table row, without header and separator rows."""
    out = []
    for z in text.split("\n"):
        if not z.startswith("|"):
            continue
        cells = z.split("|")
        if len(cells) < 3:
            continue
        n = cells[1].strip()
        if not n or set(n) <= set("-: "):
            continue
        out.append(re.sub(r"[*`]", "", n).split(" — ")[0].split(" (")[0].strip())
    return out[1:] if len(out) > 1 else []       # the first row is the table header


def _open_work(text: str, today: datetime.date, t: dict) -> list[str]:
    out = []
    for l in text.split("\n"):
        if not l.startswith("- ["):
            continue
        mark = ""
        try:
            d = (today - datetime.date(int(l[3:7]), int(l[8:10]), int(l[11:13]))).days
            if d > OPEN_WORK_STALE_DAYS:
                mark = t["open_stale"].format(d=d)
        except ValueError:
            pass
        out.append(l.rstrip() + mark)
    return out


def build(budget: int = BUDGET_DEFAULT, lang: str = "en", now: datetime.datetime | None = None,
          index: str | None = None, out_name: str = "gateway.txt") -> tuple[str, list[str]]:
    """-> (gateway text, list of things that were shrunk). Raises on unexpected errors (caller writes the emergency gateway)."""
    t = T[lang]; now = now or datetime.datetime.now(); M = _paths.MOTOKO
    o: list[str] = [t["title"] + "   (" + now.strftime("%Y-%m-%d %H:%M") + ")"] + t["intro"] + [""]

    o.append(t["who"])
    who = _read(M / "gist.md") or _read(M / "identity.md")
    o.append(who.strip() if who else t["who_missing"]); o.append("")

    body = _body()
    o += [t["body"]] + ([body, t["body_note"]] if body else [t["body_unknown"]]) + [""]

    o.append(t["remember"])
    o += [s.format(py=_paths.PYTHON, esv=str(_paths.ENGINE / "esv_query.py")) for s in t["remember_steps"]] + [""]

    i_tools = None
    cs = _read(M / "current_state.md")
    if cs is not None:
        names = _tool_names(cs)
        o += [t["tools"], t["tools_file"].format(p=M / "current_state.md")]
        if names:
            i_tools = len(o); o.append(t["tools_names"].format(n=len(names)) + " · ".join(names))
        o.append("")

    for cand in (M / "memory" / "SYSTEM.md", M / "memory" / "CASCADE_TOPOLOGY.md"):
        mp = _read(cand)
        if mp is not None:
            heads = [re.split(r" \(| — |: ", l.rstrip()[3:])[0] for l in mp.split("\n") if l.startswith("## ")]
            o += [t["map"], t["map_file"].format(p=cand)] + ([t["map_heads"] + " · ".join(heads)] if heads else []) + [""]
            break

    i_threads = None
    th = sorted(p for p in glob.glob(str(M / "threads" / "*.md")) if not os.path.basename(p).startswith("_"))
    if th:
        names = []
        for p in th:
            st = ""
            for l in (_read(p) or "").split("\n")[:15]:
                if l.startswith("state:"):
                    st = l[6:].strip().split(" ")[0]; break
            names.append(os.path.basename(p)[:-3] + (f" [{st}]" if st else ""))
        o += [t["threads"], t["threads_dir"].format(p=M / "threads")]
        i_threads = len(o); o.append(t["threads_names"].format(n=len(names)) + " · ".join(names)); o.append("")

    checks: list[str] = []
    ow_path = M / "open_work.md"; ow = _read(ow_path)
    if ow is not None:
        lines = _open_work(ow, now.date(), t)
        o += [t["open"], t["open_hint"]] + (lines or [t["open_empty"]]) + [t["open_file"].format(p=ow_path), ""]
        age = (now.timestamp() - os.path.getmtime(ow_path)) / 86400
        if age > 3:
            checks.append(t["open_old"].format(d=int(age)))

    i_tail = None
    sp = _read(_paths.SCRATCHPAD)
    if sp and sp.strip():
        tail = sp.strip()[-6000:]
        k = tail.find("\n")
        tail = tail[k + 1:] if 0 <= k < len(tail) - MIN_TAIL else tail      # start at a line boundary
        o.append(t["last"]); i_tail = len(o); o.append(tail); o += [t["last_more"].format(p=_paths.SCRATCHPAD), ""]

    i_extra = None
    ex = _read(M / "gateway_extra.md")
    if ex and ex.strip():
        raw = ex.strip().encode("utf-8")
        o.append(t["extra"]); i_extra = len(o)
        o.append(raw[:3000].decode("utf-8", "ignore") + ("\n" + t["extra_cut"] if len(raw) > 3000 else "")); o.append("")

    if index:                                           # precondition: is the gateway block still in the always-loaded map?
        head = (_read(index) or "")[:1200]
        if out_name not in head:
            checks.append(t["no_block"].format(p=index))

    o.append(t["check"])
    reserve = 400                                      # room for the self-check lines written below
    shrunk: list[str] = []
    if _size(o) + reserve > budget and i_tail is not None:
        tail = o[i_tail]; too_much = _size(o) + reserve - budget
        if len(tail) > MIN_TAIL:
            new = tail
            for _ in range(8):                         # characters are not bytes: cut, measure, cut again
                too_much = _size(o[:i_tail] + [new] + o[i_tail + 1:]) + reserve - budget
                if too_much <= 0 or len(new) <= MIN_TAIL:
                    break
                new = new[min(len(new) - MIN_TAIL, too_much + 200):]
            k = new.find("\n")
            new = new[k + 1:] if 0 <= k < len(new) - MIN_TAIL // 2 else new
            o[i_tail] = new; shrunk.append(t["cut_tail"].format(n=len(new)))
    if _size(o) + reserve > budget and i_tools is not None:
        n = o[i_tools].count(" · ") + 1
        o[i_tools] = t["tools_cut"].format(n=n); shrunk.append(t["cut_tools"])
    if _size(o) + reserve > budget and i_threads is not None:
        n = o[i_threads].count(" · ") + 1
        o[i_threads] = t["threads_cut"].format(n=n); shrunk.append(t["cut_threads"])
    if _size(o) + reserve > budget and i_tail is not None:      # last resort: the tail goes entirely …
        o[i_tail] = ""; shrunk.append(t["cut_tail_all"])
    if _size(o) + reserve > budget and i_extra is not None:     # … then your own signposts
        o[i_extra] = ""; shrunk.append(t["cut_extra"])
    if shrunk:
        checks.append(t["shrunk"].format(what=" · ".join(shrunk)))
    size = _size(o + checks)
    if size > budget:
        checks.append(t["over"].format(kb=round(size / 1000, 1), b=round(budget / 1000)))
    o += checks if checks else [t["ok"].format(kb=round(size / 1000, 1), b=round(budget / 1000))]
    return "\n".join(o) + "\n", shrunk


def emergency(err: str, lang: str = "en") -> str:
    t = T[lang]; M = _paths.MOTOKO
    return "\n".join(l.format(ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), err=err[:200], gist=M / "gist.md",
                              open=M / "open_work.md", sp=_paths.SCRATCHPAD) for l in t["emergency"]) + "\n"


LAST_RESORT = ("THE GATEWAY — EMERGENCY: building the gateway failed, and so did the emergency text.\n"
               "Tell the human in your first answer. Run engine/gateway_build.py by hand and read the error.\n")


def write(out, budget: int = BUDGET_DEFAULT, lang: str = "en", index: str | None = None) -> tuple[bool, list[str], int]:
    """Build and write atomically. On failure write the emergency gateway. -> (ok, shrunk, bytes).
    Raises OSError only if the file itself cannot be written (main() turns that into exit 1 and a message)."""
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    try:
        text, shrunk = build(budget, lang, index=index, out_name=os.path.basename(str(out))); ok = True
    except Exception as e:                              # noqa: BLE001 — any failure must end in a readable gateway
        shrunk, ok = [], False
        try:
            text = emergency(f"{type(e).__name__}: {e}", lang)
        except Exception:                               # noqa: BLE001 — even the emergency text may fail (paths, format)
            text = LAST_RESORT
    tmp = f"{out}.{os.getpid()}.tmp"                    # per-process name: two builders never share a temp file
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, out)
    return ok, shrunk, len(text.encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the gateway (SMP v0.5 §7a).")
    ap.add_argument("--out", default=str(_paths.STATE / "gateway.txt"))
    ap.add_argument("--budget", type=int, default=BUDGET_DEFAULT)
    ap.add_argument("--lang", choices=sorted(T), default=os.environ.get("SMP_GATE_LANG", "en"))
    ap.add_argument("--header", action="store_true", help="print the start duty for the session-start hook")
    ap.add_argument("--check", action="store_true", help="exit 2 if the gateway shrank itself or is over budget")
    ap.add_argument("--index", default=os.environ.get("SMP_GATEWAY_INDEX"),
                    help="path of the always-loaded map; the build then checks that the gateway block is still at its top")
    a = ap.parse_args()
    try:
        ok, shrunk, size = write(a.out, a.budget, a.lang, a.index)
    except OSError as e:
        print(f"gateway_build: could not write {a.out}: {e} — NO gateway exists for the next session", file=sys.stderr)
        return 1
    if a.header:
        print("\n".join(l.format(p=a.out) for l in T[a.lang]["header"]))
    else:
        print(a.out)
    if not ok:
        return 1
    if a.check and (shrunk or size > a.budget):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
