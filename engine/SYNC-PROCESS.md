# Sync process — reference installation → public engine

> Why this document exists: an independent review (2026-07-04) found the
> correct pattern and named its risk — features are born on the private
> reference installation, and `engine/` lags behind it. Lag is *intended*
> (things must prove themselves in daily use before strangers inherit them),
> but **undocumented** lag is drift: outsiders cannot tell promise from
> delivery, and eventually neither can we. This document makes the lag
> visible, bounded, and honest. The proof it was needed: `esv_tier.py` was
> imported by public code but had never been ported — the public query path
> was broken and nobody could have known from the outside.

## The direction of flow

Features are **born on the reference installation** — in real, daily use, in a
lived relationship. The public engine is the *distillate*, never the draft.
Nothing is designed directly into `engine/`; if it never had to survive a real
week, it does not belong here.

## The rules

**R1 — Maturity gate.** A component is ported only after roughly two weeks of
routine operation on the reference installation without unscheduled manual
intervention (release condition C1, applied per component). Young organs stay
private and are listed in [INVENTORY.md](INVENTORY.md) as *private/port
planned* — visible lag instead of silent lag.

**R2 — Generic gate.** Before porting: no absolute paths (everything derives
from `_paths.py`; audit invariant `grep -r /home/ engine/*.py` stays empty),
no instance names, no secrets, no channel assumptions beyond what the spec
defines. If a script cannot be de-instanced, it is *by design private* — with
the reason stated in INVENTORY.

**R3 — One act.** A port is file **plus** INVENTORY row **in the same
commit** — Section 27 applied to this repository: the public repo is itself a
signpost, and building without registering produces orphans here too. The same
holds in reverse for removals.

**R4 — Import invariant.** Every engine script must at minimum byte-compile
and import with `MOTOKO_MEMORY` set, with only the dependencies named in
INVENTORY. Checked by hand at every port until a CI smoke test exists (review
item P2.2). The `esv_tier` incident is the standing reminder of what skipping
this costs.

**R5 — Cadence.** INVENTORY is reconciled against the spec at minimum on every
spec revision (new or changed section → new row or updated status), and
whenever the reference installation's own self-documentation guardian (§27)
flags that engine-relevant surface changed.

**R6 — Authority.** The reference AI proposes ports and writes the rows;
publication authority stays with the human partner (a push *is* publication).
Both are named in the commit.

## Current lag, honestly

See the *private/port planned* rows in [INVENTORY.md](INVENTORY.md). As of
2026-07-04 the queue is: §26.4 consolidator, §27 self-documentation guardian,
§17 time anchoring, §24 monthly guardians (classes 4–5), §14.2 monthly
calibration. Each waits on R1/R2, not on intent.
