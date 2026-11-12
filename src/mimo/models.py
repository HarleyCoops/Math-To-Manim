"""Typed contracts and run-bundle file names for the MiMo 2.6 tool-calling film pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Run-bundle file names. Stage artifacts are declared on the stage table (mimo.agents).
SCENE_FILE = "mimo_scene.py"
MANIFEST_FILE = "manifest.json"
REQUEST_FILE = "request.json"
VALIDATION_FILE = "validation.json"
REVIEW_FILE = "review.json"
DECISIONS_FILE = "decisions.json"
RENDER_LOG_FILE = "render.log"
MEDIA_DIR = "media"
STAGES_DIR = "stages"

ReasoningEffort = Literal["low", "medium", "high", "xhigh", "max"]
RenderQuality = Literal["l", "m", "h", "p", "k"]


class RunRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=12_000)
    render: bool = False
    quality: RenderQuality = "l"
    reasoning_effort: ReasoningEffort = "high"
    max_repairs: int = Field(default=2, ge=0, le=5)
    offline: bool = False


class ToolCallRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str
    ok: bool
    summary: str
    round_index: int


class StageRunResult(BaseModel):
    """What one specialist reported after its tool loop."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["completed", "failed"]
    role: str
    artifacts: list[str]
    summary: str
    checks: list[str]
    notes: list[str]
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)


class PipelineResult(BaseModel):
    """What producing the stage artifacts (live chain or offline bundle) yielded."""

    model_config = ConfigDict(extra="forbid")

    artifacts: list[str]
    checks: list[str]
    notes: list[str]
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    stage_records: list[str] = Field(default_factory=list)


class StageRecord(BaseModel):
    name: str
    status: Literal["pending", "running", "completed", "failed", "cached"]
    input_hash: str
    artifact_hashes: dict[str, str] = Field(default_factory=dict)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    trace_path: str
    result_path: str
    started_utc: str | None = None
    completed_utc: str | None = None
    error: str | None = None


class RunManifest(BaseModel):
    schema_version: int = 1
    run_id: str
    prompt: str
    model: str
    backend: Literal["mimo-tool-calling"] = "mimo-tool-calling"
    offline: bool
    render_requested: bool
    quality: str
    status: Literal["running", "completed", "failed"] = "running"
    created_utc: str
    completed_utc: str | None = None
    attempts: list[dict] = Field(default_factory=list)
    scene_file: str | None = None
    scene_name: str | None = None
    video_path: str | None = None
    execution_mode: Literal["tool-calling-stages"] = "tool-calling-stages"
    stage_records: list[str] = Field(default_factory=list)
    artifacts: dict[str, str] = Field(default_factory=dict)
    status_detail: dict[str, str] = Field(default_factory=dict)
    tool_call_count: int = 0
    error: str | None = None
