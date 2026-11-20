"""Typed contracts for the unified Gemini 4 Neon-first pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from neon import DEFAULT_MODEL

SCENE_FILE = "neon_scene.py"
PLAN_FILE = "01_neon_plan.json"
MANIFEST_FILE = "manifest.json"
VALIDATION_FILE = "validation.json"
TOOL_LOG_FILE = "tool_calls.jsonl"

Quality = Literal["l", "m", "h", "p", "k"]
BackendName = Literal["auto", "genai", "gemini-api", "operator"]
RunState = Literal["running", "completed", "failed"]
OutcomeState = Literal[
    "film_published",
    "film_ready",
    "scene_ready",
    "needs_operator_input",
    "validation_failed",
    "render_failed",
    "pipeline_failed",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class PrerequisiteNode(BaseModel):
    concept: str
    why_needed: str
    depends_on: list[str] = Field(default_factory=list)


class MathCheck(BaseModel):
    label: str
    expression: str
    expected_note: str = ""


class VisualAct(BaseModel):
    act: int
    title: str
    duration_seconds: float
    camera_move: str
    geometry: str
    equations: list[str] = Field(default_factory=list)
    caption: str


class NeonPlan(BaseModel):
    """Unified single-artifact reasoning plan replacing the 6 legacy JSON stages."""

    title: str
    slug: str
    subtitle: str
    core_thesis: str
    verification_status: str = ""
    prerequisites: list[PrerequisiteNode] = Field(default_factory=list)
    key_formulas: list[str] = Field(default_factory=list)
    math_checks: list[MathCheck] = Field(default_factory=list)
    palette: dict[str, str] = Field(default_factory=dict)
    acts: list[VisualAct] = Field(default_factory=list)
    scene_class: str = "NeonMathJourney"
    target_duration_seconds: float = 80.0


class ToolEvent(BaseModel):
    timestamp_utc: str = Field(default_factory=utc_now)
    tool: str
    ok: bool
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)


class RunStatus(BaseModel):
    run: RunState = "running"
    stage: str = "init"
    outcome: OutcomeState | None = None
    error: str | None = None
    updated_utc: str = Field(default_factory=utc_now)


class NeonRequest(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL
    backend: BackendName = "auto"
    render: bool = False
    quality: Quality = "m"
    max_repairs: int = Field(default=3, ge=0, le=5)
    publish: bool = False
    slug: str | None = None
    workspace: str | None = None
    thinking_budget: int = 8192


class NeonManifest(BaseModel):
    run_id: str
    created_utc: str = Field(default_factory=utc_now)
    model: str = DEFAULT_MODEL
    backend: str = "operator"
    prompt: str
    status: RunStatus = Field(default_factory=RunStatus)
    scene_class: str | None = None
    scene_file: str | None = None
    video_path: str | None = None
    duration_seconds: float | None = None
    resolution: str | None = None
    contact_sheet_path: str | None = None
    gif_path: str | None = None
    published_assets: dict[str, str] = Field(default_factory=dict)
    tool_calls_count: int = 0
    repairs: int = 0
