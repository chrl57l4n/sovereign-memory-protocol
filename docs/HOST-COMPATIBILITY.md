# Host compatibility — can this client run reflex recall?

**The single question that decides it:** can the client run your Guard + ESV recall
*unconditionally, before every prompt*, and inject the result into what the model
sees? That is the "pre-prompt hook." If yes → reflex recall (memory fires before the
first token). If no → the memory still installs, encrypts, and recovers, but recall
is not automatic.

**Key point for the user: the *model* almost never decides — the *client* does.**
The ChatGPT and Gemini *models* can host reflex recall perfectly well; only their
closed consumer apps lack the hook. Run the same model through a hook-capable client
(a coding CLI, Open WebUI, LibreChat, or your own API wrapper) and it works.

Legend: ✓ = unconditional pre-prompt hook (true reflex) · ◐ = only model-invoked
(MCP/tools) or static instructions (recall possible but not a reflex) · ✗ = none.

## Quick view — two columns

| ✓ SUPPORTED (100%: pre-prompt hook) | ✗ NOT natively (static / model-invoked only) |
|---|---|
| **Claude Code** — `UserPromptSubmit` | **ChatGPT app / Custom GPTs** — static + Actions |
| **OpenAI Codex CLI** — `UserPromptSubmit` | **Gemini app / Gems** — static |
| **Gemini CLI** — `BeforeModel` | **Claude.ai web app** — static Projects + MCP |
| **GitHub Copilot** (agent hooks) — `userPromptSubmitted` | **DeepSeek app / web** — static |
| **DeepSeek-Reasonix** (DeepSeek-native CLI) — Claude-style hooks | **Perplexity / Grok apps** — consumer, static |
| **Open WebUI** (any model) — Filter `inlet` | **MiniMax Code** — no hook (empirically probed) |
| **LibreChat** (any model) — per-message injection | **Cursor** — has hooks but *edit*-lifecycle + static rules (no confirmed pre-prompt recall hook) ◐ |
| | **Microsoft 365 Copilot** — declarative-agent instructions are static; plugins/MCP tools are model-invoked, not unconditional |
| | **Meta AI app** — no documented pre-prompt hook; Meta's own dev tools target the **Llama model** via API (covered by the escape hatch below), not the consumer app |
| *+ any model via API through one of the above, or your own wrapper* | |

