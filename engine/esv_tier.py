#!/usr/bin/env python3
"""esv_tier.py — Tier-Klassifikation + Diversifizierung für ESV-Recall.

Gravitationsloch-Fix vom 24.06.2026: zeitlich/auflösungs-gleiche Quellen
duerfen Top-K nicht dominieren. Statt Wochen-Archive aus dem Index zu werfen
(Verlust der Wochen-Ebene des Gedaechtnisses) klassifizieren wir jeden Chunk
in einen Tier (Zeit-/Inhalts-Aufloesung) und erzwingen eine Max-pro-Tier-Quote
beim Top-K-Schnitt. Christian-Doktrin: Recall muss ueber Tage, Wochen, Monate
und Jahre funktionieren — alle Aufloesungen erhalten, keine abgewertet.

Tiers:
  - timeless: Prinzipien, Feedback, Plans, Identity, Infrastructure, Drafts,
              Lessons, RFCs, Auto-Memory, Constitution — kein Datum gebunden
  - day:      memory/episodes/* — Tages-Aufloesung
  - week:     archive/weekly/* — Wochen-Aufloesung (Komprimierung von day)
  - podcast:  podcasts/* — eigenstaendige Werke, datiert aber thematisch
              autonom (nicht Komprimierung anderer Schichten)

Spaeter: month, year wenn entsprechende Archive existieren.
Spaeter: Query-Intent-Erkennung (Zeitmarker -> Tier-Boost) als separater Akt.
"""
from __future__ import annotations


# Max gleichzeitige Treffer pro Tier in Top-K.
# k=3 -> max=2: ein dominanter Tier kann hoechstens 2/3 Slots klauen, der
# andere Slot bleibt fuer eine andere Aufloesung garantiert. Reicht um das
# beobachtete Gravitationsloch (W24 verdraengte principles bei
# "don't trust verify"-Query) zu schliessen ohne Score-Ordering zu erzwingen.
# k=8 -> max=4. Skaliert proportional.
def max_per_tier(k: int) -> int:
    return max(2, (k + 1) // 2)


def classify(file_path: str) -> str:
    """Path im meta.jsonl-Format -> Tier-Label.

    Index-Pfade haben Label-Praefix aus CORPUS_SOURCES:
      memory/...      (motoko-memory/motoko/*)
      podcasts/...    (motoko-server/podcasts/manuscripts/*)
      automemory/...  (motoko-memory/claude-memory/*)
    """
    p = file_path.lower()
    if "archive/weekly/" in p:
        return "week"
    if "/episodes/" in p:
        return "day"
    if p.startswith("podcasts/"):
        return "podcast"
    return "timeless"


def diversify(scored, k: int, file_of):
    """scored: Liste von Tupeln, sortiert nach Score absteigend.
    file_of(item) -> file-path string fuer Tier-Klassifikation.

    Walk durch sortierte Liste, nimm wenn Tier-Quote nicht erschoepft.
    Fallback: wenn Quote alle Kandidaten blockiert und k nicht erreicht ist,
    auffuellen mit den naechstbesten ungenommenen Items (ehrlich bleiben:
    leere Slots sind schlimmer als ein dominierter Tier).
    """
    cap = max_per_tier(k)
    counts: dict[str, int] = {}
    chosen = []
    chosen_keys = set()
    for item in scored:
        tier = classify(file_of(item))
        if counts.get(tier, 0) >= cap:
            continue
        chosen.append(item)
        chosen_keys.add(id(item))
        counts[tier] = counts.get(tier, 0) + 1
        if len(chosen) >= k:
            return chosen
    # Fallback-Fill: Quote hat zu viele blockiert, k nicht erreicht.
    for item in scored:
        if id(item) in chosen_keys:
            continue
        chosen.append(item)
        if len(chosen) >= k:
            break
    return chosen
