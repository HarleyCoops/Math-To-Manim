"""Typed contracts for the GLM-native film pipeline.

GLM talks through the Z.ai Coding Plan OpenAI-compatible
``chat/completions`` endpoint. Thinking is always on; reasoning effort is
one of ``low``, ``high``, ``max``. This module never imports Mythos, Sol,
or Grok.
"""

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
    "glm_scene.py",
    "validation.json",
    "review.json",
)

REASONING_EFFORTS = ("low", "high", "max")

# The chat/completions body has no effort enum, so the GLM-native way to
# honor low|high|max is sampling latitude plus a token budget, while the
# thinking block stays switched on in every call.
EFFORT_TEMPERATURE = {"low": 0.15, "high": 0.65, "max": 0.9}
EFFORT_MAX_TOKENS = {"low": 2048, "high": 6144, "max": 12288}

# The default paper stage every GLM scene starts on.
PAPER_STAGE_COLOR = "#f3ecd8"

Quality = Literal["l", "m", "h", "p", "k"]
Effort = Literal["low", "high", "max"]


class RunRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=12_000)
    image: str | None = None
    render: bool = False
    quality: Quality = "l"
    reasoning_effort: Effort = "high"
    max_repairs: int = Field(default=2, ge=0, le=5)
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


class StageCallResult(BaseModel):
    """One finished chat/completions exchange for a pipeline stage."""

    text: str
    payload: dict = Field(default_factory=dict)
    tool_calls: list[dict] = Field(default_factory=list)
    thinking: list[str] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict)


def tool_record(tool_call: dict) -> dict:
    """Normalize one OpenAI-style tool_call into {id, name, arguments}."""
    nested = tool_call.get("function") if isinstance(tool_call.get("function"), dict) else {}
    return {
        "id": tool_call.get("id"),
        "name": tool_call.get("name") or nested.get("name"),
        "arguments": (
            tool_call.get("arguments")
            if tool_call.get("arguments") is not None
            else nested.get("arguments")
        ),
    }
