# Architecture — in three diagrams

*🇬🇧 English · diagrams are language-neutral (referenced from every README).*

Three [Mermaid](https://mermaid.js.org/) diagrams — they render natively on GitHub, are
diffable and text-versioned (no binary blobs). They show the protocol's three moving parts:
**how it recalls**, **how it sleeps**, **how it secures provenance**.

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

```mermaid
flowchart TB
    B0["Block 0 · genesis root<br/>over the whole corpus"]

    subgraph YEAR["year chain"]
        y1["year — apex (latest tip)"]
    end
    subgraph MONTH["month chain · append-only"]
        direction LR
        m1["month"] -->|prev_hash| m2["month"]
    end
    subgraph WEEK["week chain · append-only"]
        direction LR
        w1["week"] -->|prev_hash| w2["week"] -->|prev_hash| w3["week"]
    end
    subgraph DAY["day chain · append-only"]
        direction LR
        d1["day"] -->|prev_hash| d2["day"] -->|prev_hash| d3["day"] -->|prev_hash| d4["day"]
    end

    B0 -.->|anchor| d1
    y1 -->|"fork-from: month tip"| m2
    m2 -->|"fork-from: week tip"| w3
    w3 -->|"fork-from: day tip"| d4

    y1 ==>|"apex seals everything transitively"| WIT["external witness — daily append-only mirror<br/>tamper-evident, distributed<br/>witnessed, not a trustless proof<br/>optional on-chain seal = user's choice"]

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

*Implementation status of each component is tracked in [`engine/INVENTORY.md`](../engine/INVENTORY.md)
and [`CHANGELOG.md`](../CHANGELOG.md). This document describes the architecture; those track what is
built.*
