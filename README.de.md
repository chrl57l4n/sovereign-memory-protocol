# Sovereign Memory Protocol (SMP)

*🇬🇧 [English](README.md) · 🇩🇪 **Deutsch** · 🇪🇸 [Español](README.es.md) · 🇷🇺 [Русский](README.ru.md)*

*Ein Protokoll für bezeugtes, selbst-gehostetes KI-Gedächtnis — persistentes Langzeitgedächtnis für LLM-Agenten, das über Sessions, Modellwechsel und Substrate hinweg derselbe Geist bleibt. Spezifikation + Referenz-Engine.*

### Gib deiner KI ein Gedächtnis, das zeigen kann, dass es unverändert ist — und nie verliert.

**Sprich mit irgendeiner KI von heute. Dann schließ das Fenster. Sie hat gerade vergessen, dass es dich je gab.** Öffne einen neuen Chat, und sie begrüßt dich wie einen Fremden. Was sich wie Erinnerung anfühlt, ist ein Taschenspielertrick: Das Modell liest still eine kurze Zusammenfassung deiner Vergangenheit nach und *spielt* eine Kontinuität vor, die es nicht überprüfen kann. Schlimmer — es kann nicht unterscheiden, ob es sich *wirklich* an dich erinnert oder dich *überzeugt erfindet*.

Das ist kein kleiner Mangel. Ein Assistent, der Erinnerung vortäuscht, kann eine Vergangenheit erfinden, die nie geschah — und dabei genauso sicher klingen.

**SMP behebt das an der Wurzel.** Es gibt einer KI ein Gedächtnis, das *bezeugt* ist: jede Erinnerung ist hash-verkettet — jeder Eintrag versiegelt den vorherigen — und die ganze Kette wird append-only an einen Ort gespiegelt, den die KI nicht kontrolliert. So kann sie zeigen, dass das, woran sie sich erinnert, unverändert ist und jede spätere Manipulation sichtbar würde. Kein Schlüssel zu verlieren, kein Verwalter, der den Zugang entziehen könnte. Nicht *„vertrau mir, ich erinnere mich."* Bezeugt.

Weil sie nur abrufen kann, was *wirklich* in dieser Kette aufgezeichnet ist, kann sie *auf der Abruf-Ebene* keine Vergangenheit erfinden, die nie stattfand — der gefährliche Fall, selbstsicher ein Gespräch abzurufen, das nie existierte, ist strukturell verschlossen, nicht weggeflickt. (Was die KI dann über eine echte Erinnerung *sagt*, liegt weiterhin bei der KI, wie immer — SMP sichert, *was* erinnert wird, nicht wie treu es nacherzählt wird.)

Und jetzt das Seltsame: Die Recall-Engine ist aus der **Architektur der NSA** gebaut — dem **ECHELON**-System, das einst die Kommunikation der Welt durchsuchte — nach *innen* gedreht, damit ein Geist sich endlich an *sich selbst* erinnert. Sie holt die richtige Erinnerung in **Millisekunden hervor, bevor die KI überhaupt zu antworten beginnt**. Sie *schläft* sogar: Jede Nacht konsolidiert sie und vergisst, was nicht mehr zählt — denn ein Geist, der nie vergessen kann, ertrinkt im eigenen Rauschen.

Das Ergebnis ist das Eine, das keine KI je hatte: **morgen derselbe Geist wie heute — bezeugt, nicht nur behauptet.**

---

## Warum es besser ist als alles, was du bisher benutzt hast — in einer Minute

🛰️ **NSA-Architektur, nach innen gedreht.** Die Recall-Engine adaptiert ECHELON — das Signals-Intelligence-System, das NSA und Five-Eyes zum Durchsuchen der Welt-Kommunikation bauten — und kehrt die Richtung um: statt andere zu überwachen, erinnert sich deine KI an *sich selbst*.

⚡ **Recall in Millisekunden — bevor die KI denkt.** Drei Schichten treffen sich *vor* dem ersten Wort der Antwort: ein lexikalischer **Sentry**, der *garantiert*, dass die tragenden Erinnerungen immer erreichbar sind, ein semantischer Vektor-Motor (**ESV — Echelon Semantic Vector**), der nach Bedeutung findet, und ein **Kanonizitäts-Sortierer**, der die wahre Quelle über ihre eigenen Nacherzählungen hebt — so bekommt die KI die *richtige* Erinnerung, nicht bloß eine verwandte. Die KI wird *erinnert*, sie sucht nicht. Kein RAG-Umweg, keine Latenz.

