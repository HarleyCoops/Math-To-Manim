"""Strict stage contracts for Grok replies.

Extra keys are ignored so a model can include a source field beside the
scene spec. Missing charter keys fail validation and trigger one retry.
"""

from __future__ import annotations

import os
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from grok.validation import normalize_reverse_tree, validate_reverse_tree

STAGE_NAMES = (
    "intent",
    "cartographer",
    "curriculum",
    "math-director",
    "cinematographer",
    "composer",
)


class _Loose(BaseModel):
    model_config = ConfigDict(extra="ignore")


class IntentOutput(_Loose):
    core_claim: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    emotional_arc: list[Any] = Field(min_length=1)
    scope: dict
    duration_seconds: float
    title_options: list[Any] = Field(min_length=1)
    the_big_zoom: str = Field(min_length=1)
    image_read: Any = None


class KnowledgeMapOutput(_Loose):
    target: str = Field(min_length=1)
    nodes: list[Any] = Field(min_length=1)
    edges: list[Any] = Field(min_length=1)
    spine: list[Any] = Field(min_length=1)
    sources: list[Any] = Field(default_factory=list)


class CurriculumOutput(_Loose):
    acts: list[Any] = Field(min_length=1)
    through_line: str = Field(min_length=1)


class MathDossierOutput(_Loose):
    formulas: list[Any]
    color_identity: dict
    numbers: list[Any]
    checks: list[Any]
    sources: list[Any] = Field(default_factory=list)


class ShotListOutput(_Loose):
    shots: list[Any] = Field(min_length=1)
    camera_score: str = Field(min_length=1)
    stills: list[Any] = Field(default_factory=list)
    visual_seeds: list[Any] = Field(default_factory=list)


def scene_class_required() -> str | None:
    value = os.getenv("GROK_SCENE_CLASS", "").strip()
    return value or None


def scene_name_allowed(name: str) -> bool:
    expected = scene_class_required()
    if expected:
        return name == expected
    return name.endswith("Journey") or name.endswith("Story")


class SceneSpecOutput(_Loose):
    scene_name: str = Field(min_length=1)
    scene_class: Literal["ThreeDScene"]
    palette: dict
    objects: list[Any]
    timeline: list[Any]
    constraints: list[Any]
    acceptance: list[Any]

    @field_validator("scene_name")
    @classmethod
    def _name_rule(cls, value: str) -> str:
        if not scene_name_allowed(value):
            expected = scene_class_required()
            if expected:
                raise ValueError(f"scene_name must be {expected}")
            raise ValueError("scene_name must end in Journey or Story")
        return value


class Assessment(_Loose):
    verdict: Literal["pass", "fail"]
    evidence: list[str] = Field(min_length=1)
    repair_stage: Literal[
        "intent",
        "cartographer",
        "curriculum",
        "math-director",
        "cinematographer",
        "composer",
    ]
    feedback: str = ""
    defects: list[str] = Field(default_factory=list)


STAGE_MODELS: dict[str, type[_Loose]] = {
    "intent": IntentOutput,
    "cartographer": KnowledgeMapOutput,
    "curriculum": CurriculumOutput,
    "math-director": MathDossierOutput,
    "cinematographer": ShotListOutput,
    "composer": SceneSpecOutput,
}

_COMPOSER_KEYS = (
    "scene_name",
    "scene_class",
    "palette",
    "objects",
    "timeline",
    "constraints",
    "acceptance",
)
_SOURCE_KEYS = ("source", "grok_scene.py", "scene_source")


def validate_stage_output(stage: str, payload: dict) -> tuple[dict, list[str]]:
    """Return a normalized payload and a list of validation errors."""
    model = STAGE_MODELS[stage]
    data = dict(payload or {})
    if stage == "cartographer":
        data = normalize_reverse_tree(data)
    try:
        parsed = model.model_validate(data)
    except ValidationError as exc:
        messages = []
        for error in exc.errors():
            loc = ".".join(str(part) for part in error.get("loc", ()))
            messages.append(f"{loc}: {error.get('msg')}" if loc else str(error.get("msg")))
        return data, messages
    cleaned = parsed.model_dump()
    if stage == "composer":
        for key in _SOURCE_KEYS:
            if isinstance(data.get(key), str):
                cleaned[key] = data[key]
        cleaned = {key: cleaned[key] for key in list(_COMPOSER_KEYS) + list(_SOURCE_KEYS) if key in cleaned}
    if stage == "cartographer":
        failures = validate_reverse_tree(cleaned)
        if failures:
            return cleaned, failures
    return cleaned, []


def coerce_assessment(payload: dict) -> dict:
    data = dict(payload or {})
    if data.get("repair_stage") == "render":
        data["repair_stage"] = "composer"
    verdict = data.get("verdict")
    if verdict is True:
        data["verdict"] = "pass"
    elif verdict is False:
        data["verdict"] = "fail"
    return data
