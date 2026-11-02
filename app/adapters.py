"""Opt-in adapter for an OpenAI-compatible chat completions API.

No network request is made unless a caller explicitly invokes
run_chat_completion with a configured API key.
"""
import os
import urllib.error
import urllib.request
import json

def run_chat_completion(prompt: str, model: str, *, endpoint: str | None = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    url = endpoint or "https://api.openai.com/v1/chat/completions"
    if not url.startswith("https://"):
        raise ValueError("Only HTTPS endpoints are supported")
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Provider returned HTTP {exc.code}") from exc
    return payload["choices"][0]["message"]["content"]
