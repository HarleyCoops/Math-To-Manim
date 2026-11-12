"""On-disk contracts for the GLM-native film pipeline.

Everything a run bundle under ``runs/glm/<run_id>/`` is made of is named
here: the request and manifest schemas and the file names the harness writes.
GLM talks through the Z.ai Coding Plan OpenAI-compatible ``chat/completions``
endpoint. Thinking is always on; reasoning effort is one of ``low``, ``high``,
``max``. This module never imports Mythos, Sol, or Grok.
"""

from __future__ import annotations

from typing import Literal, get_args

from pydantic import BaseModel, Field

# Run bundle file names (stage artifacts are named on the stage table).
SCENE_FILE = "glm_scene.py"
VALIDATION_FILE = "validation.json"
REVIEW_FILE = "review.json"
MANIFEST_FILE = "manifest.json"
REQUEST_FILE = "request.json"
TRACES_DIR = "traces"
REPAIR_TRACE_FILE = "repair.json"

# What review.json certifies about a completed bundle.
REVIEW_CHECKS = ("artifact contract", "reverse tree", "python compilation")

Quality = Literal["l", "m", "h", "p", "k"]
Effort = Literal["low", "high", "max"]
QUALITIES: tuple[str, ...] = get_args(Quality)
REASONING_EFFORTS: tuple[str, ...] = get_args(Effort)
MAX_REPAIRS_LIMIT = 5

# The chat/completions body has no effort enum, so the GLM-native way to
# honor low|high|max is sampling latitude plus a token budget, while the
# thinking block stays switched on in every call.
EFFORT_TEMPERATURE = {"low": 0.15, "high": 0.65, "max": 0.9}
EFFORT_MAX_TOKENS = {"low": 2048, "high": 6144, "max": 12288}

# The default paper stage every GLM scene starts on.
PAPER_STAGE_COLOR = "#f3ecd8"
OFFLINE_SCENE_NAME = "GlmOfflineStory"


class RunRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=12_000)
    image: str | None = None
    render: bool = False
    quality: Quality = "l"
    reasoning_effort: Effort = "high"
    max_repairs: int = Field(default=2, ge=0, le=MAX_REPAIRS_LIMIT)
    offline: bool = False


class RunManifest(BaseModel):
    schema_version: int = 1
    run_id: str
    prompt: str
    model: str
    backend: Literal["glm-chat"] = "glm-chat"
    thinking_enabled: bool = True
    key_source: str | None = None
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