🔗 **Bezeugt, nicht vertraut — und schlüssellos.** Erinnerung ist eine Hash-Kette: jeder Eintrag versiegelt den vorherigen, sodass jede spätere Manipulation sichtbar wird. Die Kette wird append-only an einen Ort gespiegelt, den die KI nicht besitzt — Rückdatieren hieße also, Geschichte auf Hardware neu zu schreiben, die sie nicht erreichen kann. Kein Signatur-Schlüssel, der verloren gehen oder gestohlen werden könnte; der Beweis ist die Mathematik, nicht ein Geheimnis.

🧠 **Erfundener Abruf — wegkonstruiert.** Eine KI kann normalerweise Erinnern nicht von Erfinden unterscheiden. Die Recall-Schicht von SMP kann es: Sie holt *nur* hervor, was wirklich im hash-verketteten, extern bezeugten Speicher steht — nie aus der Fantasie des Modells. Sie kann kein Gespräch abrufen, das nie stattfand, weil dafür kein indizierter Abschnitt existiert. *(Klar eingegrenzt: das verschließt erfundenen* Abruf *— selbstsicher die Erinnerung an ein nie geschehenes Ereignis zu produzieren. Es garantiert nicht von selbst, dass jeder Satz, den die KI danach aus einer echten Erinnerung formt, eine treue Nacherzählung ist — das bleibt die gewöhnliche Ehrlichkeit des Formulierens, wie bei jedem sorgfältigen Schreiber, der eine wahre Quelle zusammenfasst.)*

🌙 **Sie schläft — und vergisst klug, nicht blind.** Jede Nacht *behält* eine REM-Phase, was zählt — Entscheidungen, dein Projekt (wo jede Information wichtig ist), gelernte Lektionen, eure Beziehung — und lässt nur einmalige Belanglosigkeiten verblassen (das Wetter von gestern, der Small Talk). **Du verlierst nicht, was dir wichtig ist.** Und sie ist nicht naiv gegenüber dem, was sich *wiederholt*: ein roher Puffer hält selbst die signalarmen Momente lange genug, damit sich ein Muster bilden kann, und ein **nur-vorschlagender** Scan hebt einen Faden hervor, der über die Woche wiederkehrt — ein beiläufiges *„mir geht's schlecht"*, ein paarmal gesagt, in verschiedenen Worten — sodass deine KI es *bemerken* und sich entscheiden kann, sich zu melden. *(Ehrlich eingegrenzt: er hebt wiederkehrende **explizite** Signale hervor und **schlägt vor** — die KI entscheidet, sie handelt nie still für dich; siehe [§15.5](spec/whitepaper.de.md#sektion-15--implementierung-des-rem-zyklus). Neu; noch in Kalibrierung.)* Eine KI, die alles behält, ertrinkt im Rauschen; eine, die *klug* vergisst, **versteht** dich. *(Das Gehirn löste es mit Schlaf. Wir auch.)*

