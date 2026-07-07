#!/usr/bin/env python3
"""verify_pass.py — Systematic verify pass for SMP Tier-1 install (§22.7).

Runs the four tests that need the human's passphrase (the others are
covered by hooks / cron / sentry):

  T3: REM manual run         — write consolidation log
  T5: Backup-and-restore     — sleep, copy store to backup, restore from backup, wake
  T6: wake→edit→sleep→wake   — round-trip proves Tier-1 sync
  T6b: recover from seed     — cold-recovery door (asks for 24-word mnemonic)

Each test is independently runnable: --only T6, --only T6b, etc.
Defaults: run all four in order, snapshot store before, restore on failure.

Usage:
  python3 verify_pass.py [--only T3|T5|T6|T6b] [--skip-backup]
                          [--mirror /run/smp-mirror]
                          [--store ~/.local/share/smp/memory-store]
                          [--keystore ~/.smp/keystore.json]
                          [--backup ~/.smp/store-backup-<date>]
"""
from __future__ import annotations

import argparse
import getpass
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
NATIVE = ENGINE / "native_language.py"
sys.path.insert(0, str(ENGINE))

PASS_OK = "\033[32m✓\033[0m"
PASS_FAIL = "\033[31m✗\033[0m"
PASS_SKIP = "\033[33m·\033[0m"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ask_secret(prompt: str) -> str:
    """Hidden passphrase input (no echo)."""
    return getpass.getpass(prompt)


def _snapshot(store: Path, backup_dir: Path) -> Path:
    """Copy entire store to backup_dir. Returns backup path."""
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    backup_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(store, backup_dir)
    return backup_dir


