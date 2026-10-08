"""xAI Responses API backend. Authentication is XAI_API_KEY."""

from __future__ import annotations

from grok.client import XAIClient


class XAIAPIBackend(XAIClient):
    name = "xai-api"
