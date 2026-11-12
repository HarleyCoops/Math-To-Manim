"""Typed contracts for an Astra run and independent jev decision points.

The stage table lives here: every other module derives order, checkpoints, CLI
choices and repair routing from these tuples instead of restating stage names.
"""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from astra.render_worker import PROFILES

STAGES = ("brief", "mathematics", "storyboard", "scene")  # authoring stages, in production order
SOURCE_STAGE = "scene"        # the stage whose artifact is executable Manim source: screened, probed, rendered
CHECKPOINTS = STAGES + ("render",)                         # every independently reviewed checkpoint
# A rejected checkpoint is repaired by an authoring stage; render defects belong to the source.
REPAIR_OWNER = {**{stage: stage for stage in STAGES}, "render": SOURCE_STAGE}
# Astra sessions at these stages get live web search (primary mathematical references).
SEARCHES_WEB = frozenset({"mathematics"})
EFFORTS = ("high", "xhigh", "max")
REVIEW_MODES = ("advisory", "gated", "off")
QUALITIES = tuple(PROFILES)

Stage = Literal[STAGES]

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

class Artifact(StrictModel):
    summary: str
    content: str
    checks: list[str]
    sources: list[str]

class Assessment(StrictModel):
    mathematics: float = Field(ge=0, le=1, allow_inf_nan=False)
    pedagogy: float = Field(ge=0, le=1, allow_inf_nan=False)
    visual_design: float = Field(ge=0, le=1, allow_inf_nan=False)
    implementation: float = Field(ge=0, le=1, allow_inf_nan=False)
    verified: bool
    defects: list[str]
    feedback: str
    evidence: list[str] = Field(min_length=1)
    limitations: list[str]
    repair_stage: Stage

class Request(StrictModel):
    prompt: str = Field(min_length=10)
    quality: Literal[QUALITIES] = "h"
    effort: Literal[EFFORTS] = "high"
    max_revisions: int = Field(default=6, ge=0, le=20)
    render: bool = True
    review_mode: Literal[REVIEW_MODES] = 'advisory'
