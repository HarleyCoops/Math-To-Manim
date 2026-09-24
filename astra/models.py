"""Typed contracts for an Astra run and independent jev decision points."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

STAGES = ("brief", "mathematics", "storyboard", "scene")

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
    repair_stage: Literal["brief", "mathematics", "storyboard", "scene"]

    @property
    def approved(self):
        return self.verified and not self.defects and min(
            self.mathematics, self.pedagogy, self.visual_design, self.implementation
        ) >= 0.8

class Request(StrictModel):
    prompt: str = Field(min_length=10)
    quality: Literal["l", "m", "h"] = "h"
    effort: Literal["high", "xhigh", "max"] = "high"
    max_revisions: int = Field(default=6, ge=0, le=20)
    render: bool = True
