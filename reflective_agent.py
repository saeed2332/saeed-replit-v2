"""reflective_agent.py  –  Phase 8 helper
────────────────────────────────────────────────────────────────────────────
• shell(cmd)   → run bash / python with self-healing and log to VectorMemory
• ask(question)→ ask GPT-4o-mini using the K most relevant memories as
                 additional context
"""
from __future__ import annotations

from uuid import uuid4
from typing import List, Dict, Any

import openai                           # 👉 use the official client
from minimal_fix   import MinimalFixExtension
from vector_memory import VectorMemory


class ReflectiveAgent:
    def __init__(self, k: int = 3):
        self.k       = k
        self.memory  = VectorMemory(".vector_store")
        self.fixer   = MinimalFixExtension("fix_memory.json")
        self.client  = openai.OpenAI()                 # honours $OPENAI_API_KEY

    # ────────────────────────────────────────────────────────────────
    #  public api
    # ────────────────────────────────────────────────────────────────
    def shell(self, cmd: str) -> str:
        """Run a command with self-healing; store a short summary."""
        out = self.fixer.run(cmd)
        snippet = out[:2_000]          # keep vector-store entries small
        self.memory.add(f"CMD: {cmd}\nOUT: {snippet}")
        return out

    def ask(self, question: str,  system_msg: str | None = None) -> str:
        """Answer `question`, seeding GPT-4o with the K nearest memories."""
        recalls = self.memory.query(question, top_k=self.k)
        context = "\n\n".join(f"* {doc}" for _, doc in recalls)

        messages: List[Dict[str, Any]] = [
            {"role": "system",
             "content": system_msg or "You are an expert developer assistant."},
            {"role": "user",
             "content": (
                 "### Relevant past context\n"
                 f"{context or '(none)'}\n\n"
                 "### Question\n"
                 f"{question}"
             )},
        ]

        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content