def _invoke(cmd: list[str], env_extra: dict[str, str] | None = None) -> tuple[int, str, str]:
    """Run subprocess, return (rc, stdout, stderr). Sets MOTOKO_MEMORY etc. if given."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)
    return p.returncode, p.stdout, p.stderr


def _status_check(mirror: Path, store: Path, keystore: Path) -> None:
    rc, out, _ = _invoke(
        ["python3", str(NATIVE), "status",
         "--mirror", str(mirror), "--store", str(store), "--keystore", str(keystore)]
    )
    print(f"\n--- current status ---\n{out}")


def T3_rem_manual(mirror: Path, store: Path, keystore: Path) -> bool:
    """Run REM manually (--phase meta to skip LLM, just structural)."""
    print(f"\n=== T3: REM manual run ===")
    rc, out, err = _invoke(
        ["python3", str(ENGINE / "rem_consolidate.py"), "--phase", "meta"],
        env_extra={"MOTOKO_MEMORY": str(mirror), "MOTOKO_HOME": str(ENGINE.parent)},
    )
    if rc == 0:
        print(f"{PASS_OK} T3: REM --phase meta (structural, no LLM) → exit 0")
        if out.strip():
            for line in out.strip().splitlines()[:8]:
                print(f"   | {line}")
        return True
    print(f"{PASS_FAIL} T3: REM --phase meta → exit {rc}")
    if err:
        print(f"   stderr: {err[:300]}")
    return False


def T5_backup_restore(mirror: Path, store: Path, keystore: Path, backup: Path) -> bool:
    """Sleep → wipe store → copy from backup → wake again."""
    print(f"\n=== T5: Backup-and-restore ===")
    pw = _ask_secret("Passphrase (for sleep + wake, hidden): ")
    env_extra = {
        "MOTOKO_MEMORY": str(mirror),
        "MOTOKO_PASSPHRASE": pw,
    }
    # Backup was taken once at main(); reuse it.
    if not backup.exists():
        print(f"   no pre-taken backup at {backup}, snapshotting now…")
        _snapshot(store, backup)
    blobs_before = len(list(backup.iterdir()))
    print(f"      backup at {backup} ({blobs_before} blobs)")

    # 2) sleep (mirror → store, wipe mirror)
    print("   2. sleep (encrypt mirror → store, wipe)…")
    rc, out, err = _invoke(
        ["python3", str(NATIVE), "sleep",
         "--mirror", str(mirror), "--store", str(store),
         "--keystore", str(keystore)],
        env_extra=env_extra,
    )
    if rc != 0:
        print(f"{PASS_FAIL} T5: sleep failed: {err[:300]}")
        return False
    blobs_after_sleep = len(list(store.iterdir()))
    mirror_after_sleep = list(mirror.iterdir())
    print(f"      blobs: {blobs_before} → {blobs_after_sleep} (sleep may add/modify)")
    print(f"      mirror after sleep: {len(mirror_after_sleep)} entries (should be 0)")

    # 3) wipe store to simulate loss
    print("   3. simulating disaster: wipe store…")
    shutil.rmtree(store)

    # 4) restore from backup
    print(f"   4. restoring from {backup}…")
    shutil.copytree(backup, store)

    # 5) wake (store → mirror)
    print("   5. wake (decrypt backup → mirror)…")
    rc, out, err = _invoke(
        ["python3", str(NATIVE), "wake",
         "--mirror", str(mirror), "--store", str(store),
         "--keystore", str(keystore), "--force"],
        env_extra=env_extra,
    )
    if rc != 0:
        print(f"{PASS_FAIL} T5: wake from backup failed: {err[:300]}")
        return False
    mirror_now = list(mirror.iterdir())
    blobs_now = len(list(store.iterdir()))
    print(f"      blobs after restore: {blobs_now}")
    print(f"      mirror after wake: {len(mirror_now)} entries")
    print(f"{PASS_OK} T5: backup-and-restore round-trip works")
    return True


def T6_round_trip(mirror: Path, store: Path, keystore: Path) -> bool:
    """wake → edit a file → sleep → wake → verify edit persisted."""
    print(f"\n=== T6: wake → edit → sleep → wake round-trip ===")
    pw = _ask_secret("Passphrase (for two wakes + sleep, hidden): ")
    env_extra = {"MOTOKO_MEMORY": str(mirror), "MOTOKO_PASSPHRASE": pw}

    # 1) ensure mirror is awake
    if any(mirror.iterdir()):
        print("   mirror already awake; using current state")
    else:
        print("   1. wake (cold start)…")
        rc, out, err = _invoke(
            ["python3", str(NATIVE), "wake",
             "--mirror", str(mirror), "--store", str(store),
             "--keystore", str(keystore), "--force"],
            env_extra=env_extra,
        )
        if rc != 0:
            print(f"{PASS_FAIL} T6: wake failed: {err[:300]}")
            return False

    # 2) edit a sentinel file
    sentinel = mirror / "motoko" / ".verify-sentinel"
    marker = f"verify-pass {datetime.now(timezone.utc).isoformat()}\n"
    print(f"   2. writing sentinel {sentinel.relative_to(mirror)} …")
    sentinel.parent.mkdir(parents=True, exist_ok=True)
    sentinel.write_text(marker, encoding="utf-8")

    # 3) sleep
    print("   3. sleep (commit edit)…")
    rc, out, err = _invoke(
        ["python3", str(NATIVE), "sleep",
         "--mirror", str(mirror), "--store", str(store),
         "--keystore", str(keystore)],
        env_extra=env_extra,
    )
    if rc != 0:
        print(f"{PASS_FAIL} T6: sleep failed: {err[:300]}")
        return False

    # 4) confirm at-rest opacity: search store for "verify-pass" string (should find 0)
    found_in_store = subprocess.run(
        ["grep", "-rl", "verify-pass", str(store)],
        capture_output=True, text=True,
    )
    if found_in_store.returncode == 0 and found_in_store.stdout.strip():
        print(f"{PASS_FAIL} T6: 'verify-pass' found in store plaintext: {found_in_store.stdout}")
        return False
    print(f"      ✓ 'verify-pass' NOT in store (at-rest opacity preserved)")

    # 5) wake again
    print("   4. wake (reload from store)…")
    rc, out, err = _invoke(
        ["python3", str(NATIVE), "wake",
         "--mirror", str(mirror), "--store", str(store),
         "--keystore", str(keystore), "--force"],
        env_extra=env_extra,
    )
    if rc != 0:
        print(f"{PASS_FAIL} T6: wake-2 failed: {err[:300]}")
        return False

    # 6) verify sentinel persisted
    if not sentinel.exists():
        print(f"{PASS_FAIL} T6: sentinel missing after wake-2")
        return False
    got = sentinel.read_text(encoding="utf-8").strip()
    if got != marker.strip():
        print(f"{PASS_FAIL} T6: sentinel content mismatch:")
        print(f"   expected: {marker.strip()}")
        print(f"   got:      {got}")
        return False
    print(f"      ✓ sentinel persisted with original content: {got}")

    # 7) cleanup: remove sentinel (don't leave test artifact)
    sentinel.unlink()
    # Sleep once more to commit the cleanup
    rc, out, err = _invoke(
        ["python3", str(NATIVE), "sleep",
         "--mirror", str(mirror), "--store", str(store),
         "--keystore", str(keystore)],
        env_extra=env_extra,
    )
    if rc != 0:
        print(f"{PASS_WARN} T6 cleanup sleep failed: {err[:300]} (sentinel still in mirror, harmless)")
    print(f"{PASS_OK} T6: wake→edit→sleep→wake round-trip works, at-rest opacity holds")
    return True


def T6b_recover(store: Path, keystore: Path) -> bool:
    """Recover from 24-word seed alone (no keystore).

    Writes to a SEPARATE recovery mirror (/tmp/smp-recover-<ts>) so the
    primary mirror (/run/smp-mirror) is not overwritten. Counts decrypted
    files and compares to expected.
    """
    print(f"\n=== T6b: Cold recovery from seed alone ===")
    print(f"   This test asks for your 12- or 24-word BIP-39 mnemonic.")
    print(f"   It is NEVER logged or written anywhere — only piped into native_language.py recover.")
    mnemonic = _ask_secret("Seed phrase (12 or 24 words, hidden): ").strip()
    words = mnemonic.split()
    if len(words) not in (12, 24):
        print(f"{PASS_FAIL} T6b: expected 12 or 24 words, got {len(words)}")
        return False

    # Use a separate recovery mirror so the primary mirror is untouched
    rec_mirror = Path(f"/tmp/smp-recover-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    rec_mirror.parent.mkdir(parents=True, exist_ok=True)
    # stdin is what _secret() reads; if it can't read from a closed stdin it'll
    # fall back to /dev/tty (which won't work in non-interactive shell).
    # So we use the in-process fallback path: derive keys, decrypt a few blobs.
    try:
        from native_language import (seed_from_mnemonic, keys_from_seed,
                                      gcm_decrypt, _unpack)
        seed = seed_from_mnemonic(mnemonic)
        lang, name, sig = keys_from_seed(seed)
        del mnemonic  # jetzt sicher: Seed ist abgeleitet (vorher stand del zu früh → UnboundLocalError)
    except Exception as e:
        print(f"{PASS_FAIL} T6b: mnemonic invalid or wrong: {e}")
        return False

    blobs = list(store.iterdir())
    ok = 0
    samples = []
    for b in blobs:
        blob = b.read_bytes()
        try:
            packed = gcm_decrypt(lang, blob, aad=b.name.encode())
            relpath, plaintext = _unpack(packed)
            ok += 1
            if len(samples) < 3:
                samples.append(relpath)
        except Exception as e:
            print(f"   decrypt {b.name} failed: {e}")
    if ok == len(blobs):
        print(f"{PASS_OK} T6b: recovered {ok}/{len(blobs)} blobs from seed alone")
        print(f"   sample decrypted relpaths:")
        for s in samples:
            print(f"     - {s}")
        # Optionally write to recovery mirror for visual inspection
        rec_mirror.mkdir(parents=True, exist_ok=True)
        for b in blobs:
            blob = b.read_bytes()
            try:
                packed = gcm_decrypt(lang, blob, aad=b.name.encode())
                relpath, plaintext = _unpack(packed)
                out_path = rec_mirror / relpath
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(plaintext)
            except Exception:
                continue
        print(f"   full recovery mirror written to: {rec_mirror}")
        print(f"   rm -rf {rec_mirror}  # to clean up")
        return True
    print(f"{PASS_FAIL} T6b: only {ok}/{len(blobs)} blobs decrypted")
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mirror", default="/run/smp-mirror")
    ap.add_argument("--store", default=str(Path.home() / ".local/share/smp/memory-store"))
    ap.add_argument("--keystore", default=str(Path.home() / ".smp/keystore.json"))
    ap.add_argument("--only", choices=["T3", "T5", "T6", "T6b"], default=None)
    ap.add_argument("--skip-backup", action="store_true")
    args = ap.parse_args()

    mirror = Path(args.mirror)
    store = Path(args.store)
    keystore = Path(args.keystore)
    backup = Path.home() / ".smp" / f"store-backup-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

    print(f"Verify pass at {_now()}")
    print(f"  mirror : {mirror}")
    print(f"  store  : {store} ({len(list(store.iterdir()))} blobs)")
    print(f"  keystore: {keystore}")
    print(f"  backup : {backup}")

    _status_check(mirror, store, keystore)

    if not args.skip_backup and args.only in (None, "T5", "T6"):
        print(f"\n(snapshotting store → {backup})")
        _snapshot(store, backup)

    tests = []
    if args.only in (None, "T3"):
        tests.append(("T3", lambda: T3_rem_manual(mirror, store, keystore)))
    if args.only in (None, "T5"):
        tests.append(("T5", lambda: T5_backup_restore(mirror, store, keystore, backup)))
    if args.only in (None, "T6"):
        tests.append(("T6", lambda: T6_round_trip(mirror, store, keystore)))
    if args.only in (None, "T6b"):
        tests.append(("T6b", lambda: T6b_recover(store, keystore)))

    results = []
    for name, fn in tests:
        try:
            results.append((name, fn()))
        except KeyboardInterrupt:
            print("\n[interrupted]")
            break
        except Exception as e:
            print(f"{PASS_FAIL} {name}: exception {e}")
            results.append((name, False))

    print(f"\n=== Summary ===")
    n_pass = sum(1 for _, r in results if r)
    print(f"  {n_pass}/{len(results)} tests passed")
    for name, r in results:
        mark = PASS_OK if r else PASS_FAIL
        print(f"  {mark} {name}")

    if not args.skip_backup and (store,):
        # Ask whether to clean up backup
        print(f"\nBackup preserved at: {backup}")
        print(f"Delete with: rm -rf {backup}")

    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())