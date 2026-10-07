#!/usr/bin/env python3
"""G1-G8 tests for the gateway builder (SMP v0.5 §7a) — the deterministic properties the port rests on.

Nothing here touches real memory; every path is a temp dir.

  G1 — Minimal memory: only identity and scratchpad exist; the gateway builds, missing sections are absent.
  G2 — Hard budget: with oversized inputs the gateway stays within budget, says what it shrank,
       and the identity section is intact.
  G3 — Shrink order: conversation tail first, tool names second, thread names third.
  G4 — No silent failure: a build error ends in a short emergency gateway, never in an exception or an empty file.
  G5 — Open work: dated lines are listed, lines older than 14 days are marked.
  G6 — Deterministic: same inputs and same clock give byte-identical output.
  G7 — Precondition: a missing gateway block in the always-loaded map is reported; the German text builds.
  G8 — Last resort: tail and own signposts are dropped entirely before the budget breaks; if identity
       alone is larger than the budget, the file is over budget and says so (identity is never cut).

What these tests do NOT show: that a host surface makes a fresh session read the gateway (§7a.5 — probe, don't assume).

Run either way:
  pytest engine/tests/test_gateway_build.py -v
  python3 engine/tests/test_gateway_build.py        # no pytest needed
"""
from __future__ import annotations

import datetime
import importlib
import os
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
NOW = datetime.datetime(2026, 10, 5, 12, 0)


def _fresh(files: dict[str, str]):
    """Temp memory with the given files (paths relative to motoko/), fresh import of the builder."""
    root = Path(tempfile.mkdtemp(prefix="smp_gateway_"))
    for rel, text in files.items():
        p = root / "motoko" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    (root / "motoko").mkdir(exist_ok=True)
    os.environ["MOTOKO_MEMORY"] = str(root)
    os.environ["MOTOKO_HOME"] = str(root / "_home")
    sys.path.insert(0, str(ENGINE))
    for m in ("_paths", "gateway_build"):
        sys.modules.pop(m, None)
    return root, importlib.import_module("gateway_build")


IDENT = "# Identity\nI am a test instance. MARKER-IDENTITY-END"
TOOLS = "# State\n\n| Domain | Tool |\n|---|---|\n" + "".join(f"| tool-{i} ({i}) | x |\n" for i in range(400))


def test_g1_minimal():
    _, g = _fresh({"identity.md": IDENT, "today_scratchpad.md": "[H] hello\n[A] hi there\n"})
    text, shrunk = g.build(now=NOW)
    assert "MARKER-IDENTITY-END" in text and "hi there" in text
    assert "## 4" not in text and "## 6" not in text and "## 7" not in text      # no toolbox, threads, open work
    assert not shrunk and len(text.encode()) < g.BUDGET_DEFAULT


def test_g2_hard_budget():
    files = {"gist.md": IDENT, "current_state.md": TOOLS, "today_scratchpad.md": "\n".join(f"[H] Zeile {i} äöü " + "x" * 80 for i in range(2000))}
    files.update({f"threads/faden-{i}.md": "state: active\n" for i in range(300)})
    _, g = _fresh(files)
    for budget in (24000, 12000, 6000):
        text, shrunk = g.build(budget=budget, now=NOW)
        assert len(text.encode()) <= budget, (budget, len(text.encode()))
        assert "MARKER-IDENTITY-END" in text
        if budget < 24000:
            assert shrunk and g.T["en"]["shrunk"].split("{")[0] in text           # it says so in the self-check
        else:
            assert not shrunk                                                     # at 24000 these inputs fit: nothing may be shrunk


def test_g3_shrink_order():
    files = {"gist.md": IDENT, "current_state.md": TOOLS, "today_scratchpad.md": "y" * 20 + "\n" + "\n".join("[H] " + "x" * 90 for _ in range(300))}
    files.update({f"threads/t{i}.md": "" for i in range(40)})
    _, g = _fresh(files)
    t = g.T["en"]
    _, s0 = g.build(budget=24000, now=NOW)
    assert not s0                                                                                # fits: nothing is shrunk
    _, s1 = g.build(budget=10000, now=NOW)
    assert len(s1) == 1 and s1[0].startswith(t["cut_tail"].split("{")[0])                        # tail alone suffices
    _, s2 = g.build(budget=7000, now=NOW)
    assert t["cut_tools"] in s2 and s2.index(t["cut_tools"]) == 1


def test_g4_emergency():
    root, g = _fresh({"identity.md": IDENT})
    orig = g._body
    g._body = lambda: (_ for _ in ()).throw(RuntimeError("boom"))                # any failure inside the build
    try:
        out = root / "state" / "gateway.txt"
        ok, shrunk, size = g.write(out)
    finally:
        g._body = orig
    text = out.read_text()
    assert not ok and 0 < size < 1500 and "boom" in text and "EMERGENCY" in text
    assert not list((root / "state").glob("*.tmp"))
    g.emergency = lambda *a, **k: (_ for _ in ()).throw(KeyError("emergency broke too"))   # even the emergency text fails
    g._body = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        ok, _, size = g.write(out)
    finally:
        g._body = orig
    assert not ok and out.read_text() == g.LAST_RESORT


def test_g7_index_block_and_german():
    root, g = _fresh({"identity.md": IDENT})
    idx = root / "INDEX.md"
    idx.write_text("# my index\n- [something](x.md)\n")
    text, _ = g.build(now=NOW, index=str(idx))
    assert g.T["en"]["no_block"].split("(")[0] in text                            # block missing -> reported
    idx.write_text("## The gateway\n- Read ONE file: /somewhere/state/gateway.txt\n- [something](x.md)\n")
    text, _ = g.build(now=NOW, index=str(idx))
    assert "All in order" in text
    de, _ = g.build(now=NOW, lang="de")                                           # the second language builds
    assert "DAS TOR" in de and "Alles in Ordnung" in de


def test_g8_last_resort_shrink():
    files = {"gist.md": IDENT, "today_scratchpad.md": "\n".join("[H] " + "x" * 90 for _ in range(100)), "gateway_extra.md": "E" * 5000}
    _, g = _fresh(files)
    text, shrunk = g.build(budget=3600, now=NOW)
    assert len(text.encode()) <= 3600 and "MARKER-IDENTITY-END" in text and g.T["en"]["cut_tail_all"] in shrunk
    text, shrunk = g.build(budget=1200, now=NOW)                                  # identity + fixed parts alone are larger
    assert "MARKER-IDENTITY-END" in text and g.T["en"]["over"].split("{")[0] in text   # over budget, and it says so


def test_g5_open_work():
    ow = "# Open\n- [2026-10-04] fresh thing — next step\n- [2026-09-01] old thing — next step\n- no date line\n"
    _, g = _fresh({"identity.md": IDENT, "open_work.md": ow})
    text, _ = g.build(now=NOW)
    fresh = [l for l in text.split("\n") if "fresh thing" in l][0]
    old = [l for l in text.split("\n") if "old thing" in l][0]
    assert "⚠" not in fresh and "34 days" in old and "no date line" not in text


def test_g6_deterministic():
    _, g = _fresh({"identity.md": IDENT, "current_state.md": TOOLS, "today_scratchpad.md": "[H] a\n[A] b\n"})
    a, _ = g.build(now=NOW); b, _ = g.build(now=NOW)
    assert a == b


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print("PASS", name)
            except Exception as e:  # noqa: BLE001
                fails += 1; print("FAIL", name, "—", type(e).__name__, e)
    sys.exit(1 if fails else 0)
