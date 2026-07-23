"""Typed contracts for the Codex CLI-native Sol film pipeline."""

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
    "sol_scene.py",
    "review.json",
)


class RunRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=12_000)
    render: bool = False
    quality: Literal["l", "m", "h", "p", "k"] = "l"
    reasoning_effort: Literal["low", "medium", "high", "xhigh", "max"] = "high"
    max_repairs: int = Field(default=2, ge=0, le=5)
    offline: bool = False


class CodexRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["completed", "failed"]
    scene_file: str
    scene_name: str
    artifacts: list[str]
    rendered: bool
    video_path: str | None
    checks: list[str]
    notes: list[str]


class StageRunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["completed", "failed"]
    role: str
    artifacts: list[str]
    summary: str
    checks: list[str]
    notes: list[str]


class StageRecord(BaseModel):
    name: str
    status: Literal["pending", "running", "completed", "failed", "cached"]
    input_hash: str
    artifact_hashes: dict[str, str] = Field(default_factory=dict)
    thread_id: str | None = None
    trace_path: str
    result_path: str
    event_count: int = 0
    attempts: int = 0
    started_utc: str | None = None
    completed_utc: str | None = None
    error: str | None = None


class RunManifest(BaseModel):
    run_id: str
    prompt: str
    model: str
    backend: Literal["codex-cli"] = "codex-cli"
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
    execution_mode: Literal["monolithic", "staged"] = "monolithic"
    stage_records: list[str] = Field(default_factory=list)
    error: str | None = None
