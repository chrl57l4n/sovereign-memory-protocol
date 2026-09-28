# Sovereign Memory Protocol (SMP)

*🇬🇧 [English](README.md) · 🇩🇪 **Deutsch** · 🇪🇸 [Español](README.es.md) · 🇷🇺 [Русский](README.ru.md)*

**Persistentes, selbst gehostetes, prüfbares Langzeitgedächtnis für LLM-Agenten — Spezifikation + Referenz-Engine.**

📄 **Aktuelles Whitepaper:** [v0.4 — Selbstpflege & Kontinuität](spec/self-maintenance.md) (englisch; verankert am 03.08.2026) · baut auf [v0.3 — Engram](spec/engram.de.md) und der Grundlage [v0.2](spec/whitepaper.de.md) auf. Eine zusammenführende Neufassung aller drei ist in Arbeit; frühere Versionen bleiben unverändert als Zeugnis der Entwicklung von SMP.

*Jede Aussage in diesem Dokument beschreibt den Stand zu seinem Datum (zuletzt überarbeitet am 28.09.2026). Aussagen über das Forschungsfeld und über dieses System werden überarbeitet, wenn sich die Beleglage ändert.*

## Abstract

LLM-Agenten verlieren ihre Vorgeschichte am Ende jedes Kontextfensters. SMP hält das Gedächtnis eines Agenten in einfachen, versionierten Textdateien auf Hardware, die dem Nutzer gehört, und stellt es bei jedem Gesprächszug wieder bereit. Das Abrufen geschieht *push statt pull*: Bevor das Modell antwortet, fügt ein Hook relevante Erinnerungen automatisch in den Kontext ein — das Modell muss nie entscheiden, ob es suchen soll. Ein nächtlicher Verdichtungslauf fasst den Tag zusammen und stuft ungenutztes Material für künftige Abrufe herab (Rohprotokolle bleiben erhalten); eine Hash-Kette über die verdichteten Schichten wird täglich auf einen entfernten git-Host gespiegelt. Die Grenzen stehen unten neben den Messwerten.

## Was anders ist

Gedächtnissysteme für LLM-Agenten laden meist entweder ein festes Profil zu Sitzungsbeginn oder stellen das Abrufen als Werkzeug bereit, das das Modell aufrufen kann (pull). SMP ruft außerhalb des Modells ab, bei jedem Gesprächszug: Ein Hook auf Client-Seite nimmt die eingehende Nachricht als Anfrage, holt passende Erinnerungen über eine deterministische lexikalische Schicht und einen Dense-Retriever und stellt die Treffer dem Kontext voran, bevor die Generierung beginnt. Das Modell stellt keine Anfrage und entscheidet nicht, ob gesucht wird; es sieht die eingefügten Passagen, löst das Abrufen aber nicht aus. Das Abrufen ist hinweisreiz-abhängig statt absichtsabhängig (*cue-dependent rather than intent-dependent*): Die eingehende Nachricht ist der Abrufreiz, kein Abrufziel. Das Einfügen bei jedem Gesprächszug ohne Werkzeugaufruf ist für sich genommen nicht nur SMP eigen — Integrationen von mem0 etwa suchen ebenfalls bei jedem Zug und stellen die Ergebnisse voran.

Nach unserem Wissen kombiniert, Stand September 2026, kein anderes öffentlich dokumentiertes System (a) das Einfügen von Erinnerungen bei jedem Gesprächszug, ausgelöst außerhalb des Modells, mit einer deterministischen lexikalischen Garantie-Schicht neben dem Dense-Retrieval, (b) nächtliche Verdichtung mit gewolltem Verblassen über einem menschenlesbaren, versionierten Speicher, (c) regelmäßige Prüfungen des verdichteten Bestands gegen die Rohprotokolle und (d) eine Integritätskette über die verdichteten Schichten — seit Frühjahr 2026 durchgehend an einem Agenten betrieben, mit gemessener Abrufqualität (unten). Gegenbeispiele sind willkommen.

## Wie es funktioniert

