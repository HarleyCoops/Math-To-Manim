"""Mythos Math-To-Manim MCP server.

``math-to-manim-mythos serve-mcp`` is the operator command. Every tool runs
the Mythos chain or inspects a Mythos run through one ``MythosService``, so
the job record is the Mythos job: it carries ``stage`` (the step running now,
or the step that failed) and ``outcome`` (how a finished run ended). See
:mod:`mythos.lifecycle`.

    math-to-manim-mythos serve-mcp
    math-to-manim-mythos serve-mcp --transport streamable-http --port 8643

The Grok chain has its own server: ``math-to-manim-grok serve-mcp``.
``set_service`` swaps the shared service (tests, embedders).
"""

from __future__ import annotations

import json
import threading
from typing import Any, Literal, Optional

try:
    from mcp.server import MCPServer
    from mcp.types import ToolAnnotations
    from pydantic import BaseModel, ConfigDict, Field
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "The MCP server requires the 'mcp' extra: pip install -e '.[mcp]'"
    ) from exc

from mythos import __version__
from mythos.charter import CINEMATIC_CHARTER
from mythos.layout import SCENE_FILE
from mythos.service import MythosService

mcp = MCPServer(
    "math_to_manim_mcp",
    description="Turn a mathematics question into an inspectable Mythos Manim run.",
    version=__version__,
)

_service: MythosService | None = None
_service_lock = threading.Lock()


def get_service() -> MythosService:
    """The service every tool uses; created on first use."""
    global _service
    with _service_lock:
        if _service is None:
            _service = MythosService()
        return _service


def set_service(service: MythosService | None) -> None:
    """Replace the shared service (None resets to a fresh default on next use)."""
    global _service
    _service = service


def _json(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False)


class CreateAnimationInput(BaseModel):
    """Input for creating a new Mythos animation run."""

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
            f"False returns the storyboard + {SCENE_FILE} only."
        ),
    )
    quality: Literal["l", "m", "h", "p", "k"] = Field(
        default="l",
        description="Manim quality: l=480p (fast), m=720p, h=1080p, p=1440p, k=4K.",
    )
    offline: bool = Field(
        default=False,
        description=(
            "Deterministic rehearsal run with stub artifacts; no model calls. "
            "Use to test plumbing."
        ),
    )
    model: Optional[str] = Field(
        default=None,
        description="Model id for this run. Default: the server's configured model.",
    )
    command: Optional[str] = Field(
        default=None,
        description=(
            "Model backend for this run: claude, codex, or fugu-api. "
            "Default: the server's configured backend."
        ),
    )
    max_repairs: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum model repairs after a failed check or render.",
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
            f"'05_shot_list.json', '{SCENE_FILE}'."
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
    """Start a Mythos animation run: intent, cartographer, curriculum,
    math-director, cinematographer and scene-composer, then codegen writes a
    complete cinematic Manim scene (mythos_scene.py).

    The run executes in the background. Returns the job record immediately;
    poll with m2m_get_job until status is 'completed' or 'failed', then
    inspect artifacts with m2m_get_run / m2m_get_artifact / m2m_get_scene_code.

    Returns:
        str: JSON job record: {"id", "prompt", "status", "stage", "outcome",
        "created_utc", "options", "run_id", "manifest", "error"}. status is
        one of running|completed|failed.
    """
    options: dict[str, Any] = {
        "render": params.render,
        "quality": params.quality,
        "offline": params.offline,
        "max_repairs": params.max_repairs,
    }
    if params.model:
        options["model"] = params.model
    if params.command:
        options["command"] = params.command
    try:
        return _json(get_service().submit(params.prompt, **options).to_dict())
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
        str: JSON job record with status running|completed|failed.
        'stage' is the step running now (intent, cartographer, curriculum,
        math-director, cinematographer, scene-composer, codegen, verify,
        render, repair); on a failed job it is the step that failed.
        'outcome' is null while running, then one of film_ready (video
        exists), scene_ready (code passed checks, no render requested),
        validation_failed, render_failed, render_timed_out, render_blocked,
        chain_failed. A 'completed' job can have outcome render_failed:
        read 'outcome' to know if a film exists. When failed, 'error'
        explains why.
    """
    job = get_service().get_job(job_id.strip())
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
    """List on-disk Mythos animation runs, newest first.

    Returns:
        str: JSON list of run summaries: {"run_id", "prompt", "model",
        "offline", "created_utc", "completed", "status", "outcome",
        "scene_name"}. status is running|completed|failed|unknown.
    """
    return _json(get_service().list_runs(limit=params.limit or 20))


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
    """Full manifest and artifact listing for one Mythos run.

    Returns:
        str: JSON {"run_id", "manifest", "artifacts"} where manifest logs
        every chain stage and manifest.status holds run, stage and outcome;
        artifacts lists all files readable through m2m_get_artifact.
    """
    try:
        return _json(get_service().get_run(params.run_id))
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
    """Read one artifact from a run: the intent (01), the knowledge map
    (02_knowledge_map.json), curriculum (03), math dossier (04), shot list
    (05), scene spec (06), or the generated scene (mythos_scene.py).

    Returns:
        str: The artifact's raw text content (JSON or Python).
    """
    try:
        return get_service().read_artifact(params.run_id, params.artifact_name)
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
    """Shortcut: return the generated Manim scene file (mythos_scene.py) for
    a run, ready to render with `manim -qh mythos_scene.py <SceneName>`.

    Returns:
        str: Complete Manim CE Python module.
    """
    try:
        return get_service().read_artifact(params.run_id, SCENE_FILE)
    except (FileNotFoundError, ValueError) as exc:
        return f"Error: {exc}"


@mcp.tool(
    name="m2m_cinematic_charter",
    annotations=ToolAnnotations(
        title="Get the Mythos Cinematic Charter",
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def m2m_cinematic_charter() -> str:
    """The Mythos Cinematic Charter: the rules every generated scene obeys.
    Use it to write or review Manim scenes in the Mythos house style without
    running the chain.

    Returns:
        str: The charter text.
    """
    return CINEMATIC_CHARTER


def main(transport: str = "stdio", port: int = 8643) -> None:
    """Entry point used by `math-to-manim-mythos serve-mcp`."""
    if transport == "stdio":
        mcp.run()
    else:
        mcp.run(
            transport="streamable-http",
            host="127.0.0.1",
            port=port,
        )


__all__ = ["main", "mcp", "get_service", "set_service"]


if __name__ == "__main__":
    main()
