#!/usr/bin/env python3
"""
agent_runner.py – Phase 9
────────────────────────────────────────────────────────────────────────────
Launch one AutoGen ConversableAgent (**dev**) and equip it with:

• MinimalFixExtension – run shell / python; auto-heal simple NameErrors
• FileManager         – read / write any workspace file
• VectorMemory        – store useful context across sessions

Usage
-----
    python agent_runner.py                    → default: pytest -q tests
    python agent_runner.py "echo hello"       → run any ad-hoc shell task
"""

from __future__ import annotations

import sys
from autogen.agentchat.conversable_agent import ConversableAgent as Agent
from autogen.oai import OpenAIWrapper

from minimal_fix   import MinimalFixExtension
from file_manager  import FileManager
from vector_memory import VectorMemory


SYSTEM_MSG = (
    "You are a senior software-engineer agent with shell access. "
    "Whenever a command fails, inspect stderr, edit code via FileManager, "
    "and retry until the exit-code is 0 **and** all tests pass. "
    "Store helpful context in VectorMemory for future tasks."
)


# ────────────────────────────────────────────────────────────────
def build_dev() -> Agent:
    """Create the ‘dev’ agent and wire in LLM + tools, coping with every
    historical AutoGen API variant."""
    dev = Agent(name="dev", system_message=SYSTEM_MSG)

    # Attach the OpenAI client  (attribute name changed across releases)
    llm = OpenAIWrapper()
    for attr in ("client", "_client", "llm", "_llm"):
        if hasattr(dev, attr):
            setattr(dev, attr, llm)
            break

    # Tools to register
    tools = [
        MinimalFixExtension("fix_memory.json"),
        FileManager(),
        VectorMemory(".vector_store"),
    ]

    # Register tools – try every known method name
    for tool in tools:
        for method in ("add_tool", "register_tool"):
            if hasattr(dev, method):
                getattr(dev, method)(tool)
                break
        else:                                  # very old 0.7 / 0.8 releases
            if hasattr(dev, "_tools"):
                dev._tools.append(tool)
            else:
                raise RuntimeError(
                    "Unknown Agent API – cannot attach tools"
                )

    return dev


# ────────────────────────────────────────────────────────────────
# entry-point
# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    task = " ".join(sys.argv[1:]).strip() or "pytest -q tests"
    dev  = build_dev()

    # AutoGen ≥ 0.9:  dev.run() returns RunResponse
    if hasattr(dev, "run"):
        resp = dev.run(task)

    # AutoGen 0.8.x:  dev.start_chat() returns a list of messages
    elif hasattr(dev, "start_chat"):
        resp = dev.start_chat(task)

    else:
        raise RuntimeError("Cannot locate a suitable entry-point on Agent")

    # ── pretty-print the agent’s last reply, if any ────────────────────
    try:
        from autogen.io.run_response import RunResponse  # type: ignore
    except Exception:
        RunResponse = ()  # fallback when module doesn’t exist

    if isinstance(resp, RunResponse) and resp.chat_history:
        print(resp.chat_history[-1]["content"])
    elif isinstance(resp, list) and resp:
        print(resp[-1]["content"])