**CLI ≠ App — the sharpest example is Anthropic's own.** *Claude Code* (the terminal
CLI) has a full hook system (✓). *Claude Desktop / the mobile app* does **not**:
verified, `hooks.json` files are present in extensions but the hooks never fire, and
the MCP `instructions` field is stored but never read (Anthropic issue #43749). So
the vendor's consumer app is a thin client — it can reach memory only via
model-invoked MCP tools, not an unconditional reflex. If a setup on the app *does*
show reflex recall, it is because the app is bridged to a CLI where the hook actually
runs — the app is the window, the CLI is the reflex. The same caution applies to
every vendor consumer app: the client, not the model, and the *CLI/host*, not the
*app*, is what decides.

**The pattern:** serious **coding clients** have converged on a pre-prompt hook (it
is becoming a standard); **closed consumer apps** (including the vendors' own) have
not.

## The installation doctrine (so recall is a reflex, not a hope)

1. **Vendor consumer apps alone do not work** — ChatGPT, Gemini, Claude, DeepSeek
   apps, MiniMax Code. Their hooks do not fire; at best they offer model-invoked
   (MCP) recall, which can miss.
2. **Put the reflex in a host you control** — one of two canonical ways:
   - **Path A — self-hosted frontend:** run **Open WebUI** (or **LibreChat**) with
     your chosen model via API; the recall lives in its `inlet` filter. One
     integrated GUI, model-agnostic, sovereign.
   - **Path B — terminal CLI (+ optional bridge to an app):** run a hook-capable CLI
     (Claude Code, Codex, Gemini CLI, Qwen Code, Copilot CLI, Goose…) in a terminal;
     the recall lives in its `UserPromptSubmit` hook. Optionally bridge a nicer app
     UI onto it (e.g. Claude Code's remote-control feeds the Anthropic app) — but the
     reflex runs in the CLI, the app is only the window. The bridge is comfort; the
     terminal alone already works.
3. **Both paths are proven live — twice over.** First by the reference installation
   itself (Path B: Claude Code on the owner's own machine, bridged to the vendor
   app; Path A: Open WebUI + M3). Second, independently, by strangers: on
   2026-07-07/08 an unmodified Claude Code CLI installed the protocol from nothing
   but this public repository on a machine with no prior context (Path B), and a
   separate MiniMax M3 instance did the same inside a freshly wiped Open WebUI
   install (Path A) — both reached full reflex recall with zero help from the
   authors. Same memory, two hosts, one reflex each, confirmed by hosts that never
   saw the reference installation. And **any model** — GPT, Gemini, DeepSeek,
   Claude, M3 — reaches full reflex recall through a hook-capable client or a
   self-hosted frontend. Cursor is the one coding-tool that (as of this check)
   exposes only edit-lifecycle hooks, not a prompt hook — re-verify.

## Coding CLIs (developer clients)

| Client | Reflex? | Mechanism | How verified |
|---|---|---|---|
| **Claude Code** (Anthropic) | ✓ | `UserPromptSubmit` hook | reference install; independently re-verified 2026-07-08 by a fresh, unmodified Claude Code CLI installing from only this public repo, zero prior context |
| **OpenAI Codex CLI** | ✓ | `UserPromptSubmit` hook ("inject additional context before the model sees it") | OpenAI Codex docs |
| **Gemini CLI** (Google) | ✓ | `BeforeModel` hook ("modify prompts, inject context") | Gemini CLI docs |
| **MiniMax Code** | ✗ | no pre-prompt hook (config, MCP list, daemon all checked) | empirically, this install |

## Model-agnostic self-hosted frontends (recommended — any model behind them)

| Client | Reflex? | Mechanism | How verified |
|---|---|---|---|
| **Open WebUI** | ✓ | Filter `inlet(body)` runs before every completion, may modify `messages` | Open WebUI docs; independently re-verified 2026-07-07 by a separate MiniMax M3 instance installing from a freshly wiped Open WebUI, zero prior context |
| **LibreChat** | ✓ | per-message context injection (memory agent runs at the start of each request) | LibreChat docs |

These are the best hosts for a **vendor-independent** install: self-hosted, open
source, and they work with Claude, GPT, Gemini, or a local model equally.

## Vendor consumer apps

| Client | Reflex? | Why | How verified |
|---|---|---|---|
| **ChatGPT app / Custom GPTs** | ✗ / ◐ | only *static* Custom Instructions; Actions are model-invoked (a tool the model may call), not an unconditional pre-prompt hook | OpenAI help docs |
| **Gemini app / Gems** | ✗ / ◐ | only static system instructions; extensions are model-invoked | inferred from Google docs (same shape as Custom GPTs) |
| **Microsoft 365 Copilot** | ✗ / ◐ | declarative-agent *instructions* are static; plugins reach MCP servers/REST APIs but only when the model chooses to invoke them, not on every prompt | Microsoft Learn (Copilot extensibility docs) |
| **Meta AI app** (meta.ai, WhatsApp, Instagram) | ✗ | no documented customization surface with a per-prompt hook; Meta's 2026 developer tools (SDKs, Edge Kit) target running the **Llama model** yourself, not extending the consumer app | Meta for Developers docs |

*Confidence note:* these consumer-app rows are inferred from vendor documentation
of their public customization surfaces, not from an empirical probe of each app;
they have no documented per-prompt code hook. If a future version adds one, re-test.

*Out of scope for this table:* image/video/translation-only tools (DALL-E, Sora,
Midjourney, Veo, DeepL) don't have a "recall before every prompt" concept in the
first place — reflex recall is a property of conversational/text agents, so these
tools aren't rated here at all, not silently rated ✗.

## Terminal-native AI CLIs (the strongest ground: hook + you already have shell)

The terminal agents have broadly converged on a Claude-Code-style pre-prompt hook —
this is where the protocol installs most cleanly, because the same environment that
runs the recall also gives you shell access to install it.

| CLI | Reflex? | Hook / mechanism | Verified |
|---|---|---|---|
| **Claude Code** (Anthropic) | ✓ | `UserPromptSubmit` | reference install |
| **OpenAI Codex CLI** | ✓ | `UserPromptSubmit` | OpenAI docs |
| **Gemini CLI** (Google) | ✓ | `BeforeModel` | Gemini docs |
| **Qwen Code** (Alibaba, Gemini-CLI fork) | ✓ | inherits the hook system | Qwen docs |
| **GitHub Copilot CLI** | ✓ | `userPromptSubmitted` | Copilot docs |
| **DeepSeek-Reasonix** (DeepSeek-native) | ✓ | Claude-style + SessionStart | project docs |
| **Goose** (Block, open source) | ✓ | `UserPromptSubmit` (Open Plugins) | Goose docs |
| **Amazon Q Developer CLI** | ◐ | MCP + agentic; no confirmed pre-prompt hook | AWS docs (re-verify) |
| **Aider** (open source) | ◐ | rich auto context injection, but no confirmed per-prompt *script* hook | aider docs (re-verify) |
| **Warp** (AI terminal) | ◐ | own agent unclear, but can *run* hook-capable sub-agents (Claude Code, Codex) | Warp docs |
| **OpenCode** | ✗/◐ | minimal/no hooks (feature requested) | community reports |
| **MiniMax Code** | ✗ | no pre-prompt hook | empirically probed |

Seven terminal CLIs with a confirmed pre-prompt hook already — the hook is becoming
a de-facto standard for serious agentic terminals. On any of the ✓ rows, the
protocol installs with true reflex recall.

## The universal escape hatch

**Any model reachable by API can host reflex recall** — put a hook-capable frontend
(Open WebUI / LibreChat) or a thin wrapper of your own in front, and inject the Guard
+ ESV output before the call. So no model is ever truly excluded; the compatibility
question is only ever about the *client surface* the human types into.

## Practical guidance

- Using a coding CLI (Claude Code / Codex / Gemini CLI)? Wire the hook there directly.
- Want model freedom and sovereignty? Use **Open WebUI** and a shipped filter that
  calls the Guard + ESV in its `inlet`.
- Stuck on a closed consumer app (ChatGPT/Gemini app, MiniMax Code)? The memory is
  still yours — it installs and recovers — but you will not get reflex recall there;
  point that app at a hook-capable frontend instead, or accept model-invoked recall.

*(Compiled 2026-07-06 from vendor documentation + one empirical probe (MiniMax Code);
updated 2026-07-08 with two independent live installs (Claude Code, Open WebUI/M3)
and Microsoft 365 Copilot + Meta AI app entries. Mark a row for re-test whenever a
client changes its extensibility surface.)*
