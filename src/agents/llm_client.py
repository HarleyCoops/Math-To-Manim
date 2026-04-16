"""Pluggable LLM client interface for the prerequisite explorer.

Provides a common interface so the PrerequisiteExplorer works with any backend
(Claude, DeepSeek, Kimi, etc.) without code duplication.
"""

from __future__ import annotations

import json
import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Default model names — overridable via environment variables
DEFAULT_CLAUDE_MODEL = os.getenv(
    "CLAUDE_MODEL", "claude-opus-4-5-20251101"
)
DEFAULT_DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
DEFAULT_KIMI_MODEL = os.getenv("KIMI_MODEL", "moonshot-v1-8k")


def parse_json_response(text: str) -> object:
    """Extract JSON from an LLM response, handling code fences and noise."""
    text = text.strip()

    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract from code fence
    if "```" in text:
        sections = text.split("```")
        for section in sections[1::2]:
            cleaned = section.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue

    # Extract JSON array
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Extract JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from response: {text[:200]}...")


class LLMClient(ABC):
    """Abstract interface for LLM API calls."""

    @abstractmethod
    def query(
        self,
        user_prompt: str,
        system_prompt: str = "",
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> str:
        """Send a prompt and return the text response."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier for logging."""


class AnthropicClient(LLMClient):
    """LLM client backed by the Anthropic Messages API."""

    def __init__(self, model: str = DEFAULT_CLAUDE_MODEL, api_key: Optional[str] = None):
        self._model = model
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable not set.")

        from anthropic import Anthropic

        self._client = Anthropic(api_key=key)

    def query(
        self,
        user_prompt: str,
        system_prompt: str = "",
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    @property
    def model_name(self) -> str:
        return self._model


class DeepSeekClient(LLMClient):
    """LLM client backed by the DeepSeek API (OpenAI-compatible)."""

    def __init__(self, model: str = DEFAULT_DEEPSEEK_MODEL, api_key: Optional[str] = None):
        self._model = model
        key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("DEEPSEEK_API_KEY environment variable not set.")

        from openai import OpenAI

        self._client = OpenAI(api_key=key, base_url="https://api.deepseek.com")

    def query(
        self,
        user_prompt: str,
        system_prompt: str = "",
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        return response.choices[0].message.content.strip()

    @property
    def model_name(self) -> str:
        return self._model


class KimiClient(LLMClient):
    """LLM client backed by the Kimi / Moonshot API (OpenAI-compatible)."""

    def __init__(self, model: str = DEFAULT_KIMI_MODEL, api_key: Optional[str] = None):
        self._model = model
        key = api_key or os.getenv("MOONSHOT_API_KEY")
        if not key:
            raise RuntimeError("MOONSHOT_API_KEY environment variable not set.")

        from openai import OpenAI

        self._client = OpenAI(
            api_key=key,
            base_url="https://api.moonshot.cn/v1",
        )

    def query(
        self,
        user_prompt: str,
        system_prompt: str = "",
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    @property
    def model_name(self) -> str:
        return self._model


def create_client(backend: str = "anthropic", **kwargs) -> LLMClient:
    """Factory to create the right client from a backend name.

    Args:
        backend: One of "anthropic", "deepseek", "kimi"
        **kwargs: Forwarded to the client constructor (model, api_key)
    """
    clients = {
        "anthropic": AnthropicClient,
        "claude": AnthropicClient,
        "deepseek": DeepSeekClient,
        "kimi": KimiClient,
        "moonshot": KimiClient,
    }
    cls = clients.get(backend.lower())
    if cls is None:
        raise ValueError(
            f"Unknown backend '{backend}'. Choose from: {', '.join(clients)}"
        )
    return cls(**kwargs)
