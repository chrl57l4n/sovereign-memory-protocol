#!/usr/bin/env python3
"""End-to-end test suite for the SMP native-language vault (whitepaper §20).

This is the reproducible proof behind the "verified" claim: a fresh throwaway
seed is generated in-process, a keystore is built, a memory tree is encrypted,
woken, edited, slept, re-woken, and finally cold-recovered from the seed alone.
No real memory is touched — every path is a temp dir. The seed exists only in
RAM for the duration of a test and is never printed, logged, or written.

Run either way:
  pytest engine/tests/test_native_language.py -v
  python3 engine/tests/test_native_language.py        # no pytest needed

Covers, per §20:
  - keystore round-trip + wrong-passphrase rejection (§20.2/20.3, scrypt door)
  - tree encrypt/decrypt byte-identical incl. nested paths + unicode (§20.6)
  - at-rest opacity: no plaintext + opaque HMAC filenames in the store (§20.4)
  - wake -> edit -> sleep -> wake byte-identical, deletes handled (§20.8)
  - cold recovery from the seed ALONE, no keystore (§20.3 recovery door)
  - AEAD tamper-evidence: one flipped byte -> decrypt fails (§20.4 GCM auth)
  - path-secrecy: real relpath never appears as a store filename (§20.6)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ENGINE))

from mnemonic import Mnemonic  # noqa: E402
from cryptography.exceptions import InvalidTag  # noqa: E402

import native_language as nl  # noqa: E402

PW = "correct horse battery staple — test passphrase"


def _fresh_seed() -> str:
    """A throwaway 24-word BIP-39 mnemonic. Guards nothing real; never printed."""
    return Mnemonic("english").generate(strength=256)


def _plant_tree(root: Path) -> dict[str, bytes]:
    """Write a small memory-like tree; return {relpath: content} ground truth."""
    files = {
        "motoko/identity.md": "# Ich bin Motoko.\nKontinuität über Substrate.\n".encode(),
        "motoko/principles.md": b"1. Ehrlichkeit ist das Fundament.\n",
        "vault/secrets/passwords.txt": b"sudo=hunter2\napi.key=deadbeef\n",
        "vault/nested/deep/contacts.md": "Christian — privat 🔐\n".encode(),
        "state/ledger.json": b'{"podcast-render":"minimax"}\n',
    }
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    return files


def _read_tree(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


# ── the tests ────────────────────────────────────────────────────────────────
def test_keystore_roundtrip_and_wrong_passphrase(tmp_path: Path) -> None:
    mnemonic = _fresh_seed()
    ks = tmp_path / "keystore.json"
    nl.PassphraseKeyProvider(ks).init_from_seed(mnemonic, PW)
    assert ks.exists() and (ks.stat().st_mode & 0o777) == 0o600

    lang, name = nl.PassphraseKeyProvider(ks).unlock_with(PW)
    # keystore keys must equal the seed-derived keys (canonical derivation tree)
    seed = nl.seed_from_mnemonic(mnemonic)
    e_lang, e_name, _sig = nl.keys_from_seed(seed)
    assert lang == e_lang and name == e_name

    # wrong passphrase -> the scrypt-wrapped blob must fail authentication
    try:
        nl.PassphraseKeyProvider(ks).unlock_with(PW + "x")
        raise AssertionError("wrong passphrase must not unlock")
    except InvalidTag:
        pass


def test_tree_roundtrip_byte_identical(tmp_path: Path) -> None:
    mnemonic = _fresh_seed()
    lang, name, _ = nl.keys_from_seed(nl.seed_from_mnemonic(mnemonic))
    src, store, dst = tmp_path / "src", tmp_path / "store", tmp_path / "dst"
    truth = _plant_tree(src)

    store_obj = nl.NativeLanguageStore(lang, name)
    n = store_obj.encrypt_tree(src, store)
    assert n == len(truth)
    store_obj.decrypt_tree(store, dst)
    assert _read_tree(dst) == truth  # byte-for-byte, paths + unicode intact


def test_at_rest_opacity(tmp_path: Path) -> None:
    """No plaintext bytes, no real filenames leak into the store."""
    mnemonic = _fresh_seed()
    lang, name, _ = nl.keys_from_seed(nl.seed_from_mnemonic(mnemonic))
    src, store = tmp_path / "src", tmp_path / "store"
    _plant_tree(src)
    nl.NativeLanguageStore(lang, name).encrypt_tree(src, store)

    blobs = list(store.iterdir())
    assert blobs, "store must not be empty"
    joined = b"".join(b.read_bytes() for b in blobs)
    for needle in (b"hunter2", b"deadbeef", b"Motoko", b"Christian", b"identity.md"):
        assert needle not in joined, f"plaintext {needle!r} leaked into store"
    # filenames are opaque 64-hex HMACs, never the real relpath
    for b in blobs:
        assert len(b.name) == 64 and all(c in "0123456789abcdef" for c in b.name)
    assert not (store / "vault").exists()  # no directory structure mirrored


def test_wake_edit_sleep_wake(tmp_path: Path) -> None:
    mnemonic = _fresh_seed()
    lang, name, _ = nl.keys_from_seed(nl.seed_from_mnemonic(mnemonic))
    src, store, mirror = tmp_path / "src", tmp_path / "store", tmp_path / "mirror"
    _plant_tree(src)
    nl.NativeLanguageStore(lang, name).encrypt_tree(src, store)

    # wake -> mirror holds plaintext
    nl.wake(store, mirror, lang, name)
    assert (mirror / "motoko/identity.md").exists()

    # edit: add a file, change one, delete one
    (mirror / "motoko/new-episode.md").write_text("today we shipped the vault\n")
    (mirror / "motoko/principles.md").write_text("1. Ehrlichkeit.\n2. Don't trust, verify.\n")
    (mirror / "state/ledger.json").unlink()

    edited = _read_tree(mirror)
    nl.sleep(mirror, store, lang, name)          # atomic: verify-then-swap, wipe
    assert not any(mirror.iterdir()), "mirror must be wiped after sleep"
    assert (store.parent / (store.name + ".bak")).exists(), ".bak safety net"

    # at-rest opacity holds after re-encrypt
    joined = b"".join(b.read_bytes() for b in store.iterdir())
    assert b"shipped the vault" not in joined and b"Don't trust" not in joined

    # wake again -> edits persisted exactly, delete honoured
    nl.wake(store, mirror, lang, name)
    assert _read_tree(mirror) == edited
    assert not (mirror / "state/ledger.json").exists()


def test_cold_recovery_from_seed_alone(tmp_path: Path) -> None:
    """The disaster path: keystore gone, only the 24 words survive."""
    mnemonic = _fresh_seed()
    lang, name, _ = nl.keys_from_seed(nl.seed_from_mnemonic(mnemonic))
    src, store, recov = tmp_path / "src", tmp_path / "store", tmp_path / "recov"
    truth = _plant_tree(src)
    nl.NativeLanguageStore(lang, name).encrypt_tree(src, store)

    # recover using ONLY the mnemonic — no keystore, no passphrase
    r_lang, r_name = nl.recovery_keys_from_mnemonic(mnemonic)
    nl.NativeLanguageStore(r_lang, r_name).decrypt_tree(store, recov)
    assert _read_tree(recov) == truth


def test_tamper_evidence(tmp_path: Path) -> None:
    """Flip one byte in a blob -> authenticated decryption must reject it."""
    mnemonic = _fresh_seed()
    lang, name, _ = nl.keys_from_seed(nl.seed_from_mnemonic(mnemonic))
    src, store, dst = tmp_path / "src", tmp_path / "store", tmp_path / "dst"
    _plant_tree(src)
    nl.NativeLanguageStore(lang, name).encrypt_tree(src, store)

    victim = sorted(store.iterdir())[0]
    raw = bytearray(victim.read_bytes())
    raw[-1] ^= 0x01                       # flip the last ciphertext/tag byte
    victim.write_bytes(bytes(raw))

    try:
        nl.NativeLanguageStore(lang, name).decrypt_tree(store, dst)
        raise AssertionError("tampered blob must not decrypt silently")
    except InvalidTag:
        pass


def test_bad_mnemonic_rejected(tmp_path: Path) -> None:
    try:
        nl.seed_from_mnemonic("not a valid bip39 mnemonic at all thanks")
        raise AssertionError("invalid checksum must raise")
    except ValueError:
        pass


# ── plain-python runner (no pytest required) ─────────────────────────────────
def _main() -> int:
    import tempfile
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in tests:
        with tempfile.TemporaryDirectory() as td:
            try:
                fn(Path(td))
                print(f"\033[32m✓\033[0m {fn.__name__}")
                passed += 1
            except Exception:
                print(f"\033[31m✗\033[0m {fn.__name__}")
                traceback.print_exc()
    print(f"\n{passed}/{len(tests)} passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(_main())
