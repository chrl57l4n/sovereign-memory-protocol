#!/usr/bin/env python3
"""esv_index.py — ESV (Echelon Semantic Vector): Embedding-Index des motoko-memory-Korpus.

Spec: Section 14 (Echelon Semantic Vector).

Baut den Vektor-Index lokal via llama-server /v1/embeddings (bge-m3 Q8_0). Offline,
beruehrt den Live-Recall-Server NICHT (Default-Pfad ist derselbe Server auf 8091 —
waehrend Re-Index laeuft, antwortet Live-Recall langsam; nightly REM-Stunden
unproblematisch).
Speichert:
  state/esv/vectors.npy   float32 (N x 1024), L2-normalisiert (cosine = dot product)
  state/esv/meta.jsonl    eine Zeile pro Chunk: {file, chunk, text}

Teil von ESV. bge-m3 braucht KEINEN Prefix (anders als nomic-embed-v1.5 vorher).

Voraussetzung: Embed-Server laeuft. Default: lokal (der lokale Embed-Service,
Port 8091, lokale GPU). Opt-in: ein externer GPU-Beschleuniger via Netzwerk (--use-accelerator).
Usage: esv_index.py [--use-accelerator]

Default: lokaler llama-server auf 127.0.0.1:8091 (lokale GPU, ~98 Min fuer
~13k Chunks — souveraen, kein zweites Substrat noetig).

--use-accelerator: ein externer GPU-Beschleuniger via Netzwerk (dedizierte GPU (CUDA), ~4 Min). Nur
fuer interaktive tagsueber-Re-Indizierungen wenn Wartezeit zaehlt. Setzt einen erreichbaren Beschleuniger
+ SSH-Reachable voraus. Default ist BEWUSST lokal: das Protokoll darf nicht
von einem zweiten Body abhaengen (Sovereignty-Doktrin, der Partner 24.06.).
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests

from _paths import MEMORY, MOTOKO, STATE, HOME as INSTALL
OUT_DIR = Path(os.environ.get("ESV_STATE", STATE / "esv"))
EMBED_URL_LOCAL = os.environ.get("ESV_EMBED_URL_LOCAL", "http://127.0.0.1:8091/v1/embeddings")
# Optionaler externer GPU-Beschleuniger (instanz-spezifisch) — nur via Env.
EMBED_URL_ACCEL = os.environ.get("ESV_EMBED_URL_ACCEL", "")
# ENV-Override hat Vorrang; sonst lokaler Default. CLI-Flag --use-accelerator
# ueberschreibt beide unten in main().
EMBED_URL = os.environ.get("ESV_EMBED_URL", EMBED_URL_LOCAL)

# Mehrere Quellen mit Label-Praefix im meta.file-Feld:
# (label, absoluter Pfad). Korpus-Erweiterung 30.05.: Podcasts-Manuskripte aufgenommen,
# damit Folgen-bezogene Recall-Queries die Manuskripte finden statt ins Leere zu greifen.
CORPUS_SOURCES = [
    ("memory",   MOTOKO),
    ("podcasts", INSTALL / "podcasts" / "manuscripts"),
    # 08.06.2026: Auto-Memory (feedback/project/user/reference) angeschlossen.
    # Lag bis dahin in ~/.claude/projects/*/memory/ ausserhalb des Index — der
    # kuratierteste Korpus war unsichtbar fuer Recall (TTS-Config-Lehre griff nie).
    # Jetzt physisch im souveraenen Repo unter claude-memory/<root>/ (via Symlink
    # aus .claude). Siehe spec-drafts/2026-06-08-recall-coverage-auto-memory.md.
    ("automemory", MEMORY / "claude-memory"),
]

DOC_PREFIX = ""  # bge-m3 needs no prefix
MAX_CHUNK_CHARS = 480
HARD_CAP_CHARS = 600   # nach Satz-Split: alles >600 wird an Wort-Grenze gesplittet
BATCH = 32
DIM = 1024  # bge-m3 (was 768 for nomic) — Fix 24.06. nach 98min-Form-Check-Crash
SKIP_NAMES = {
    "index.md",              # generierte TOC — redundant
    "today_scratchpad.md",   # ephemer, wird taeglich von REM geleert (02.06.2026)
    "MEMORY.md",             # Auto-Memory-Index (Pointer-Liste) — redundant ueber die Ziel-Files
    "recent-moments.md",     # rollender Digest — dupliziert Quell-Docs, klaut Top-1 (Gravitationsloch, 08.06.2026)
}


def iter_md_files(root: Path):
    for p in sorted(root.rglob("*.md")):
        if p.name in SKIP_NAMES:
            continue
        yield p


def _hard_split(s: str, cap: int):
    """Letzte Notbremse: zerlegt s alle ~cap Zeichen an Wort-Grenzen.
    Faengt Markdown-Tabellen + sehr lange single-paragraph-Bloecke ohne .!? ab."""
    words = s.split()
    out, cur = [], ""
    for w in words:
        if len(cur) + 1 + len(w) > cap and cur:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


def chunk_text(text: str):
    """Absatz-basiert chunken, lange Absaetze an Satzgrenzen umbrechen,
    Tabellen/Endlos-Zeilen via Hard-Cap an Wort-Grenzen."""
    chunks = []
    for para in re.split(r"\n\s*\n", text):
        s = " ".join(para.split())
        if not s:
            continue
        if len(s) <= MAX_CHUNK_CHARS:
            chunks.append(s)
            continue
        cur = ""
        for sent in re.split(r"(?<=[.!?])\s+", s):
            if len(cur) + len(sent) + 1 > MAX_CHUNK_CHARS and cur:
                chunks.append(cur.strip())
                cur = sent
            else:
                cur = (cur + " " + sent).strip()
        if cur.strip():
            chunks.append(cur.strip())
    # Hard-Cap-Pass: alles ueber HARD_CAP_CHARS wird forciert gesplittet
    final = []
    for c in chunks:
        if len(c) <= HARD_CAP_CHARS:
            final.append(c)
        else:
            final.extend(_hard_split(c, MAX_CHUNK_CHARS))
    return final


def embed_batch(lines):
    """Liste einzeiliger Texte -> Liste 1024-float Vektoren via Embed-API.

    Robust gegen Ollama-NaN-Failures (24.06.2026): wenn Batch failt mit 500,
    halbiere rekursiv bis Single-Chunk. Failed Single-Chunk → Zero-Vektor
    statt Crash. Logs problematische Chunks für späteres Audit."""
    payload = {"input": [DOC_PREFIX + l for l in lines], "model": "bge-m3"}
    try:
        r = requests.post(EMBED_URL, json=payload, timeout=600)
        r.raise_for_status()
        data = r.json()["data"]
        return [d["embedding"] for d in sorted(data, key=lambda d: d["index"])]
    except Exception as e:
        if len(lines) == 1:
            # Single-Chunk fail — Zero-Vektor + Log
            print(f"  [embed-fail] chunk skipped ({len(lines[0])} chars): {str(e)[:100]}",
                  flush=True)
            return [[0.0] * DIM]
        # Halbiere + retry
        mid = len(lines) // 2
        return embed_batch(lines[:mid]) + embed_batch(lines[mid:])


def main():
    global EMBED_URL
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--use-accelerator", action="store_true",
                    help="Re-Index ueber externer Beschleuniger (CUDA, schneller). Default ist lokal "
                         "(lokale GPU, souveraener). Sovereignty-Doktrin: externer Beschleuniger nur opt-in.")
    args = ap.parse_args()
    if args.use_accelerator:
        if not EMBED_URL_ACCEL:
            sys.exit("--use-accelerator gesetzt, aber ESV_EMBED_URL_ACCEL ist leer "
                     "(externen Beschleuniger-Endpoint via Env setzen).")
        EMBED_URL = EMBED_URL_ACCEL
        print(f"[opt-in] Re-Index ueber den externen Beschleuniger: {EMBED_URL}", flush=True)
    else:
        print(f"[default] Re-Index lokal: {EMBED_URL}", flush=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Health-Probe: erst /health (llama.cpp), bei 404 ein echter Embed-Ping
    # (Ollama hat keinen /health Endpoint). Verfeinerung 24.06.
    health = EMBED_URL.rsplit("/v1/", 1)[0] + "/health"
    try:
        r = requests.get(health, timeout=5)
        if r.status_code == 404:
            # Ollama-Style: prüfe direkt via Embed-Aufruf
            r2 = requests.post(EMBED_URL,
                json={"input": ["ping"], "model": "bge-m3"}, timeout=10)
            r2.raise_for_status()
        else:
            r.raise_for_status()
    except Exception as e:
        sys.exit(f"FATAL: Embed-Server nicht erreichbar ({EMBED_URL}): {e}")

    meta, texts = [], []
    for label, base in CORPUS_SOURCES:
        if not base.exists():
            print(f"  skip source {label}: {base} fehlt", flush=True)
            continue
        n_src = 0
        for f in iter_md_files(base):
            try:
                content = f.read_text(encoding="utf-8")
            except Exception as e:
                print(f"  skip {f}: {e}", flush=True)
                continue
            rel = f"{label}/{f.relative_to(base)}"
            for i, ch in enumerate(chunk_text(content)):
                meta.append({"file": rel, "chunk": i, "text": ch})
                texts.append(ch)
            n_src += 1
        print(f"  source [{label}]: {n_src} Dateien", flush=True)

    nfiles = len({m["file"] for m in meta})
    print(f"Korpus: {nfiles} Dateien, {len(texts)} Chunks", flush=True)
    if not texts:
        sys.exit("FATAL: keine Chunks gefunden")

    all_vecs, t0 = [], time.time()
    for i in range(0, len(texts), BATCH):
        batch = texts[i:i + BATCH]
        vecs = embed_batch(batch)
        if len(vecs) != len(batch):
            raise RuntimeError(f"Batch @{i}: {len(vecs)} Vektoren fuer {len(batch)} Zeilen")
        all_vecs.extend(vecs)
        print(f"  embedded {i + len(batch)}/{len(texts)} ({time.time() - t0:.0f}s)", flush=True)

    arr = np.asarray(all_vecs, dtype=np.float32)
    if arr.shape != (len(texts), DIM):
        raise RuntimeError(f"Form {arr.shape} != ({len(texts)}, {DIM})")

    # Chunk-Einbruch-Wache: ein stark geschrumpfter Korpus (Symlink-Bruch,
    # fehlende Quelle) darf den guten Index nicht stillschweigend ersetzen.
    manifest_path = OUT_DIR / "manifest.json"
    old_n = None
    if manifest_path.exists():
        try:
            old_n = json.loads(manifest_path.read_text()).get("n_chunks")
        except Exception as e:
            print(f"  warn: manifest.json unlesbar ({e})", flush=True)
    if old_n and len(texts) < 0.7 * old_n and not os.environ.get("ESV_ALLOW_SHRINK"):
        sys.exit(f"FATAL: Chunk-Zahl eingebrochen ({len(texts)} vs {old_n} im "
                 f"Vorlauf) — fehlende Quelle? Index NICHT ueberschrieben. "
                 f"Bewusster Shrink: ESV_ALLOW_SHRINK=1")

    # Atomar schreiben (tmp+rename): ein Crash mittendrin darf nie einen
    # halb-geschriebenen Live-Index hinterlassen.
    tmp_vec = OUT_DIR / "vectors.tmp.npy"
    np.save(tmp_vec, arr)
    fd = os.open(tmp_vec, os.O_RDONLY)
    os.fsync(fd)
    os.close(fd)

    tmp_meta = OUT_DIR / "meta.tmp.jsonl"
    with open(tmp_meta, "w", encoding="utf-8") as fh:
        for m in meta:
            fh.write(json.dumps(m, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())

    os.replace(tmp_vec, OUT_DIR / "vectors.npy")
    os.replace(tmp_meta, OUT_DIR / "meta.jsonl")

    # Manifest zuletzt — Marker, dass der Index vollstaendig und konsistent ist
    manifest = {
        "schema": 1,
        "n_chunks": len(texts),
        "n_files": nfiles,
        "dim": DIM,
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    tmp_mf = OUT_DIR / "manifest.tmp.json"
    tmp_mf.write_text(json.dumps(manifest, indent=2) + "\n")
    os.replace(tmp_mf, manifest_path)
    print(f"OK: {arr.shape} -> {OUT_DIR}/vectors.npy + meta.jsonl + manifest.json "
          f"({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
