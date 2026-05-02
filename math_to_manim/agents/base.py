"""Shared agent adapter primitives.

The production path is OpenAI Agents SDK-compatible, while tests and offline
development can use deterministic stage implementations with the same artifact
contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from typing import Any, Callable, Generic, TypeVar

from math_to_manim.config import RuntimeConfig

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


@dataclass
class AgentInvocation:
    """Trace metadata for a single agent stage call."""

    agent_name: str
    model: str
    used_sdk: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class StageAgent(Generic[InputT, OutputT]):
    """Base class for typed pipeline stages."""

    name = "stage"

    def __init__(self, config: RuntimeConfig | None = None):
        self.config = config or RuntimeConfig.from_env()

    def run(self, value: InputT) -> OutputT:
        raise NotImplementedError

    def invocation(self, *, used_sdk: bool = False, **metadata: Any) -> AgentInvocation:
        return AgentInvocation(
            agent_name=self.name,
            model=self.config.model,
            used_sdk=used_sdk,
            metadata=metadata,
        )


def load_openai_agents_sdk() -> dict[str, Any] | None:
    """Load OpenAI Agents SDK symbols across observed package layouts.

    The installed package is `openai-agents`; some environments expose
    top-level symbols from `agents`, while others require submodule imports.
    """

    try:
        from agents import Agent, Runner, function_tool, handoff  # type: ignore

        return {
            "Agent": Agent,
            "Runner": Runner,
            "function_tool": function_tool,
            "handoff": handoff,
        }
    except Exception:
        pass

    try:
        from agents.agent import Agent  # type: ignore
        from agents.run import Runner  # type: ignore
        from agents.tool import function_tool  # type: ignore
        from agents.handoffs import handoff  # type: ignore

        return {
            "Agent": Agent,
            "Runner": Runner,
            "function_tool": function_tool,
            "handoff": handoff,
        }
    except Exception:
        return None


def maybe_run_sdk_agent(
    *,
    name: str,
    instructions: str,
    prompt: str,
    model: str,
    output_parser: Callable[[str], OutputT],
) -> OutputT | None:
    """Run a simple SDK agent when credentials and imports are available.

    This intentionally returns `None` instead of raising for missing optional
    runtime state. The deterministic pipeline remains the offline baseline.
    """

    if not os.getenv("OPENAI_API_KEY"):
        return None

    sdk = load_openai_agents_sdk()
    if sdk is None:
        return None

    Agent = sdk["Agent"]
    Runner = sdk["Runner"]
    agent = Agent(name=name, instructions=instructions, model=model)
    result = Runner.run_sync(agent, prompt)
    output = getattr(result, "final_output", result)
    if not isinstance(output, str):
        output = json.dumps(output)
    return output_parser(output)


def run_structured_sdk_agent(
    *,
    name: str,
    instructions: str,
    prompt: str,
    model: str,
    output_type: type[OutputT],
) -> OutputT | None:
    """Run an OpenAI Agents SDK stage and return a typed artifact.

    Returns ``None`` only when the SDK or API key is unavailable. If credentials
    exist and the stage fails, the exception is allowed to surface because a
    silent deterministic fallback would hide that the real chain did not run.
    """

    if not os.getenv("OPENAI_API_KEY"):
        return None

    sdk = load_openai_agents_sdk()
    if sdk is None:
        return None

    from agents.agent_output import AgentOutputSchema  # type: ignore

    Agent = sdk["Agent"]
    Runner = sdk["Runner"]
    agent = Agent(
        name=name,
        instructions=instructions,
        model=model,
        output_type=AgentOutputSchema(output_type, strict_json_schema=False),
    )
    result = Runner.run_sync(agent, prompt)
    output = getattr(result, "final_output", result)
    if isinstance(output, output_type):
        return output
    return output_type.model_validate(output)


def mark_sdk_metadata(artifact: OutputT, *, agent_name: str, model: str) -> OutputT:
    """Annotate a Pydantic artifact with runtime provenance metadata."""

    metadata = dict(getattr(artifact, "metadata", {}) or {})
    metadata.update(
        {
            "source_agent": agent_name,
            "runtime": "openai_agents_sdk",
            "model": model,
        }
    )
    return artifact.model_copy(update={"metadata": metadata})  # type: ignore[return-value]
