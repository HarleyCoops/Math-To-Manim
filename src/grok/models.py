"""Typed contracts and file names for the Grok-native film pipeline."""

from __future__ import annotations

from typing import Literal, get_args

from pydantic import BaseModel, Field

# Files every run bundle contains besides the stage artifacts (see grok.stages).
SCENE_FILE = "grok_scene.py"
VALIDATION_FILE = "validation.json"
REVIEW_FILE = "review.json"
MANIFEST_FILE = "manifest.json"
REQUEST_FILE = "request.json"
TRACES_DIR = "traces"
STILLS_DIR = "stills"
MEDIA_DIR = "media"

Quality = Literal["l", "m", "h", "p", "k"]
ReasoningEffort = Literal["low", "medium", "high", "xhigh"]
QUALITIES: tuple[str, ...] = get_args(Quality)
REASONING_EFFORTS: tuple[str, ...] = get_args(ReasoningEffort)
MAX_REPAIRS = 5


class RunRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=12_000)
    image: str | None = None
    render: bool = False
    quality: Quality = "l"
    # None means the client's default (XAI_MODEL / XAI_REASONING_EFFORT).
    model: str | None = None
    reasoning_effort: ReasoningEffort | None = None
    max_repairs: int = Field(default=2, ge=0, le=MAX_REPAIRS)
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
    """One completed Responses exchange.

    ``payload`` is the JSON object parsed from the final text, or None when the
    model answered with something that is not a JSON object.
    """

    text: str
    payload: dict | None = None
    tool_calls: list[dict] = Field(default_factory=list)
    thinking: list[str] = Field(default_factory=list)
    images: list[dict] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict)
