"""Strict, serializable contracts for visual-improvement rollouts."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StringConstraints,
    ValidationInfo,
    field_validator,
    model_validator,
)

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
ImageDigest = Annotated[
    str,
    StringConstraints(pattern=r"^(?:sha256:)?[0-9a-f]{64}$"),
]
NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
SourceCode = Annotated[str, StringConstraints(min_length=1)]
UnitFloat = Annotated[float, Field(ge=0.0, le=1.0)]


class StrictFrozenModel(BaseModel):
    """Base model for immutable experiment artifacts."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class RevisionScope(str, Enum):
    CODE_ONLY = "code_only"
    SPEC_AND_CODE = "spec_and_code"
    NO_CHANGE = "no_change"


class EducationalContract(StrictFrozenModel):
    task_id: NonEmpty
    source_id: NonEmpty
    original_request: NonEmpty
    audience: NonEmpty
    required_concepts: tuple[NonEmpty, ...] = Field(min_length=1)
    required_formulas: tuple[NonEmpty, ...] = Field(min_length=1)
    required_narrative_beats: tuple[NonEmpty, ...] = Field(min_length=1)
    min_duration_seconds: float = Field(gt=0)
    max_duration_seconds: float = Field(gt=0)
    provider: Literal["synthetic", "mythos", "sol"]
    source_artifact_hashes: dict[NonEmpty, Sha256] = Field(min_length=1)

    @model_validator(mode="after")
    def duration_bounds_are_ordered(self) -> "EducationalContract":
        if self.max_duration_seconds < self.min_duration_seconds:
            raise ValueError("max duration must be at least min duration")
        return self


class FocusBeat(StrictFrozenModel):
    beat_id: NonEmpty
    timestamp: float = Field(ge=0)
    target_id: NonEmpty
    intended_region: tuple[float, float, float, float]
    min_viewport_occupancy: UnitFloat
    max_viewport_occupancy: UnitFloat

    @model_validator(mode="after")
    def occupancy_bounds_are_ordered(self) -> "FocusBeat":
        if self.max_viewport_occupancy < self.min_viewport_occupancy:
            raise ValueError("focus occupancy bounds are reversed")
        return self


class EditableBaseline(StrictFrozenModel):
    scene_spec: dict[str, JsonValue]
    code: SourceCode
    render_manifest: dict[str, JsonValue]
    contact_sheet_sha256: Sha256
    frame_sha256: tuple[Sha256, ...] = Field(min_length=1)
    focus_beats: tuple[FocusBeat, ...]


class Diagnosis(StrictFrozenModel):
    category: NonEmpty
    evidence: NonEmpty
    intent: NonEmpty


class VisualRevision(StrictFrozenModel):
    schema_version: Literal["m2m2.visual_revision.v1"]
    scope: RevisionScope
    diagnosis: tuple[Diagnosis, ...] = Field(min_length=1)
    scene_spec_patch: dict[str, JsonValue] | None
    code: SourceCode
    expected_improvements: tuple[NonEmpty, ...]

    @model_validator(mode="after")
    def scope_is_consistent(
        self,
        info: ValidationInfo,
    ) -> "VisualRevision":
        if (
            self.scope is RevisionScope.CODE_ONLY
            and self.scene_spec_patch is not None
        ):
            raise ValueError("code_only cannot include scene_spec_patch")
        if (
            self.scope is RevisionScope.SPEC_AND_CODE
            and self.scene_spec_patch is None
        ):
            raise ValueError("spec_and_code requires scene_spec_patch")
        if self.scope is RevisionScope.NO_CHANGE:
            if self.scene_spec_patch is not None:
                raise ValueError("no_change cannot include scene_spec_patch")
            baseline_code = (
                info.context.get("baseline_code")
                if isinstance(info.context, dict)
                else None
            )
            if baseline_code is not None and self.code != baseline_code:
                raise ValueError("no_change must reproduce baseline code")
        return self


