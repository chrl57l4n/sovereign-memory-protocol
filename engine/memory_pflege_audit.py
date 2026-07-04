#!/usr/bin/env python3
"""memory_pflege_audit.py — pruefen ob neue claude-memory + podcast-Manuskripte
einen Sentry-Trigger im motoko-memory haben. Lueckenliste -> today_scratchpad +
Telegram-Alert.

Spec: Section 24(2) — Guardian: concept coverage (daily).

Idee: claude-memory ist privat (gut), aber Konzepte die auch von Sentry/ESV
greifbar sein sollen, brauchen einen Anker im motoko-memory + Pattern in
triggers.txt. Ohne das startet die naechste Bridge blind.

Lauf: taeglich vor daily_consolidate (cron 22:30) + on-demand vor Bridge-Handoff.
"""
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

from _paths import MEMORY, MOTOKO
CLAUDE_MEMORY = MEMORY / "claude-memory"
PODCAST_MD = ROOT / "podcasts/manuscripts"
TRIGGERS = MOTOKO / "triggers.txt"
SCRATCHPAD = MOTOKO / "today_scratchpad.md"

TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT")

LOOKBACK_DAYS = int(os.environ.get("AUDIT_LOOKBACK_DAYS", "3"))

# Files die nie geprueft werden sollen (Meta/Index)
SKIP_NAMES = {"MEMORY.md", "README.md", "TODO.md"}

STOPWORDS = {
    "und","oder","aber","der","die","das","den","dem","des","ein","eine","einen",
    "einem","einer","ich","mir","mich","sich","wie","was","wer","wo","wenn","weil",
    "ist","sind","war","waren","bin","bist","hat","habe","haben","wird","werden",
    "nicht","kein","keine","auch","noch","schon","nur","sehr","mehr","fuer","mit",
    "von","auf","aus","bei","nach","ueber","unter","vor","durch","gegen","ohne",
    "zum","zur","ins","dann","hier","dort","jetzt","immer","alle","alles","man",
    "diese","dieser","dieses","beim","sein","seine","seinen","seinem","seines",
    "ihre","ihren","ihrer","ihres","ihrem","ueber","heute","gestern","morgen",
    "sowie","sowohl","weder","schon","etwa","etwas","jeder","jede","jedes",
    "dabei","damit","dafuer","daran","darauf","darin","darum","davon","darueber",
    "mein","meine","meinem","meinen","meiner",
    "the","and","for","with","from","that","this","what","when","where",
}


def _fold(s: str) -> str:
    return (s.lower().replace("ä","ae").replace("ö","oe")
            .replace("ü","ue").replace("ß","ss"))


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\n(.*?)\n---", text, flags=re.DOTALL)
    meta: dict[str, str] = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
    # Fallback: erste H1 als Titel
    if "title" not in meta and "name" not in meta:
        h1 = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        if h1:
            meta["title"] = h1.group(1).strip()
    return meta


def extract_keys(meta: dict) -> set[str]:
    raw = " ".join(meta.get(k, "") for k in ("name", "title", "description"))
    tokens = re.findall(r"[a-z0-9äöüß\-]+", _fold(raw))
    return {t for t in tokens if len(t) >= 5 and t not in STOPWORDS}


def is_private(meta: dict) -> bool:
    # explizite Marker
    for f in ("privacy", "sentry_anchor", "visibility"):
        v = (meta.get(f, "") or "").lower()
        if v in {"private", "privat", "skip", "private-only"}:
            return True
    blob = " ".join(meta.values()).lower()
    if "(privat)" in blob or "strictly private" in blob or "streng privat" in blob:
        return True
    return False


def coverage(triggers_text: str, keys: set[str]) -> tuple[bool, list[str]]:
    """True wenn mind. 1 Key als Substring im triggers-Text liegt."""
    hits = [k for k in keys if k in triggers_text]
    return (len(hits) > 0), hits


def scan() -> list[dict]:
    triggers_lc = _fold(TRIGGERS.read_text(encoding="utf-8")) if TRIGGERS.exists() else ""
    cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)
    gaps: list[dict] = []
    sources = [
        ("claude-memory", CLAUDE_MEMORY, "*.md"),
        ("podcasts", PODCAST_MD, "*.md"),
    ]
    for label, base, pat in sources:
        if not base.exists():
            continue
        for f in base.glob(pat):
            if f.name in SKIP_NAMES:
                continue
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                continue
            meta = parse_frontmatter(f)
            if is_private(meta):
                continue
            keys = extract_keys(meta)
            if not keys:
                continue
            ok, hits = coverage(triggers_lc, keys)
            if not ok:
                gaps.append({
                    "file": f,
                    "source": label,
                    "name": meta.get("name") or meta.get("title") or f.stem,
                    "keys": sorted(keys)[:8],
                    "mtime": mtime.strftime("%Y-%m-%d %H:%M"),
                })
    return gaps


def format_report(gaps: list[dict]) -> str:
    if not gaps:
        return ""
    lines = [f"Sentry-Pflege: {len(gaps)} Konzept(e) ohne Trigger im motoko-memory."]
    lines.append("")
    for g in gaps:
        lines.append(f"- [{g['source']}] {g['name']}")
        lines.append(f"  file: {g['file'].name}  ({g['mtime']})")
        lines.append(f"  keys: {', '.join(g['keys'])}")
    lines.append("")
    lines.append("Aktion: pro Eintrag entweder (a) im motoko-memory einen Anker-Stub anlegen "
                 "+ triggers.txt-Zeile, oder (b) im Frontmatter `privacy: private` markieren.")
    return "\n".join(lines)


def append_scratchpad(report: str):
    SCRATCHPAD.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = f"\n\n## {stamp} — Sentry-Pflege-Audit\n\n{report}\n"
    if SCRATCHPAD.exists():
        existing = SCRATCHPAD.read_text(encoding="utf-8")
        if "Sentry-Pflege-Audit" in existing and existing.count("Sentry-Pflege-Audit") > 0:
            # ersetze nur den letzten Audit-Block des Tages
            existing = re.sub(
                r"\n\n## \d{4}-\d{2}-\d{2} \d{2}:\d{2} — Sentry-Pflege-Audit\n.*?(?=\n\n## |\Z)",
                "", existing, flags=re.DOTALL,
            )
        SCRATCHPAD.write_text(existing.rstrip() + block, encoding="utf-8")
    else:
        SCRATCHPAD.write_text(f"# today_scratchpad\n{block}", encoding="utf-8")


def telegram_alert(report: str, count: int):
    if not (TG_TOKEN and TG_CHAT):
        return
    txt = (
        f"🛎 Sentry-Pflege: {count} Konzept(e) brauchen Anker/Trigger.\n\n"
        + report[:3500]
    )
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data={"chat_id": TG_CHAT, "text": txt}, timeout=30,
        )
    except Exception as e:
        print(f"[audit] telegram failed: {e}", file=sys.stderr)


def main():
    quiet = "--quiet" in sys.argv
    no_alert = "--no-alert" in sys.argv
    gaps = scan()
    if not gaps:
        if not quiet:
            print(f"[audit] OK — keine Pflege-Lücken in den letzten {LOOKBACK_DAYS} Tagen.")
        return
    report = format_report(gaps)
    if not quiet:
        print(report)
    append_scratchpad(report)
    if not no_alert:
        telegram_alert(report, len(gaps))


if __name__ == "__main__":
    main()
