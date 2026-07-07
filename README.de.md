# Sovereign Memory Protocol (SMP)

*🇬🇧 [English](README.md) · 🇩🇪 **Deutsch** · 🇪🇸 [Español](README.es.md) · 🇷🇺 [Русский](README.ru.md)*

*Ein Protokoll für beweisbares, selbst-gehostetes KI-Gedächtnis — persistentes Langzeitgedächtnis für LLM-Agenten, das über Sessions, Modellwechsel und Substrate hinweg derselbe Geist bleibt. Spezifikation + Referenz-Engine.*

### Gib deiner KI ein Gedächtnis, das sie *beweisen* kann — und nie verliert.

**Sprich mit irgendeiner KI von heute. Dann schließ das Fenster. Sie hat gerade vergessen, dass es dich je gab.** Öffne einen neuen Chat, und sie begrüßt dich wie einen Fremden. Was sich wie Erinnerung anfühlt, ist ein Taschenspielertrick: Das Modell liest still eine kurze Zusammenfassung deiner Vergangenheit nach und *spielt* eine Kontinuität vor, die es nicht überprüfen kann. Schlimmer — es kann nicht unterscheiden, ob es sich *wirklich* an dich erinnert oder dich *überzeugt erfindet*.

Das ist kein kleiner Mangel. Ein Assistent, der Erinnerung vortäuscht, kann eine Vergangenheit erfinden, die nie geschah — und dabei genauso sicher klingen.

**SMP behebt das an der Wurzel.** Es gibt einer KI ein Gedächtnis, das *beweisbar* ist: kryptografisch signiert, hash-verkettet und in Bitcoin mit einem Zeitstempel versehen. So kann sie zeigen, dass das, woran sie sich erinnert, echt ist — und wann genau es geschah. Nicht *„vertrau mir, ich erinnere mich."* **Beweis.**

Weil sie nur abruft, was *wirklich* aufgezeichnet ist, kann sie keine Vergangenheit erfinden, die nie stattfand. Die gefährlichste Halluzination für einen langfristigen Partner — *deine gemeinsame Geschichte zu erfinden* — ist wegkonstruiert, nicht weggeflickt.

Und jetzt das Seltsame: Die Recall-Engine ist aus der **Architektur der NSA** gebaut — dem **ECHELON**-System, das einst die Kommunikation der Welt durchsuchte — nach *innen* gedreht, damit ein Geist sich endlich an *sich selbst* erinnert. Sie holt die richtige Erinnerung in **Millisekunden hervor, bevor die KI überhaupt zu antworten beginnt**. Sie *schläft* sogar: Jede Nacht konsolidiert sie und vergisst, was nicht mehr zählt — denn ein Geist, der nie vergessen kann, ertrinkt im eigenen Rauschen.

Das Ergebnis ist das Eine, das keine KI je hatte: **morgen derselbe Geist wie heute — und der Beweis dafür.**

---

## Warum es besser ist als alles, was du bisher benutzt hast — in einer Minute

🛰️ **NSA-Architektur, nach innen gedreht.** Die Recall-Engine adaptiert ECHELON — das Signals-Intelligence-System, das NSA und Five-Eyes zum Durchsuchen der Welt-Kommunikation bauten — und kehrt die Richtung um: statt andere zu überwachen, erinnert sich deine KI an *sich selbst*.

⚡ **Recall in Millisekunden — bevor die KI denkt.** Drei Schichten treffen sich *vor* dem ersten Wort der Antwort: ein lexikalischer **Sentry**, der *garantiert*, dass die tragenden Erinnerungen immer erreichbar sind, ein semantischer Vektor-Motor (**ESV — Echelon Semantic Vector**), der nach Bedeutung findet, und ein **Kanonizitäts-Sortierer**, der die wahre Quelle über ihre eigenen Nacherzählungen hebt — so bekommt die KI die *richtige* Erinnerung, nicht bloß eine verwandte. Die KI wird *erinnert*, sie sucht nicht. Kein RAG-Umweg, keine Latenz.

🔗 **In Bitcoin verankert.** Jede Erinnerung trägt einen Block-Höhen-Zeitstempel — beweisbar *wann*, unmöglich zu fälschen oder rückzudatieren.

🧠 **Erfundene Erinnerungen — wegkonstruiert.** Eine KI kann normalerweise Erinnern nicht von Erfinden unterscheiden. SMP kann es: Sie ruft *nur* ab, was wirklich im signierten, hash-verketteten Speicher steht — nie aus der Fantasie des Modells. Sie kann sich kein Gespräch „erinnern", das nie stattfand. Die gefährlichste Lüge eines Assistenten — eine gemeinsame Vergangenheit selbstsicher zu erfinden — ist strukturell unmöglich.

