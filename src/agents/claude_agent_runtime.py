"""Utility helpers for interacting with Claude via the Agent SDK.

The Math-To-Manim agents historically spoke to the Anthropic Messages API
directly. Certain newer Claude releases are distributed primarily through the
Claude Code / Agent SDK interface, which does not require specifying an exact
`model=` name.  This module provides a minimal wrapper so existing synchronous
call sites can fall back to the Agent SDK whenever the legacy endpoint is
unavailable (for example, when a Messages API request returns a 404 for a
model that now lives exclusively in Claude Code).
"""

from __future__ import annotations

import asyncio
from typing import Optional

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    ToolResultBlock,
    query,
)


async def _run_query_async(
    prompt: str,
    *,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """Internal async helper that streams responses from Claude Code."""

    options = ClaudeAgentOptions()
    if system_prompt is not None:
        options.system_prompt = system_prompt

    # Pass temperature/max tokens as extra CLI arguments when provided.
    if temperature is not None:
        options.extra_args["temperature"] = str(temperature)
    if max_tokens is not None:
        options.extra_args["max-tokens"] = str(max_tokens)

    chunks: list[str] = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    chunks.append(block.text)
                elif isinstance(block, ToolResultBlock):
                    content = block.content
                    if isinstance(content, str):
                        chunks.append(content)
                    elif isinstance(content, list):
                        for item in content:
                            text = item.get("text")
                            if text:
                                chunks.append(text)

    return "".join(chunks).strip()


def run_query_via_sdk(
    prompt: str,
    *,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """Public synchronous wrapper used by legacy call sites."""

    return asyncio.run(
        _run_query_async(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    )


__all__ = ["run_query_via_sdk"]


