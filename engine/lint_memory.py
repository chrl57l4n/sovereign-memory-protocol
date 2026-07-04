#!/usr/bin/env python3
"""Memory-Linter — Anti-Vergesslichkeit + Constitution-Consistency.

Spec: Section 24(1) — Guardian: structural hygiene (daily).

Cron-Trigger: taeglich 03:30 vor daily_journal.

Checks:
1. Dead-Links — Markdown-Pfad-Referenzen die nicht existieren
2. Orphans — Files die von keiner Schicht referenziert sind
3. Constitution-Consistency — sind Aktive Reflexe + Konvensionen mit Datum + Quelle?
4. Onboarding-Compliance — fuer aktive Body in MOTOKO_IDENTITY: alle Pflicht-Items in
   `bodies/<hostname>.md` abgehakt?
5. Open-Drift-Tags — Reminder-Liste fuer Self-Review (Reflex-13)

Output: state/lint-report.md + Telegram-Notify wenn neue Issues seit letztem Lauf.

Referenz: rfcs/2026-05-11T14-memory-structure-vergesslichkeits-resilienz.md
          + Constitution Schicht-0-Pflicht
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Lazy-Import (Telegram-Send nur bei Bedarf, vermeidet Hard-Dep)
try:
    import requests
except ImportError:
    requests = None

from _paths import MOTOKO as MOTOKO_DIR, STATE as STATE_DIR, MEMORY, DOTENV as ENV_FILE
REPORT_FILE = STATE_DIR / "lint-report.md"
HASH_FILE = STATE_DIR / "lint-report.lasthash"
IDENTITY_FILE = MEMORY / "IDENTITY.json"

# Bot-Loader-Schichten — sind nie "orphan", werden ueber load_schichten() referenziert
BOT_LOADED_LAYERS = {
    "constitution.md",
    "partner-und-ki.md",
    "recent-moments.md",
    "identity.md",
    "workflow.md",
    "reflexes.md",
    "milestones.md",
    "wallet.md",
    "infrastructure.md",
    "recent-engagement.md",
    "sovereignty.md",
    "drift_tags.md",
}


def lint_dead_links() -> list[dict]:
    """Pruefe ob alle Markdown-Pfad-Referenzen existieren."""
    issues = []
    if not MOTOKO_DIR.exists():
        return issues
    for md in MOTOKO_DIR.rglob("*.md"):
        try:
            text = md.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        # [label](path.md) Pattern
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+\.md)\)", text):
            label, link = m.group(1), m.group(2)
            if link.startswith(("http", "#")):
                continue
            link_path = (md.parent / link).resolve()
            if not link_path.exists():
                issues.append({"file": str(md.relative_to(MOTOKO_DIR)), "label": label, "link": link})
    return issues


def lint_orphans() -> list[str]:
    """Files die von keiner Schicht referenziert sind."""
    if not MOTOKO_DIR.exists():
        return []
    all_md = {str(p.relative_to(MOTOKO_DIR)) for p in MOTOKO_DIR.rglob("*.md")}
    referenced = set()
    for md in MOTOKO_DIR.rglob("*.md"):
        try:
            text = md.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for ref in re.findall(r"\(([^)]+\.md)\)", text) + re.findall(r"`([^`]+\.md)`", text):
            ref = ref.lstrip("./")
            referenced.add(ref)
    orphans = sorted(all_md - referenced - BOT_LOADED_LAYERS)
    # Journal + Episodes + Backup-Files raus (sind eigen-cyclic)
    return [
        o for o in orphans
        if not o.startswith(("journal/", "monolog/", "episodes/", "archive/"))
        and not o.endswith((".bak", ".bak-pre-monolog", ".bak-pre-ryzen"))
    ]


def lint_constitution() -> dict:
    """Constitution-Consistency-Check.

    Prueft:
    - Datei existiert
    - Pro Konvention: Datum + Quelle + Wortlaut oder Inhalt
    """
    const_file = MOTOKO_DIR / "constitution.md"
    if not const_file.exists():
        return {"error": "constitution.md fehlt im motoko-memory"}
    text = const_file.read_text()
    # Konvensionen sind H3-Headers mit Datum-Prefix (### YYYY-MM-DD ...)
    konventions = re.findall(r"^### (\d{4}-\d{2}-\d{2}.*?)$", text, re.MULTILINE)
    issues = []
    for k in konventions:
        # Sektion isolieren: bis naechster H3 oder H2
        section_re = re.compile(
            r"^### " + re.escape(k) + r"\s*$(.*?)(?=^### |\Z)",
            re.MULTILINE | re.DOTALL,
        )
        match = section_re.search(text)
        section = match.group(1) if match else ""
        has_quelle = "Quelle" in section or "Source" in section
        has_status = "Status" in section
        if not has_quelle:
            issues.append({"konvention": k, "missing": "Quelle-Feld"})
        if not has_status:
            issues.append({"konvention": k, "missing": "Status-Feld"})
    return {
        "konvensionen_count": len(konventions),
        "issues": issues,
    }


def lint_onboarding() -> dict:
    """Body-Onboarding-Compliance: ist body-md fuer aktiven Body komplett abgehakt?"""
    if not IDENTITY_FILE.exists():
        return {"error": "MOTOKO_IDENTITY.json fehlt"}
    try:
        identity = json.loads(IDENTITY_FILE.read_text())
    except json.JSONDecodeError:
        return {"error": "MOTOKO_IDENTITY.json nicht parsebar"}
    hostname = identity.get("hostname", "unknown")
    body_md = MOTOKO_DIR / "bodies" / f"{hostname}.md"
    if not body_md.exists():
        return {"body": hostname, "warning": f"bodies/{hostname}.md fehlt"}
    text = body_md.read_text()
    unchecked = []
    for line in text.split("\n"):
        m = re.match(r"^\s*- \[ \] (.+)$", line)
        if m:
            unchecked.append(m.group(1))
    return {"body": hostname, "unchecked_items": unchecked}


def lint_open_drift_tags() -> list[str]:
    """Liste offene Drift-Tags."""
    drift = MOTOKO_DIR / "drift_tags.md"
    if not drift.exists():
        return []
    text = drift.read_text()
    open_tags = []
    # H3-Header als Tag-Name
    for m in re.finditer(r"^### `?([a-z0-9-]+)`?\s*$", text, re.MULTILINE):
        tag = m.group(1)
        section_re = re.compile(
            r"^### `?" + re.escape(tag) + r"`?\s*$(.*?)(?=^### |\Z)",
            re.MULTILINE | re.DOTALL,
        )
        match = section_re.search(text)
        section = (match.group(1) if match else "").lower()
        if "resolved" in section or "aufgeloest" in section or "geloest" in section:
            continue
        if "status: closed" in section:
            continue
        open_tags.append(tag)
    return open_tags


def render_report(dead_links, orphans, constitution, onboarding, drift_tags) -> str:
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Memory-Lint-Report — {today}",
        "",
        "Auto-generiert von `lint_memory.py` taeglich. Reflex-13-Anker fuer Self-Review.",
        "",
        f"## Dead-Links ({len(dead_links)})",
        "",
    ]
    for d in dead_links[:15]:
        lines.append(f"- `{d['file']}` → `{d['link']}`")
    if len(dead_links) > 15:
        lines.append(f"- ...{len(dead_links) - 15} weitere")
    lines.append("")

    lines += [
        f"## Orphans ({len(orphans)})",
        "",
        "_Files die von keiner Schicht referenziert sind (ausser Bot-Loaded + Journal/Episodes)_",
        "",
    ]
    for o in orphans[:15]:
        lines.append(f"- `{o}`")
    if len(orphans) > 15:
        lines.append(f"- ...{len(orphans) - 15} weitere")
    lines.append("")

    lines += [
        "## Constitution-Consistency",
        "",
    ]
    if "error" in constitution:
        lines.append(f"❌ {constitution['error']}")
    else:
        lines.append(f"✅ {constitution['konvensionen_count']} Konvensionen gefunden.")
        if constitution["issues"]:
            lines.append(f"⚠️ {len(constitution['issues'])} Konvensionen ohne Pflicht-Felder:")
            for i in constitution["issues"][:10]:
                lines.append(f"  - `{i['konvention']}` fehlt: {i['missing']}")
    lines.append("")

    lines += [
        "## Onboarding-Compliance (aktiver Body)",
        "",
    ]
    if "error" in onboarding:
        lines.append(f"❌ {onboarding['error']}")
    elif "warning" in onboarding:
        lines.append(f"⚠️ {onboarding['warning']}")
    else:
        unchecked = onboarding.get("unchecked_items", [])
        body = onboarding["body"]
        if unchecked:
            lines.append(f"⚠️ Body **{body}**: {len(unchecked)} offene Onboarding-Items")
            for item in unchecked[:8]:
                lines.append(f"  - [ ] {item}")
        else:
            lines.append(f"✅ Body **{body}**: alle Onboarding-Items abgehakt")
    lines.append("")

    lines += [
        f"## Offene Drift-Tags ({len(drift_tags)})",
        "",
        "_Reflex-13: pro Tag pruefen — resolved / still open / stale_",
        "",
    ]
    for tag in drift_tags:
        lines.append(f"- `{tag}`")
    lines.append("")
    lines.append("🫡")
    return "\n".join(lines) + "\n"


def telegram_notify(msg: str) -> None:
    try:
        from _tg import send as _tgsend
        _tgsend(msg, source='lint_memory')
        return True
    except Exception:
        pass

    """Notify if requests + .env available."""
    if requests is None or not ENV_FILE.exists():
        return
    env = dict(
        line.strip().split("=", 1)
        for line in ENV_FILE.read_text().splitlines()
        if "=" in line and not line.strip().startswith("#")
    )
    token = env.get("TELEGRAM_BOT_TOKEN", "").strip("\"'")
    chat_id = env.get("TELEGRAM_CHAT_ID", "").strip("\"'")
    if not token or not chat_id:
        return
    # Pflicht: durch _tg.send routen damit Lint-Alerts im Scratchpad landen
    # (Bauplan=Reparaturplan, jeder Send durch den zentralen Wrapper).
    try:
        from _tg import send as _tg_send
        _tg_send(msg[:4000], source='lint_memory', parse_mode='HTML')
    except Exception:
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data={"chat_id": chat_id, "text": msg[:4000], "parse_mode": "HTML"},
                timeout=10,
            )
        except Exception:
            pass


def main():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    dead_links = lint_dead_links()
    orphans = lint_orphans()
    constitution = lint_constitution()
    onboarding = lint_onboarding()
    drift_tags = lint_open_drift_tags()

    report = render_report(dead_links, orphans, constitution, onboarding, drift_tags)
    REPORT_FILE.write_text(report)
    print(f"Lint-Report: {REPORT_FILE}")
    print()
    print(report)

    # Hash für Change-Detection (Telegram-Notify nur bei neuen Issues)
    import hashlib
    current_hash = hashlib.sha256(report.encode()).hexdigest()
    last_hash = HASH_FILE.read_text().strip() if HASH_FILE.exists() else ""

    if current_hash != last_hash:
        HASH_FILE.write_text(current_hash + "\n")
        # Kurzfassung fuer Telegram
        summary = [
            "🧹 <b>Memory-Lint</b>",
            f"Dead-Links: {len(dead_links)}",
            f"Orphans: {len(orphans)}",
            f"Constitution-Issues: {len(constitution.get('issues', []))}",
            f"Onboarding offen: {len(onboarding.get('unchecked_items', []))}",
            f"Drift-Tags offen: {len(drift_tags)}",
        ]
        telegram_notify("\n".join(summary))


if __name__ == "__main__":
    main()
