"""Typed contracts for the Codex CLI-native Sol film pipeline."""

from __future__ import annotations

from typing import Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, field_validator

from sol.manifest_schema import CURRENT_SCHEMA_VERSION

Quality = Literal["l", "m", "h", "p", "k"]
ReasoningEffort = Literal["low", "medium", "high", "xhigh", "max"]
Evaluator = Literal["cinematographer", "astra_review"]

QUALITY_CHOICES: tuple[str, ...] = get_args(Quality)
REASONING_EFFORT_CHOICES: tuple[str, ...] = get_args(ReasoningEffort)
EVALUATOR_CHOICES: tuple[str, ...] = get_args(Evaluator)
MAX_REPAIRS_LIMIT = 5


class RunRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=12_000)
    render: bool = False
    quality: Quality = "l"
    # None keeps each stage's own effort from the stage table; a value overrides
    # every stage of this run.
    reasoning_effort: ReasoningEffort | None = None
    max_repairs: int = Field(default=2, ge=0, le=MAX_REPAIRS_LIMIT)
    offline: bool = False
    evaluator: Evaluator = "cinematographer"

    @field_validator('evaluator', mode='before')
    @classmethod
    def migrate_legacy_reviewer_name(cls, value):
        # Old saved requests used this incorrect name for an Astra reviewer.
        return 'astra_review' if value == 'jev' else value


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
    followups: list[dict] = Field(default_factory=list)
    started_utc: str | None = None
    completed_utc: str | None = None
    error: str | None = None


class RunManifest(BaseModel):
    schema_version: int = CURRENT_SCHEMA_VERSION
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
    artifacts: dict[str, str] = Field(default_factory=dict)
    status_detail: dict[str, str] = Field(default_factory=dict)
    error: str | None = None