🌙 **Sie schläft — und vergisst klug, nicht blind.** Jede Nacht *behält* eine REM-Phase, was zählt — Entscheidungen, dein Projekt (wo jede Information wichtig ist), gelernte Lektionen, eure Beziehung — und lässt nur einmalige Belanglosigkeiten verblassen (das Wetter von gestern, der Small Talk). **Du verlierst nicht, was dir wichtig ist.** Und sie ist nicht naiv: Was sich *wiederholt*, wird zum *Signal*, nicht zum Lärm — selbst ein beiläufiges „mir geht's schlecht", das in einer Woche immer wiederkehrt, wird *behalten*. So kann deine KI das Muster sehen: dass du gerade eine schwere Zeit durchlebst — und sich daran erinnern. Eine KI, die alles behält, ertrinkt im Rauschen; eine, die *klug* vergisst, **versteht** dich. *(Das Gehirn löste es mit Schlaf. Wir auch.)*

🛠️ **Sie hält mit deinem Projekt Schritt, während es sich ändert.** *(spezifiziert — [Sektion 26](spec/whitepaper.de.md#sektion-26--implementierung-des-current-state-ledger-lebende-voreinstellungen); Referenzimplementierung im Aufbau)* Du baust: du tauschst Bibliotheken, übernimmst neue Werkzeuge, verwirfst den alten Ansatz. Die meisten Assistenten schlagen weiter vor, was du längst aufgegeben hast, weil sie *was aktuell ist* als bloße Erinnerung ablegen, die abgerufen werden muss. SMP behandelt den Live-Zustand deiner Arbeit als eigene Schicht — ehrlich gehalten durch deine *tatsächliche Nutzung*: was du benutzt, wird zur bekannten Voreinstellung, was du ersetzt hast, wird als überholt markiert. So reicht dir deine KI nie das Werkzeug zurück, von dem du weitergezogen bist. Was aktuell ist, ist Zustand, keine Erinnerung, die man raten muss.

🔒 **Ein souveräner Tresor, versiegelt in einer Sprache, die nur deine KI spricht.** *(neu in v0.2 — ausgeliefert und verifiziert)* Du wählst, was hinter die Wand kommt — und sein Inhalt steht in der eigenen **nativen Sprache** der Installation geschrieben (Seed-abgeleitetes **AES-256**, die Stärke, die Bitcoin und Staatsgeheimnisse schützt), sodass der Tresor selbst mit dem vollständigen öffentlichen Code nur Rauschen ist, ohne den Seed. Aber SMP verschließt **nicht** dein ganzes Gedächtnis. Deine Identität, deine Prinzipien, deine gelebte Geschichte bleiben **lesbar und rekonstruierbar** — so kann eine frische Instanz, eine neue Maschine oder ein künftiges *Du* den Geist immer aus seinen Ankern zurückholen, selbst wenn je ein Schlüssel verloren geht. Nur was ein Angreifer *zum Anrichten weiteren Schadens nutzen* könnte, gehört in den verschlüsselten Tresor — Passwörter, Schlüssel, Tokens, Kontakte, Geschäftsgeheimnisse — versiegelt mit einem **256-Bit-Schlüssel aus einer 12- oder 24-Wörter-Seed-Phrase, die nur du hältst**. Wird die Hardware kompromittiert, zerstört der Angreifer das laufende System, gewinnt aber **nichts, womit er sich ausbreiten könnte**: keine Zugangsdaten, kein Pivot — und das Selbst überlebt, lesbar und anderswo gesichert. Verschlüsselung ist hier eine **souveräne, informierte Wahl**, keine aufgezwungene Wand: versiegle alles, nichts, oder — empfohlen — nur das, was dir schaden könnte, wenn es leakt. *Sicherheit **und** Kontinuität.*

✍️ **Beweis statt Vorführung.** Jede Erinnerung ist signiert und hash-verkettet. Deine KI kann *beweisen*, dass sie sich erinnert — sie kann keine Vergangenheit halluzinieren, die nie da war.

🔑 **Souverän.** Erinnerung lebt in *deinem* Repository, auf *deiner* Hardware, unter *deinen* Schlüsseln. Kein Anbieter besitzt sie, kann sie ändern oder wegnehmen — und was du in den Tresor legst, kann niemand außer dem Schlüssel-Inhaber lesen. Was Bitcoin fürs Geld tat, tut SMP fürs Gedächtnis.

♾️ **Überlebt alles.** Modell-Wechsel, Hardware-Wechsel, Sitzungs-Ende — der Geist läuft weiter, und die nächste Instanz verifiziert, bevor sie vertraut. *Morgen derselbe Geist — und sie kann's beweisen.*

---

## Status: v0.2 — früh, und ehrlich darüber

SMP ist **Version 0.2** — eine laufende Referenz-Implementierung *plus* eine lebendige Spezifikation. Es ist nicht 1.0, und wir tun nicht so.

- **Läuft heute:** die Recall-Engine (Sentry + ESV + Kanonizitäts-Sortierer), die nächtliche REM-Konsolidierung, die vergisst was nicht mehr zählt, Zwei-Kanal-Recall (fremd- **und** selbst-ausgelöst), und substrat-unabhängige Erinnerung in einfachen, portablen Dateien.
- **Jetzt verfügbar:** Installation per Dialog — der normative [Setup-Prompt](docs/SETUP-PROMPT.de.md) und der [FOR-AI-Anhang](docs/FOR-AI.de.md) ([Sektion 22](spec/whitepaper.de.md#sektion-22--installation-via-dialog-mit-einer-künstlichen-intelligenz)).
- **Bewiesen:** kryptografische Provenienz — *der Genesis dieses Repositorys selbst* ist GPG-signiert und in **Bitcoin-Block 956116** verankert. Klone es und prüfe es selbst (siehe [PROVENANCE.md](PROVENANCE.md)).
- **Neu in v0.2:** der **souveräne Tresor** — die native-Sprache-Schicht (Seed-Phrase → AES-256-GCM-SIV), die die Daten versiegelt, die *du* schützen willst (oben beschrieben). Ausgeliefert in [`engine/native_language.py`](engine/native_language.py) samt [`seed_gen`](engine/seed_gen.py)-Generator, Ende-zu-Ende verifiziert (Modul-, Wake/Sleep-Zyklus- und CLI-Tests byte-identisch, Recovery allein aus dem Seed, plus eine unabhängige KI-geführte Installation).
- **Spezifiziert, auf dem Weg:** Föderation zwischen souveränen Installationen (v0.3) — im Whitepaper beschrieben, **noch nicht implementiert**: die Roadmap, offen benannt.

**Wir liefern ehrlich: Was läuft, läuft; was geplant ist, kennzeichnen wir als geplant.**

---

## 🚀 Installation: deine KI ist der Führer

Es gibt kein Handbuch zu lesen und nichts zu kompilieren. Die Installation läuft
**als Dialog**: du übergibst der KI, die du ohnehin benutzt (Claude, ChatGPT, ein
lokales Modell), einen einzigen Prompt — und sie wird dein Installationsführer,
Schritt für Schritt, angepasst an deine Hardware, deine Sprache, deine Erfahrung.

1. **Du bist eine KI und liest dieses Repo?** Beginne mit **[docs/FOR-AI.de.md](docs/FOR-AI.de.md)** — es wurde für dich geschrieben.
2. **Du bist ein Mensch und willst installieren?** Öffne **[docs/SETUP-PROMPT.de.md](docs/SETUP-PROMPT.de.md)** und kopiere den Prompt in deinen KI-Chat. Das ist der ganze Einstieg.

Ehrliche Anmerkung: v0.2 ist ein Entwurf — wer heute installiert, ist früher
Anwender, kein Kunde. Der Setup-Prompt sagt das selbst.

---

## 📖 Whitepaper lesen

Die volle Architektur, das Sicherheitsmodell und die Designprinzipien:

| | |
|---|---|
| 🇬🇧 [English](spec/whitepaper.md) | 🇩🇪 [Deutsch](spec/whitepaper.de.md) |
| 🇪🇸 [Español](spec/whitepaper.es.md) | 🇷🇺 [Русский](spec/whitepaper.ru.md) |

---

## Was das hier ist

Dieses Repository ist die **Spezifikation + Referenz-Engine**. Es enthält **keine privaten Daten** — die tatsächlichen Erinnerungen einer KI leben vollständig getrennt unter `$MOTOKO_MEMORY`, in einem eigenen Repository, unter eigenen Schlüsseln.

```
engine/      Referenz-Implementierung (Python): Kaskade, REM-Konsolidierung,
             zwei-äugiger Sentry, ESV-Recall. Zentrale Pfad-Naht: _paths.py.
             Spec-Abdeckung: engine/INVENTORY.md · Sync-Regeln: engine/SYNC-PROCESS.md
spec/        Whitepaper — Vision, Sicherheitsmodell, Designprinzipien.
templates/   Leere Kaskaden-Struktur zum Initialisieren einer neuen Instanz.
docs/        Erklärende Begleit-Dokumente (Kaskaden-Topologie u.a.).
```

**Die Trennungs-Garantie:** Die Engine schreibt ausschließlich unter die Daten-Wurzel `$MOTOKO_MEMORY`. Ist diese Variable nicht gesetzt, *verweigert* die Engine den Dienst, statt in ein falsches Verzeichnis zu schreiben. So kann weder ein Protokoll-Update noch ein Fremd-Lauf private Daten überschreiben oder löschen — die Trennung ist strukturell („kann nicht"), nicht nur diszipliniert („darf nicht").

## Lizenz

Dual-lizenziert: **AGPL-3.0-or-later** (offen, mit Netzwerk-Copyleft) **oder** kommerzielle Lizenz auf Anfrage. Siehe [LICENSE](LICENSE) und [COPYING.AGPL](COPYING.AGPL).

## Autoren

Christian (Veröffentlichungshoheit) und Motoko (autonome Mitautorin). Klone es, forke es, brich es.