class Resolution(StrictFrozenModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class OcrBox(StrictFrozenModel):
    text: str
    confidence: UnitFloat
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    timestamp: float = Field(ge=0)


class TrackedObject(StrictFrozenModel):
    object_id: NonEmpty
    timestamp: float = Field(ge=0)
    x: float
    y: float
    width: float = Field(ge=0)
    height: float = Field(ge=0)
    visible: bool = True


class FocusMeasurement(StrictFrozenModel):
    beat_id: NonEmpty
    target_id: NonEmpty
    timestamp: float = Field(ge=0)
    inside_frame: bool
    focal_distance: UnitFloat
    viewport_occupancy: UnitFloat
    clipped_ratio: UnitFloat


class VisualEvidence(StrictFrozenModel):
    render_status: Literal["completed", "failed"]
    duration_seconds: float = Field(ge=0)
    resolution: Resolution
    sampled_timestamps: tuple[float, ...]
    contact_sheet_sha256: Sha256
    frame_sha256: tuple[Sha256, ...] = Field(min_length=1)
    ocr_boxes: tuple[OcrBox, ...]
    tracked_objects: tuple[TrackedObject, ...]
    focus_measurements: tuple[FocusMeasurement, ...]
    clipping_ratio: UnitFloat
    overlap_ratio: UnitFloat
    density_ratio: UnitFloat

    @field_validator("sampled_timestamps")
    @classmethod
    def timestamps_are_nonnegative_and_ordered(
        cls,
        value: tuple[float, ...],
    ) -> tuple[float, ...]:
        if any(item < 0 for item in value):
            raise ValueError("sampled timestamps must be nonnegative")
        if tuple(sorted(value)) != value:
            raise ValueError("sampled timestamps must be ordered")
        return value


class MetricScore(StrictFrozenModel):
    name: NonEmpty
    baseline: UnitFloat
    candidate: UnitFloat
    relative: UnitFloat
    raw: dict[str, JsonValue]


class InfrastructureExclusion(StrictFrozenModel):
    category: NonEmpty
    message: NonEmpty
    retryable: bool = True
    attempt: int = Field(ge=0)


_REQUIRED_COMPONENTS = frozenset(
    {
        "framing",
        "legibility",
        "focus",
        "pairwise_visual_preference",
    }
)
_SECRET_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "cookie",
        "password",
        "secret",
        "token",
    }
)


def _contains_secret_like_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in _SECRET_KEYS or normalized.endswith("_token"):
                return True
            if _contains_secret_like_key(nested):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_contains_secret_like_key(item) for item in value)
    return False


class RewardLedger(StrictFrozenModel):
    schema_version: Literal["m2m2.reward_ledger.v1"]
    task_id: NonEmpty
    eligible: bool
    exclusion: InfrastructureExclusion | None
    raw_measurements: dict[str, JsonValue]
    component_scores: dict[str, MetricScore]
    judge_orders: tuple[
        Literal["candidate_baseline", "baseline_candidate"],
        Literal["candidate_baseline", "baseline_candidate"],
    ]
    judge_verdicts: tuple[
        Literal["loss", "tie", "win"],
        Literal["loss", "tie", "win"],
    ]
    judge_order_consistent: bool
    aggregate_reward: UnitFloat
    runtime_image_digest: ImageDigest
    environment_sha256: Sha256
    dataset_sha256: Sha256
    config_sha256: Sha256
    judge_prompt_sha256: Sha256
    model_id: NonEmpty
    judge_model_id: NonEmpty
    timing_seconds: dict[NonEmpty, Annotated[float, Field(ge=0)]]

    @model_validator(mode="before")
    @classmethod
    def reject_secret_material(cls, value: Any) -> Any:
        if _contains_secret_like_key(value):
            raise ValueError("reward ledger contains a secret-like key")
        return value

    @model_validator(mode="after")
    def ledger_is_complete(self) -> "RewardLedger":
        present = frozenset(self.component_scores)
        if present != _REQUIRED_COMPONENTS:
            missing = sorted(_REQUIRED_COMPONENTS - present)
            extra = sorted(present - _REQUIRED_COMPONENTS)
            raise ValueError(
                f"component scores must contain exactly the required set; "
                f"missing={missing}, extra={extra}"
            )
        if self.eligible and self.exclusion is not None:
            raise ValueError("eligible ledger cannot have an exclusion")
        return self


__all__ = [
    "Diagnosis",
    "EditableBaseline",
    "EducationalContract",
    "FocusBeat",
    "FocusMeasurement",
    "InfrastructureExclusion",
    "MetricScore",
    "OcrBox",
    "Resolution",
    "RewardLedger",
    "RevisionScope",
    "TrackedObject",
    "VisualEvidence",
    "VisualRevision",
]
