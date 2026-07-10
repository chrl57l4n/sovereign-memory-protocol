#!/usr/bin/env python3
"""native_language.py — SMP native-Sprache: verschlüsselte Gedächtnis-Schicht.

Tag-2-Bau (05.07.2026). Lebt ZUERST hier auf der Referenz-Installation
(SYNC-PROCESS R1: reift, bevor es ins öffentliche engine/ portiert wird).
Basiert auf dem bewiesenen Prototyp (scratch/native_lang_proto.py, 17/17 grün).

Design + Entscheidungen: plans/2026-07-05-native-sprache-forward-sim.md.

Drei Schichten:
  1. Krypto-Kern      — HKDF-Ableitung, AES-256-GCM, HMAC-opake Dateinamen.
  2. KeyProvider      — liefert (language_key, name_key). Passphrase-Backend (v1);
                        Hardware-Backend (BitBox02) dockt später an dieselbe
                        Schnittstelle an (Signatur → HKDF → dieselben Keys).
  3. NativeLanguageStore — verschlüsselt einen Klartext-Baum → opaker Cipher-Store
                        und zurück (tmpfs-Spiegel). Echter Pfad reist IM Blob.

BERÜHRT KEIN echtes Gedächtnis. Alle Operationen auf explizit übergebenen Pfaden.

Sicherheitsstufen (Klartext / Software-Passphrase / Hardware) + Bedrohungsmodell:
siehe Plan. Kurz: schützt at-rest (gestohlenes Repo/Backup/Platte) + Provenienz;
NICHT den laufenden Schlüssel im RAM (Live-Root = T9, ungewinnbar).
"""
from __future__ import annotations

import hmac as _hmac
import hashlib as _hashlib
import json
import os
import struct
import sys
from pathlib import Path
from typing import Tuple

from mnemonic import Mnemonic
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV

# ── Protokoll-Konstanten (nicht geheim) ──────────────────────────────────────
HKDF_SALT = b"smp-native-language-v1"
INFO_LANGUAGE = b"smp:language-key:v1"   # AES-256-GCM der Inhalte
INFO_NAME = b"smp:name-key:v1"           # HMAC → opake Dateinamen
INFO_SIGNATURE = b"smp:signature-key:v1"  # RESERVIERT, ungenutzt: Integrität ist keyless (§17,
                                          # Pro-Stufe-Hashkette + externer Zeuge). Kein Eintrag wird
                                          # signiert; dieser Schlüssel schützt NICHTS am Gedächtnis.
                                          # Bleibt im Ableitungsbaum nur aus Stabilität (Tuple/Tests).
# scrypt-Parameter der Warm-Tür. n=2^17 (OWASP-2026-Empfehlung, ~134 MB, ~0.4s):
# gehärtet gegen Offline-Brute-Force der Betriebs-Passphrase (Sia-Befund #5). argon2id
# wäre die modernere Alternative — als Cipher-Agility-Slot notiert, nicht v1-nötig.
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2 ** 17, 8, 1
KEY_LEN = 32
# §22: Der KI-Installations-Führer ist flüchtig (Session-Tod/Überlast). Der Zustand
# liegt auf Platte. Dieses Log macht die Installation wiederaufnehmbar — die Krypto-
# Schritte schreiben SELBST hinein (nicht auf KI-Disziplin angewiesen).
STATE_DEFAULT = os.path.expanduser("~/.smp/install-state.md")
_MNEMO = Mnemonic("english")


# ── 1. Krypto-Kern ───────────────────────────────────────────────────────────
def seed_from_mnemonic(words: str, bip39_pass: str = "") -> bytes:
    """BIP-39 Mnemonic → 64-Byte-Seed. Prüft die Prüfsumme (fängt Recovery-Tippfehler)."""
    if not _MNEMO.check(words):
        raise ValueError("BIP-39-Mnemonic hat ungültige Prüfsumme")
    return _MNEMO.to_seed(words, passphrase=bip39_pass)


def derive_key(seed: bytes, info: bytes, length: int = KEY_LEN) -> bytes:
    return HKDF(algorithm=SHA512(), length=length, salt=HKDF_SALT, info=info).derive(seed)


