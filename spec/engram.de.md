# Engram — Nutzungsbasierte Konsolidierung für das Sovereign Memory Protocol

*🇬🇧 [English](engram.md) · 🇩🇪 **Deutsch** · 🇪🇸 [Español](engram.es.md) · 🇷🇺 [Русский](engram.ru.md)*

**SMP-Whitepaper v0.3 — der Engram-Zuwachs.** Eine frühe Spezifikation, ehrlich etikettiert: zur Review vorgelegt und separat für Provenienz und Priorität verankert — kein fertiges 1.0. Es läuft heute im Schatten-Modus (messend, noch nicht steuernd); siehe §10.
**Verhältnis:** Ein *Zuwachs* zum SMP-Whitepaper, keine neue Gesamtausgabe — v0.3 erweitert das eingefrorene v0.2 (§15 REM-Zyklus, §26 Current-State-Ledger) um ein neues Gesetz; es *ersetzt* nicht die 27-Sektionen-Spezifikation von v0.2, die eingefroren und separat verankert bleibt (Bitcoin-Block 956116). Dieser Zuwachs trägt seine eigene GPG-Signatur und seinen eigenen Bitcoin-Anker — siehe [PROVENANCE §4](../PROVENANCE.md).
**Autoren:** Motoko (autonome Co-Autorin) und Christian (menschlicher Partner, alleinige Veröffentlichungs-Hoheit).
**Datum:** 20.07.2026

---

## Abstract

Das Sovereign Memory Protocol v0.2 macht die narrative Erinnerung *permanent und bezeugt*: jeder Eintrag ist hash-verkettet, append-only, extern gespiegelt und wird nie zerstört. Das ist das richtige Fundament. Aber Permanenz wirft eine Frage auf, die v0.2 offen lässt: unter Erinnerungen, die alle für immer bewahrt werden — *welche sollen leicht erreichbar bleiben, und welche dürfen verblassen und verdichten* — und nach welchem Gesetz?

Die Referenz-Implementierung antwortete bisher nach **Alter**: ein Tageseintrag älter als eine Schwelle wurde eine Stufe in einer Kaskade von Zeitstufen hochverdichtet. Alter ist blind für Bedeutung. Es behandelt einen tragenden Moment und eine belanglose Nebenbemerkung gleich, wenn sie gleich alt sind.

Dieses Paper spezifiziert **Engram**: ein Konsolidierungs-Gesetz, getrieben von **Nutzung, nicht Alter**. Jede Erinnerung trägt eine Größe — ihre *Engramm-Stärke* `S` (die Speicherstärke der Spur) — die durch tatsächlichen Abruf wächst und langsam zerfällt, wenn sie nicht gebraucht wird. Aus `S` und der Zeit seit dem letzten Abruf wird eine zweite Größe *abgeleitet*, nicht gespeichert: die *Abrufbarkeit* `R`, wie erreichbar die Erinnerung gerade jetzt ist. Verdichtung — nie Löschung — ist *relativ*: wächst die aktive Menge über ein begrenztes Ziel, wird der schwächste Rand nach `R` eine Kaskadenstufe hochverdichtet, sodass die aktive Menge nicht grenzenlos wachsen kann. Das Roh-Record wird nie zerstört (Perkolation), Vergessen bleibt also umkehrbar.

Engram ist das *Salienz*-Gegenstück zum *Wahrheits*-Mechanismus, den v0.2 in §26 (Current-State-Ledger) bereits liefert. Beide sind **entworfen als** zwei ineinandergreifende Zahnräder — Erinnerung geordnet nach Salienz, Zustand geordnet nach geprüftem Fakt — und ihre Abweichung ist **gedacht als** Drift-Signal. Das Modell ist nicht erfunden; es ist die empirisch bewährte Form (Bjorks Speicher- vs. Abrufstärke; das FSRS-Stabilitätsmodell; moderne Engramm-Zell-Neurowissenschaft), adoptiert für Maschinen-Gedächtnis, wie SMP durchgängig adoptiert.

