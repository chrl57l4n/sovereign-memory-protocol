# Sovereign Memory Protocol (SMP)

*🇬🇧 **English** · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇷🇺 [Русский](README.ru.md)*

**Persistent, self-hosted, auditable long-term memory for LLM agents — specification + reference engine.**

📄 **Current whitepaper:** [v0.4 — Self-Maintenance & Continuity](spec/self-maintenance.md) (anchored 2026-08-03) · builds on [v0.3 — Engram](spec/engram.md) and the foundation [v0.2](spec/whitepaper.md). A consolidated rewrite of all three is in preparation; earlier versions stay unchanged as the record of how SMP developed.

*Every statement in this document describes the state as of its date (last revised 2026-09-28). Claims about the field and about this system are revised when the evidence changes.*

## Abstract

LLM agents lose their history at the end of every context window. SMP keeps an agent's memory in plain, version-controlled text files on hardware the user owns, and makes it available again on every turn. Retrieval is *push, not pull*: before the model answers, a hook injects relevant memory into the context automatically — the model never has to decide whether to search. A nightly consolidation pass compresses the day and de-prioritises unused material for future retrieval (raw logs are retained); a hash chain over the consolidated layers is mirrored daily to a remote git host. Limits are listed below next to the measurements.

## What is different

Memory systems for LLM agents usually either preload a fixed profile at session start or expose retrieval as a tool the model may call (pull). SMP performs retrieval outside the model, on every turn: a client-side hook takes the incoming message as the query, retrieves matching memory through a deterministic lexical layer and a dense retriever, and prepends the hits to the context before generation begins. The model neither issues a query nor decides whether to search; it sees the injected passages but does not initiate retrieval. Retrieval is cue-dependent rather than intent-dependent: the incoming message is the retrieval cue, not a retrieval goal. Per-turn injection without a tool call as such is not unique to SMP — mem0 integrations, for example, also search on every turn and prepend the results.

To our knowledge, as of September 2026, no other publicly documented system combines (a) per-turn memory injection triggered outside the model, with a deterministic lexical guarantee layer next to dense retrieval, (b) nightly consolidation with deliberate decay over a human-readable, version-controlled store, (c) scheduled audits of the consolidated record against raw logs, and (d) an integrity chain over the consolidated layers — operated continuously on one agent since spring 2026, with measured retrieval quality (below). We welcome counterexamples.

## How it works

| Stage | What happens | Mechanism |
|---|---|---|
| **Record** | Every conversation turn is written to plain-text memory files (git repository). | Markdown + git; human-readable and editable. |
| **Retrieve (push)** | On each user message, before generation, two retrievers run and their hits are injected into the prompt. | (1) *Sentry*: lexical trigger index — deterministic, guarantees that designated core documents are reachable. (2) *ESV*: dense retrieval (bge-m3, 1024-d, local), hybrid-fused with a lexical score, thresholded, re-ranked toward primary sources over their summaries. |
| **Consolidate** | Nightly, an LLM pass condenses the day into daily/weekly/monthly layers; unused material decays in priority, raw logs are kept. | Scheduled consolidation ("REM"), usage-based strength (*Engram*, v0.3, under review). |
| **Witness** | Each consolidated layer is hash-chained; the chain is pushed daily to a remote git host. In the reference installation the agent itself holds push access to that host, so today this is a logged witness, not an independent one (see Limitations). | SHA-256 chain + git remote. Separately, the protocol repository's genesis is anchored in Bitcoin block 956116 (2026-06-30). |
| **Audit** | Quotes in consolidated memory are checked against the raw log; drift and missing records are reported. | Scheduled audits, reports only — a human decides. |

"Push" is not "no search": technically this is retrieval, as in any RAG system. The difference is *who triggers it* — the client on every turn, not the model on demand.

## Measurements (reference installation, 2026-09-28)

