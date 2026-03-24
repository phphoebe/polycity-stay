"""Wire Ollama (OpenAI-compatible) as default chat-completions backend."""

from __future__ import annotations

from openai import AsyncOpenAI

from agents import set_default_openai_api, set_default_openai_client, set_tracing_disabled

from polycity_stay.config import OLLAMA_API_KEY, OLLAMA_BASE_URL

_configured = False


def ensure_ollama() -> None:
    global _configured
    if _configured:
        return
    client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
    set_default_openai_client(client=client, use_for_tracing=False)
    set_default_openai_api("chat_completions")
    set_tracing_disabled(True)
    _configured = True