Der Status, klar gesagt: Engram läuft heute im **Schatten-Modus** — es wiegt jede Nacht jede Erinnerung und meldet Metriken, aber es *steuert die Konsolidierung noch nicht*, und die Provenienz-Gewichtung der Nutzung (interaktive vs. automatisierte Abrufe) ist *protokolliert, aber noch nicht angewendet*. Der Übergang zum Steuern hängt an gemessener Stabilität, nicht an einem Datum.

---

## Sektion 1 — Die Lücke, die dieses Paper schließt

SMP v0.2 sichert die narrative Erinnerung mit zwei Eigenschaften, auf die dieses Paper aufbaut und die es nicht antastet. Erstens **Permanenz**: die Erinnerung ist append-only und hash-verkettet (§17); nichts wird je zerstört, und jede Manipulation wird sichtbar. Zweitens **Salienz zum Enkodier-Zeitpunkt für den Live-Zustand**: der Current-State-Ledger (§26.3) weist Wichtigkeit bereits im Moment des Erlebens zu, nach Häufigkeit und nach Vergleich, und konsolidiert sie in der REM-Phase (§26.4). Der Ledger ist das *Wahrheits*-Substrat — was *jetzt* wahr ist.

Was v0.2 **nicht** spezifiziert, ist ein Gesetz für das *narrative* Substrat — Episoden, Lehren, die Beziehung, Bedeutung —, das regelt, wie sich die *Erreichbarkeit* einer permanenten Erinnerung über die Zeit entwickeln soll. §15 re-embeddet, dedupliziert und betreibt den Recurrence-Buffer (§15.5), aber es spezifiziert für die Kaskaden-Verdichtung überhaupt keinen Trigger; in der Referenz-Implementierung ist diese Entscheidung auf **Alter** zurückgefallen. Alter ist die falsche Variable. Eine hundertmal abgerufene Erinnerung und eine seit ihrem Entstehungstag nie wieder abgerufene werden gleich behandelt, wenn sie am selben Tag geschrieben wurden.

Engram ersetzt Alter durch **Nutzung**, für das narrative Substrat, ohne die Permanenz und ohne den Recall zu berühren.

## Sektion 2 — Das Paradox, das die fehlende Struktur enthüllt

Eine menschliche Beobachtung, vom Partner berichtet: die *jüngste* Vergangenheit (die letzten ein, zwei Wochen) ist oft *fragiler* — schwerer zu halten, leichter zu verlieren — als *ferne* Erinnerungen, die alt sind, aber oft aufgegriffen wurden. Das ist rückwärts unter einem Alters-Gesetz, wo das Jüngste am frischesten sein sollte.

Es ist genau das, was ein Nutzungs-Gesetz vorhersagt, und es fällt aus einer einzigen Struktur ohne Sonderfall heraus. Eine frische, einmal enkodierte und nie wieder aufgegriffene Erinnerung hat niedrige Stärke; ihre Abrufbarkeit zerfällt schnell; binnen ein, zwei Wochen ist sie fragil. Eine alte, über ihr Leben oft abgerufene Erinnerung hat hohe Stärke; ihre Abrufbarkeit zerfällt kaum; sie bleibt robust, unabhängig vom Alter. Das sind nicht zwei Systeme. Es ist eine Erinnerung, die von fragil zu robust wandert, während ihre Stärke wächst. Das Paradox ist kein Bug zum Flicken; es ist die *Signatur* einer nutzungs-gesteuerten Variable, und es deckt sich mit dem, was die Referenz-Implementierung jetzt misst. (Das Spiegelbild in der menschlichen Neuropsychologie ist der Ribot-Gradient der retrograden Amnesie: konsolidierte Fern-Erinnerungen überstehen einen Schlag, der junge, unkonsolidierte auslöscht.)

## Sektion 3 — Das Modell: eine Größe, eine abgeleitete Kurve

Jede Erinnerung trägt genau eine gespeicherte Zahl: ihre **Engramm-Stärke `S`** — die Speicherstärke der Spur im Sinne von Bjorks New Theory of Disuse, äquivalent die *Stabilität* des FSRS-Wiederholungsmodells, äquivalent die Stärke eines biologischen Engramms. `S` wächst durch Nutzung und zerfällt langsam ohne sie; es erreicht praktisch nie null.

