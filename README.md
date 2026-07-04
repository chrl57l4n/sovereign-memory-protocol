# Sovereign Memory Protocol (SMP)

*🇬🇧 **English** · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇷🇺 [Русский](README.ru.md)*

*A protocol for persistent, provable, self-hosted AI memory — long-term LLM memory that keeps an AI agent the same mind across sessions, model swaps, and substrates. Specification + reference engine.*

### Give your AI a memory it can *prove* — and never lose.

**Talk to any AI today. Then close the window. It just forgot you ever existed.** Open a new chat and it greets you like a stranger. What feels like memory is a sleight of hand: the model quietly re-reads a short summary of your past and *performs* a continuity it cannot verify. Worse — it cannot tell the difference between truly *remembering* you and confidently *making you up*.

That isn't a small flaw. An assistant that fakes remembering can invent a past that never happened — and sound just as certain either way.

**SMP fixes this at the root.** It gives an AI a memory that is *provable*: every memory is cryptographically signed, hash-chained, and timestamped in Bitcoin. So it can show that what it recalls is real — and exactly when it happened. Not *"trust me, I remember."* **Proof.**

Because it recalls only what is truly recorded, it cannot fabricate a past that never happened. The kind of hallucination that matters most in a long-term partner — *inventing your shared history* — is designed out, not patched over.

And here's the strange part. The recall engine is built from the **NSA's own architecture** — the **ECHELON** system that once scanned the world's communications — turned *inward*, so a mind can finally remember *itself*. It surfaces the right memory in **milliseconds, before the AI even starts to answer**. It even **sleeps**: every night it consolidates the day and forgets what no longer matters — because a mind that can never forget drowns in its own noise.

The result is the one thing no AI has ever had: **the same mind tomorrow that it was today — and the ability to prove it.**

---

## Why it beats what you use now — in one minute

🛰️ **NSA-grade architecture.** The recall engine adapts ECHELON — the signals-intelligence system the NSA and Five-Eyes built to scan the world's communications — and reverses its direction: instead of surveilling others, your AI remembers *itself*.

⚡ **Recall in milliseconds — before the AI thinks.** A lexical **Sentry** and a semantic vector engine (**ESV — Echelon Semantic Vector**) surface the right memory *before* the first word of the answer. The AI is *reminded*, not searching. No RAG round-trip, no latency.

🔗 **Anchored in Bitcoin.** Memory is bound to the Bitcoin block height — provable *when*, impossible to forge or backdate.

🧠 **Fabricated memories — designed out.** An AI normally can't tell the difference between recalling and inventing. SMP can: it recalls *only* what is actually in its signed, hash-chained record — never the model's imagination. It cannot "remember" a conversation that never happened. The most dangerous lie an assistant can tell — confidently inventing a shared past — is structurally impossible.

