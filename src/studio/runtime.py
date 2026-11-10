"""Where Studio agents run.

An agent is defined once (a name, a system prompt, a tool list, an optional
JSON schema for its answer). A runtime runs it and returns a typed result.

Runtimes:

- ``local-sdk`` (default): the Claude Agent SDK on this machine. It drives the
  installed ``claude`` CLI, so it uses that CLI's login. Set
  ``STUDIO_CLAUDE_CONFIG_DIR`` to choose which login (for example the personal
  one) without changing the rest of the environment.
- ``managed-agents``: Claude Managed Agents. Not available yet: the signed-in
  organization has no API credit, so agents cannot be created there. The
  environment definition is kept in ``environments/studio/``.

Environment:

    STUDIO_RUNTIME             local-sdk | managed-agents      default local-sdk
    STUDIO_CLAUDE_CONFIG_DIR   passed to the CLI as CLAUDE_CONFIG_DIR
    STUDIO_MODEL               model id for agents             default claude-fable-5-2
"""

from __future__ import annotations

import asyncio
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Protocol

DEFAULT_MODEL = "claude-fable-5-2"
RUNTIMES = ("local-sdk", "managed-agents")

#: ``query_fn(prompt=..., options=...)`` -> async iterator of SDK messages.
QueryFn = Callable[..., AsyncIterator[Any]]


class RuntimeUnavailable(RuntimeError):
    """The chosen runtime cannot run agents on this machine or account."""


@dataclass(frozen=True)
class AgentSpec:
    """One agent: what it is told, what it may use, what it must return."""

    name: str
    system: str
    tools: tuple[str, ...] = ()
    model: str | None = None
    schema: dict[str, Any] | None = None
    max_turns: int = 20


@dataclass
class AgentResult:
    ok: bool
    output: dict[str, Any] | None = None
    text: str | None = None
    session_id: str | None = None
    turns: int | None = None
    cost_usd: float | None = None
    error: str | None = None
    runtime: str = ""
    model: str | None = None
    denied_tools: list[str] = field(default_factory=list)


class AgentRuntime(Protocol):
    name: str

    def run(self, spec: AgentSpec, prompt: str, *, cwd: Path) -> AgentResult: ...


def load_agent_file(path: Path, *, tools: tuple[str, ...] = (),
                    schema: dict[str, Any] | None = None) -> AgentSpec:
    """Read an agent definition: YAML front matter (name, model), then the system prompt.

    The same files are applied to Managed Agents with ``ant apply``, so one
    definition serves both runtimes. Only ``name`` and ``model`` are read here;
    the tool list for the local runtime is given by the caller.
    """
    text = Path(path).read_text(encoding="utf-8")
    front, body = "", text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            front, body = text[3:end], text[end + 4:]

    def value(key: str) -> str | None:
        match = re.search(rf"^{key}:\s*(.+?)\s*$", front, flags=re.MULTILINE)
        return match.group(1).strip("'\"") if match else None

    return AgentSpec(name=value("name") or Path(path).stem, system=body.strip(),
                     tools=tools, model=value("model"), schema=schema)


class LocalSdkRuntime:
    """Run an agent with the Claude Agent SDK and the local ``claude`` CLI."""

    name = "local-sdk"

    def __init__(self, *, query_fn: QueryFn | None = None,
                 config_dir: str | None = None, default_model: str | None = None):
        self._query_fn = query_fn
        self.config_dir = config_dir if config_dir is not None else os.getenv(
            "STUDIO_CLAUDE_CONFIG_DIR")
        self.default_model = default_model or os.getenv("STUDIO_MODEL") or DEFAULT_MODEL

    def _options(self, spec: AgentSpec, cwd: Path) -> dict[str, Any]:
        """The SDK options as plain values (kept separate so tests can read them)."""
        options: dict[str, Any] = {
            "system_prompt": spec.system,
            "allowed_tools": list(spec.tools),
            # Deny every tool that is not in allowed_tools; never prompt.
            "permission_mode": "dontAsk",
            # No user or project settings: the agent sees only what Studio gives it.
            "setting_sources": [],
            "model": spec.model or self.default_model,
            "max_turns": spec.max_turns,
            "cwd": str(cwd),
        }
        if spec.schema is not None:
            options["output_format"] = {"type": "json_schema", "schema": spec.schema}
        if self.config_dir:
            options["env"] = {"CLAUDE_CONFIG_DIR": self.config_dir}
        return options

    def run(self, spec: AgentSpec, prompt: str, *, cwd: Path) -> AgentResult:
        options = self._options(spec, cwd)
        query_fn = self._query_fn
        sdk_options: Any = options
        if query_fn is None:
            try:
                from claude_agent_sdk import ClaudeAgentOptions, query
            except ImportError as exc:
                raise RuntimeUnavailable(
                    "the local runtime needs the 'studio' extra: "
                    "pip install -e '.[studio]'") from exc
            query_fn = query
            sdk_options = ClaudeAgentOptions(**options)
        result = AgentResult(ok=False, runtime=self.name, model=options["model"])

        async def collect() -> None:
            async for message in query_fn(prompt=prompt, options=sdk_options):
                if not hasattr(message, "structured_output"):
                    continue  # only the final result message carries the answer
                result.session_id = getattr(message, "session_id", None)
                result.turns = getattr(message, "num_turns", None)
                result.cost_usd = getattr(message, "total_cost_usd", None)
                result.text = getattr(message, "result", None)
                structured = getattr(message, "structured_output", None)
                result.output = structured if isinstance(structured, dict) else None
                denials = getattr(message, "permission_denials", None) or []
                result.denied_tools = [str(d.get("tool_name", d)) if isinstance(d, dict)
                                       else str(d) for d in denials]
                if getattr(message, "is_error", False):
                    errors = getattr(message, "errors", None)
                    result.error = (str(errors) if errors
                                    else str(getattr(message, "subtype", "error")))

        try:
            asyncio.run(collect())
        except Exception as exc:  # noqa: BLE001 - runtime boundary
            result.error = f"{type(exc).__name__}: {exc}"
            return result
        if result.error is None and spec.schema is not None and result.output is None:
            result.error = "the agent returned no structured output"
        if result.error is None and result.session_id is None:
            result.error = "the agent returned no result message"
        result.ok = result.error is None
        return result


def get_runtime(name: str | None = None) -> AgentRuntime:
    """The runtime named by the argument, else ``STUDIO_RUNTIME``, else ``local-sdk``."""
    chosen = name or os.getenv("STUDIO_RUNTIME") or "local-sdk"
    if chosen == "local-sdk":
        return LocalSdkRuntime()
    if chosen == "managed-agents":
        raise RuntimeUnavailable(
            "managed-agents is not available: the signed-in organization has no API "
            "credit, so agents cannot be created. Use STUDIO_RUNTIME=local-sdk.")
    raise ValueError(f"unknown runtime {chosen!r}; choose one of: {', '.join(RUNTIMES)}")
