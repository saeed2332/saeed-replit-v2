#!/usr/bin/env python3
import osfrom autogen import ConversableAgentnfrom autogen.oai import OpenAIWrapperper
from minimal_fix import MinimalFixExtension
from file_manager import FileManager
from vector_memory import VectorMemory
import sys

SYSTEM_MSG = ("You are a senior software-engineer agent with shell access. "
              "When a command fails, inspect stderr, edit code via FileManager, "
              "and retry until exit-code 0 and **all** tests pass. "
              "Store helpful context in VectorMemory. For research, use web_search tool. "
              "Abort if >10 files changed or task >5min.")

def build_dev():
    config_list = []
    if os.getenv("XAI_API_KEY"):
        config_list.append({
            "model": "grok-4",
            "api_key": os.getenv("XAI_API_KEY"),
            "base_url": "https://api.x.ai/v1"
        })
    else:
        config_list.append({
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY")
        })

    dev = ConversableAgent(
        name="dev",
        system_message=SYSTEM_MSG,
        llm_config={"config_list": config_list},
        human_input_mode="NEVER"
    )

    tools = [
        MinimalFixExtension("fix_memory.json"),
        FileManager(),
        VectorMemory(".vector_store"),
        {"function": web_search_tool, "name": "web_search", "description": "Search web for info"}
    ]
    for tool in tools:
        dev.register_for_llm(tool)

    return dev

def web_search_tool(query: str) -> str:
    import requests
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url)
    return response.text[:1000]

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]).strip() or "pytest -q tests"
    dev = build_dev()
    resp = dev.initiate_chat(recipient=dev, message=task)
    print(resp.chat_history[-1]["content"] if resp.chat_history else "No response")