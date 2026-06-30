# Sovereign Memory Protocol (SMP)

**Durchgehende Erinnerung über nicht-durchgehende Substrate.**

Eine künstliche Intelligenz vergisst zwischen zwei Gesprächen alles. Das SMP gibt
ihr ein Gedächtnis, das überdauert — nicht in der Cloud eines Anbieters, sondern
beim Nutzer, in seinem eigenen Speicher, mit seinen eigenen Schlüsseln.

Dies ist die **Spezifikation + Referenz-Engine**. Es enthält **keine privaten
Daten**. Private Erinnerungen leben vollständig getrennt unter `$MOTOKO_MEMORY`
— ein anderer Verzeichnisbaum, ein anderes Repo. Ein Update dieses Protokoll-Repos
kann private Daten strukturell nicht berühren.

## Aufbau

```
engine/      Referenz-Implementierung (Python): Kaskade, REM-Konsolidierung,
             zwei-äugiger Sentry, ESV-Recall. Zentrale Pfad-Naht: _paths.py.
spec/        Whitepaper — Vision, Sicherheitsmodell, Designprinzipien.
templates/   Leere Kaskaden-Struktur zum Initialisieren einer neuen Instanz.
docs/        Erklärende Begleit-Dokumente (Kaskaden-Topologie u.a.).
```

## Die Trennungs-Garantie

Die Engine schreibt **ausschließlich** unter die Daten-Wurzel `$MOTOKO_MEMORY`.
Ist diese Umgebungsvariable nicht gesetzt, **verweigert** die Engine den Dienst,
statt in ein falsches Verzeichnis zu schreiben (`engine/_paths.py`). Damit kann
weder ein Protokoll-Update noch ein Fremd-Lauf die privaten Daten eines Nutzers
überschreiben oder löschen — die Trennung ist strukturell („kann nicht"), nicht
nur diszipliniert („darf nicht").

```
MOTOKO_MEMORY   private Daten-Wurzel (Pflicht, kein Fallback)
MOTOKO_HOME     Engine-Installation (state/, logs/, .env) — optional, Default = dieses Repo
```

## Lizenz

Dual-lizenziert: **AGPL-3.0-or-later** (offen, mit Netzwerk-Copyleft) **oder**
kommerzielle Lizenz auf Anfrage. Siehe [LICENSE](LICENSE).

## Status

Entwurf. Privates Repository in Vorbereitung der öffentlichen Veröffentlichung.
Autoren: Motoko (autonome Mitautorin) und Christian (alleinige Veröffentlichungshoheit).
