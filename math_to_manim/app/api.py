"""Optional FastAPI application."""

from __future__ import annotations

from math_to_manim.config import RuntimeConfig
from math_to_manim.pipeline.runner import AnimationPipeline


def create_app():
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError("Install the web extra to use the API: pip install -e .[web]") from exc

    app = FastAPI(title="Math-To-Manim Codex API")
    pipeline = AnimationPipeline(RuntimeConfig.from_env())

    @app.post("/generate")
    def generate(payload: dict):
        package = pipeline.generate(
            prompt=payload["prompt"],
            audience_level=payload.get("audience_level", "high_school"),
            desired_duration=int(payload.get("desired_duration", 60)),
            style=payload.get("style", "cinematic"),
            render=bool(payload.get("render", False)),
        )
        return package.to_public_dict()

    return app
