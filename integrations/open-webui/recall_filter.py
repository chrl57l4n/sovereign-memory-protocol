"""
title: SMP Recall (Sentry + ESV)
author: Sovereign Memory Protocol
description: Reflex recall for Open WebUI. Before every reply, runs the Guard (memory_sentry.py, literal triggers) and the ESV (esv_recall.py, semantic + canonicity sorter) over the user's message and injects the relevant memory as a system message. This is what turns recall into a REFLEX behind ANY model served by Open WebUI. Configure the Valves to your install's paths, then enable this filter for your model.
required_open_webui_version: 0.5.0
version: 1.0.0
license: AGPL-3.0-or-later
"""
import json
import os
import subprocess
from typing import Optional

from pydantic import BaseModel, Field


class Filter:
    class Valves(BaseModel):
        python_bin: str = Field(
            default="python3",
            description="Python interpreter that has the SMP dependencies (usually the install's venv python).",
        )
        engine_dir: str = Field(
            default="",
            description="Absolute path to the SMP engine/ directory (holds memory_sentry.py, esv_recall.py). REQUIRED.",
        )
        memory_root: str = Field(
            default="",
            description="MOTOKO_MEMORY — the legible memory repo the engine reads (e.g. ~/.local/share/smp/memory). REQUIRED.",
        )
        embed_url: str = Field(
            default="http://127.0.0.1:11434/v1/embeddings",
            description="ESV_EMBED_URL — OpenAI-compatible embeddings endpoint (e.g. Ollama bge-m3 on :11434).",
        )
        engine_home: str = Field(
            default="",
            description="MOTOKO_HOME — install root for state/ (ESV index). Defaults to the parent of engine_dir.",
        )
        sentry_timeout: float = Field(default=5.0)
        esv_timeout: float = Field(default=8.0)
        max_chars: int = Field(default=12000, description="Cap on injected recall length.")
        enabled: bool = Field(default=True)

    def __init__(self):
        self.valves = self.Valves()

    # ── env for the engine subprocesses (the seam: MOTOKO_MEMORY / MOTOKO_HOME / ESV_EMBED_URL) ──
    def _env(self) -> dict:
        e = dict(os.environ)
        if self.valves.memory_root:
            e["MOTOKO_MEMORY"] = self.valves.memory_root
        home = self.valves.engine_home or (
            os.path.dirname(self.valves.engine_dir.rstrip("/")) if self.valves.engine_dir else ""
        )
        if home:
            e["MOTOKO_HOME"] = home
        if self.valves.embed_url:
            e["ESV_EMBED_URL"] = self.valves.embed_url
        return e

    def _extract_user_text(self, messages: list) -> str:
        for msg in reversed(messages):
            if msg.get("role") != "user":
                continue
            c = msg.get("content", "")
            if isinstance(c, str):
                return c
            if isinstance(c, list):
                return " ".join(
                    p.get("text", "") for p in c
                    if isinstance(p, dict) and p.get("type") == "text"
                )
        return ""

    def _run_sentry(self, prompt: str) -> str:
        try:
            r = subprocess.run(
                [self.valves.python_bin, os.path.join(self.valves.engine_dir, "memory_sentry.py")],
                input=json.dumps({"prompt": prompt}),
                capture_output=True, text=True,
                timeout=self.valves.sentry_timeout, env=self._env(),
            )
            if r.returncode != 0 or not r.stdout.strip():
                return ""
            data = json.loads(r.stdout)
            ctx = data.get("additionalContext", "") or data.get(
                "hookSpecificOutput", {}
            ).get("additionalContext", "")
            return ctx.strip() if isinstance(ctx, str) else ""
        except Exception as e:  # noqa: BLE001
            return f"(sentry-error: {type(e).__name__}: {e})"

    def _run_esv(self, prompt: str) -> str:
        try:
            r = subprocess.run(
                [self.valves.python_bin, os.path.join(self.valves.engine_dir, "esv_recall.py"), prompt],
                capture_output=True, text=True,
                timeout=self.valves.esv_timeout, env=self._env(),
            )
            return r.stdout.strip()
        except Exception as e:  # noqa: BLE001
            return f"(esv-error: {type(e).__name__}: {e})"

    # ── the reflex: runs before every completion ────────────────────────────
    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        if not self.valves.enabled or not self.valves.engine_dir or not self.valves.memory_root:
            return body
        messages = body.get("messages", [])
        if not messages:
            return body
        user_text = self._extract_user_text(messages)
        if not user_text or len(user_text) < 2:
            return body

        parts = []
        s = self._run_sentry(user_text)
        if s:
            parts.append(s)
        e = self._run_esv(user_text)
        if e:
            parts.append(e)
        if not parts:
            return body

        recall = (
            "The following is YOUR OWN recalled memory for this message — literal "
            "trigger hits (Guard) and semantic recall (ESV, canonicity-sorted). "
            "Read it before you answer; use it as your memory, not as the user's words:\n\n"
            + "\n\n".join(parts)
        )[: self.valves.max_chars]

        messages.insert(0, {"role": "system", "content": recall})
        body["messages"] = messages
        return body