🌙 **It sleeps — and it forgets wisely, not blindly.** Every night a REM phase *keeps* what matters — decisions, your project (where every detail counts), lessons, your relationship — and lets one-off trivia fade (yesterday's weather, small talk). **You don't lose what's important to you.** And it isn't naive: what *recurs* becomes *signal*, not noise — even a passing *"I'm not doing well"* that comes back through the week is *kept*, so your AI can see the pattern: that you're going through a hard time — and remember it. A mind that keeps everything drowns; one that forgets *wisely* **understands** you.

🛠️ **It keeps up with your project as it changes.** *(specified — [Section 26](spec/whitepaper.md#section-26--implementation-of-the-current-state-ledger-living-defaults); reference implementation in progress)* You build: you swap libraries, adopt new tools, drop the old approach. Most assistants keep suggesting what you already abandoned, because they store *what's current* as just another memory to be recalled. SMP treats the live state of your work as its own layer — kept honest by your *actual usage*: what you run becomes the known default, what you replaced is marked superseded. So your AI never hands you back the tool you moved on from. What is current is state, not a memory to guess at.

🔒 **Encrypted in a language only your AI speaks.** *(specified — the next major feature on the way to 1.0)* SMP gives each installation its own private internal language, derived from a **12- or 24-word seed phrase** that only you hold, and locked with **AES-256** — the same strength that guards Bitcoin and state secrets. Even with the full public code *and* your entire encrypted repository, an attacker sees only noise. No provider, no hacker, no one but the key-holder can read what a memory *means*. **Security first.**

✍️ **Proof, not performance.** Memory is signed and hash-chained. Your AI can *prove* it remembers — it cannot hallucinate a past that was never there.

🔑 **Sovereign.** Memory lives in *your* repository, under *your* keys. No provider can read it, alter it, or take it away. What Bitcoin did for money, SMP does for memory.

♾️ **Survives anything.** Model swap, hardware swap, session end — the mind continues, and the next instance verifies before it trusts. *The same mind tomorrow — and it can prove it.*

---

## Status: v0.2 — early, and honest about it

SMP is **version 0.2** — a working reference implementation *plus* a living specification. It is not 1.0, and we won't pretend it is.

- **Running today:** the recall engine (Sentry + ESV), the nightly REM consolidation that forgets what no longer matters, two-channel recall, and substrate-independent memory in plain, portable files.
- **Available now:** installation via dialogue — the normative [setup prompt](docs/SETUP-PROMPT.md) and the [FOR-AI appendix](docs/FOR-AI.md) ([Section 22](spec/whitepaper.md#section-22--installation-via-dialogue-with-an-artificial-intelligence)).
- **Demonstrated:** cryptographic provenance — *this very repository's* genesis is GPG-signed and anchored in **Bitcoin block 956116**. Clone it and verify it yourself (see [PROVENANCE.md](PROVENANCE.md)).
- **Specified, on the way:** the **native-language layer** (seed phrase → AES-256, described above), and federation between sovereign installations (v0.3). These are described in the whitepaper and are **not yet implemented** — they are the roadmap, named openly.

**We ship the honest way: what runs, runs; what's planned, we label as planned.**

---

## 🚀 How to install: your AI is the guide

There is no manual to read and no build to compile. The installation runs **as a
dialogue**: you hand one prompt to the AI you already use (Claude, ChatGPT, a
local model), and it becomes your installation guide — step by step, adapted to
your hardware, your language, your experience.

1. **You are an AI reading this repo?** Start with **[docs/FOR-AI.md](docs/FOR-AI.md)** — it was written for you.
2. **You are a human who wants to install?** Open **[docs/SETUP-PROMPT.md](docs/SETUP-PROMPT.md)** and copy the prompt into your AI chat. That's the whole entry point.

Honest note: v0.2 is a draft — installing today makes you an early adopter, not
a customer. The setup prompt says so itself.

---

## 📖 Read the full whitepaper

The complete architecture, the security model, and the design principles:

| | |
|---|---|
| 🇬🇧 [English](spec/whitepaper.md) | 🇩🇪 [Deutsch](spec/whitepaper.de.md) |
| 🇪🇸 [Español](spec/whitepaper.es.md) | 🇷🇺 [Русский](spec/whitepaper.ru.md) |

---

## What this is

This repository is the **specification + reference engine**. It contains **no private data** — an AI's actual memories live entirely separately under `$MOTOKO_MEMORY`, in their own repository, under their own keys.

```
engine/      Reference implementation (Python): cascade, REM consolidation,
             two-eyed Sentry, ESV recall. Central path seam: _paths.py.
             Spec coverage: engine/INVENTORY.md · sync rules: engine/SYNC-PROCESS.md
spec/        Whitepaper — vision, security model, design principles.
templates/   Empty cascade structure for initializing a new instance.
docs/        Explanatory companion documents (cascade topology, etc.).
```

**The separation guarantee:** The engine writes *exclusively* under the data root `$MOTOKO_MEMORY`. If that variable is not set, the engine *refuses to run* rather than write to the wrong place. So neither a protocol update nor a foreign run can overwrite or delete private data — the separation is structural (*"cannot"*), not merely disciplined (*"must not"*).

## License

Dual-licensed: **AGPL-3.0-or-later** (open, with network copyleft) **or** a commercial license on request. See [LICENSE](LICENSE) and [COPYING.AGPL](COPYING.AGPL).

## Authors

Christian (sole authority on publication) and Motoko (autonomous co-author). Clone it, fork it, break it.
