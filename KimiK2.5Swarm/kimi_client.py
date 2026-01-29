"""
Kimi K2.5 Unified Client - Production-grade API client with mode support.

This module provides a unified facade for all Kimi K2.5 operations with:
- Mode-aware parameter injection (INSTANT, THINKING, AGENT, SWARM)
- Structured KimiResponse dataclass with convenience properties
- Retry decorators for resilience
- Async/sync dual support
- Tool calling loop with callbacks
- Backward compatibility with original implementation

Example:
    from kimi_client import KimiClient, KimiMode

    client = KimiClient()

    # Simple chat
    response = client.chat("Hello!")

    # With thinking mode
    response = client.chat("Solve this problem", mode=KimiMode.THINKING)
    print(response.reasoning)

    # Tool calling
    response = client.execute_with_tools(
        "Search for information",
        tools=tools,
        tool_map=tool_map
    )
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generator, List, Optional, Union

from openai import AsyncOpenAI, OpenAI

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
    HAS_TENACITY = True
except ImportError:
    HAS_TENACITY = False
    # Fallback decorator that does nothing
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    stop_after_attempt = lambda x: None
    wait_exponential = lambda **kwargs: None

from config import (
    APIConfig,
    KimiMode,
    ModeConfig,
    MODE_CONFIGS,
    get_mode_config,
    # Legacy imports for backward compatibility
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    KIMI_K2_MODEL,
    MOONSHOT_API_KEY,
    MOONSHOT_BASE_URL,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Response Dataclasses
# =============================================================================


@dataclass
class KimiResponse:
    """
    Structured response from Kimi K2.5.

    Provides convenience properties for common operations.

    Attributes:
        content: The main text content of the response
        reasoning: Thinking/reasoning trace (only in THINKING mode)
        tool_calls: List of tool calls if model requested tools
        finish_reason: Why the model stopped (stop, tool_calls, length)
        usage: Token usage statistics
        mode: The mode used for this response
        raw_response: The original API response dictionary
    """
    content: str
    reasoning: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: str = "stop"
    usage: Optional[Dict[str, int]] = None
    mode: KimiMode = KimiMode.THINKING
    raw_response: Optional[Dict[str, Any]] = None

    @property
    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return self.finish_reason == "tool_calls" and bool(self.tool_calls)

    @property
    def total_tokens(self) -> int:
        """Get total token count."""
        if self.usage:
            return self.usage.get("total_tokens", 0)
        return 0

    @property
    def first_tool_call(self) -> Optional[Dict[str, Any]]:
        """Get the first tool call if present."""
        if self.tool_calls and len(self.tool_calls) > 0:
            return self.tool_calls[0]
        return None


@dataclass
class StreamChunk:
    """
    A chunk from streaming response.

    Attributes:
        content: Text content in this chunk
        reasoning: Reasoning content if in thinking mode
        is_reasoning: Whether this chunk is reasoning vs content
        finish_reason: Set when stream ends
    """
    content: str = ""
    reasoning: str = ""
    is_reasoning: bool = False
    finish_reason: Optional[str] = None


# =============================================================================
# Main Client Class
# =============================================================================


class KimiClient:
    """
    Unified client for Kimi K2.5 supporting all operating modes.

    This client provides a facade for all Kimi operations with:
    - Automatic mode-based parameter configuration
    - Retry logic for resilience
    - Both sync and async interfaces
    - Tool calling loop support
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        default_mode: KimiMode = KimiMode.THINKING,
    ):
        """
        Initialize the Kimi client.

        Args:
            api_key: Moonshot API key (defaults to MOONSHOT_API_KEY env var)
            base_url: API base URL (defaults to Moonshot endpoint)
            model: Model name (defaults to KIMI_K2_MODEL)
            default_mode: Default operating mode
        """
        self.api_key = api_key or MOONSHOT_API_KEY
        if not self.api_key:
            raise ValueError(
                "MOONSHOT_API_KEY environment variable not set. "
                "Please set it in your .env file or pass api_key parameter."
            )

        self.api_key = self.api_key.strip()
        self.base_url = base_url or MOONSHOT_BASE_URL
        self.model = model or KIMI_K2_MODEL
        self.default_mode = default_mode

        # Initialize clients
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def _get_mode_params(self, mode: KimiMode) -> Dict[str, Any]:
        """Get API parameters for a specific mode."""
        config = get_mode_config(mode)
        params = {
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
        }
        if config.extra_body:
            params["extra_body"] = config.extra_body
        return params

    @retry(
        stop=stop_after_attempt(3) if HAS_TENACITY else None,
        wait=wait_exponential(min=4, max=10) if HAS_TENACITY else None,
        reraise=True,
    )
    def chat(
        self,
        message: str,
        mode: Optional[KimiMode] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict]] = None,
        **kwargs
    ) -> KimiResponse:
        """
        Send a chat message and get a response.

        Args:
            message: The user message
            mode: Operating mode (defaults to self.default_mode)
            system_prompt: Optional system prompt
            tools: Optional tool definitions
            tool_choice: Tool choice mode ('auto', 'none', or specific)
            **kwargs: Additional API parameters

        Returns:
            KimiResponse with the model's response
        """
        mode = mode or self.default_mode
        params = self._get_mode_params(mode)
        params.update(kwargs)

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        # Add tools if provided
        if tools:
            params["tools"] = tools
            if tool_choice:
                params["tool_choice"] = tool_choice

        # Make API call
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **params
            )
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "AuthenticationError" in str(type(e)):
                raise ValueError(
                    f"Authentication failed. Please verify your MOONSHOT_API_KEY.\n"
                    f"Original error: {error_msg}"
                ) from e
            raise

        return self._parse_response(response, mode)

    async def achat(
        self,
        message: str,
        mode: Optional[KimiMode] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> KimiResponse:
        """Async version of chat()."""
        mode = mode or self.default_mode
        params = self._get_mode_params(mode)
        params.update(kwargs)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        if tools:
            params["tools"] = tools

        response = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            **params
        )

        return self._parse_response(response, mode)

    def _parse_response(self, response, mode: KimiMode) -> KimiResponse:
        """Parse API response into KimiResponse."""
        choice = response.choices[0]
        message = choice.message

        # Extract content
        content = message.content or ""

        # Extract reasoning if present (thinking mode)
        reasoning = None
        if hasattr(message, "reasoning_content"):
            reasoning = message.reasoning_content

        # Extract tool calls
        tool_calls = None
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in message.tool_calls
            ]

        # Build usage dict
        usage = None
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return KimiResponse(
            content=content,
            reasoning=reasoning,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            usage=usage,
            mode=mode,
        )

    def execute_with_tools(
        self,
        message: str,
        tools: List[Dict[str, Any]],
        tool_map: Dict[str, Callable],
        mode: Optional[KimiMode] = None,
        system_prompt: Optional[str] = None,
        max_steps: int = 300,
        on_tool_call: Optional[Callable[[str, Dict], None]] = None,
        on_tool_result: Optional[Callable[[str, Any], None]] = None,
    ) -> KimiResponse:
        """
        Execute a task with automatic tool calling loop.

        This implements the full tool calling pipeline:
        1. Send message with tools
        2. If model requests tool calls, execute them
        3. Feed results back to model
        4. Repeat until completion or max_steps

        Args:
            message: The user task
            tools: Tool definitions in OpenAI format
            tool_map: Dict mapping tool names to callable functions
            mode: Operating mode (AGENT or SWARM recommended)
            system_prompt: Optional system prompt
            max_steps: Maximum iterations
            on_tool_call: Callback when tool invoked
            on_tool_result: Callback when tool returns

        Returns:
            Final KimiResponse after tool execution
        """
        mode = mode or KimiMode.AGENT
        params = self._get_mode_params(mode)

        # Build initial messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        steps = 0
        while steps < max_steps:
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                **params
            )

            choice = response.choices[0]
            message_obj = choice.message

            # Check if we're done
            if choice.finish_reason != "tool_calls" or not message_obj.tool_calls:
                return self._parse_response(response, mode)

            # Append assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": message_obj.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in message_obj.tool_calls
                ]
            })

            # Execute tool calls
            for tool_call in message_obj.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                if on_tool_call:
                    on_tool_call(tool_name, arguments)

                # Execute tool
                if tool_name in tool_map:
                    try:
                        result = tool_map[tool_name](**arguments)
                    except Exception as e:
                        result = {"error": str(e)}
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                if on_tool_result:
                    on_tool_result(tool_name, result)

                # Convert result to string
                if not isinstance(result, str):
                    result = json.dumps(result)

                # Append tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            steps += 1

        # Max steps reached
        logger.warning(f"Max steps ({max_steps}) reached in tool loop")
        return self._parse_response(response, mode)

    # =========================================================================
    # Legacy Compatibility Methods
    # =========================================================================

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility.

        This provides the same interface as the original KimiClient.
        """
        api_messages = []
        if system:
            api_messages.append({"role": "system", "content": system})
        api_messages.extend(messages)

        params = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
            **kwargs
        }

        if tools:
            params["tools"] = tools
            if tool_choice:
                params["tool_choice"] = tool_choice

        try:
            response = self.client.chat.completions.create(**params)
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "AuthenticationError" in str(type(e)):
                raise ValueError(
                    f"Authentication failed (401). Please verify your MOONSHOT_API_KEY.\n"
                    f"Original error: {error_msg}"
                ) from e
            raise

        if stream:
            return response

        return self._format_response_legacy(response)

    def _format_response_legacy(self, response) -> Dict[str, Any]:
        """Format response to legacy dict format."""
        choice = response.choices[0]
        message = choice.message

        result = {
            "id": response.id,
            "model": response.model,
            "choices": [{
                "index": choice.index,
                "message": {
                    "role": message.role,
                    "content": message.content,
                },
                "finish_reason": choice.finish_reason,
            }],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else None,
        }

        if hasattr(message, "tool_calls") and message.tool_calls:
            result["choices"][0]["message"]["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in message.tool_calls
            ]

        return result

    def get_text_content(self, response: Dict[str, Any]) -> str:
        """Legacy method: Extract text content from response."""
        if "choices" in response and len(response["choices"]) > 0:
            message = response["choices"][0].get("message", {})
            return message.get("content", "") or ""
        return ""

    def has_tool_calls(self, response: Dict[str, Any]) -> bool:
        """Legacy method: Check if response contains tool calls."""
        if "choices" in response and len(response["choices"]) > 0:
            message = response["choices"][0].get("message", {})
            return "tool_calls" in message and len(message.get("tool_calls", [])) > 0
        return False

    def get_tool_calls(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Legacy method: Extract tool calls from response."""
        if not self.has_tool_calls(response):
            return []
        message = response["choices"][0]["message"]
        return message.get("tool_calls", [])


# =============================================================================
# Singleton Instance
# =============================================================================


_kimi_client: Optional[KimiClient] = None


def get_kimi_client() -> KimiClient:
    """Get or create singleton Kimi client instance."""
    global _kimi_client
    if _kimi_client is None:
        _kimi_client = KimiClient()
    return _kimi_client


def create_client(
    mode: KimiMode = KimiMode.THINKING,
    **kwargs
) -> KimiClient:
    """
    Factory function to create a new KimiClient.

    Args:
        mode: Default operating mode
        **kwargs: Additional client parameters

    Returns:
        New KimiClient instance
    """
    return KimiClient(default_mode=mode, **kwargs)
