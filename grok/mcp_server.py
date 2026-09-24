"""Grok-native Math-To-Manim MCP server.

``math-to-manim serve-mcp`` is the operator command. Every tool runs the
Grok 4.6 chain (or inspects a Grok run). Existing tool names are unchanged
so current MCP clients keep working.

    math-to-manim serve-mcp
    math-to-manim serve-mcp --transport streamable-http --port 8643
"""

from __future__ import annotations

import json
from typing import Any, Literal, Optional

try:
    from mcp.server import MCPServer
    from mcp.types import ToolAnnotations
    from pydantic import BaseModel, ConfigDict, Field
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "The MCP server requires the 'mcp' extra: pip install -e '.[mcp]'"
    ) from exc

from grok import __version__
from grok.charters import cinematic_charter
from grok.models import RunRequest
from grok.service import GrokService

DEFAULT_MCP_MODEL = "grok-4.6"

mcp = MCPServer(
    "math_to_manim_mcp",
    description="Turn a mathematics question into an inspectable Grok 4.6 Manim run.",
    version=__version__,
)
_service = GrokService()


def _json(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False)


class CreateAnimationInput(BaseModel):
    """Input for creating a new Grok animation run."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    prompt: str = Field(
        ...,
        min_length=3,
        max_length=4000,
        description=(
            "One sentence describing what the film should explain "
            "(e.g., 'A 3 kg cart at 4 m/s hits a spring k=200. "
            "How far does it compress?')."
        ),
    )
    render: bool = Field(
        default=False,
        description=(
            "Render an MP4 after codegen (requires local manim; slow). "
            "False returns the storyboard + grok_scene.py only."
        ),
    )
    quality: Literal["l", "m", "h", "p", "k"] = Field(
        default="l",
        description="Manim quality: l=480p (fast), m=720p, h=1080p, p=1440p, k=4K.",
    )
    offline: bool = Field(
        default=False,
        description=(
            "Deterministic rehearsal run with stub artifacts; no xAI calls. "
            "Use to test plumbing."
        ),
    )
    model: str = Field(
        default=DEFAULT_MCP_MODEL,
        description="Grok Responses model id. Default grok-4.6. Claude/Codex ids are ignored.",
    )
    image: Optional[str] = Field(
        default=None,
        description="Path to a photographed homework page or diagram for intent vision.",
    )
    command: Optional[str] = Field(
        default=None,
        description="Ignored. This server always runs the Grok chain.",
    )
    reasoning_effort: Literal["low", "medium", "high", "xhigh"] = Field(
        default="high",
        description="Grok reasoning effort for live runs.",
    )


class RunIdInput(BaseModel):
    """Input identifying one run."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    run_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description=(
            "Run directory name, e.g. "
            "'20260819-231524-a-3-kg-cart-at-4-m-s'. "
            "Get these from m2m_list_runs."
        ),
    )


class ArtifactInput(RunIdInput):
    """Input identifying one artifact within a run."""

    artifact_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description=(
            "Artifact file name, e.g. '02_knowledge_map.json', "
            "'05_shot_list.json', 'grok_scene.py'."
        ),
    )


class ListRunsInput(BaseModel):
    """Input for listing runs."""

    model_config = ConfigDict(extra="forbid")

    limit: Optional[int] = Field(
        default=20,
        ge=1,
        le=200,
        description="Maximum runs to return (newest first).",
    )


@mcp.tool(
    name="m2m_create_animation",
    annotations=ToolAnnotations(
        title="Create Math Animation",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=True,
    ),
)
def m2m_create_animation(params: CreateAnimationInput) -> str:
    """Start a Grok 4.6 animation run: intent, reverse cartography, curriculum,
    math-director (code_interpreter), cinematographer, and composer write a
    complete cinematic Manim scene (grok_scene.py).

    The run executes in the background. Returns the job record immediately;
    poll with m2m_get_job until status is 'completed', then inspect
    artifacts with m2m_get_run / m2m_get_artifact / m2m_get_scene_code.

    Returns:
        str: JSON job record: {"id", "prompt", "status", "created_utc",
        "options", "run_id", "manifest", "error"}. status is one of
        queued|running|completed|failed.
    """
    try:
        if params.model and params.model != DEFAULT_MCP_MODEL:
            _service.harness.client.model = params.model
        job = _service.submit(
            RunRequest(
                prompt=params.prompt,
                image=params.image,
                render=params.render,
                quality=params.quality,
                offline=params.offline,
                reasoning_effort=params.reasoning_effort,
            )
        )
        return _json(job.to_dict())
    except ValueError as exc:
        return f"Error: {exc}"