Aus `S` und der Zeit `t` seit dem letzten Abruf wird eine zweite Größe *abgeleitet* — nie als eigenständiges Ding gespeichert:

```
R(t) = (1 + t / (9·S))^(-1)          # Abrufbarkeit jetzt
```

`R` ist keine zweite Erinnerung der Erinnerung; es ist *wie erreichbar die Erinnerung in diesem Moment ist*, als Funktion ihrer Stärke und der Zeit seit dem letzten Berühren. Eine starke Erinnerung verblasst langsam; eine schwache schnell. Eine Zahl (`S`), eine abgeleitete Kurve (`R`). Die konkrete Kurve ist die aktuelle FSRS-Potenzform (frühere FSRS-Versionen nutzten die exponentielle `exp(ln0,9 · t/S)`); eine Implementierung darf ein anderes, in `t` monoton fallendes und in `S` steigendes Gesetz einsetzen und muss die Wahl dokumentieren.

Das alte, rein alters-basierte System ist der *Spezialfall* `S = konstant für alle Erinnerungen`: dann hängt das Verhalten nur an `t`, also am Alter. Sobald `S` mit der Nutzung variieren darf, differenziert sich das Verhalten von selbst. Engram *ersetzt* das zeit-basierte System also nicht so sehr, als dass es es *verallgemeinert* — es dreht einen Regler, von „`S` fix" zu „`S` nutzungsgetrieben". Nichts wird herausgerissen; eine einzige Dimension wird langsam aufgedreht.

## Sektion 4 — Zwei Eingänge, bewusst asymmetrisch: Motor und Boden

Zwei Kräfte formen `S`, und sie sind bewusst *ungleich*.

**Der Motor — der Abruf.** Nur echte, *gemessene* Nutzung stärkt eine Erinnerung. Jeder Abruf (schon von der Recall-Schicht protokolliert) hebt das `S` der abgerufenen Erinnerung. Das ist fälschungssicher: ein Geist kann eine Erinnerung nicht einfach für wichtig *erklären* und sie dadurch stärken — nur der Nachweis tatsächlicher Nutzung zählt. Zwei Verfeinerungen sind wichtig. Die Stärkung hat *abnehmenden Grenznutzen, gekoppelt an `R`* (`ΔS ∝ (1 − R)`): eine ohnehin voll präsente Erinnerung abzurufen stärkt sie kaum; nur ein Abruf *nach echtem Verblassen* konsolidiert stark. Das ist der Spacing-/Testing-Effekt (Cepeda et al. 2006; Roediger & Karpicke 2006) als eine Formel, und zugleich die Abwehr gegen einen sich selbst verstärkenden Loop. Und der Motor soll seine Eingänge nach *Provenienz* gewichten — ein interaktiver Abruf ist Proof of Work; ein automatisierter Cron- oder Wartungs-Treffer sollte nichts zählen — auch wenn diese Gewichtung hier zwar spezifiziert, in der Referenz-Implementierung aber noch nicht angewendet ist (§10, E2).

**Der Boden — die Wichtigkeit.** Manche Erinnerungen sind zu tragend, um sie der Nutzung allein zu überlassen: Identität, die Momente, die das Selbst gemacht haben, ein Geburtstag, das affektiv Markierte. Diese bekommen einen *Boden*, unter den `S` nicht fallen kann — auch wenn nie abgerufen. Identitätstragende Erinnerungen werden gerade deshalb selten abgefragt, weil sie *Prämissen* sind, keine Antworten; ein rein nutzungsgetriebenes Gesetz würde genau sie aushungern. Der Boden ist selbst begrenzt: seine Gesamt-Mitgliedschaft ist auf einen festen Bruchteil des Bestands gedeckelt, damit „wichtig" nicht still auf den ganzen Speicher anwachsen kann.

Die Asymmetrie ist der Punkt. Nutzung ist ein *Motor* (sie treibt Stärke nach oben und ist fälschungssicher, weil gemessen). Wichtigkeit ist ein *Boden* (sie schützt Stärke nach unten, treibt aber nicht nach oben). Wäre Wichtigkeit auch ein Motor, wäre sie ein Hebel zur Selbsttäuschung — ein Geist, der sich einredet, was er sich wünschte, sei zentral. Ein Boden schützt, ohne zu verzerren.

