"""Typed boundary between Sol reasoning and executable Manim code."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SolutionStep(BaseModel):
    index: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=100)
    explanation: str = Field(min_length=1, max_length=800)
    expression_latex: str = Field(default="", max_length=500)


class VisualBeat(BaseModel):
    kind: Literal["premise", "transformation", "verification", "conclusion"]
    caption: str = Field(min_length=1, max_length=180)
    expression_latex: str = Field(default="", max_length=500)
    accent: Literal["coral", "blue", "gold", "green"] = "coral"


class CalculationResult(BaseModel):
    problem: str = Field(min_length=1, max_length=4000)
    answer: str = Field(min_length=1, max_length=1000)
    answer_latex: str = Field(min_length=1, max_length=500)
    method: str = Field(min_length=1, max_length=200)
    steps: list[SolutionStep] = Field(min_length=1, max_length=12)
    verification: str = Field(min_length=1, max_length=1000)
    assumptions: list[str] = Field(default_factory=list, max_length=8)
    scene: list[VisualBeat] = Field(min_length=1, max_length=12)


class CalculationRequest(BaseModel):
    problem: str = Field(min_length=2, max_length=4000)
    audience: Literal["student", "technical", "expert"] = "student"
    reasoning_effort: Literal["low", "medium", "high", "xhigh", "max"] = "medium"
    offline: bool = False
    render: bool = False


class CalculationResponse(BaseModel):
    run_id: str
    engine: Literal["gpt-5.6-sol", "local-symbolic"]
    model: str
    result: CalculationResult
    manim_source: str
    video_path: str | None = None
