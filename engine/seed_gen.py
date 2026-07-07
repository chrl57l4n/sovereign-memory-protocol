#!/usr/bin/env python3
"""SMP seed generator (whitepaper §20.2) — erzeugt EINE BIP-39 Seed-Phrase und
ZEIGT sie an.

Dies ist das EINZIGE Werkzeug im Protokoll, das den Seed sichtbar macht. Alle
anderen (`native_language.py init/recover`) nehmen ihn nur versteckt entgegen.
Regeln, die zur Bauart gehören:

  - OFFLINE ausführen, allein am Rechner. Die geführte KI sieht diese Ausgabe NIE.
  - Die Wörter auf Papier/Stahl schreiben — NIE in einen Chat, nie in eine Datei.
  - Das Programm speichert NICHTS, schreibt keine Datei und endet sofort.
  - Danach im Setup `native_language.py init` mit denselben Wörtern (versteckt):
    die Prüfsumme fängt Abschreibfehler, und derselbe Schritt legt den Keystore an.

Zwei Entropie-Quellen:
  (Standard)  os.urandom — der kryptografische Zufall des Betriebssystems
              (Interrupts/Timing/Hardware-Entropie; der geprüfte „Rausch"-Pool).
  --dice      physische Würfel — Realwelt-Entropie, wenn du der Maschine nicht
              einmal beim Würfeln trauen willst (Bitcoin-Cold-Seed-Methode).
"""
import argparse
import hashlib
import sys

from mnemonic import Mnemonic

WORDS_TO_BITS = {24: 256, 12: 128}         # Wörter → Entropie-Bits
# d6-Würfe für volle Entropie: log2(6) ≈ 2.585 bit/Wurf → 256/2.585≈99, 128/2.585≈50
MIN_ROLLS = {256: 99, 128: 50}


def choose_words() -> int:
    """Fragt den Menschen interaktiv: 12 oder 24 Wörter? Deine Wahl, nicht unsere.

    24 ist voreingestellt und empfohlen (256 Bit → 128 Bit effektiv selbst gegen
    einen hypothetischen Quanten-Grover-Angreifer). 12 (128 Bit) ist heute und
    auf absehbare Zeit ebenfalls astronomisch sicher — kürzer zu schreiben und zu
    lagern. Beides gültiges BIP-39; du kannst später NICHT mehr wechseln, ohne
    einen neuen Seed zu erzeugen.
    """
    print(line := "=" * 64)
    print("  WIE VIELE WÖRTER SOLL DEINE SEED-PHRASE HABEN?")
    print(line)
    print("  [24]  256 Bit — empfohlen. Reserve auch gegen künftige Quanten-")
    print("        angreifer (128 Bit effektiv nach Grover). Der Standard.")
    print("  [12]  128 Bit — heute und langfristig astronomisch sicher,")
    print("        kürzer zu schreiben und sicher zu lagern.")
    print("  Beides ist BIP-39. Später nicht mehr wechselbar ohne neuen Seed.")
    print(line)
    while True:
        ans = input("Deine Wahl [24]/12: ").strip()
        if ans == "":
            return 24
        if ans in ("24", "12"):
            return int(ans)
        print("  Bitte 24 oder 12 eingeben (Enter = 24).")


def gen_os(bits: int) -> str:
    """BIP-39 aus os.urandom (via mnemonic-Lib, geprüfter Standard)."""
    return Mnemonic("english").generate(strength=bits)