@mcp.tool(
    name="m2m_get_job",
    annotations=ToolAnnotations(
        title="Get Animation Job Status",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def m2m_get_job(job_id: str) -> str:
    """Poll one background animation job by id (from m2m_create_animation).

    Returns:
        str: JSON job record with status queued|running|completed|failed.
        When completed, 'run_id' names the on-disk run and 'manifest'
        summarizes every stage. When failed, 'error' explains why.
    """
    job = _service.get_job(job_id.strip())
    if job is None:
        return (
            f"Error: no job {job_id!r}. Jobs live in server memory; "
            "use m2m_list_runs for on-disk history."
        )
    return _json(job.to_dict())


@mcp.tool(
    name="m2m_list_runs",
    annotations=ToolAnnotations(
        title="List Animation Runs",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def m2m_list_runs(params: ListRunsInput) -> str:
    """List on-disk Grok animation runs, newest first.

    Returns:
        str: JSON list of run summaries: {"run_id", "prompt", "model",
        "offline", "created_utc", "completed", "scene_name"}.
    """
    return _json(_service.list_run_summaries(limit=params.limit or 20))


@mcp.tool(
    name="m2m_get_run",
    annotations=ToolAnnotations(
        title="Get Animation Run Details",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def m2m_get_run(params: RunIdInput) -> str:
    """Full manifest and artifact listing for one Grok run.

    Returns:
        str: JSON {"run_id", "manifest", "artifacts"} where manifest logs
        every chain stage, and artifacts lists all files readable through
        m2m_get_artifact.
    """
    try:
        return _json(_service.inspect_run(params.run_id))
    except (FileNotFoundError, ValueError) as exc:
        return f"Error: {exc}"


@mcp.tool(
    name="m2m_get_artifact",
    annotations=ToolAnnotations(
        title="Read Run Artifact",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def m2m_get_artifact(params: ArtifactInput) -> str:
    """Read one artifact from a run: the intent (01), the reverse reasoning
    tree (02_knowledge_map.json), curriculum (03), math dossier (04), shot
    list (05), scene spec (06), or the generated scene (grok_scene.py).

    Returns:
        str: The artifact's raw text content (JSON or Python).
    """
    try:
        return _service.read_artifact(params.run_id, params.artifact_name)
    except (FileNotFoundError, ValueError) as exc:
        return f"Error: {exc}"


@mcp.tool(
    name="m2m_get_scene_code",
    annotations=ToolAnnotations(
        title="Get Generated Manim Scene",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def m2m_get_scene_code(params: RunIdInput) -> str:
    """Shortcut: return the generated Manim scene file for a run, ready to
    render with `manim -qh grok_scene.py <SceneName>`. Prefers grok_scene.py
    and falls back to mythos_scene.py for older on-disk runs.

    Returns:
        str: Complete Manim CE Python module.
    """
    try:
        return _service.read_scene_code(params.run_id)
    except (FileNotFoundError, ValueError) as exc:
        return f"Error: {exc}"


@mcp.tool(
    name="m2m_cinematic_charter",
    annotations=ToolAnnotations(
        title="Get the Grok Cinematic Contract",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def m2m_cinematic_charter() -> str:
    """The Grok cinematic contract: composer + cinematography rules every
    generated scene obeys (camera-as-narrator, headlines before symbols,
    term zooms, captions, palette, verify_scene). Use it to write or review
    Manim scenes in the Grok house style without running the chain.

    Returns:
        str: The contract text.
    """
    return cinematic_charter()


def main(transport: str = "stdio", port: int = 8643) -> None:
    """Entry point used by `math-to-manim serve-mcp`."""
    if transport == "stdio":
        mcp.run()
    else:
        mcp.run(
            transport="streamable-http",
            host="127.0.0.1",
            port=port,
        )


if __name__ == "__main__":
    main()
