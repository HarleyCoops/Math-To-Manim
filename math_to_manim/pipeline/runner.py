"""End-to-end typed animation pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any

from math_to_manim.agents import (
    CurriculumAgent,
    IntentAgent,
    ManimCodeAgent,
    MathAgent,
    PrerequisiteGraphAgent,
    PublisherAgent,
    RenderAgent,
    SceneSpecAgent,
    StaticReviewAgent,
    StoryboardAgent,
    VideoReviewAgent,
)
from math_to_manim.agents.codegen import write_generated_code
from math_to_manim.config import RuntimeConfig
from math_to_manim.pipeline.state import PipelineState
from math_to_manim.pipeline.tracing import TraceWriter
from math_to_manim.schemas import AnimationPackage, RenderResult, UserRequest


class AnimationPipeline:
    """Coordinates all stage agents and persists canonical artifacts."""

    def __init__(self, config: RuntimeConfig | None = None):
        self.config = config or RuntimeConfig.from_env()
        self.intent_agent = IntentAgent(self.config)
        self.graph_agent = PrerequisiteGraphAgent(self.config)
        self.curriculum_agent = CurriculumAgent(self.config)
        self.math_agent = MathAgent(self.config)
        self.storyboard_agent = StoryboardAgent(self.config)
        self.scene_spec_agent = SceneSpecAgent(self.config)
        self.codegen_agent = ManimCodeAgent(self.config)
        self.static_review_agent = StaticReviewAgent(self.config)
        self.render_agent = RenderAgent(self.config)
        self.video_review_agent = VideoReviewAgent(self.config)
        self.publisher_agent = PublisherAgent(self.config)

    def generate(
        self,
        *,
        prompt: str,
        audience_level: str = "high_school",
        desired_duration: int = 60,
        style: str = "cinematic",
        render: bool = True,
    ) -> AnimationPackage:
        request = UserRequest(
            prompt=prompt,
            target_audience=audience_level,
            duration_seconds=desired_duration,
            style=style,
            constraints={
                "output_formats": ["mp4", "gif", "readme"],
                "target_platform": "local",
            },
            metadata={"requested_model": self.config.model},
        )
        run_dir = self._create_run_dir(prompt)
        state = PipelineState(run_dir=run_dir)
        trace = TraceWriter(run_dir / "trace.jsonl", enabled=self.config.trace_enabled)

        state.put("request", request)
        save_artifact(run_dir, "request", request)
        trace.event("request", request.to_public_dict())

        intent = state.put("intent", self.intent_agent.run(request))
        save_artifact(run_dir, "intent", intent)
        trace.event("intent", intent.to_public_dict())

        graph = state.put("knowledge_graph", self.graph_agent.run(intent))
        save_artifact(run_dir, "knowledge_graph", graph)
        trace.event("knowledge_graph", graph.to_public_dict())

        curriculum = state.put("curriculum", self.curriculum_agent.run(graph))
        save_artifact(run_dir, "curriculum", curriculum)

        math_packet = state.put("math_packet", self.math_agent.run(curriculum))
        save_artifact(run_dir, "math_packet", math_packet)

        storyboard = state.put("storyboard", self.storyboard_agent.run(math_packet))
        save_artifact(run_dir, "storyboard", storyboard)

        scene_spec = state.put("scene_spec", self.scene_spec_agent.run(storyboard))
        save_artifact(run_dir, "scene_spec", scene_spec)

        generated = state.put("generated_code", self.codegen_agent.run(scene_spec))
        save_artifact(run_dir, "generated_code", generated)
        code_path = write_generated_code(generated, run_dir)

        validation = state.put("validation_report", self.static_review_agent.run((generated, code_path)))
        save_artifact(run_dir, "validation_report", validation)

        if render and validation.is_successful:
            render_result = state.put(
                "render_result",
                self.render_agent.run((generated, code_path, self.config.default_quality)),
            )
        else:
            render_result = state.put(
                "render_result",
                RenderResult(
                    status="failed",
                    scene_name=generated.scene_name,
                    output_path=None,
                    command=[],
                    stdout="",
                    stderr="render skipped" if not render else "static validation did not pass",
                    metadata={"skipped": True},
                ),
            )
        save_artifact(run_dir, "render_result", render_result)

        review = state.put("review_report", self.video_review_agent.run(render_result))
        save_artifact(run_dir, "review_report", review)

        reports = [
            str(run_dir / "validation_report.json"),
            str(run_dir / "render_result.json"),
            str(run_dir / "review_report.json"),
        ]
        package = state.put(
            "animation_package",
            self.publisher_agent.run((request, run_dir, render_result, review, reports)),
        )
        package = package.model_copy(
            update={
                "intent": intent,
                "knowledge_graph": graph,
                "curriculum_plan": curriculum,
                "math_packet": math_packet,
                "storyboard": storyboard,
                "scene_specs": [scene_spec],
                "generated_code": [generated],
                "validation_report": validation,
            }
        )
        save_artifact(run_dir, "animation_package", package)
        save_json(
            run_dir / "manifest.json",
            {
                "run_dir": str(run_dir),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "model": self.config.model,
                "render_requested": render,
                "artifacts": sorted(state.artifacts.keys()),
            }
        )
        return package

    def _create_run_dir(self, prompt: str) -> Path:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", prompt.lower()).strip("-")[:48] or "animation"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = self.config.runs_dir / f"{timestamp}-{slug}"
        run_dir.mkdir(parents=True, exist_ok=False)
        return run_dir


def save_artifact(run_dir: Path, name: str, artifact: Any) -> None:
    save_json(run_dir / f"{name}.json", artifact.to_public_dict())


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
