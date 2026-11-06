"""Typed contracts for the Argon Google Agent SDK (google-adk + google-genai) film pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# Files every run bundle contains besides the per-stage JSON artifacts
# (those names live on the stage table in argon.stages).
SCENE_FILE = "argon_scene.py"
VALIDATION_FILE = "validation.json"
REVIEW_FILE = "review.json"
MANIFEST_FILE = "manifest.json"
REQUEST_FILE = "request.json"
TRACES_DIR = "traces"

SDK_NAME = "google-adk + google-genai"

REASONING_EFFORTS = ("low", "medium", "high", "xhigh")


class RunRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=16_000)
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
    backend: Literal["google-adk-genai", "argon-operator"] = "google-adk-genai"
    sdk: str = SDK_NAME
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
    operator_note: str | None = None
    error: str | None = None


class StageCallResult(BaseModel):
    """One model turn. ``payload`` is the parsed JSON object, or None when the reply was not JSON."""

    text: str
    payload: dict | None = None
    tool_calls: list[dict] = Field(default_factory=list)
    thinking: list[str] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict)