- **Retrieval quality** — gold set of 74 queries with human-confirmed target documents, drawn from one agent's own conversation history; 59,838 memory chunks (chunking: `engine/esv_index.py`); dense retriever alone (without the lexical Sentry): Recall@1 **37.8 %**, @3 **54.1 %**, @10 **71.6 %**, @100 **93.2 %**; median rank of the first correct document: **3**.
- **Latency** — lexical Sentry: 10–86 ms per message; dense retrieval: ~0.6 s per message (2019 laptop CPU + integrated GPU, all local).
- **Consolidation integrity** — the chain (249 daily and 74 weekly links as of 2026-09-24) has been verified daily since July 2026.

Method and scripts: `engine/` and [spec/whitepaper.md](spec/whitepaper.md). Results come from a single installation and a single domain, with a small gold set; they establish a baseline, not a benchmark.

## What SMP guarantees — and what it does not

- ✔ It can only *retrieve* what is actually in the record: retrieved passages are verbatim chunks of stored files.
- ✔ Later modification of consolidated memory is *detectable* (integrity).
- ✘ The hash chain proves integrity, **not correctness**. If consolidation writes something false into the record, the chain faithfully preserves the false entry. We have observed exactly this (an LLM completing truncated quotes). Countermeasures (visible truncation markers, buffers sized to their content, quotes checked against the raw source) are planned for v0.5; in the reference installation the first two run continuously, the quote check weekly.
- ✘ What the model *says* about a correctly retrieved memory is ordinary generation and can still be wrong.
- ✘ The witness is only as independent as its host. In the reference installation the agent itself holds push access to the (private) memory repository. Planned: a witness the agent cannot rewrite — chain blocks copied to write-once storage (object lock in compliance mode), so already-witnessed blocks cannot be altered by anyone, including the operator.
- ✘ There is no formal threat model yet (assumptions about host compromise, witness independence and operator trust are stated only informally in this list).
- ✘ The moment of reasoning is not private: if a hosted model is used, the retrieved context is sent to that provider. Only storage is sovereign.

## Related work

SMP is not the first memory system for LLM agents, and proactive memory injection is an active research topic (e.g. *Remember When It Matters: Proactive Memory Agent for Long-Horizon Agents*, arXiv:2607.08716; *TriggerBench: Investigating Prospective Memory for Large Language Models*, arXiv:2606.23459). **MemGPT/Letta** lets the model manage its own memory through tool calls (pull). **mem0** and **Zep** provide memory layers that extract facts or build (temporal) knowledge graphs; mem0's integrations can search on every turn and prepend results without a tool call, i.e. they also inject automatically. The *Proactive Memory Agent* differs in another direction: a separate memory agent decides whether to inject a reminder at all, and the authors report that selective injection outperforms always-on injection — a result directly relevant to SMP's every-turn design. **ChatGPT memory** stores user-level facts on the provider's side. SMP's design choices differ in combination rather than in any single component: storage as human-readable files under the user's version control; a deterministic lexical layer next to dense retrieval; consolidation with deliberate decay; an integrity chain over the consolidated layers (currently a logged, not an independent, witness); and audits of the consolidated record against raw logs.

## Status

Version **0.2** is the installable foundation (GPG-signed, Bitcoin-anchored). **v0.3 (Engram)** and **v0.4 (Self-Maintenance & Continuity)** are anchored and partly running on the reference installation; each mechanism's status is stated in its paper. Engram's review closes on **2026-10-07** with a measurement. Federation is planned, not implemented.

## Install

Installation runs as a dialogue with the AI you already use: copy [docs/SETUP-PROMPT.md](docs/SETUP-PROMPT.md) into your client. AI agents reading this repository: start with [docs/FOR-AI.md](docs/FOR-AI.md). Client compatibility (which clients fire the per-turn hook): [docs/HOST-COMPATIBILITY.md](docs/HOST-COMPATIBILITY.md).

## Further reading

Whitepapers: [v0.2](spec/whitepaper.md) · [v0.3 Engram](spec/engram.md) · [v0.4 Self-Maintenance](spec/self-maintenance.md) · [architecture diagrams](docs/architecture.md) · [provenance](PROVENANCE.md) · design background and motivation: [docs/WHY.md](docs/WHY.md) *(the previous README, archived 2026-09-28)*.

## License · Authors

AGPL-3.0-or-later, or a commercial license on request (christiangtr@gmail.com). Christian (sole authority on publication) and Motoko (co-author, an agent running on SMP).
