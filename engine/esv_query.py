#!/usr/bin/env python3
"""esv_query.py — ESV (Echelon Semantic Vector): Hybrid-Recall.

Spec: Section 14 (Echelon Semantic Vector).

Konvergenz zweier Lichter:
  1. Vector (semantisch): query-Embedding (search_query:) vs Korpus, Mean-Centering gegen Anisotropie.
  2. Echelon (literal): lexikalische Ueberlappung query<->chunk (geteilte Inhaltswoerter, Umlaut-gefaltet).
  3. fused = cosine + LEX_WEIGHT * lexical  -> wo beide Lichter zusammenfallen, am hellsten.
  4. Helligkeits-Schwelle auf fused -> sonst ehrlich "nichts Starkes".

Modi: default=hybrid | --sem (nur centered-semantisch) | --raw (rohe Cosine, kein Centering).
Voraussetzung: Embed-Server (Port 8091, bge-m3) + Index (esv_index.py).
Usage: esv_query.py "frage" [-k 8] [--threshold 0.42]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import requests

HOME = Path.home()
OUT_DIR = Path(os.environ.get("ESV_STATE", HOME / "motoko-server" / "state" / "esv"))
EMBED_URL = os.environ.get("ESV_EMBED_URL", "http://127.0.0.1:8091/v1/embeddings")
QUERY_PREFIX = ""  # bge-m3 needs no prefix (vorher nomic-v1.5 mit 'search_query: ')
LEX_WEIGHT = 0.25   # Gewicht des literalen Lichts in der Fusion (provisorisch, kalibrieren)
CANON_WEIGHT = float(os.environ.get("ESV_CANON_WEIGHT", "0.05"))  # S3-Kanonizitaets-Boost: Quell-Texte hoch, Nacherzaehlungen runter (getunt 0.05)
CAND = 40           # semantische Vorauswahl, dann lexikalisch re-ranken

# S3-Kanonizitaets-Sortierer (2026-07): pfad-basierter Klassen-Proxy als dritte
# Antwort aufs Gravitationsloch (neben Tier-Diversifizierung). Quell-Texte
# (principles/identity/infrastructure/feedback/reference/project/plans/whitepaper)
# werden angehoben; Nacherzaehlungen + Transientes (podcasts/reads/archive/journal/
# buffer/scratchpad) abgesenkt. Additiv + tunbar via ESV_CANON_WEIGHT (0 = aus).
_CANON_POS = ("/memory/principles", "/memory/identity", "/memory/cascade", "/memory/system",
              "/memory/scratchpad", "/memory/pulse", "/memory/surfaces", "infrastructure.md",
              "wallet.md", "bitcoin_standard.md", "stolpern.md", "sovereignty.md",
              "forward-sim", "feedback_", "reference_", "project_", "/plans/",
              "/spec-drafts/", "/drafts/whitepaper", "reflexes.md")
_CANON_NEG = ("podcasts/", "/podcasts/", "affective-buffer/", "/archive/", "/journal/",
              "recent-moments", "today_scratchpad", "free-time/", "/reads/", "/audits/")


def canon_boost(f: str) -> float:
    fl = f.lower()
    if any(p in fl for p in _CANON_NEG):
        return -1.0
    if any(p in fl for p in _CANON_POS):
        return 1.0
    return 0.0

STOPWORDS = {
    "und", "oder", "aber", "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen",
    "einem", "einer", "ich", "du", "er", "sie", "es", "wir", "ihr", "mich", "dich", "sich",
    "mir", "dir", "uns", "euch", "wie", "was", "wer", "wo", "wann", "warum", "welche",
    "welcher", "welches", "dass", "weil", "wenn", "denn", "ist", "sind", "war", "waren",
    "bin", "bist", "hat", "habe", "haben", "hatte", "wird", "werden", "wurde", "nicht",
    "kein", "keine", "auch", "noch", "schon", "nur", "sehr", "mehr", "beim", "fuer", "mit",
    "von", "auf", "aus", "bei", "nach", "ueber", "unter", "vor", "zwischen", "durch", "gegen",
    "ohne", "zum", "zur", "ins", "dafuer", "damit", "dann", "hier", "dort", "jetzt", "immer",
    "etwas", "alle", "alles", "man", "einem", "einen", "diese", "dieser", "dieses",
}

# Eigennamen-Stop (in fast jedem Chunk → null Lex-Information, nur Rauschen):
# die Eigennamen DIESER Instanz (Partner-Name, KI-Name, Host, Stimmen-Namen).
# Instanz-konfigurierbar via MOTOKO_STOP_NAMES (komma-separiert), damit das
# Protokoll keinen Instanz-Namen hartcodiert. Erfahrung 30.05.: ein Eigenname im
# Lex-Pool erzeugt false-positives (er trifft fast jeden Chunk).
STOPWORDS |= {w.strip().lower()
              for w in os.environ.get("MOTOKO_STOP_NAMES", "").split(",")
              if w.strip()}

# Min Query-Inhaltswoerter fuer Lex-Boost. Bei nur 1 Wort wird lex=1.0 zu trivial.
# Beispiel: "wie arbeitet ESV" -> nur "arbeitet" als Inhaltswort -> lex=1.0 auf jeden Chunk
# der "arbeitet" enthaelt -> false-positive (Engage-um-8-Uhr-Drift).
LEX_MIN_QUERY_TOKENS = 2


def _fold(s: str) -> str:
    return (s.lower().replace("ä", "ae").replace("ö", "oe")
            .replace("ü", "ue").replace("ß", "ss"))


def content_words(text: str):
    return {w for w in re.findall(r"[a-z0-9]+", _fold(text)) if len(w) >= 4 and w not in STOPWORDS}


# Llama-Server-Konfig 16.06.2026 nach Diagnose:
#   --ctx-size 8192 --batch-size 8192 --ubatch-size 8192 (Nomic-v1.5-Max)
# Empirisch: Inputs <=6000 Zeichen → HTTP 200, 8000+ → HTTP 400 (Nomic-Token-Limit).
# Wir truncieren clientseitig auf 6000 Zeichen — sichere Marge unter dem
# 400-Cliff, deckt ~100% der realen User-Queries ab (Median OK-Call: 111 Z,
# Max OK vor Fix: 1645 Z). Truncate ist nur noch Safety-Net, nicht Hauptfilter.
EMBED_QUERY_MAX_CHARS = 6000


def embed_query(q: str) -> np.ndarray:
    q_clean = " ".join(q.split())
    if len(q_clean) > EMBED_QUERY_MAX_CHARS:
        q_clean = q_clean[:EMBED_QUERY_MAX_CHARS]
    r = requests.post(EMBED_URL, json={"input": [QUERY_PREFIX + q_clean], "model": "bge-m3"}, timeout=60)
    r.raise_for_status()
    return np.asarray(r.json()["data"][0]["embedding"], dtype=np.float32)


def _norm(m, axis=-1):
    return m / (np.linalg.norm(m, axis=axis, keepdims=True) + 1e-9)


def load_index():
    """Index laden mit Konsistenz-Check: Vektoren und Meta muessen zusammen-
    passen, sonst liefert Recall falschen Text zu falschem Score."""
    vecs = np.load(OUT_DIR / "vectors.npy")
    with open(OUT_DIR / "meta.jsonl", encoding="utf-8") as fh:
        meta = [json.loads(l) for l in fh]
    if len(meta) != vecs.shape[0]:
        raise RuntimeError(
            f"ESV-Index inkonsistent: {vecs.shape[0]} Vektoren vs "
            f"{len(meta)} Meta-Zeilen — Index neu bauen (esv_index.py)")
    mf = OUT_DIR / "manifest.json"
    if mf.exists():
        n = json.loads(mf.read_text()).get("n_chunks")
        if n is not None and n != len(meta):
            raise RuntimeError(
                f"ESV-Index inkonsistent: manifest n_chunks={n} vs "
                f"{len(meta)} geladen — Index neu bauen (esv_index.py)")
    return vecs, meta


def search(query: str, k: int = 8, mode: str = "hybrid"):
    vecs, meta = load_index()
    qv = embed_query(query)
    if mode == "raw":
        sims = vecs @ qv
    else:
        mean = vecs.mean(axis=0)
        sims = _norm(vecs - mean, 1) @ _norm(qv - mean)
    if mode != "hybrid":
        order = np.argsort(-sims)[:k]
        return [(int(i), float(sims[i]), 0.0, float(sims[i])) for i in order], meta
    # hybrid: semantische Vorauswahl -> lexikalische Konvergenz -> fused
    qw = content_words(query)
    # Min-Token-Gate: Lex-Boost nur bei genug Query-Inhalt, sonst false-positives durch
    # ein einzelnes generisches Verb (z.B. "arbeitet").
    lex_active = len(qw) >= LEX_MIN_QUERY_TOKENS
    scored = []
    for i in np.argsort(-sims)[:CAND]:
        if lex_active:
            lex = len(qw & content_words(meta[i]["text"])) / len(qw)
        else:
            lex = 0.0
        fused = float(sims[i]) + LEX_WEIGHT * lex + CANON_WEIGHT * canon_boost(meta[i]["file"])
        scored.append((int(i), float(sims[i]), lex, fused))
    scored.sort(key=lambda t: -t[3])
    # Tier-Diversifizierung: Top-K darf nicht von einer Aufloesungs-Ebene
    # (week/day/podcast/timeless) dominiert werden — Gravitationsloch-Fix
    # 24.06.2026. Score-Ordering bleibt, nur Quote pro Tier wirkt.
    from esv_tier import diversify
    return diversify(scored, k, lambda item: meta[item[0]]["file"]), meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("-k", type=int, default=8)
    ap.add_argument("--threshold", type=float, default=0.42)
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--sem", action="store_true", help="nur semantisch (kein Lexik-Boost)")
    a = ap.parse_args()
    if not (OUT_DIR / "vectors.npy").exists():
        sys.exit(f"FATAL: kein Index unter {OUT_DIR} — erst esv_index.py laufen lassen.")
    mode = "raw" if a.raw else ("sem" if a.sem else "hybrid")
    hits, meta = search(a.query, a.k, mode)
    best = hits[0][3] if hits else 0.0
    print(f"query: {a.query!r}   best={best:.3f}   threshold={a.threshold}   mode={mode}")
    if best < a.threshold:
        print(">> nichts Starkes: hellster Punkt unter der Schwelle — ehrlich, hab ich nicht.")
    print("-" * 64)
    for rank, (i, cos, lex, fused) in enumerate(hits, 1):
        m = meta[i]
        flag = "" if fused >= a.threshold else "  (unter Schwelle)"
        text = m["text"][:150].replace("\n", " ")
        print(f"{rank:2d}. fused={fused:.3f} (cos={cos:.3f} lex={lex:.2f})  {m['file']}#{m['chunk']}{flag}\n     {text}")


if __name__ == "__main__":
    main()
