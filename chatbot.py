"""
LexieLingua - Ultra-fast ChatGPT-grade conversational engine with instant token streaming.
"""

import os
import re
from openai import AzureOpenAI

def _clean_base_url(url: str) -> str:
    if not url:
        return ""
    match = re.match(r"^(https?://[^/]+)", url.strip())
    return match.group(1) if match else url.strip().rstrip("/")

def is_ai_mode_available() -> bool:
    return bool(
        os.getenv("AZURE_OPENAI_API_KEY")
        and os.getenv("AZURE_OPENAI_ENDPOINT")
        and os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )

_CLIENT = None

def get_client():
    global _CLIENT
    if _CLIENT is None and is_ai_mode_available():
        base_endpoint = _clean_base_url(os.environ["AZURE_OPENAI_ENDPOINT"])
        api_key = os.environ["AZURE_OPENAI_API_KEY"].strip()
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview").strip()
        _CLIENT = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=base_endpoint,
            api_key=api_key,
        )
    return _CLIENT

def stream_answer(question: str, history: list):
    """Streams tokens from GPT-5.4 with sub-second TTFT."""
    if not is_ai_mode_available():
        yield "⚠️ Azure API credentials missing in `.env`. Running in offline mode."
        return

    client = get_client()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4").strip()

    system_prompt = (
        "You are Karpom AI, a brilliant, unrestricted, and highly capable academic assistant.\n\n"
        "Guidelines:\n"
        "1. Answer ANY question across coding, computer science, mathematics, literature, and analysis.\n"
        "2. For coding: Provide clean, fully working code with clear markdown syntax highlighting and comments.\n"
        "3. Provide structured, accurate, and direct responses without unnecessary filler."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-8:]:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    try:
        response_stream = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_completion_tokens=4096,
            stream=True,
        )

        for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content

    except Exception as exc:
        yield f"⚠️ **Azure API Error:** `{exc}`"