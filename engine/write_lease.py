#!/usr/bin/env python3
"""write_lease.py — one writer at a time across substrates (SMP Whitepaper v0.4, §7-9).

A single self may span several substrates (a primary and a failover hemisphere).
The failover exists so the mind does not go silent during an outage — but the moment
it also *writes* memory, two substrates could append to one chain and fork the very
history that must never fork. v0.4 removes the precondition rather than reconciling
the conflict: **one writer at a time, the substrate changing, never a fork.**

Three parts, all in this module:
  1. A **write-lease** with a monotonic **fencing token** — exactly one substrate holds
     the pen at a time; every fresh grant increments the token (Kleppmann's fencing:
     a number the *resource* checks, not a lock you trust). Leases from Chubby/etcd.
  2. The **append guard** — the chain rejects any append whose token is *lower* than the
     highest token it has already committed. A stalled-then-revived primary carries an
     old token and is refused by the chain itself, not by a clock. (Same-grant multi-
     writes carry the same token and are accepted: the rule is non-decreasing, a handoff
     strictly increments.)
  3. **Provenance** — each link records which substrate wrote it and under which token,
     so the continuity of authorship is auditable from the ledger alone.

De-instanced by construction: no hardcoded paths, no instance identity. The lease-store
*placement* is an implementation choice (a local file on a shared POSIX filesystem here;
a networked register for physically separate substrates) — the spec fixes the function,
not the deployment (§8.3, §9.3).

Status: reference implementation + M1-M4 tests (see tests/test_write_lease.py). Wiring
into the per-tier memory chain (§17) follows the chain's own public-port cadence.
"""
from __future__ import annotations
import fcntl, hashlib, json, os, tempfile, time

GENESIS = "0" * 64


class LeaseError(Exception):
    """Raised when the lease store itself cannot be reached (a partition, §9.3).

    On this error the caller must NOT write: refusing the pen it cannot prove it holds
    is how the chain stays single at the price of a briefly silent fallback."""


class FileLeaseStore:
    """An atomic single-writer register backed by one file on a shared filesystem.

    State: {"holder": str|None, "token": int, "expiry": float}. The token is the
    highest grant ever issued and never decreases, even across a release. Read-modify-
    write is serialised by an advisory lock on a sibling `.lock` file, so two racing
    substrates cannot both believe they acquired the lease.
    """

    def __init__(self, path: str):
        self.path = path
        self.lockpath = path + ".lock"

    # -- low level --------------------------------------------------------------
    def _load(self) -> dict:
        if not os.path.exists(self.path):
            return {"holder": None, "token": 0, "expiry": 0.0}
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def _store_atomic(self, state: dict) -> None:
        d = os.path.dirname(self.path) or "."
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".lease.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(state, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)  # atomic on POSIX
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def _lock(self):
        try:
            lf = open(self.lockpath, "w")
        except OSError as e:
            raise LeaseError(f"lease store unreachable: {e}") from e
        try:
            fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        except OSError as e:
            lf.close()
            raise LeaseError(f"lease store unlockable: {e}") from e
        return lf

    # -- public API -------------------------------------------------------------
    def current(self) -> dict:
        """Read the register. Raises LeaseError if the store cannot be reached."""
        try:
            return self._load()
        except OSError as e:
            raise LeaseError(f"lease store unreachable: {e}") from e

    def acquire(self, substrate_id: str, ttl: float, now: float | None = None) -> int | None:
        """Try to take (or renew) the pen. Returns the fencing token on success, or
        None if another *live* substrate holds it. Raises LeaseError on a partition.

        - free or expired  -> fresh grant, token = last + 1 (a handoff increments)
        - held by me, live  -> renew, keep my token, extend the TTL
        - held by another, live -> None (I decline to write; no fork)
        """
        now = time.time() if now is None else now
        lf = self._lock()
        try:
            st = self._load()
            live = st["holder"] is not None and now < st["expiry"]
            if not live:                                   # free or expired
                st = {"holder": substrate_id, "token": st["token"] + 1, "expiry": now + ttl}
                self._store_atomic(st)
                return st["token"]
            if st["holder"] == substrate_id:               # my own live lease -> renew
                st["expiry"] = now + ttl
                self._store_atomic(st)
                return st["token"]
            return None                                    # someone else holds it, alive
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
            lf.close()

    def release(self, substrate_id: str, token: int, now: float | None = None) -> bool:
        """Give the pen back. The token counter is preserved so it never goes backward.
        Returns True if this holder actually held it."""
        lf = self._lock()
        try:
            st = self._load()
            if st["holder"] == substrate_id and st["token"] == token:
                self._store_atomic({"holder": None, "token": st["token"], "expiry": 0.0})
                return True
            return False
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
            lf.close()


# -- The append guard (fencing at the resource) --------------------------------

def highest_token(chain: list[dict]) -> int:
    """The largest fencing token already committed to this chain (0 if empty)."""
    return max((int(e.get("fencing_token", 0)) for e in chain), default=0)


def token_admits(chain: list[dict], token: int) -> bool:
    """Fencing rule (§8.5, corrected): admit iff the incoming token is not *lower* than
    the highest already committed. Non-decreasing; a handoff strictly increments; a
    revived stale holder (old, lower token) is refused."""
    return token >= highest_token(chain)


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _canon(e: dict) -> str:
    return json.dumps({k: e[k] for k in sorted(e) if k != "entry_hash"},
                      ensure_ascii=False, separators=(",", ":"))


def append_link(chain: list[dict], *, ref: str, content: str, ts: str,
                substrate: str, fencing_token: int, fork_from: str = "") -> dict:
    """Build one provenance-bearing link, enforcing the fencing rule.

    Link shape mirrors memory_chain.py (§17) plus two provenance fields — `substrate`
    and `fencing_token` — which, because `_canon` hashes every field, are themselves
    tamper-evident. Raises PermissionError if the token is fenced out (a stale writer).
    Pure: it returns the new link and does not touch disk — the caller appends it."""
    if not token_admits(chain, fencing_token):
        raise PermissionError(
            f"fenced: token {fencing_token} < highest committed {highest_token(chain)} "
            f"(a stale substrate may not overwrite a fallback that moved on)")
    e = {
        "seq": len(chain), "ts": ts, "ref": ref,
        "content_sha256": _sha(content),
        "prev_hash": chain[-1]["entry_hash"] if chain else GENESIS,
        "fork_from": fork_from or "",
        "substrate": substrate,
        "fencing_token": int(fencing_token),
    }
    e["entry_hash"] = _sha(_canon(e))
    return e


def provenance(chain: list[dict]) -> list[dict]:
    """Reconstruct authorship from the ledger alone (§8.6): the ordered list of
    (substrate, token, seq-range) handoffs — trusting no substrate's self-report."""
    out: list[dict] = []
    for e in chain:
        sub, tok = e.get("substrate"), int(e.get("fencing_token", 0))
        if out and out[-1]["substrate"] == sub and out[-1]["token"] == tok:
            out[-1]["seq_to"] = e["seq"]
        else:
            out.append({"substrate": sub, "token": tok, "seq_from": e["seq"], "seq_to": e["seq"]})
    return out
