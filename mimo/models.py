"""Typed contracts for the MiMo 2.6 tool-calling film pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ARTIFACT_NAMES = (
    "01_intent.json",
    "02_knowledge_map.json",
    "03_curriculum.json",
    "04_math_dossier.json",
    "05_shot_list.json",
    "06_scene_spec.json",
    "mimo_scene.py",
    "validation.json",
    "review.json",
)

TOOL_NAMES = (
    "write_artifact",
    "read_artifact",
    "list_artifacts",
    "record_decision",
    "verify_geometry",
    "verify_scene",
)

class RunRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=12_000)
    render: bool = False
    quality: Literal["l", "m", "h", "p", "k"] = "l"
    reasoning_effort: Literal["low", "medium", "high", "xhigh", "max"] = "high"
    max_repairs: int = Field(default=2, ge=0, le=5)
    offline: bool = False


class ToolCallRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str
    ok: bool
    summary: str
    round_index: int


class MimoRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["completed", "failed"]
    scene_file: str
    scene_name: str
    artifacts: list[str]
    rendered: bool
    video_path: str | None
    checks: list[str]
    notes: list[str]
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)


class StageRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["completed", "failed"]
    role: str
    artifacts: list[str]
    summary: str
    checks: list[str]
    notes: list[str]
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)


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
