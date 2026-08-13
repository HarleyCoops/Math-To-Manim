"""math_to_manim_mcp: the Math-To-Manim MCP server.

Exposes the Mythos animation chain as MCP tools so any MCP client (Claude
Desktop, Claude Code, Cowork, ...) can turn one sentence into a cinematic
Manim film and inspect every artifact the chain produced.

Run it:
    math-to-manim serve-mcp                 # stdio (local clients)
    math-to-manim serve-mcp --transport streamable-http --port 8643

Claude Desktop / Claude Code config:
    {
      "mcpServers": {
        "math-to-manim": {
          "command": "math-to-manim",
          "args": ["serve-mcp"]
        }
      }
    }
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

from mythos import __version__
from mythos.backends import DEFAULT_COMMAND, DEFAULT_MODEL
from mythos.charter import CINEMATIC_CHARTER
from mythos.service import MythosService

mcp = MCPServer(
    "math_to_manim_mcp",
    description="Turn a mathematics question into an inspectable Mythos Manim run.",
    version=__version__,
)
_service = MythosService()


def _json(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------- #
# Input models                                                           #
# --------------------------------------------------------------------- #

class CreateAnimationInput(BaseModel):
    """Input for creating a new animation run."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    prompt: str = Field(
        ..., min_length=3, max_length=4000,
        description="One sentence describing what the film should explain "
                    "(e.g., 'Show why the harmonic oscillator has discrete "
                    "energy levels').")
    render: bool = Field(
        default=False,
        description="Render an MP4 after codegen (requires local manim; slow). "
                    "False returns the storyboard + scene code only.")
    quality: Literal["l", "m", "h", "p", "k"] = Field(
        default="l", description="Manim quality: l=480p (fast), m=720p, "
                                 "h=1080p, p=1440p, k=4K.")
    offline: bool = Field(
        default=False,
        description="Deterministic rehearsal run with stub artifacts; "
                    "no model calls. Use to test plumbing.")
    model: str = Field(default=DEFAULT_MODEL, description="Baseline model id.")
    command: str = Field(
        default=DEFAULT_COMMAND,
        description="Model backend: 'claude' (Claude CLI), 'codex' "
                    "(Codex CLI), or 'fugu-api' (OpenAI-compatible HTTP).")


class RunIdInput(BaseModel):
    """Input identifying one run."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    run_id: str = Field(..., min_length=1, max_length=200,
                        description="Run directory name, e.g. "
                                    "'20260706-101500-explain-qft'. "
                                    "Get these from m2m_list_runs.")


class ArtifactInput(RunIdInput):
    """Input identifying one artifact within a run."""

    artifact_name: str = Field(
        ..., min_length=1, max_length=200,
        description="Artifact file name, e.g. '02_knowledge_map.json', "
                    "'05_shot_list.json', 'mythos_scene.py'.")


class ListRunsInput(BaseModel):
    """Input for listing runs."""

    model_config = ConfigDict(extra="forbid")

    limit: Optional[int] = Field(default=20, ge=1, le=200,
                                 description="Maximum runs to return "
                                             "(newest first).")


# --------------------------------------------------------------------- #
# Tools                                                                  #
# --------------------------------------------------------------------- #

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
    """Start a Mythos animation run: six reasoning agents turn one sentence
    into a knowledge map, curriculum, shot list, scene spec, and a complete
    cinematic Manim scene file.

    The run executes in the background. Returns the job record immediately;
    poll with m2m_get_job until status is 'completed', then inspect
    artifacts with m2m_get_run / m2m_get_artifact / m2m_get_scene_code.

    Returns:
        str: JSON job record: {"id", "prompt", "status", "created_utc",
        "options", "run_id", "manifest", "error"}. status is one of
        queued|running|completed|failed.
    """
    try:
        job = _service.submit(
            params.prompt,
            render=params.render,
            quality=params.quality,
            offline=params.offline,
            model=params.model,
            command=params.command,
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
        return (f"Error: no job {job_id!r}. Jobs live in server memory; "
                "use m2m_list_runs for on-disk history.")
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
    """List on-disk animation runs, newest first.

    Returns:
        str: JSON list of run summaries: {"run_id", "prompt", "model",
        "offline", "created_utc", "completed", "scene_name"}.
    """
    return _json(_service.list_runs(limit=params.limit or 20))


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
    """Full manifest and artifact listing for one run.

    Returns:
        str: JSON {"run_id", "manifest", "artifacts"} where manifest logs
        every chain stage with timing, and artifacts lists all files
        readable through m2m_get_artifact.
    """
    try:
        return _json(_service.get_run(params.run_id))
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
    list (05), scene spec (06), or the generated scene (mythos_scene.py).

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
    render with `manim -qh mythos_scene.py <SceneName>`.

    Returns:
        str: Complete Manim CE Python module.
    """
    try:
        return _service.read_artifact(params.run_id, "mythos_scene.py")
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
    """The Mythos Cinematic Charter: the visual contract every generated
    scene obeys (camera-as-narrator, headlines before symbols, term zooms,
    captions, palette). Use it to write or review Manim scenes in the
    Mythos house style without running the chain.

    Returns:
        str: The charter text.
    """
    return CINEMATIC_CHARTER


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
