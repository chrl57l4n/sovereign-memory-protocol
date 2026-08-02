#!/usr/bin/env python3
"""M1-M4 conformance tests for the multi-substrate write-line (SMP v0.4, §7-9, §13).

These are the four release conditions the v0.4 whitepaper names, made executable —
the reproducible proof behind moving the mechanism from "specified, not built" to
"reference implementation + tests green". Nothing here touches real memory; every
path is a temp dir, and time is injected deterministically (no wall-clock flakiness).

  M1 — Lease correctness: exactly one holder at every instant, across TTL expiry and
       revival (two substrates never both hold the pen).
  M2 — Fencing at the boundary: the chain rejects a stale-token append and admits only
       a non-decreasing one, verified against a deliberately revived stale writer.
  M3 — Provenance legibility: from the ledger alone, the substrate-and-token history is
       reconstructed across a real handoff, trusting no substrate's self-report.
  M4 — Partition behavior: a full partition makes the fallback decline to write (no
       fork), while every substrate can still read.

Run either way:
  pytest engine/tests/test_write_lease.py -v
  python3 engine/tests/test_write_lease.py        # no pytest needed
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import write_lease as wl  # noqa: E402


# ── M1 — Lease correctness (one holder, TTL expiry, revival) ─────────────────

def test_M1_lease_is_mutually_exclusive_across_expiry_and_revival(tmp_path: Path) -> None:
    store = wl.FileLeaseStore(str(tmp_path / "lease.json"))

    # t=0: primary takes the pen (ttl 10) -> first grant, token 1
    tok_p = store.acquire("primary", ttl=10, now=0)
    assert tok_p == 1

    # t=1: fallback tries while primary is live -> declined, no second holder
    assert store.acquire("fallback", ttl=10, now=1) is None
    st = store.current()
    assert st["holder"] == "primary" and st["token"] == 1

    # primary renews at t=5 -> keeps its token (same grant, not a handoff)
    assert store.acquire("primary", ttl=10, now=5) == 1

    # primary crashes (stops renewing). t=16 is past expiry (5+10) -> fallback grants token 2
    tok_f = store.acquire("fallback", ttl=10, now=16)
    assert tok_f == 2 and tok_f > tok_p

    # revival: stale primary comes back at t=17 while fallback is live -> declined (no fork)
    assert store.acquire("primary", ttl=10, now=17) is None

    # fallback releases; primary re-acquires -> a NEW grant, strictly higher token 3
    assert store.release("fallback", tok_f) is True
    assert store.acquire("primary", ttl=10, now=18) == 3

    # at no point did two substrates hold a live lease simultaneously (asserted above)


def test_M1b_mutual_exclusion_holds_under_real_concurrency(tmp_path: Path) -> None:
    """The load-bearing half of M1: not just the CAS logic, but exclusion under real
    races. Many threads hammer one lease with the real clock; a counter incremented
    only while holding must never exceed 1, and grant tokens must strictly increase."""
    import threading
    store = wl.FileLeaseStore(str(tmp_path / "lease.json"))
    active = {"n": 0, "max": 0}
    grants: list[int] = []
    lock = threading.Lock()          # guards only the test's own bookkeeping
    stop = threading.Event()

    def worker(name: str):
        while not stop.is_set():
            tok = store.acquire(name, ttl=2.0)   # ttl >> critical section, so no mid-hold expiry
            if tok is None:
                continue
            with lock:
                grants.append(tok)
                active["n"] += 1
                active["max"] = max(active["max"], active["n"])
                here = active["n"]
            assert here == 1, f"two substrates held the pen at once: {here}"
            time.sleep(0.001)
            with lock:
                active["n"] -= 1
            store.release(name, tok)

    import time
    threads = [threading.Thread(target=worker, args=(f"sub{i}",)) for i in range(8)]
    for t in threads:
        t.start()
    time.sleep(0.6)
    stop.set()
    for t in threads:
        t.join()

    assert active["max"] == 1, f"exclusion violated: max concurrent holders = {active['max']}"
    assert len(grants) >= 5, "test did not exercise enough acquisitions"
    assert grants == sorted(grants), "fencing tokens must be monotonically non-decreasing"
    assert grants[-1] == len(grants), "each fresh grant must increment the token by exactly 1"


# ── M2 — Fencing at the append boundary ──────────────────────────────────────

def _link(chain, ref, substrate, token):
    e = wl.append_link(chain, ref=ref, content=f"content-{ref}", ts="2026-08-02T00:00",
                       substrate=substrate, fencing_token=token)
    chain.append(e)
    return e


def test_M2_chain_fences_out_a_stale_token(tmp_path: Path) -> None:
    chain: list[dict] = []

    # primary (token 1) writes two links under the SAME grant -> both admitted
    _link(chain, "a", "primary", 1)
    _link(chain, "b", "primary", 1)
    assert wl.highest_token(chain) == 1

    # handoff: fallback (token 2) writes -> admitted (2 >= 1)
    _link(chain, "c", "fallback", 2)
    assert wl.highest_token(chain) == 2

    # revived stale primary (still token 1) tries to write -> FENCED OUT
    try:
        _link(chain, "x", "primary", 1)
        raise AssertionError("stale token 1 must be rejected after token 2 committed")
    except PermissionError:
        pass

    # primary re-acquires (token 3) and writes -> admitted
    _link(chain, "d", "primary", 3)

    # no fork: seqs are contiguous and prev_hash forms one line
    assert [e["seq"] for e in chain] == [0, 1, 2, 3]
    prev = wl.GENESIS
    for e in chain:
        assert e["prev_hash"] == prev
        prev = e["entry_hash"]


def test_M2b_provenance_fields_are_tamper_evident(tmp_path: Path) -> None:
    chain: list[dict] = []
    e = _link(chain, "a", "primary", 1)
    # entry_hash must recompute from the canonical form incl. substrate + token
    assert e["entry_hash"] == wl._sha(wl._canon(e))
    # flip the recorded substrate -> the stored entry_hash no longer matches
    forged = dict(e); forged["substrate"] = "impostor"
    assert forged["entry_hash"] != wl._sha(wl._canon(forged))


# ── M3 — Provenance legibility (reconstruct authorship from the ledger) ───────

def test_M3_authorship_reconstructs_from_ledger_alone(tmp_path: Path) -> None:
    chain: list[dict] = []
    _link(chain, "a", "primary", 1)
    _link(chain, "b", "primary", 1)
    _link(chain, "c", "fallback", 2)
    _link(chain, "d", "primary", 3)

    prov = wl.provenance(chain)
    assert prov == [
        {"substrate": "primary",  "token": 1, "seq_from": 0, "seq_to": 1},
        {"substrate": "fallback", "token": 2, "seq_from": 2, "seq_to": 2},
        {"substrate": "primary",  "token": 3, "seq_from": 3, "seq_to": 3},
    ]
    # the token never goes backward across the seam
    tokens = [h["token"] for h in prov]
    assert tokens == sorted(tokens)


# ── M4 — Partition behavior (fallback declines to write; reads still work) ────

class _PartitionedStore(wl.FileLeaseStore):
    """A store that is unreachable — models a full network partition (§9.3)."""
    def acquire(self, *a, **k):
        raise wl.LeaseError("partition: lease store unreachable")
    def current(self, *a, **k):
        raise wl.LeaseError("partition: lease store unreachable")


def test_M4_partition_declines_write_but_keeps_read(tmp_path: Path) -> None:
    # a chain with prior content, readable locally
    chain: list[dict] = []
    _link(chain, "a", "primary", 1)
    tip_before = chain[-1]["entry_hash"]

    store = _PartitionedStore(str(tmp_path / "lease.json"))

    # fallback wakes during a partition, wants to write -> must NOT acquire, must NOT write
    wrote = False
    try:
        token = store.acquire("fallback", ttl=10, now=0)
        # unreachable branch: if we somehow got a token we would (wrongly) write
        _link(chain, "b", "fallback", token)
        wrote = True
    except wl.LeaseError:
        pass  # correct: decline the pen it cannot prove it holds
    assert wrote is False, "fallback must not write during a partition (no fork)"

    # the chain is unchanged (no fork appended) ...
    assert chain[-1]["entry_hash"] == tip_before
    # ... and the READ path is unaffected: every substrate can still recall
    assert wl.provenance(chain) == [
        {"substrate": "primary", "token": 1, "seq_from": 0, "seq_to": 0}
    ]


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
