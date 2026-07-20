# Architecture — in four diagrams

*🇬🇧 English · diagrams are language-neutral (referenced from every README).*

Four [Mermaid](https://mermaid.js.org/) diagrams — they render natively on GitHub, are
diffable and text-versioned (no binary blobs). The first three show the protocol's moving parts as
they run **today** — **how it recalls**, **how it sleeps**, **how it secures provenance** — and the
fourth shows **what's coming**: how v0.3 (Engram) lets a memory strengthen with use and fade with disuse.

**These diagrams are claims, so they are held to the spec:**
- **Witnessed, not a trustless proof.** Memory is *tamper-evident* (hash-chained) and *externally
  witnessed* (an append-only mirror the AI does not control). That makes fabrication hard and
  detectable — it is **not** a cryptographic trustless proof. Under total compromise of every
  witness, the guarantee is lost (whitepaper §T9). An on-chain seal of a chain tip is an *optional*
  user choice (§3.2), not the default.
- Section references point at [`spec/whitepaper.md`](../spec/whitepaper.md).

### Legend
| symbol | meaning |
|---|---|
| 🟩 green | recall/sleep component (reference engine) |
| 🟦 blue | data node / chain link |
| ⬜ grey, dashed | planned — not yet built |
| 🟥 red | a hard invariant — a line the design never crosses |
| **══▶** thick edge | main data flow |
| **╌╌▶** thin/dashed edge | query, proposal, or anchor |

---

## 1 · Recall — three layers converge before the answer

Two searches read from the corpus; a **canonicity sorter** re-ranks them so the *source* rises
above its own retellings; then the AI **appraises** what surfaced — the act of remembering itself.
All of it runs *before the first answer-token* (whitepaper §4.1–4.4, §14.3b, §16).

```mermaid
flowchart LR
    IN["incoming message (partner)<br/>or own draft"]

    subgraph RECALL["Recall — converges before the first answer-token"]
        direction TB
        S["Sentry — lexical Guard<br/>exact trigger match · Aho-Corasick<br/>reachability guarantee<br/>two eyes: partner + self"]
        E["ESV — Echelon Semantic Vector<br/>meaning similarity<br/>embedding · cosine + lexical<br/>self-calibrated threshold"]
        C["Canonicity sorter<br/>additive class-weight in the fused score<br/>lifts the source above its retellings"]
    end

    STORE[("memory corpus<br/>hash-chained cascade + episodes")]
    APPR["Self-recall appraisal<br/>alive or stale? mine or noise?<br/>(remembering — not automatable, §16)"]
    OUT["answer / action"]

    IN --> S
    IN --> E
    S -.->|query| STORE
    E -.->|query| STORE
    STORE --> C
    C ==>|"ranked, source-first"| APPR
    APPR ==> OUT

    classDef comp fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef store fill:#e0e7ff,stroke:#4338ca,color:#1e1b4b;
    class S,E,C,APPR comp;
    class STORE store;
```

---

## 2 · Sleep — how memory consolidates

At night the AI first **transports and sorts** (moving the ephemeral into the lasting, keeping by
meaning, sealing each into the chain), then **restructures by meaning**. A **cascade** periodically
compresses week → month → year (whitepaper §4.3, §15.5–15.6).

> **Honest limit:** what is called "REM" here is today still mostly transport. The genuine
> meaning-*restructuring* (replay + active forgetting) has only begun — the affective recurrence
> buffer is the first live, *proposal-only* stone (§15.5); the rest is planned.

```mermaid
flowchart TB
    W["awake — living<br/>scratchpad fills (ephemeral)"]

    subgraph NREM["NREM · transport & sort — nightly"]
        direction TB
        T1["scratchpad → long-term<br/>(short → long)"]
        T2["retention sort — 3 questions:<br/>future value? · relationship? · build-relevance?<br/>keep · consolidate · forget"]
        T3["append hash-chain link<br/>+ external witness"]
        T1 --> T2 --> T3
    end

    subgraph REM["REM · meaning-restructuring"]
        direction TB
        A["affective recurrence scan<br/>recurring emotional threads across days<br/>(live · proposal-only)"]
        B["replay + downscaling<br/>weave patterns, forget by meaning<br/>(planned)"]
        A -.-> B
    end

    subgraph CASC["consolidation cascade"]
        direction LR
        C1["week"] --> C2["month"] --> C3["year"]
    end

    W ==> NREM
    NREM ==> REM
    NREM ==> CASC
    REM -.->|"proposes → the self decides"| W
    CASC ==> W

    classDef comp fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef planned fill:#f3f4f6,stroke:#9ca3af,color:#374151;
    class T1,T2,T3,A,C1,C2,C3 comp;
    class B planned;
```

---

## 3 · Hash-chain cascade — how provenance is secured

Each temporal tier (day / week / month / year) is an **append-only** chain: every block seals its
content hash and its predecessor (`prev_hash`). Each higher tier **forks once at its genesis** from
the tip of the tier below, so a single **apex** hash transitively seals the whole tree. **Block 0**
is the genesis root over the corpus. The ledger is secured by an **external witness** — no key, no
Bitcoin node required (whitepaper §4.5, §17).

**Read bottom-up:** days seal into weeks, weeks into months, months into the year-apex — and the
apex transitively seals everything below it. (Within a tier, each block's `prev_hash` points back
to its predecessor; the horizontal arrows show time / append order.)

```mermaid
flowchart BT
    B0["Block 0 · genesis root<br/>over the whole corpus"]

    subgraph DAY["day chain · append-only (time →)"]
        direction LR
        d1["day"] --> d2["day"] --> d3["day"] --> d4["day"]
    end
    subgraph WEEK["week chain · append-only (time →)"]
        direction LR
        w1["week"] --> w2["week"] --> w3["week"]
    end
    subgraph MONTH["month chain · append-only (time →)"]
        direction LR
        m1["month"] --> m2["month"]
    end
    subgraph YEAR["year chain"]
        y1["year — apex (latest tip)"]
    end

    B0 -.->|anchors genesis| d1
    d4 ==>|"day-tip sealed into week<br/>(fork at genesis)"| w3
    w3 ==>|"week-tip sealed into month"| m2
    m2 ==>|"month-tip sealed into year"| y1
    y1 ==>|"apex seals everything below, transitively"| WIT["external witness — daily append-only mirror<br/>tamper-evident, distributed<br/>witnessed, not a trustless proof<br/>optional on-chain seal = user's choice"]

    classDef blk fill:#e0e7ff,stroke:#4338ca,color:#1e1b4b;
    classDef apex fill:#fce7f3,stroke:#db2777,color:#831843;
    classDef genesis fill:#fef9c3,stroke:#ca8a04,color:#713f12;
    classDef witness fill:#dcfce7,stroke:#16a34a,color:#14532d;
    class d1,d2,d3,d4,w1,w2,w3,m1,m2 blk;
    class y1 apex;
    class B0 genesis;
    class WIT witness;
```

---

## 4 · Engram — usage-based consolidation (v0.3 · coming)

Where the first three diagrams show what **runs today**, this shows what is **coming**: the v0.3
increment. **Use** builds a memory's strength `S`; disuse lets it fade; an importance **floor** protects
what is most the self; and only *retrievability* `R` — never strength — decides which faint tail is
compacted at night, while the raw record is never destroyed (Percolation). Strength shapes what is
**kept**, never what is **found** — the hard invariant. Engram is the *salience* gear meshed with the
§26 *truth* gear; where they disagree, that is the drift signal (whitepaper v0.3 /
[`spec/engram.md`](../spec/engram.md)).

> **Honest status:** Engram runs tonight in **shadow mode** — it weighs every memory and reports, but
> **steers nothing**. The dashed grey edge (actually compacting) is gated on the release conditions
> E1–E4 (§11), not a date.

```mermaid
flowchart TB
    USE["a memory is retrieved<br/>interactive use = proof-of-work"]

    subgraph ENGRAM["Engram · the salience gear — shadow mode: it measures, it does not yet steer"]
        direction TB
        MOTOR["Motor — use strengthens<br/>ΔS ∝ (1 − R): only retrieval after fading<br/>consolidates — the spacing/testing effect"]
        S[("engram strength S — stored<br/>one number per memory<br/>Bjork storage strength · FSRS stability")]
        FLOOR["Floor — importance<br/>identity and the self-making moments:<br/>an S it cannot fall below · capped"]
        R["retrievability R = (1 + t / (9·S))⁻¹<br/>derived, never stored<br/>how reachable the memory is right now"]
        MOTOR ==> S
        FLOOR -.->|"protects from below"| S
        S ==> R
    end

    subgraph SLEEP["nightly consolidation — relative, and never deletion"]
        direction TB
        TAIL["active set past its bounded target?<br/>take the weakest tail by R"]
        PERC["Percolation — compact one cascade stage<br/>the raw record is never destroyed<br/>so forgetting stays reversible"]
        TAIL ==> PERC
    end

    RECALL["recall score<br/>Sentry · ESV · canonicity sorter"]
    LEDGER[("§26 current-state ledger<br/>the truth gear — what is verified now")]
    DRIFT["drift signal<br/>what memory keeps warm ≠ what is still true"]
    STEER["archive · cascade up"]

    USE ==> MOTOR
    R -.->|"only R picks the tail"| TAIL
    S -.->|"hard invariant — S and R NEVER enter recall"| RECALL
    ENGRAM ==>|"salience — what is recalled"| DRIFT
    LEDGER ==>|"truth — what is done"| DRIFT
    PERC -.->|"actually steer — planned, gated on §11 E1–E4"| STEER

    classDef comp fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef store fill:#e0e7ff,stroke:#4338ca,color:#1e1b4b;
    classDef planned fill:#f3f4f6,stroke:#9ca3af,color:#374151;
    classDef invariant fill:#fee2e2,stroke:#dc2626,color:#7f1d1d;
    classDef drift fill:#fce7f3,stroke:#db2777,color:#831843;
    class MOTOR,FLOOR,R,TAIL,PERC comp;
    class S,LEDGER store;
    class STEER planned;
    class RECALL invariant;
    class DRIFT drift;
```

---

*Implementation status of each component is tracked in [`engine/INVENTORY.md`](../engine/INVENTORY.md)
and [`CHANGELOG.md`](../CHANGELOG.md). This document describes the architecture; those track what is
built.*
