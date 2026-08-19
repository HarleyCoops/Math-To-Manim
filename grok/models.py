"""Typed contracts for the Grok-native film pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ARTIFACT_NAMES = (
    "01_intent.json",
    "02_knowledge_map.json",
    "03_curriculum.json",
    "04_math_dossier.json",
    "05_shot_list.json",
    "06_scene_spec.json",
    "grok_scene.py",
    "validation.json",
    "review.json",
)

REASONING_EFFORTS = ("low", "medium", "high", "xhigh")


class RunRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=12_000)
    image: str | None = None
    render: bool = False
    quality: Literal["l", "m", "h", "p", "k"] = "l"
    reasoning_effort: Literal["low", "medium", "high", "xhigh"] = "high"
    max_repairs: int = Field(default=2, ge=0, le=5)
    offline: bool = False


class RunManifest(BaseModel):
    schema_version: int = 1
    run_id: str
    prompt: str
    model: str
    backend: Literal["xai-responses"] = "xai-responses"
    offline: bool
    render_requested: bool
    quality: str
    image: str | None = None
    status: Literal["running", "completed", "failed"] = "running"
    created_utc: str
    completed_utc: str | None = None
    stages: list[dict] = Field(default_factory=list)
    attempts: list[dict] = Field(default_factory=list)
    scene_file: str | None = None
    scene_name: str | None = None
    video_path: str | None = None
    artifacts: dict[str, str] = Field(default_factory=dict)
    status_detail: dict[str, str] = Field(default_factory=dict)
    error: str | None = None


class StageCallResult(BaseModel):
    text: str
    payload: dict
    tool_calls: list[dict] = Field(default_factory=list)
    thinking: list[str] = Field(default_factory=list)
    images: list[dict] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict)