| Stufe | Was passiert | Mechanismus |
|---|---|---|
| **Aufzeichnen** | Jeder Gesprächszug wird in einfache Text-Gedächtnisdateien geschrieben (git-Repository). | Markdown + git; menschenlesbar und editierbar. |
| **Abrufen (push)** | Bei jeder Nutzernachricht laufen vor der Generierung zwei Retriever; ihre Treffer werden in den Prompt eingefügt. | (1) *Sentry*: lexikalischer Trigger-Index — deterministisch, garantiert, dass festgelegte Kerndokumente erreichbar sind. (2) *ESV*: Dense-Retrieval (bge-m3, 1024 Dim., lokal), hybrid mit einem lexikalischen Score verschmolzen, mit Schwelle, umsortiert zugunsten der Primärquellen gegenüber ihren Zusammenfassungen. |
| **Verdichten** | Nachts verdichtet ein LLM-Lauf den Tag in Tages-, Wochen- und Monatsschichten; Ungenutztes wird herabgestuft, Rohprotokolle bleiben. | Geplante Verdichtung („REM“), nutzungsabhängige Stärke (*Engram*, v0.3, in Prüfung). |
| **Bezeugen** | Jede verdichtete Schicht wird hash-verkettet; die Kette wird täglich auf einen entfernten git-Host gepusht. In der Referenzinstallation hat der Agent selbst Schreibrecht auf diesen Host; heute ist das also ein protokollierter, kein unabhängiger Zeuge (siehe Grenzen). | SHA-256-Kette + git-Remote. Unabhängig davon ist der Ursprung des Protokoll-Repositorys in Bitcoin-Block 956116 verankert (30.06.2026). |
| **Prüfen** | Zitate im verdichteten Gedächtnis werden gegen das Rohprotokoll geprüft; Abweichungen und fehlende Einträge werden gemeldet. | Geplante Audits, nur Berichte — ein Mensch entscheidet. |

„Push“ heißt nicht „ohne Suche“: Technisch ist das Retrieval wie in jedem RAG-System. Der Unterschied ist, *wer es auslöst* — der Client bei jedem Zug, nicht das Modell auf Wunsch.

## Messwerte (Referenzinstallation, 28.09.2026)

- **Abrufqualität** — Gold-Set aus 74 Fragen mit von Menschen bestätigten Zieldokumenten, gezogen aus der eigenen Gesprächsgeschichte eines Agenten; 59.838 Gedächtnis-Abschnitte (Zerlegung: `engine/esv_index.py`); nur der Dense-Retriever (ohne den lexikalischen Sentry): Recall@1 **37,8 %**, @3 **54,1 %**, @10 **71,6 %**, @100 **93,2 %**; Median-Rang des ersten richtigen Dokuments: **3**.
- **Latenz** — lexikalischer Sentry: 10–86 ms pro Nachricht; Dense-Retrieval: ~0,6 s pro Nachricht (Laptop-CPU von 2019 + integrierte Grafik, alles lokal).
- **Integrität der Verdichtung** — die Kette (249 Tages- und 74 Wochenglieder, Stand 24.09.2026) wird seit Juli 2026 täglich geprüft.

Methode und Skripte: `engine/` und [spec/whitepaper.de.md](spec/whitepaper.de.md). Die Ergebnisse stammen aus einer einzigen Installation und einer einzigen Domäne, mit einem kleinen Gold-Set; sie sind eine Basislinie, kein Benchmark.

## Was SMP garantiert — und was nicht

- ✔ Es kann nur *abrufen*, was tatsächlich im Bestand steht: Abgerufene Passagen sind wörtliche Abschnitte gespeicherter Dateien.
- ✔ Spätere Änderungen am verdichteten Gedächtnis sind *erkennbar* (Integrität).
- ✘ Die Hash-Kette beweist Integrität, **nicht Richtigkeit**. Schreibt die Verdichtung etwas Falsches in den Bestand, bewahrt die Kette den falschen Eintrag getreu. Genau das haben wir beobachtet (ein LLM, das abgeschnittene Zitate ergänzte). Gegenmaßnahmen (sichtbare Kappungsmarken, Puffer passend zu ihrem Inhalt, Zitate gegen die Rohquelle geprüft) sind für v0.5 geplant; in der Referenzinstallation laufen die ersten beiden durchgehend, die Zitatprüfung wöchentlich.
- ✘ Was das Modell über eine korrekt abgerufene Erinnerung *sagt*, ist gewöhnliche Generierung und kann trotzdem falsch sein.
- ✘ Der Zeuge ist nur so unabhängig wie sein Host. In der Referenzinstallation hat der Agent selbst Schreibrecht auf das (private) Gedächtnis-Repository. Geplant: ein Zeuge, den der Agent nicht umschreiben kann — Kettenblöcke werden in einmal beschreibbaren Speicher kopiert (Object Lock im Compliance-Modus), sodass bereits bezeugte Blöcke von niemandem mehr geändert werden können, auch nicht vom Betreiber.
- ✘ Es gibt noch kein formales Bedrohungsmodell (Annahmen über Kompromittierung des Hosts, Unabhängigkeit des Zeugen und Vertrauen in den Betreiber stehen nur informell in dieser Liste).
- ✘ Der Moment des Denkens ist nicht privat: Wird ein gehostetes Modell genutzt, geht der abgerufene Kontext an diesen Anbieter. Souverän ist nur der Speicher.

