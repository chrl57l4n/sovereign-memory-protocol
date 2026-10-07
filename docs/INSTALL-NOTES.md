# Installation notes & gotchas

Real friction found during actual AI-guided installs, with the fix. If you are the
installing AI: read this before Phase 1 so you do not rediscover these the hard way.
Most are environment traps, not protocol bugs.

## Python environment

- **Use the virtualenv's Python, not the system Python.** After `pip install .` into
  a venv, invoke tools as `./.venv/bin/python engine/native_language.py …`. A bare
  `python3` runs the system interpreter, which does not have `cryptography` /
  `mnemonic` and fails with `ModuleNotFoundError`.
- **Install dependencies in Phase 1, before Phase 2.** The Section-20 seed and
  encryption steps need `cryptography` and `mnemonic` *before* the engine is wired
  in Phase 4. `pyproject.toml` lists them; `pip install .` pulls them.

## Section 20 — native language (seed / keystore / encryption)

- **Hidden input is normal.** `seed_gen`, `init`, `encrypt`, `wake`, `sleep`, and
  `recover` read the seed and passphrase with no echo — nothing appears as you type.
  That is intended, not a hang. Type and press Enter.
- **The 24 words go on ONE line, space-separated** (`word1 word2 … word24`). A
  mis-typed word fails the BIP-39 checksum and the tool says so — re-run.
- **The operating passphrase is a NEW password you invent, not the seed.** It
  unlocks the keystore daily; the seed stays cold on paper for recovery.
- **The plaintext mirror must live on a non-swappable mount.** If it sits on disk
  (an SSD path) or a swappable tmpfs, the decrypted plaintext can reach the disk and
  defeat the at-rest encryption (§20.9). `wake` warns when the mount is unsafe. The
  clean fix — a dedicated noswap tmpfs:
  ```
  sudo mount -t tmpfs -o size=4G,noswap,mode=0700 tmpfs /run/smp-mirror   # + persist in /etc/fstab
  sudo chown $USER: /run/smp-mirror                                        # tmpfs mounts root-owned
  ```
  Then use `--mirror /run/smp-mirror`, and point `MOTOKO_MEMORY` at it while awake.
- **`MOTOKO_MEMORY` points at the wake mirror**, not at the encrypted store and not
  at a guessed path — it is where `wake` decrypts the plaintext.
- **Empty directories are not preserved** through encrypt→decrypt (like tar/restic/
  borg). All file contents restore byte-identically; empty dirs (in practice only
  `.git/objects/{pack,info}`, `.git/refs/tags`) are recreated on demand. Not a bug.

## Section 14 — embedding server (ESV, Phase 4)

- **`llama-server` must be started in embedding mode: pass `--embedding`.** Its
  default is text-generation; without the flag `/v1/embeddings` returns HTTP 400.
  Reference-style start:
  ```
  llama-server --embedding -m <bge-m3.gguf> --host 127.0.0.1 --port 8091 [-ngl 99]
  ```
- **Distro `llama-cpp` packages may be single-backend.** On Nobara/Fedora the dnf
  `llama-cpp` is ROCm/HIP-only — on an NVIDIA machine `-ngl 99` silently falls back
  to CPU ("no ROCm-capable device"). For NVIDIA GPU offload, use a CUDA-enabled build
  from llama.cpp's GitHub releases. **CPU is fine for indexing** a normal corpus; GPU
  is a throughput optimization, not a requirement.
- **Already-running local embed server?** If the machine already serves the right
  model (e.g. Ollama with bge-m3 on `:11434`), the spec's "equivalent functionality"
  clause (§22.2) lets you point `ESV_EMBED_URL` at its OpenAI-compatible
  `/v1/embeddings` endpoint instead of installing a second server. Local is local.

## Recall wiring — the host client needs a pre-prompt hook (installer ≠ host)