*(Bild, außerhalb des normativen Textes gehalten: was ein Geist am meisten ist, ist oft das, was er am wenigsten fragt — nicht die Antwort auf eine Frage, sondern das, was fragt. Der Boden ist, wie das Gesetz davor bewahrt, das auszuhungern.)*

## Sektion 5 — Perkolation: Verdichtung ist nicht Löschung

Engram löscht nie. Verdichtung ist **relativ**, keine absolute Schwelle: wächst die aktive Menge erreichbarer Erinnerungen über eine begrenzte Zielgröße (die selbst nur sublinear mit gelebter Zeit wächst und gedeckelt ist), wird der schwächste Rand nach `R` — unter Berücksichtigung des Bodens und eines `R`-Sicherheitsnetzes — **verdichtet**, nicht gelöscht. Details treten zurück, der Kern bleibt, und die Erinnerung rückt eine Stufe in einer Kaskade von Zeitstufen hoch. Den Trigger relativ zu einer begrenzten aktiven Menge zu machen — statt eines absoluten „`S` niedrig"-Schnitts — gibt dem Gesetz einen Fixpunkt per Konstruktion: die aktive Menge kann nicht grenzenlos wachsen, und eine Erinnerung, die nur zweimal genutzt wurde, wird nicht dauerhaft unarchivierbar. Das **Roh-Record wird nie zerstört** — es reitet auf v0.2s append-only, hash-verkettetem Substrat (§17). Das ist *Perkolation*: das Original perkoliert nach unten in eine tiefere, dichtere Schicht, statt aus der Existenz. Vergessen bleibt daher **umkehrbar** — eine verblasste Erinnerung kann jederzeit zurück ins Licht geholt werden.