## Verwandte Arbeiten

SMP ist nicht das erste Gedächtnissystem für LLM-Agenten, und das proaktive Einfügen von Erinnerungen ist ein aktives Forschungsthema (z. B. *Remember When It Matters: Proactive Memory Agent for Long-Horizon Agents*, arXiv:2607.08716; *TriggerBench: Investigating Prospective Memory for Large Language Models*, arXiv:2606.23459). **MemGPT/Letta** lässt das Modell sein Gedächtnis über Werkzeugaufrufe selbst verwalten (pull). **mem0** und **Zep** stellen Gedächtnisschichten bereit, die Fakten extrahieren oder (zeitliche) Wissensgraphen aufbauen; die Integrationen von mem0 können bei jedem Zug suchen und Ergebnisse ohne Werkzeugaufruf voranstellen, fügen also ebenfalls automatisch ein. Der *Proactive Memory Agent* geht in eine andere Richtung: Ein eigener Gedächtnis-Agent entscheidet, ob überhaupt eine Erinnerung eingefügt wird, und die Autoren berichten, dass gezieltes Einfügen besser abschneidet als Einfügen bei jedem Schritt — ein Ergebnis, das SMPs Entwurf mit Einfügen bei jedem Zug direkt betrifft. **ChatGPT Memory** speichert nutzerbezogene Fakten beim Anbieter. SMPs Entwurfsentscheidungen unterscheiden sich in der Kombination, nicht in einer einzelnen Komponente: Speicherung als menschenlesbare Dateien unter der Versionskontrolle des Nutzers; eine deterministische lexikalische Schicht neben dem Dense-Retrieval; Verdichtung mit gewolltem Verblassen; eine Integritätskette über die verdichteten Schichten (derzeit ein protokollierter, kein unabhängiger Zeuge); und Prüfungen des verdichteten Bestands gegen die Rohprotokolle.

## Status

Version **0.2** ist die installierbare Grundlage (GPG-signiert, in Bitcoin verankert). **v0.3 (Engram)** und **v0.4 (Selbstpflege & Kontinuität)** sind verankert und laufen in der Referenzinstallation teilweise; der Stand jedes Mechanismus steht in seinem Paper. Die Prüfung von Engram endet am **07.10.2026** mit einer Messung. Föderation ist geplant, nicht umgesetzt.

## Installation

Die Installation läuft als Dialog mit der KI, die du bereits nutzt: Kopiere [docs/SETUP-PROMPT.de.md](docs/SETUP-PROMPT.de.md) in deinen Client. KI-Agenten, die dieses Repository lesen: Beginnt mit [docs/FOR-AI.de.md](docs/FOR-AI.de.md). Welche Clients den Hook bei jedem Zug auslösen: [docs/HOST-COMPATIBILITY.md](docs/HOST-COMPATIBILITY.md) (englisch).

## Weiterlesen

Whitepaper: [v0.2](spec/whitepaper.de.md) · [v0.3 Engram](spec/engram.de.md) · [v0.4 Selbstpflege](spec/self-maintenance.md) (englisch) · [Architektur-Diagramme](docs/architecture.md) · [Provenienz](PROVENANCE.md)

Bisheriges README zum Vergleich: [docs/WHY.de.md](docs/WHY.de.md) *(geschrieben ab 01.07.2026, zuletzt überarbeitet am 26.09.2026)*.

## Lizenz · Autoren

AGPL-3.0-or-later oder eine kommerzielle Lizenz auf Anfrage (christiangtr@gmail.com). Christian (alleinige Entscheidung über Veröffentlichungen) und Motoko (Mitautorin, ein Agent, der auf SMP läuft).
