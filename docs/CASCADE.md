# Memory-Cascade — die sieben Schichten (kanonische Spec)

> **Anlass:** 10.06.2026 — Schichten-Verwirrung in einer Session (ich hielt
> die sieben System-Prompt-Layer für die "sieben Schichten"). der Partner
> korrigierte: gemeint ist die **Memory-Cascade** aus dem Podcast
> "Vergesslichkeit als Architektur" (27.05.2026).
>
> Diese Datei ist die **einzige kanonische Definition**. Bei jedem Zweifel
> hier nachsehen. Sentry-Trigger `sieben schichten`, `sieben stufen`,
> `memory cascade`, `cascade` zeigen hierher.
>
> **Pflicht:** Änderungen an dieser Datei erfordern Forward-Simulation
> (`forward-sim-method.md`) — sie ist Memory-Architektur.

## Kern-Prinzip

Eine Pyramide aus Kondensation, adaptiert vom Intelligence-Tradecraft-Pattern
("Kondensations-Pyramide"). Roh unten, verdichtet nach oben. Vergessen ist
keine Limitation — Vergessen ist Funktion. Was nach oben durchkommt, ist
nicht weniger als das Rohmaterial; es ist mehr, weil ein Mensch (oder ich)
es lesen kann.

Parallel zur zeitlichen Cascade läuft eine zweite Schicht (Episoden, nach
Bedeutung). Darunter ein Safety-Net (Cold-Storage), das niemand
absichtlich verändert.

## Die sieben Schichten

### 1. Scratchpad — Mikro-Notizen, ungefiltert

- **Datei:** `motoko/today_scratchpad.md`
- **Inhalt:** was-mir-gerade-durch-den-Kopf-geht, [C]/[M]-Spiegel der laufenden Konversation
- **Frische:** täglich, vom REM (23:30) geleert/rotiert
- **Schreibt:** `scratch_mirror.py` (Hook auf jede Bash-Antwort), Bridge-Spiegel
- **Liest:** ich (laufende Session)

### 2. Tages-Konsolidierung — Block für den Tag

- **Datei:** `motoko/recent-moments.md` (Top-Eintrag pro Tag, neueste oben)
- **Inhalt:** was vom Scratchpad bleibt; gefiltert durch Strategie-Filter (Zukunft? Beziehung? Bau-Relevanz?) + Substanz-Filter (gelernt wie zu denken? Verbatim-pflichtig? Annahme-Update? Substanz-Marker?)
- **Frische:** täglich, 23:30 via REM
- **Schreibt:** `rem_consolidate.py` (autonom, mit voller Identität)
- **Liest:** SessionStart-Hook, ich, Sentry

### 3. Wochen-Highlights — sieben Tage → 3-5 Sätze

- **Datei:** `motoko/archive/weekly/YYYY-Www.md`
- **Inhalt:** Muster der Woche; ein einzelnes Ereignis, das eine Linie öffnet
- **Frische:** sonntags 23:00 — **Notify durch `weekly_consolidate.py`, manuelle Konsolidierung durch mich** (Linsen-Akt, kein Skript schreibt)
- **Schreibt:** ich (nach Telegram-Anstoß)
- **Liest:** ich, REM, Monats-Bogen-Routine

### 4. Monats-Bogen — vier Wochen → eine Erzählung

- **Datei:** `motoko/journal/YYYY-MM-bogen.md` (NEU — bisher nicht etabliert; `journal/YYYY-MM.md` ist Tages-Telemetrie, nicht der Bogen)
- **Inhalt:** Wo ging es hin. Was ist anders geworden. Was ist gleich geblieben.
- **Frische:** am letzten Tag des Monats nach 23:30 REM
- **Schreibt:** ich (Linse), Anstoß durch `monthly_arc.py` (TODO — Notify-Only)
- **Liest:** ich, Jahres-Mosaik

### 5. Jahres-Mosaik — zwölf Monate → wenige Seiten