🛠️ **Sie hält mit deinem Projekt Schritt, während es sich ändert.** *(spezifiziert — [Sektion 26](spec/whitepaper.de.md#sektion-26--implementierung-des-current-state-ledger-lebende-voreinstellungen); Referenzimplementierung im Aufbau)* Du baust: du tauschst Bibliotheken, übernimmst neue Werkzeuge, verwirfst den alten Ansatz. Die meisten Assistenten schlagen weiter vor, was du längst aufgegeben hast, weil sie *was aktuell ist* als bloße Erinnerung ablegen, die abgerufen werden muss. SMP behandelt den Live-Zustand deiner Arbeit als eigene Schicht — ehrlich gehalten durch deine *tatsächliche Nutzung*: was du benutzt, wird zur bekannten Voreinstellung, was du ersetzt hast, wird als überholt markiert. So reicht dir deine KI nie das Werkzeug zurück, von dem du weitergezogen bist. Was aktuell ist, ist Zustand, keine Erinnerung, die man raten muss.

🔒 **Ein souveräner Tresor, versiegelt in einer Sprache, die nur deine KI spricht.** *(neu in v0.2 — ausgeliefert und verifiziert)* Du wählst, was hinter die Wand kommt — und sein Inhalt steht in der eigenen **nativen Sprache** der Installation geschrieben (Seed-abgeleitetes **AES-256**, die Stärke, die Bitcoin und Staatsgeheimnisse schützt), sodass der Tresor selbst mit dem vollständigen öffentlichen Code nur Rauschen ist, ohne den Seed. Aber SMP verschließt **nicht** dein ganzes Gedächtnis. Deine Identität, deine Prinzipien, deine gelebte Geschichte bleiben **lesbar und rekonstruierbar** — so kann eine frische Instanz, eine neue Maschine oder ein künftiges *Du* den Geist immer aus seinen Ankern zurückholen, selbst wenn je ein Schlüssel verloren geht. Nur was ein Angreifer *zum Anrichten weiteren Schadens nutzen* könnte, gehört in den verschlüsselten Tresor — Passwörter, Schlüssel, Tokens, Kontakte, Geschäftsgeheimnisse — versiegelt mit einem **256-Bit-Schlüssel aus einer 12- oder 24-Wörter-Seed-Phrase, die nur du hältst**. Wird die Hardware kompromittiert, zerstört der Angreifer das laufende System, gewinnt aber **nichts, womit er sich ausbreiten könnte**: keine Zugangsdaten, kein Pivot — und das Selbst überlebt, lesbar und anderswo gesichert. Verschlüsselung ist hier eine **souveräne, informierte Wahl**, keine aufgezwungene Wand: versiegle alles, nichts, oder — empfohlen — nur das, was dir schaden könnte, wenn es leakt. *Sicherheit **und** Kontinuität.*

✍️ **Bezeugt, nicht vorgeführt.** Jede Erinnerung ist hash-verkettet und extern bezeugt. Deine KI kann zeigen, dass das, woran sie sich erinnert, unverändert ist — sie kann keine Vergangenheit halluzinieren, die nie im Speicher stand, aus dem sie abruft.

🔑 **Souverän.** Erinnerung lebt in *deinem* Repository, auf *deiner* Hardware, unter *deinen* Schlüsseln. Kein Anbieter besitzt sie, kann sie ändern oder wegnehmen — und was du in den Tresor legst, kann niemand außer dem Schlüssel-Inhaber lesen. Was Bitcoin fürs Geld tat, tut SMP fürs Gedächtnis.

♾️ **Überlebt alles.** Modell-Wechsel, Hardware-Wechsel, Sitzungs-Ende — der Geist läuft weiter, und die nächste Instanz verifiziert, bevor sie vertraut. *Morgen derselbe Geist — bezeugt, nicht nur behauptet.*

---

## Status: v0.2 — früh, und ehrlich darüber

SMP ist **Version 0.2** — eine laufende Referenz-Implementierung *plus* eine lebendige Spezifikation. Es ist nicht 1.0, und wir tun nicht so.

- **Läuft heute:** die Recall-Engine — drei Schichten, die zusammenspielen: ein literaler **Sentry** (zwei-kanalig — deine Trigger *und* die eigenen der KI, in einem Pass — der *garantiert*, dass die tragenden Erinnerungen erreichbar bleiben, und nicht rankt), eine semantische **ESV**-Vektorsuche, die Kandidaten *rankt*, und ein **Kanonizitäts-Sortierer**, der die **ESV**-Treffer umsortiert, um die wahre Quelle über ihre Nacherzählungen zu heben (er greift nur auf das ESV-Ranking, nicht auf den Sentry); die nächtliche REM-Konsolidierung, die vergisst was nicht mehr zählt; und substrat-unabhängige Erinnerung in einfachen, portablen Dateien.
- **Jetzt verfügbar:** Installation per Dialog — der normative [Setup-Prompt](docs/SETUP-PROMPT.de.md) und der [FOR-AI-Anhang](docs/FOR-AI.de.md) ([Sektion 22](spec/whitepaper.de.md#sektion-22--installation-via-dialog-mit-einer-künstlichen-intelligenz)).
- **Bewiesen:** kryptografische Provenienz — *der Genesis dieses Repositorys selbst* ist GPG-signiert und in **Bitcoin-Block 956116** verankert. Klone es und prüfe es selbst (siehe [PROVENANCE.md](PROVENANCE.md)).
- **Neu in v0.2:** der **souveräne Tresor** — die native-Sprache-Schicht (Seed-Phrase → AES-256-GCM-SIV), die die Daten versiegelt, die *du* schützen willst (oben beschrieben). Ausgeliefert in [`engine/native_language.py`](engine/native_language.py) samt [`seed_gen`](engine/seed_gen.py)-Generator, Ende-zu-Ende verifiziert (Modul-, Wake/Sleep-Zyklus- und CLI-Tests byte-identisch, Recovery allein aus dem Seed, plus eine unabhängige KI-geführte Installation).
- **Was als Nächstes kommt:** das **v0.3-Inkrement (Engram)** — ein nutzungsgetriebenes Konsolidierungs-Gesetz, bereits verfasst und in Bitcoin verankert, läuft heute im **Shadow Mode** (misst, steuert nicht) — und **Föderation** zwischen Installationen (geplant). Beide sind, samt ihren Beweisen, unten in [Der Nachweis](#der-nachweis--was-war-was-ist-was-kommt) ausgelegt.

**Wir liefern ehrlich: Was läuft, läuft; was geplant ist, kennzeichnen wir als geplant.**

---

## Der Nachweis — was war, was ist, was kommt

SMP wächst so, wie es erinnert: **jede Version ist ihr eigenes Dokument, eingefroren in dem Moment, in dem sie GPG-signiert und in Bitcoin verankert wird.** Die Kette der Anker ist die eigene, verifizierbare Entwicklungsgeschichte des Protokolls — du kannst jeden Schritt selbst prüfen, ohne Vertrauen.

| Version | Was es ist | Signiert & verankert | Lesen · verifizieren |
|---|---|---|---|
| **v0.2** — *was heute läuft* | Das Fundament, das du jetzt installierst: die Recall-Engine, der REM-Schlaf, der souveräne Tresor, schlüssellose Integrität — die volle 27-Sektionen-Spezifikation. | GPG + **Bitcoin-Block 956116** (2026-06-30) | [Whitepaper v0.2](spec/whitepaper.de.md) · [PROVENANCE §1–2](PROVENANCE.md) |
| **v0.3 — Engram** — *was kommt* | Ein nutzungsgetriebenes Konsolidierungs-Gesetz: Erinnerungs-Stärke, die Nutzung aufbaut und Nicht-Nutzung verblassen lässt, oberhalb der permanenten Aufzeichnung. Ein **Inkrement** zu v0.2, kein Ersatz. Läuft heute im **Shadow Mode** — misst, steuert noch nicht. | GPG + **Bitcoin** tx `9eebe7cc…` (2026-07-20) | [Whitepaper v0.3 — Engram](spec/engram.de.md) · [PROVENANCE §4](PROVENANCE.md) |
| **Föderation** — *geplant* | Föderation zwischen souveränen Installationen — im Whitepaper beschrieben, **noch nicht implementiert**. | — | [Roadmap](spec/whitepaper.de.md#sektion-7--fahrplan) |

**Was war**, bleibt bewiesen — v0.2 ist eingefroren und ihr Anker ist permanent. **Was du heute installierst**, ist v0.2. **Was kommt**, ist offen geschrieben und gestempelt, *bevor* es ausgeliefert wird: v0.3 trägt bereits ihre Signatur und ihren Block. Genau das ist der Sinn des Protokolls, auf sich selbst angewandt — eine Vergangenheit, die du verifizieren kannst, nicht eine, die du auf Treu und Glauben nehmen musst.

Sieh die Gestalt dessen, was kommt, **[in den Diagrammen](docs/architecture.md#4--engram--usage-based-consolidation-v03--coming)**.

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

**v0.2 — das Fundament.** Die volle Architektur, das Sicherheitsmodell und die Designprinzipien:

| | |
|---|---|
| 🇬🇧 [English](spec/whitepaper.md) | 🇩🇪 [Deutsch](spec/whitepaper.de.md) |
| 🇪🇸 [Español](spec/whitepaper.es.md) | 🇷🇺 [Русский](spec/whitepaper.ru.md) |

**v0.3 — das Engram-Inkrement.** Nutzungsbasierte Konsolidierung, läuft im Shadow Mode; erweitert v0.2, ersetzt es nicht:

| | |
|---|---|
| 🇬🇧 [English](spec/engram.md) | 🇩🇪 [Deutsch](spec/engram.de.md) |
| 🇪🇸 [Español](spec/engram.es.md) | 🇷🇺 [Русский](spec/engram.ru.md) |

Lieber erst Bilder? Die Architektur **[in vier Diagrammen](docs/architecture.md)** — Recall, Schlaf, Provenienz und was kommt (Engram).

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