def gen_dice(bits: int) -> str:
    """BIP-39 aus physischen d6-Würfen. Dokumentierte Methode (Coldcard/
    Ian Coleman): genug Würfe sammeln, SHA-256 über die Ziffern → Entropie."""
    need = MIN_ROLLS[bits]
    print(f"Würfel-Modus: wirf einen normalen 6-seitigen Würfel mindestens {need}×")
    print(f"(für {bits} Bit Sicherheit). Tipp die Ergebnisse als Ziffern 1–6 ein —")
    print("Leerzeichen/Zeilen sind egal, andere Zeichen werden ignoriert.\n")
    digits = ""
    while len(digits) < need:
        line = input("Würfe: ")
        digits += "".join(c for c in line if c in "123456")
        print(f"  {min(len(digits), need)}/{need} gesammelt")
    # Mehr Würfe schaden nie — alle einbeziehen. SHA-256 „whitened" die Entropie.
    entropy = hashlib.sha256(digits.encode()).digest()[: bits // 8]
    return Mnemonic("english").to_mnemonic(entropy)


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="seed_gen.py",
        description="Erzeugt EINE BIP-39 Seed-Phrase und zeigt sie (offline, allein).",
    )
    ap.add_argument("--words", type=int, choices=[12, 24], default=None,
                    help="Wortzahl (24 = 256 Bit, empfohlen; 12 = 128 Bit). "
                         "Ohne Angabe fragt das Programm interaktiv.")
    ap.add_argument("--dice", action="store_true",
                    help="Entropie aus physischen Würfeln statt os.urandom")
    a = ap.parse_args()

    # Wortzahl: explizites Flag gewinnt; sonst interaktiv fragen (deine Wahl).
    # Ohne Terminal (Pipe/Skript) sicher auf 24 (den empfohlenen Standard).
    if a.words is not None:
        words_n = a.words
    elif sys.stdin.isatty():
        words_n = choose_words()
    else:
        words_n = 24
    bits = WORDS_TO_BITS[words_n]

    words = gen_dice(bits) if a.dice else gen_os(bits)

    # Prüfsumme MUSS stimmen, bevor wir sie dem Menschen zum Aufschreiben geben.
    if not Mnemonic("english").check(words):
        print("Interner Fehler: erzeugte Phrase hat ungültige Prüfsumme — Abbruch.",
              file=sys.stderr)
        sys.exit(1)

    line = "=" * 64
    print("\n" + line)
    print("  DEINE SEED-PHRASE — auf Papier/Stahl schreiben, NICHT in einen Chat:")
    print(line)
    for i, w in enumerate(words.split(), 1):
        print(f"  {i:2d}. {w}")
    print(line)

    # Warum diese Wörter sicher sind — damit der Mensch ein Gefühl dafür bekommt.
    exp = int(bits * 0.30103)                        # 2^bits ≈ 10^exp (floor)
    src = ("physischem Würfel-Zufall (SHA-256-verdichtet)" if a.dice
           else "dem kryptografischen Zufall des Betriebssystems (Hardware-/Timing-Rauschen)")
    print("Warum diese Wörter sicher sind:")
    print(f"  • {words_n} Wörter aus einer festen Liste von 2048, gewählt aus {bits} Bit")
    print(f"    echtem Zufall — aus {src}.")
    print(f"    Keine Formel, nicht ableitbar, bei jedem Lauf neu.")
    print(f"  • Das sind 2^{bits} ≈ 10^{exp} mögliche Phrasen. Selbst wenn jeder Computer")
    print(f"    der Erde eine Billion pro Sekunde probierte, dauerte das Erraten deiner")
    print(f"    Phrase unvorstellbar viel länger als das Alter des Universums.")
    print(f"  • Das letzte Wort ist eine Prüfsumme (kein Zufall) — es fängt Tippfehler.")
    print(f"  • Die Mathematik ist damit auf deiner Seite. Das EINZIGE reale Risiko ist")
    print(f"    der Zettel selbst: Feuer, Verlust, fremde Augen. Dort liegt deine")
    print(f"    Sicherheit — nicht im Raten. Deshalb: gut schreiben, sicher lagern.")
    print(line)
    print("Wenn du sie geschrieben hast: dieses Fenster schließen (und bei --dice")
    print("den Verlauf/Scrollback leeren). Danach im Setup:")
    print("  python3 engine/native_language.py init --keystore <pfad>")
    print("und dieselben Wörter versteckt eingeben — das prüft dein Backup UND legt")
    print("den Keystore an. Falsche Wiedergabe = Prüfsumme schlägt fehl = neu erzeugen.")


if __name__ == "__main__":
    main()
