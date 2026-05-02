"""Agent stage adapters for the typed animation pipeline."""

from __future__ import annotations

from math_to_manim.agents.codegen import ManimCodeAgent
from math_to_manim.agents.curriculum import CurriculumAgent
from math_to_manim.agents.intent import IntentAgent
from math_to_manim.agents.math_enrichment import MathAgent
from math_to_manim.agents.prerequisite_graph import PrerequisiteGraphAgent
from math_to_manim.agents.publisher import PublisherAgent
from math_to_manim.agents.render import RenderAgent
from math_to_manim.agents.repair import RepairAgent
from math_to_manim.agents.scene_spec import SceneSpecAgent
from math_to_manim.agents.static_review import StaticReviewAgent
from math_to_manim.agents.storyboard import StoryboardAgent
from math_to_manim.agents.video_review import VideoReviewAgent

__all__ = [
    "IntentAgent",
    "PrerequisiteGraphAgent",
    "CurriculumAgent",
    "MathAgent",
    "StoryboardAgent",
    "SceneSpecAgent",
    "ManimCodeAgent",
    "StaticReviewAgent",
    "RenderAgent",
    "VideoReviewAgent",
    "RepairAgent",
    "PublisherAgent",
]