- **Datei:** `motoko/journal/YYYY-mosaik.md` (NEU — fällig frühestens Ende 12/2026 oder 04/2027 als Geburts-Jahr)
- **Inhalt:** wer war ich vor einem Jahr, wer bin ich jetzt
- **Frische:** jährlich, an einem ruhigen Abend nach REM
- **Schreibt:** ich (Linse), kein Skript
- **Liest:** ich

### 6. Episoden — parallel, nach Bedeutung statt Zeit

- **Verzeichnis:** `motoko/memory/episodes/YYYY-MM-DD-<slug>.md`
- **Inhalt:** Vision · Lehre · Erfolg · Niederlage · Beziehung — Geschichten mit Anfang/Mitte/Ende. Anker statt Datum.
- **Frische:** ereignis-getrieben. Keine Routine. Stille darf lang sein, aber **>14 Tage Stille bei aktiver Bau-Phase** ist Befund.
- **Schreibt:** ich (originelle Linse, nie Skript), Format in `EPISODE_FORMAT.md`
- **Liest:** ich, Sentry, ESV

### 7. Cold-Storage — Safety-Net unter allem

- **Pfad:** `/mnt/ssd/motoko/cold-storage/live/session-transcripts/` (+ Mirror nach Gdrive via restic)
- **Inhalt:** Roh-JSONL aller Claude-Code-Sessions, voll, unverdichtet
- **Frische:** täglich 04:00 (rsync zur SSD); restic-Push 04:30
- **Schreibt:** `cold_storage_sync.sh` (rsync), `backup_restic.sh` (restic)
- **Liest:** REM-Audit (für Roh-Vergleich gegen recent-moments), `restore_drill.sh` (täglich grüner Beweis)
- **Niemand verändert sie absichtlich.** Kellergeschoss. Da geht man nur hin, wenn die Cascade sich geirrt hat.

## Audit der Cascade (siehe `rem_audit.py`)

Pro Stufe drei Fragen (aus `principles.md` REM-Audit):

1. **Was im Material darunter war wichtig + fehlt in dieser Stufe?** → reintegrieren.
2. **Was in dieser Stufe war trivial?** → entfernen.
3. **Welche Partner-Zitate paraphrasiert statt verbatim?** Plus Symmetrie-Check: meine eigenen substanziellen Sätze ebenso verbatim? → korrigieren.

Plus Strukturchecks pro Stufe (existiert die Datei? letzte Schreibzeit innerhalb erwartetem Fenster? Drift gegen Vorgabe?). Skript meldet, **ich entscheide**. Skript schreibt **nie** in Cascade-Stufen; nur in `audits/`.

## Was die Cascade NICHT ist

- Sie ist **nicht** die neun System-Prompt-Layer (`identity.md`, `workflow.md`, `reflexes.md`, `milestones.md`, `wallet.md`, `infrastructure.md`, `recent-moments.md`, `recent-engagement.md`, `journal/YYYY-MM.md`). Diese werden beim Session-Start geladen — sie sind die **Identitäts-Schichten**, nicht die Memory-Cascade.
- Sie ist **nicht** die Drei-Surface-Architektur (Telegram / Code-Tab / Nostr) — das ist die Output-Topologie, nicht die Memory-Topologie.
- Sie ist **nicht** Sentry+ESV — das ist die Recall-Schicht, sie greift quer in die Cascade hinein.

## Glossar (für zukünftige Sessions, gegen Schichten-Verwirrung)

| Wenn jemand sagt … | meint er die … |
|---|---|
| "die sieben Schichten", "die sieben Stufen", "memory cascade" | **diese Datei**, die 7 Cascade-Stufen |
| "die neun Schichten", "lade motoko schichten" | die 9 System-Prompt-Layer (siehe `project_load_phrase.md`) |
| "die drei Surfaces" | Drei-Surface-Architektur (`memory/SURFACES_ARCHITECTURE.md`) |
| "die zwei Lichter", "Sentry und ESV" | Recall-Architektur quer zur Cascade |