def keys_from_seed(seed: bytes) -> Tuple[bytes, bytes, bytes]:
    """Der kanonische Ableitungsbaum: (language_key, name_key, signature_key).
    language_key = Inhalts-Verschlüsselung (Vault), name_key = opake Dateinamen.
    signature_key ist RESERVIERT und ungenutzt — Gedächtnis-Integrität ist keyless
    (§17). Der Seed schützt nur den Vault, nie die Echtheit des Ketten-Records."""
    return (
        derive_key(seed, INFO_LANGUAGE),
        derive_key(seed, INFO_NAME),
        derive_key(seed, INFO_SIGNATURE),
    )


def gcm_encrypt(key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    # AES-256-GCM-SIV (RFC 8452): nonce-misuse-RESISTENT. Anders als reines GCM ist eine
    # zufällige Nonce-Kollision hier NICHT katastrophal — sie leakt höchstens die Gleichheit
    # zweier identischer Klartexte, nie den Authentication-Key. Schließt Sia-Befund #1
    # (Nonce-Reuse über viele SLEEP-Re-Encrypt-Zyklen) als ganze Klasse. 96-bit random Nonce.
    nonce = os.urandom(12)
    return nonce + AESGCMSIV(key).encrypt(nonce, plaintext, aad)


def gcm_decrypt(key: bytes, blob: bytes, aad: bytes = b"") -> bytes:
    return AESGCMSIV(key).decrypt(blob[:12], blob[12:], aad)


def opaque_name(name_key: bytes, relpath: str) -> str:
    """Deterministischer, undurchsichtiger Dateiname. Aus dem Seed neu berechenbar,
    kein gespeichertes Manifest nötig (recovery-sicher)."""
    return _hmac.new(name_key, relpath.encode(), _hashlib.sha256).hexdigest()


def _pack(relpath: str, content: bytes) -> bytes:
    p = relpath.encode()
    return struct.pack(">I", len(p)) + p + content


def _unpack(buf: bytes) -> Tuple[str, bytes]:
    (n,) = struct.unpack(">I", buf[:4])
    return buf[4:4 + n].decode(), buf[4 + n:]


# ── 2. KeyProvider (Auth-Schicht, einsteckbare Backends) ─────────────────────
class KeyProvider:
    """Liefert (language_key, name_key). Backends: Passphrase (v1), Hardware (später)."""

    def unlock(self) -> Tuple[bytes, bytes]:
        raise NotImplementedError


class PassphraseKeyProvider(KeyProvider):
    """Software-Stufe: on-disk Keystore, entsperrt per scrypt-Passphrase.

    EHRLICH: offline-brute-forcebar (nur so stark wie die Passphrase). Für die
    nicht-knackbare Stufe: HardwareKeyProvider (BitBox02), später.
    """

    def __init__(self, keystore_path: str | os.PathLike):
        self.keystore_path = Path(keystore_path)

    def init_from_seed(self, mnemonic: str, passphrase: str, bip39_pass: str = "") -> None:
        """Einmalig beim Setup: Seed → Keys → unter Passphrase gewickelt auf Platte.
        Der Seed berührt danach nichts mehr; Alltag läuft über die Passphrase."""
        seed = seed_from_mnemonic(mnemonic, bip39_pass)
        lang, name, sig = keys_from_seed(seed)
        salt = os.urandom(16)
        wrap = Scrypt(salt=salt, length=KEY_LEN, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P).derive(
            passphrase.encode()
        )
        blob = gcm_encrypt(wrap, lang + name + sig, aad=b"smp-keystore-v1")
        self.keystore_path.parent.mkdir(parents=True, exist_ok=True)
        self.keystore_path.write_text(json.dumps({
            "version": 1, "kdf": "scrypt", "salt": salt.hex(), "blob": blob.hex(),
        }))
        # Best effort: restriktive Rechte.
        try:
            os.chmod(self.keystore_path, 0o600)
        except OSError:
            pass

    def unlock(self) -> Tuple[bytes, bytes]:
        raise RuntimeError("Passphrase nötig — unlock_with(passphrase) verwenden")

    def unlock_with(self, passphrase: str) -> Tuple[bytes, bytes]:
        d = json.loads(self.keystore_path.read_text())
        salt = bytes.fromhex(d["salt"])
        wrap = Scrypt(salt=salt, length=KEY_LEN, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P).derive(
            passphrase.encode()
        )
        raw = gcm_decrypt(wrap, bytes.fromhex(d["blob"]), aad=b"smp-keystore-v1")
        lang, name = raw[:KEY_LEN], raw[KEY_LEN:2 * KEY_LEN]
        return lang, name


def recovery_keys_from_mnemonic(mnemonic: str, bip39_pass: str = "") -> Tuple[bytes, bytes]:
    """Katastrophen-Recovery: (language_key, name_key) direkt aus dem Seed,
    ohne Keystore. Öffnet Daten auf fremder Hardware."""
    lang, name, _sig = keys_from_seed(seed_from_mnemonic(mnemonic, bip39_pass))
    return lang, name


# ── 3. NativeLanguageStore (Klartext-Baum ↔ opaker Cipher-Store) ─────────────
class NativeLanguageStore:
    """Verschlüsselt einen Verzeichnisbaum → opaker Store (flache Blobs mit
    HMAC-Namen) und zurück. Der echte Pfad reist VERSCHLÜSSELT im Blob → voller
    Restore braucht KEIN name_key, nur den language_key."""

    def __init__(self, language_key: bytes, name_key: bytes):
        self.language_key = language_key
        self.name_key = name_key

    def encrypt_tree(self, src_dir: str | os.PathLike, cipher_dir: str | os.PathLike) -> int:
        # Verschlüsselt DATEIEN, nicht leere Verzeichnisse — wie tar/restic/borg. Ein
        # verlustfreier Round-Trip stellt alle Datei-Inhalte + Pfade her, aber KEINE
        # leeren Verzeichnisse (bewusst; sie tragen keine Payload, werden bei Bedarf neu
        # angelegt). Für Memory-Inhalte irrelevant; nur .git-Interna haben leere Dirs.
        src, cipher = Path(src_dir), Path(cipher_dir)
        cipher.mkdir(parents=True, exist_ok=True)
        count = 0
        for path in sorted(src.rglob("*")):
            if not path.is_file():
                continue
            relpath = str(path.relative_to(src))
            name = opaque_name(self.name_key, relpath)
            blob = gcm_encrypt(self.language_key, _pack(relpath, path.read_bytes()),
                               aad=name.encode())
            (cipher / name).write_bytes(blob)
            count += 1
        return count

    def decrypt_tree(self, cipher_dir: str | os.PathLike, dst_dir: str | os.PathLike) -> int:
        cipher, dst = Path(cipher_dir), Path(dst_dir)
        dst.mkdir(parents=True, exist_ok=True)
        count = 0
        for blob_path in cipher.iterdir():
            if not blob_path.is_file():
                continue
            name = blob_path.name
            relpath, content = _unpack(
                gcm_decrypt(self.language_key, blob_path.read_bytes(), aad=name.encode())
            )
            out = dst / relpath
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(content)
            count += 1
        return count

    def read_one(self, cipher_dir: str | os.PathLike, relpath: str) -> bytes:
        """Gezielter Zugriff auf EINE Datei (via HMAC-Name), ohne Voll-Restore."""
        name = opaque_name(self.name_key, relpath)
        blob = (Path(cipher_dir) / name).read_bytes()
        rp, content = _unpack(gcm_decrypt(self.language_key, blob, aad=name.encode()))
        assert rp == relpath
        return content


# ── 4. tmpfs-Wach/Schlaf-Zyklus (operative Hülle) ────────────────────────────
# Beim Wecken: at-rest Cipher-Store → Klartext-Spiegel in tmpfs (RAM, echte Namen).
# engine/Sentry/ESV laufen unverändert gegen den Spiegel (MOTOKO_MEMORY zeigt darauf).
# Beim Schlafen: Spiegel → Store zurück (ATOMAR: neu bauen + swap, alten als .bak),
# dann tmpfs wischen. Rebuild-Ansatz behandelt Adds/Changes/Deletes sauber.
import shutil as _shutil


def _ensure_clean_tmpfs(d) -> None:
    """Leert den Spiegel, behält aber das Verzeichnis selbst — MOUNTPOINT-SICHER.
    Ein dedizierter noswap-tmpfs (§20.9-Empfehlung) ist ein Mountpoint; `rmdir`/`rmtree`
    auf den Mountpoint selbst schlägt als User fehl (PermissionError, im Kernel verankert).
    Also nur den INHALT wischen, nie das Verzeichnis. Legt es an, falls es fehlt."""
    p = Path(d)
    if not p.exists():
        p.mkdir(parents=True)
        return
    for child in p.iterdir():
        if child.is_dir() and not child.is_symlink():
            _shutil.rmtree(child)
        else:
            child.unlink()


def wake(cipher_dir, tmpfs_dir, language_key: bytes, name_key: bytes) -> int:
    """Store → frischer Klartext-Spiegel in tmpfs. Gibt Datei-Anzahl zurück.
    tmpfs_dir ist typisch ein dedizierter noswap-tmpfs-Mountpoint (z.B. /run/smp-mirror)."""
    tmpfs = Path(tmpfs_dir)
    _ensure_clean_tmpfs(tmpfs)
    try:
        os.chmod(tmpfs, 0o700)
    except OSError:
        pass
    return NativeLanguageStore(language_key, name_key).decrypt_tree(cipher_dir, tmpfs)


def sleep(tmpfs_dir, cipher_dir, language_key: bytes, name_key: bytes,
          wipe: bool = True) -> int:
    """Spiegel → Store zurück, atomar. Gibt Datei-Anzahl zurück.
    Reihenfolge heilig: erst neuen Store bauen + verifizieren, DANN swappen, DANN wipen."""
    cipher = Path(cipher_dir)
    store = NativeLanguageStore(language_key, name_key)
    staging = cipher.parent / (cipher.name + ".new")
    if staging.exists():
        _shutil.rmtree(staging)
    n = store.encrypt_tree(tmpfs_dir, staging)

    # Verifikation VOR dem Swap: Round-Trip aus dem Staging muss den tmpfs-Stand
    # exakt reproduzieren — sonst kein Swap (Store bleibt unberührt).
    verify_dir = cipher.parent / (cipher.name + ".verify")
    if verify_dir.exists():
        _shutil.rmtree(verify_dir)
    store.decrypt_tree(staging, verify_dir)

    def _tree(root):
        root = Path(root)
        return {str(p.relative_to(root)): p.read_bytes()
                for p in sorted(root.rglob("*")) if p.is_file()}

    if _tree(verify_dir) != _tree(tmpfs_dir):
        _shutil.rmtree(staging, ignore_errors=True)
        _shutil.rmtree(verify_dir, ignore_errors=True)
        raise RuntimeError("sleep: Round-Trip-Verifikation gescheitert — Store NICHT angetastet")
    _shutil.rmtree(verify_dir, ignore_errors=True)

    # Atomarer Swap: alten Store nach .bak, staging → live.
    backup = cipher.parent / (cipher.name + ".bak")
    if cipher.exists():
        if backup.exists():
            _shutil.rmtree(backup)
        cipher.rename(backup)
    staging.rename(cipher)

    if wipe:
        _ensure_clean_tmpfs(tmpfs_dir)  # Inhalt wischen, Mountpoint am Leben lassen
    return n


# ── 5. CLI ───────────────────────────────────────────────────────────────────
# Sicherheits-Disziplin (Narben: nak-bunker 01.06.): Seed + Passphrase NUR über
# getpass (stdin, kein Echo) — NIE als argv (ps/pgrep leakt), nie geloggt, nie
# in Fehlermeldungen. Ehrliche Grenze: Python kann bytes nicht sicher zeroizen
# (immutable) — echtes mlock/Zeroize ist spätere Härtung (Review M3-1).
def _secret(prompt: str) -> str:
    import getpass
    sys.stdout.flush()  # sicherstellen, dass vorherige Erklär-prints VOR dem Prompt stehen
    return getpass.getpass(prompt)


def _checkpoint(event: str, state_path: str = STATE_DEFAULT) -> None:
    """Hängt einen Zeitstempel-Eintrag ans Install-Fortschritts-Log an. Überlebt
    Session-Tod → macht die Installation wiederaufnehmbar (`resume`). Bewusst
    best-effort (blockt nie eine echte Operation)."""
    try:
        from datetime import datetime
        p = Path(state_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.write_text(
                "# SMP — Installations-Fortschritt\n\n"
                "Automatisch von den Werkzeugen + von der KI geführt. Wenn die "
                "Installations-Session stirbt:\n"
                "`python3 engine/native_language.py resume` zeigt den Stand + nächsten Schritt.\n\n",
                encoding="utf-8")
        with p.open("a", encoding="utf-8") as f:
            f.write(f"- {datetime.now().strftime('%Y-%m-%d %H:%M')} — {event}\n")
    except OSError:
        pass


def _warn_if_unsafe_mirror(mirror: str) -> None:
    """§20.9: der Klartext-Spiegel darf nie auf Platte landen. Warnt (blockt NICHT,
    um legitime ramfs/encrypted-swap-Setups nicht zu verhindern), wenn der Spiegel
    nicht auf tmpfs/ramfs liegt bzw. auf tmpfs OHNE noswap."""
    try:
        target = os.path.realpath(mirror)
        best_mp = best_fs = best_opts = ""
        with open("/proc/mounts", encoding="utf-8", errors="replace") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 4:
                    continue
                mp, fs, opts = parts[1], parts[2], parts[3]
                if (target == mp or target.startswith(mp.rstrip("/") + "/")) and len(mp) > len(best_mp):
                    best_mp, best_fs, best_opts = mp, fs, opts
        if best_fs not in ("tmpfs", "ramfs"):
            print(f"⚠  Spiegel liegt auf '{best_fs or '?'}' ({best_mp or mirror}), NICHT auf tmpfs/ramfs —\n"
                  f"   der entschlüsselte KLARTEXT landet damit auf der Platte (§20.9-Leck).\n"
                  f"   Besser: noswap-tmpfs, z.B.  sudo mount -t tmpfs -o size=4G,noswap,mode=0700 tmpfs /run/smp-mirror",
                  file=sys.stderr)
        elif "noswap" not in best_opts.split(","):
            print(f"⚠  Spiegel auf tmpfs ({best_mp}) OHNE 'noswap' — unter Speicherdruck kann der\n"
                  f"   Klartext in den Swap ausgelagert werden (§20.9). 'noswap'-Mount empfohlen.",
                  file=sys.stderr)
    except OSError:
        pass


def _cli() -> None:
    import argparse

    p = argparse.ArgumentParser(
        prog="native_language.py",
        description="SMP native-Sprache — Verschlüsselungs-CLI (Passphrase-Backend)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init", help="Keystore aus Seed anlegen (einmalig beim Setup)")
    pi.add_argument("--keystore", required=True)

    pe = sub.add_parser("encrypt", help="Klartext-Baum → initialer Store (einmalig, Erst-Verschlüsselung)")
    pe.add_argument("--keystore", required=True)
    pe.add_argument("--src", required=True, help="Klartext-Quellbaum (z.B. das frische templates-Repo)")
    pe.add_argument("--store", required=True, help="Zielverzeichnis für den verschlüsselten Store")
    pe.add_argument("--force", action="store_true", help="vorhandenen nicht-leeren Store überschreiben")

    pw = sub.add_parser("wake", help="Store → tmpfs-Klartext-Spiegel entschlüsseln")
    pw.add_argument("--keystore", required=True)
    pw.add_argument("--store", required=True)
    pw.add_argument("--mirror", default="/run/smp-mirror")
    pw.add_argument("--force", action="store_true", help="vorhandenen Spiegel überschreiben")

    ps = sub.add_parser("sleep", help="tmpfs-Spiegel → Store zurück (atomar), wipen")
    ps.add_argument("--keystore", required=True)
    ps.add_argument("--store", required=True)
    ps.add_argument("--mirror", default="/run/smp-mirror")

    pr = sub.add_parser("recover", help="Store NUR aus Seed entschlüsseln (Recovery)")
    pr.add_argument("--store", required=True)
    pr.add_argument("--mirror", required=True)

    pst = sub.add_parser("status", help="Status: Keystore / Store / Spiegel")
    pst.add_argument("--keystore")
    pst.add_argument("--store")
    pst.add_argument("--mirror", default="/run/smp-mirror")

    prs = sub.add_parser("resume",
                         help="Nach Session-Tod: zeigt verifizierten Install-Stand + nächsten Schritt")
    prs.add_argument("--keystore", default=os.path.expanduser("~/.smp/keystore.json"))
    prs.add_argument("--store", default=os.path.expanduser("~/.local/share/smp/memory-store"))
    prs.add_argument("--mirror", default="/run/smp-mirror")
    prs.add_argument("--state", default=STATE_DEFAULT)

    a = p.parse_args()

    if a.cmd == "init":
        print("── Schritt A: deine Seed-Wörter eingeben ──────────────────────────")
        print("Tippe jetzt ALLE deine Wörter in EINER Zeile, mit je einem Leerzeichen")
        print("dazwischen (also: wort1 wort2 wort3 … (alle deine, 12 oder 24)), dann Enter.")
        print("Die Eingabe bleibt UNSICHTBAR (kein Echo) — das ist Absicht, nicht")
        print("kaputt. Einfach tippen; es wird nicht angezeigt und nicht geloggt.")
        mnemonic = _secret("Deine Seed-Wörter (12 oder 24, versteckt): ").strip()
        print()
        print("── Schritt B: dein Passwort erstellen (NICHT die Seed-Wörter) ─────────")
        print("Denk dir JETZT ein Passwort aus — etwas Eigenes, das du dir merkst,")
        print("NICHT deine Seed-Wörter. Damit entsperrst du das Gedächtnis im Alltag;")
        print("der Seed bleibt kalt fürs Recovery. Gib das Passwort zweimal ein (unsichtbar).")
        pw1 = _secret("Dein neues Passwort (NICHT die Seed-Wörter): ")
        if _secret("Passwort wiederholen: ") != pw1:
            print("Passwörter stimmen nicht überein — nichts angelegt. Bitte 'init' neu starten.",
                  file=sys.stderr)
            sys.exit(1)
        try:
            PassphraseKeyProvider(a.keystore).init_from_seed(mnemonic, pw1)
        except ValueError:
            print("Die eingegebenen Wörter ergeben keine gültige BIP-39-Prüfsumme — "
                  "vermutlich ein Tippfehler. Bitte alle deine Wörter prüfen und 'init' neu starten.",
                  file=sys.stderr)
            sys.exit(1)
        print(f"✓ Keystore angelegt: {a.keystore} (chmod 600). Seed zurück aufs Papier, "
              f"Passwort merken.")
        _checkpoint(f"Phase 2 ✓ — Keystore erstellt ({a.keystore})")

    elif a.cmd == "encrypt":
        store_dir = Path(a.store)
        if store_dir.exists() and any(store_dir.iterdir()) and not a.force:
            print(f"Store {store_dir} existiert + ist nicht leer — --force zum Überschreiben.",
                  file=sys.stderr)
            sys.exit(1)
        lang, name = PassphraseKeyProvider(a.keystore).unlock_with(
            _secret("Dein Passwort (NICHT die Seed-Wörter), versteckt: "))
        n = NativeLanguageStore(lang, name).encrypt_tree(a.src, store_dir)
        print(f"✓ Erst-Verschlüsselung: {n} Dateien aus {a.src} → opaker Store {a.store}.")
        print("  Klartext-Quelle bleibt unberührt — nach Verifikation selbst löschen/wegsichern.")
        _checkpoint(f"Phase 3 ✓ — {n} Dateien in opaken Store verschlüsselt ({a.store})")

    elif a.cmd == "wake":
        mirror = Path(a.mirror)
        if mirror.exists() and any(mirror.iterdir()) and not a.force:
            print(f"Spiegel {mirror} existiert + ist nicht leer. Das ist kein Fehler — wähle:\n"
                  f"  • Hält er schon den aktuellen Stand (bereits einmal geweckt)? Dann ist\n"
                  f"    nichts zu tun: MOTOKO_MEMORY dorthin zeigen und weiterarbeiten.\n"
                  f"  • Ungespeicherte Änderungen drin? Erst 'sleep' (schreibt sie in den Store).\n"
                  f"  • Sauber aus dem Store neu aufbauen? '--force' (überschreibt den Spiegel).",
                  file=sys.stderr)
            sys.exit(1)
        _warn_if_unsafe_mirror(str(mirror))
        lang, name = PassphraseKeyProvider(a.keystore).unlock_with(
            _secret("Dein Passwort (NICHT die Seed-Wörter), versteckt: "))
        n = wake(a.store, mirror, lang, name)
        print(f"✓ Wach: {n} Dateien in {mirror} (RAM). MOTOKO_MEMORY dorthin zeigen.")
        _checkpoint(f"wake — {n} Dateien im Spiegel {mirror} (WACH)")

    elif a.cmd == "sleep":
        lang, name = PassphraseKeyProvider(a.keystore).unlock_with(
            _secret("Dein Passwort (NICHT die Seed-Wörter), versteckt: "))
        n = sleep(a.mirror, a.store, lang, name, wipe=True)
        print(f"✓ Schlafend: {n} Dateien verschlüsselt, Spiegel gewischt, alt → .bak.")
        _checkpoint(f"sleep — {n} Dateien re-verschlüsselt, Spiegel gewischt (SCHLAFEND)")

    elif a.cmd == "recover":
        print("Recovery: gib ALLE Seed-Wörter in EINER Zeile ein, mit Leerzeichen")
        print("dazwischen. Unsichtbar (kein Echo) — das ist normal, einfach tippen + Enter.")
        try:
            lang, name = recovery_keys_from_mnemonic(_secret("Deine Seed-Wörter (12 oder 24, versteckt): ").strip())
        except ValueError:
            print("Ungültige BIP-39-Prüfsumme — Tippfehler? Alle deine Wörter prüfen und neu.",
                  file=sys.stderr)
            sys.exit(1)
        n = NativeLanguageStore(lang, name).decrypt_tree(a.store, a.mirror)
        print(f"✓ Recovery: {n} Dateien aus dem Seed entschlüsselt → {a.mirror}")

    elif a.cmd == "status":
        if a.keystore:
            print(f"Keystore: {'vorhanden' if Path(a.keystore).exists() else 'FEHLT'} ({a.keystore})")
        if a.store:
            sd = Path(a.store)
            print(f"Store:    {sum(1 for _ in sd.iterdir()) if sd.exists() else 0} Blobs ({a.store})")
        md = Path(a.mirror)
        awake = md.exists() and any(md.iterdir())
        print(f"Spiegel:  {'WACH (entschlüsselt in RAM)' if awake else 'geschlossen'} ({a.mirror})")

    elif a.cmd == "resume":
        print("═══ SMP Installations-Stand — verifiziert von der Platte, nicht geraten ═══\n")
        sp = Path(a.state)
        if sp.exists():
            print(f"Fortschritts-Log ({a.state}):")
            print(sp.read_text(encoding="utf-8").rstrip() + "\n")
        else:
            print(f"(kein Fortschritts-Log unter {a.state} — evtl. ganz frische Installation)\n")

        ks, st, mir = Path(a.keystore), Path(a.store), Path(a.mirror)
        ks_ok = ks.exists()
        n_blobs = sum(1 for _ in st.iterdir()) if st.exists() else 0
        bak = st.parent / (st.name + ".bak")
        awake = mir.exists() and any(mir.iterdir())
        print("Verifizierter Zustand der §20-Schicht (Grundwahrheit):")
        print(f"  Keystore:  {'✓ vorhanden' if ks_ok else '✗ fehlt'} ({a.keystore})")
        print(f"  Store:     {n_blobs} verschlüsselte Blobs ({a.store})")
        print(f"  .bak-Netz: {'✓ vorhanden' if bak.exists() else '—'}")
        print(f"  Spiegel:   {'WACH — Klartext in ' + str(mir) if awake else 'geschlossen (schlafend)'}")

        print("\nNächster Schritt:")
        if not ks_ok:
            print("  → Phase 2: Seed erzeugen (`seed_gen.py`), dann Keystore anlegen (`init`).")
        elif n_blobs == 0:
            print("  → Phase 3: Klartext-Baum in den Store verschlüsseln (`encrypt`).")
        else:
            print("  → Die §20-Verschlüsselungs-Schicht steht. Weiter mit Phase 4 (Recall-")
            print("    Organe: Embed-Server + ESV-Index) laut docs/SETUP-PROMPT.md.")
        print("\nFrische KI-Session: lies `START-HERE.md` + `docs/SETUP-PROMPT.md`, dann mach")
        print("ab dem Schritt weiter, den das Log oben zuletzt zeigt. Ein Schritt, dann Prüfung.")


if __name__ == "__main__":
    _cli()