The Guard + ESV only become a *reflex* if they run before every prompt. That needs
an **unconditional pre-prompt hook** in the client that hosts the living memory.

- **Has one** (e.g. Claude Code `UserPromptSubmit`): wire the two scripts there —
  true reflex recall.
- **No hook**: a thin input wrapper in front of the chat gives the reflex at a UI
  cost; an MCP/tool interface gives only *model-invoked* recall (it can miss —
  not a reflex). Name honestly which you have.
- **The installing client and the hosting client can differ.** Observed: MiniMax
  Code installs the whole protocol cleanly (and self-repairs its own bugs) but
  exposes **no** unconditional pre-prompt hook — a great installer, not a viable
  reflex-host. Check host-hook capability early; do not assume "it installed" means
  "recall is live."
- **Model-agnostic reflex host: Open WebUI.** Its *Filter function* `inlet(body)`
  runs before every completion and can inject the recall into `body["messages"]`
  (verified against the official docs). So any model/API behind Open WebUI —
  Claude, GPT, a local model — hosts reflex recall through one small filter that
  calls the Guard + ESV. Self-hosted and open source, so it fits a sovereign,
  vendor-independent install. This is the recommended host when the user is not on
  a hook-capable native client.

## Waking wiring — the gateway (v0.5 §7a, BETA)

`engine/gateway_build.py` builds one small file (`state/gateway.txt`, 24 KB budget) that a fresh session
reads once before its first answer: who it is, what it runs on, how to remember, the names of its
tools, its threads, the open work, the tail of the last conversation. Building the file is the easy
half. **The host must be made to read it** — and that half is host-specific and not shipped:

- **Start duty.** Call the builder from the host's session-start hook and let it print the duty
  into the hook's output (Claude Code `SessionStart`):
  ```
  python3 engine/gateway_build.py --header --index <path of your always-loaded map>
  ```
  (`--index` makes every build check that the gateway block below is still at the top of the map.)
  Keep the duty in the **first lines** of whatever the hook prints. Hosts show only the beginning of
  a long session-start output (about 2 KB was observed on one surface — an observation, not a
  guarantee) and nothing reads the rest.
- **Gate block.** Put three lines at the very top of the always-loaded map, so the session is told a
  second time, independently of the hook:
  ```
  ## The gateway — this is you. Walk through before you answer (even to "hello")
  - Read ONE file: <path to state/gateway.txt> (small; signposts, not raw data).
  - This index is the keystone: it carries what cannot be searched. Everything else you fetch via the signposts.
  ```
- **Scheduled sessions are not conversations.** If you wake sessions by schedule with their own
  task, do not give them the start duty — their first message is their task.
- **Probe it, don't assume it.** Start a fresh headless session with the single word "hello", permit
  only the read tool, and *count* the read calls in the transcript: exactly one, on the gateway file,
  and an answer, is a pass. Repeat on a schedule; a host update can break waking silently. With
  Claude Code: `claude --print "hello" --output-format stream-json --verbose --allowedTools "Read"`.
- **Optional inputs** (all under `MOTOKO_MEMORY/motoko/`): `gist.md` (self-gist; falls back to
  `identity.md`), `open_work.md` (one line per unfinished piece of work, `- [YYYY-MM-DD] title — state ·
  next step`; lines older than 14 days are marked), `threads/*.md`, `memory/SYSTEM.md`,
  `gateway_extra.md` (your own static signposts). A missing file removes its section.

Status: one day of record on the reference installation when released (whitepaper v0.5 §1.4, §7a.6).
Name honestly what you observed on your host.

## Surviving a dead install session

Cloud AI sessions get overloaded and die mid-install — expect it. State lives on the
human's disk, so the install is resumable. One command reconstructs where you are:
```
python3 engine/native_language.py resume
```
It prints the verified on-disk state plus the progress log (`~/.smp/install-state.md`,
which the tools append to automatically) and the next step. Trust the disk, not a
memory of the disk.