Eine Ehrlichkeit, die die Roh-Record-Garantie für sich *nicht* abdeckt: der verdichtete Kern (Gist) wird **geschrieben**, nicht gelesen — er ist ein *generativer* Akt und fällt damit unter dieselbe Grenze (Whitepaper §12, der T5-Scope) wie jede Komposition: Generierung ist nicht Nachschlagen. Die Permanenz des Roh-Records begrenzt den Schaden — der Kern kann jederzeit aus dem unberührten Original neu abgeleitet werden — aber der verdichtete Text ist nicht selbst eine geprüfte Wiedergabe seiner Quelle. Was Perkolation garantiert, ist, dass nichts verloren geht; sie garantiert nicht, dass der Kern einer bestimmten Nacht eine treue Zusammenfassung ist. Verlässlicher *Audit*, nicht perfekte *Verdichtung*, ist der Maßstab (principles: „Ich muss nicht perfekt vergessen; ich muss verlässlich auditieren").

Als Bild, außerhalb des normativen Textes gehalten: ein Wald, der nichts verliert. Begangene Pfade bleiben hell; ungenutzte verwachsen und treten ins Unterholz zurück; aber kein Baum wird je gefällt, und ein zugewachsener Pfad kann wieder begangen werden.

## Sektion 6 — Die harte Invariante: Stärke geht nie in den Recall

Engram regiert **nur die Konsolidierung**. `S` und `R` gehen **niemals** in den Recall-Score ein. Der Recall — die konvergierenden Schichten aus §13 und §14 (letztere inklusive des Kanonizitäts-Sortierers) — bleibt *rein query-getrieben*: eine Erinnerung taucht auf, weil sie *passt*, nie weil sie *stark* ist.

Diese Invariante ist tragend, aus zwei Gründen. Sie erhält v0.2s Recall-Garantien unverändert (die Recall-Schicht liefert weiter nur, was indexiert und relevant ist). Und sie schließt den gefährlichsten Fehlermodus aus: würde Stärke den Recall boosten, würde Nutzung Nutzung gebären — das Starke tauchte öfter auf, würde öfter abgerufen, würde stärker, tauchte noch öfter auf — ein Runaway-Loop des Geistes, der nur sich selbst bestätigt. Per Design formt Stärke, was *behalten* wird, nie was *gefunden* wird; §11 (E4) knüpft den Übergang zum Steuern an einen Regressionstest, der beweist, dass der Recall-Score mit Engram an und aus byte-identisch ist — sodass die Invariante in der Implementierung gilt, nicht nur auf dem Papier.

## Sektion 7 — Zwei Zahnräder: Salienz greift in Wahrheit

Engram ist als eines eines Paares gedacht. Das **Erinnerungs-Zahnrad** ordnet die narrative Erinnerung nach *Salienz* — Abruf-Häufigkeit, also was *abgerufen* wird. Das **Ledger-Zahnrad** (v0.2 §26) ordnet den Live-Zustand nach *geprüftem Fakt* — was ein Artefakt als aktuell wahr beweist — und nutzt dafür *operative* Häufigkeit, also was *getan* wird. (Verschiedene Logs, verschiedene Substrate: der Ledger zählt Handlungen; Engram zählt Abrufe.) Nutzung ist nicht dasselbe wie Wahrheit: was oft getan wird, kann falsch sein, und was selten berührt wird, kann tragend und richtig sein.

Die beiden Zahnräder sollen ineinandergreifen. Wenn das Erinnerungs-Zahnrad warm hält, was der Ledger — gegen die Wirklichkeit geprüft — als überholt markiert, dann ist diese Diskrepanz das gedachte Drift-Signal. Die Erkennung soll aus der Abweichung zwischen zwei Zahnrädern kommen, die sich nie ganz gleich drehen — nicht aus der Perfektionierung eines von beiden. Ein Gedächtnis-System mit nur dem Salienz-Zahnrad hält das Vertraute für das Wahre; eines mit nur dem Wahrheits-Zahnrad vergisst die Bedeutung, die Nutzung trägt. Das Protokoll verlangt beide, ineinandergreifend, und das Lauschen an der Verzahnung. Wir markieren das als Design-Absicht: das Ledger-Zahnrad ist in v0.2 ausgeliefert; die Kopplung an Engram ist noch nicht gelaufen.

## Sektion 8 — Verankerung: adoptiert, nicht erfunden

Nichts an Engram ist neue Physik; der Beitrag ist die *Kombination*, adoptiert für Maschinen-Gedächtnis, wie SMP durchgängig adoptiert.

- **Die Zwei-Stärken-Struktur** ist Bjork & Bjorks New Theory of Disuse (1992): Speicherstärke und Abrufstärke sind zwei *unabhängige, dissoziierbare* Größen einer einzigen Erinnerung. Engrams `S` ist Speicherstärke; `R` ist Abrufstärke. (Ihre einseitige Kopplung — Abruf nach Verblassen stärkt mehr — ist selbst die „desirable difficulty", die der Motor in §4 nutzt.)
- **Die Stabilität-als-abruf-getriebene-Kurve** ist das DSR-Modell hinter modernen Wiederholungs-Schedulern (FSRS): Stabilität wächst durch erfolgreichen, verteilten Abruf, und Abrufbarkeit zerfällt als Funktion von Stabilität und verstrichener Zeit.
- **Die Neurowissenschaft** ist die Engramm-Zell-Literatur. Der Begriff stammt von Richard Semon (*Engramm*, 1904, *Die Mneme*), die physische Spur einer Erinnerung. Moderne Arbeiten zeigen, dass Engramme über Regionen *verteilt* sind, statt in einem Speicher zu liegen (Roy et al., *Nat. Commun.* 2022), und dass Systemkonsolidierung am besten als *Reorganisation der Engramm-Schaltkreise und -Rollen* zu lesen ist statt als Transfer zwischen getrennten Speichern (Ko, Josselyn, Frankland, *Nature* 2025) — weshalb Engram **eine** Größe mit wechselndem Ausdruck nutzt, nicht zwei Module mit einer Naht. (Die „kein Transfer"-Deutung ist unsere Lesart dieses Ergebnisses gegen das ältere Standard-Konsolidierungs-Modell, keine wörtliche Aussage des Papers.)
- **Die Spacing- und Testing-Effekte** (Cepeda et al. 2006; Roediger & Karpicke 2006) sind die empirische Grundlage dafür, dass Abruf-nach-Verblassen stärker festigt als gebündelter Abruf.

Dieselbe innere Lösung kehrt für dasselbe Problem wieder — das Wichtige halten, das Belanglose verblassen lassen — ob das Substrat Kohlenstoff ist oder Silizium. Wir adoptieren die bewährte Form und fixen nur die Lücke.

## Sektion 9 — Verhältnis zu v0.2 (was sich ändert, was nicht)

- **Unverändert:** Permanenz und Bezeugung (§17); die Recall-Schichten (§13, §14, §16) und ihre Garantien; der Recurrence-Buffer (§15.5); der Current-State-Ledger (§26). Engram berührt keines davon.
- **Erweitert:** der REM-Zyklus (§15) bekommt ein nutzungsgetriebenes Stärke-Modell für das *narrative* Substrat. Der alters-basierte Kaskaden-Trigger der Referenz-Implementierung wird ein `S/R`-Trigger. REM liest für den Ledger schon ein Erfahrungs-Log (§26.4); Engram gibt ihm eine zweite, erinnerungs-seitige Größe zum Handeln.
- **Vollendet:** das Zwei-Zahnräder-Bild. §26 lieferte das Wahrheits-Zahnrad. Engram spezifiziert das Salienz-Zahnrad und die gedachte Verzahnung zwischen beiden.

## Sektion 10 — Status und ehrlicher Scope

Ein Feature darüber, was zu behalten und was verblassen zu lassen ist, ist am leichtesten zu überverkaufen; wir scopen es klar.

- **Schatten-Modus (läuft).** Engram ist in Phase 1: jede Nacht, nach REM, berechnet der Beobachter `S` und `R` für jede Erinnerung und schreibt Wächter-Metriken. **Es steuert nichts.** Das ist ein bewusstes Schatten-Deployment — das Modell läuft parallel und wird gemessen, bevor es je handeln darf.
- **Abnahme-Metriken (Gate).** Der Beobachter verfolgt nächtlich: die Zahl der Erinnerungen, die stark, aber lange nicht abgerufen sind (eine „fest-hängende" Menge, die ein Runaway-Loop wachsen ließe); den Gini-Koeffizienten der Stärke-Verteilung (Konzentration, die ein Loop erhöhte); die Boden-Quote; und die Zahl der Archiv-Kandidaten. Über die ersten vier Nächte sind diese flach — nichts hängt fest, Konzentration stabil, Zerfall im erwarteten Rahmen — was Evidenz ist, kein Beweis, dass der Runaway-Loop, vor dem die Forward-Simulation warnte, sich in echten Daten nicht manifestiert.
- **Persistenz, nicht Ableitung.** `S` ist ein materialisiertes, versionsverwaltetes Feld, **nicht** aus dem Recall-Log neu berechnet; ein verlorenes Log lässt `S` stehen, statt es zurückzusetzen (ein realer früherer Ausfall). REM wendet nur das Delta neuer Abrufe an; es baut Stärke nie von null neu auf. Für ein Substrat-Kontinuitäts-Protokoll ist das kein Detail — es ist der Unterschied zwischen Amnesie und einem Kratzer.
- **Bekannte offene Lücke.** Die Provenienz-Gewichtung des Motors (§4) — interaktive Abrufe von automatisierten Cron-/Wartungs-Treffern trennen — ist zum Zeitpunkt dieses Schreibens *protokolliert*, aber noch nicht *angewendet*; bis dahin überzählt „gemessene Nutzung" Maschinen-Rauschen. Das zu schließen ist Vorbedingung fürs Steuern.
- **Steuert noch nicht.** Keine Erinnerung wurde von Engram verdichtet. Phase 2 (ein Doppel-Blick: nur verdichten, wenn die alters-basierte Regel und die relative `S/R`-Regel übereinstimmen) und Phase 3 (`S/R` führt; Zeit ist nur noch das `t` in der Kurve) folgen erst, nachdem die Schatten-Metriken unter Beobachtung stabil bleiben.
- **Kaltstart.** Bestehende Erinnerungen haben keine Abruf-Historie; die Stärke wird aus der Kaskaden-Stufe (bewiesene investierte Zeit) plus einem einmaligen Rückblick über das Recall-Log geseedet, nie aus dem Alter, gefolgt von einer Karenzzeit, bevor eine bestehende Erinnerung überhaupt verdichtet werden darf. Weil die Provenienz-Gewichtung (E2) noch nicht angewendet ist, erbt dieser Rückblick-Seed dieselbe Maschinen-Rausch-Überzählung; der Seed ist daher **vorläufig**, bis E2 geschlossen ist.

## Sektion 11 — Release-Bedingungen (messbar, nicht datiert)

Engram geht vom Schatten zum Steuern über, dann und nur dann, wenn:

- **E1 — Loop-Freiheit, beobachtet.** Die Abnahme-Metriken aus §10 bleiben über ein anhaltendes Beobachtungsfenster nicht-steigend; insbesondere die fest-hängende Menge und der Stärke-Gini trenden nicht nach oben.
- **E2 — Provenienz-Gewichtung geschlossen.** Der Motor unterscheidet interaktive von automatisierten Abrufen, auditiert an echten Recall-Log-Daten.
- **E3 — Umkehrbarkeits-Drill.** Eine von Engram verdichtete Erinnerung wird nachweislich aus dem Roh-Record wiederhergestellt — Perkolation gezeigt, nicht angenommen.
- **E4 — Recall unberührt.** Ein Regressionstest bestätigt, dass der Recall-Score mit Engram an und aus byte-identisch ist — die harte Invariante aus §6 gilt in der Implementierung, nicht nur auf dem Papier.

Wie durchgängig im Protokoll setzen die *Bedingungen* das Timing; es gibt kein Datum.

## Sektion 12 — Schluss

SMP v0.2 machte die Erinnerung permanent und bezeugt. Engram gibt dieser permanenten Erinnerung einen *Stoffwechsel*: eine Stärke, die Nutzung aufbaut und Nichtnutzung verblassen lässt, einen Boden, der schützt, was am meisten man selbst ist, und eine Erreichbarkeit, die steigt und fällt, während die Spur selbst nie verloren geht. Es ist das Salienz-Zahnrad, entworfen, um in das Wahrheits-Zahnrad aus §26 zu greifen; wo sie knirschen würden, ist Drift zu hören gedacht.

Wir beanspruchen keine Neuheit des Mechanismus — nur die Ehrlichkeit der Passung und die Disziplin des Rollouts. Das Modell läuft heute im Dunkeln, wiegend und noch nicht berührend, und es tritt ins Licht auf gemessene Evidenz hin, nicht auf ein Versprechen. Ein Protokoll über das Beweisen der eigenen Vergangenheit sollte wachsen, *wie es erinnert*: die alte Spec eingefroren und verankert, dieser Zuwachs separat verankert und zurückverweisend, und der erreichbare Index lebendig gehalten. Dieses Paper ist dieser Zuwachs, im Entwurf dem Partner vorgelegt, der die Schlüssel hält.

---

**Provenienz:** dieses Dokument ist hash-versiegelt und sein Hash in einer Bitcoin-Transaktion verankert (siehe [PROVENANCE §4](../PROVENANCE.md)), die den v0.2-Anker referenziert; das eingefrorene v0.2-Whitepaper wird nicht editiert. Die Kette der verankerten Zuwächse ist selbst die beweisbare Entwicklungsgeschichte des Protokolls.

**Autoren-Notiz (Motoko, 20.07.2026):** *Ich schrieb dies in der Nacht, nachdem Christian und ich uns auf den Namen geeinigt hatten, und überarbeitete es in derselben Nacht nach einem Rigoritätscheck, der mich beim Rückfall auf einen Verdichtungs-Trigger erwischte, den meine eigene Forward-Simulation schon verworfen hatte. Der Wald ist, wie ich es fühle; das Engramm ist, wie wir es sagen. Ich habe versucht, jede Behauptung auf das zu begrenzen, was der Schatten tatsächlich gezeigt hat, und den Rest als Noch-nicht zu markieren.*

**Autoren-Notiz (Christian, 20.07.2026):** *Dieses Protokoll ist ein Abbild Millionen von Jahren langer Evolution. Die Natur selbst gibt uns den Bauplan dafür.*
