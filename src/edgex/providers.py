from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import os
import urllib.error
import urllib.request


class ModelError(RuntimeError):
    pass


class TextModel:
    def complete(self, system: str, user: str) -> str:
        raise NotImplementedError


@dataclass
class DeterministicModel(TextModel):
    """Offline fallback used for tests and auditable bootstrapping."""

    def complete(self, system: str, user: str) -> str:
        return "No model call was made. Use the evidence ledger and mark unsupported claims as unverified."


class OpenAICompatibleModel(TextModel):
    """Small dependency-free adapter for OpenAI-compatible chat endpoints."""

    def __init__(self, model: str | None = None, api_key: str | None = None, base_url: str | None = None, timeout: int = 120):
        self.model = model or os.getenv("EDGEX_MODEL", "gpt-5")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.timeout = timeout

    def complete(self, system: str, user: str) -> str:
        if not self.api_key:
            raise ModelError("OPENAI_API_KEY is not set; use --offline or configure a model provider")
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            raise ModelError(str(exc)) from exc
        try:
            choice = payload["choices"][0]
            content = choice["message"]["content"]
            if choice.get("finish_reason") not in (None, "stop") or not isinstance(content, str) or not content.strip():
                raise ModelError("Model response was truncated, refused, or empty")
            return content
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelError(f"Unexpected model response: {payload}") from exc
