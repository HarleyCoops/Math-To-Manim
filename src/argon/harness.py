"""Argon Google ADK (`google-adk` + `google-genai`) 6-stage reasoning chain harness.

``run()`` produces a run bundle (live stages or the offline rehearsal), checks it
against the stage contract, repairs the scene through the composer when needed,
optionally renders, then writes validation.json, review.json and the final
manifest. Every bundle file goes through ``argon.bundle``.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from argon import bundle
from argon.jsonutil import extract_scene_source
from argon.models import SCENE_FILE, RunManifest, RunRequest
from argon.offline import OFFLINE_MODEL, write_offline_bundle
from argon.render import render_scene
from argon.stages import COMPOSER, STAGES, Stage, stage_prompt

if TYPE_CHECKING:
    from argon.client import ArgonClient


def _stderr_progress(message: str) -> None:
    print(message, file=sys.stderr)


class ArgonHarness:
    """Runs the 6-stage Argon Google ADK chain: intent -> cartographer -> curriculum ->
    math-director -> cinematographer -> composer, then static verify & Manim render.

    The Google client is created on first live use, so offline runs and the run
    ledger work without ``google-adk`` installed.
    """

    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: ArgonClient | None = None,
        progress: Callable[[str], None] = _stderr_progress,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else bundle.default_runs_dir()
        self._client = client
        self.progress = progress

    @property
    def client(self) -> ArgonClient:
        if self._client is None:
            from argon.client import ArgonClient

            self._client = ArgonClient()
        return self._client

    def run(self, request: RunRequest) -> dict:
        run_dir = bundle.create_run_dir(self.runs_dir, request.prompt)
        model = OFFLINE_MODEL if request.offline else self.client.model
        manifest = bundle.new_manifest(
            run_dir,
            prompt=request.prompt,
            model=model,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            image=request.image,
        )
        bundle.write_request(run_dir, request.model_dump())

        try:
            if request.offline:
                write_offline_bundle(run_dir, request)
                manifest.attempts.append({"attempt": 0, "mode": "offline", "status": "completed"})
            else:
                self._run_live(run_dir, request, manifest)

            failures, scene_name = bundle.validate_run(run_dir)
            repairs = 0
            while failures and not request.offline and repairs < request.max_repairs:
                repairs += 1
                self._repair_scene(run_dir, request, failures)
                manifest.attempts.append(
                    {"attempt": repairs, "mode": "composer-repair", "input_failures": failures}
                )
                failures, scene_name = bundle.validate_run(run_dir)
            if failures:
                raise RuntimeError("run bundle validation failed: " + "; ".join(failures))
            assert scene_name is not None

            video_path = None
            if request.render and not request.offline:
                video_path = render_scene(run_dir, scene_name, request.quality)

            bundle.write_validation(run_dir)
            bundle.write_review(run_dir, offline=request.offline, model=model, video_path=video_path)
            bundle.complete_manifest(run_dir, manifest, scene_name=scene_name, video_path=video_path)
            return json.loads(manifest.model_dump_json())
        except Exception as exc:
            bundle.fail_manifest(run_dir, manifest, str(exc))
            raise

    def _run_live(self, run_dir: Path, request: RunRequest, manifest: RunManifest) -> None:
        from argon.client import ArgonClientError

        client = self.client
        client.require_key()
        image_path = Path(request.image) if request.image else None
        if image_path is not None and not image_path.is_file():
            raise ArgonClientError(f"image file not found: {request.image}")

        prior: dict[str, dict] = {}
        for stage in STAGES:
            result = client.complete(
                stage,
                text=stage_prompt(stage, request.prompt, prior),
                reasoning_effort=request.reasoning_effort,
                image_path=image_path if stage.accepts_image else None,
            )
            if not result.payload:
                raise ArgonClientError(f"stage {stage.name} did not return JSON")
            try:
                payload = stage.prepare(result.payload)
            except ValueError as exc:
                raise ArgonClientError(str(exc)) from exc
            bundle.write_artifact(run_dir, stage, payload)
            prior[stage.artifact] = payload

            if stage.writes_scene:
                try:
                    source = extract_scene_source(payload, result.text, result.tool_calls)
                except ValueError as exc:
                    raise ArgonClientError(f"{stage.name} did not return {SCENE_FILE} source") from exc
                bundle.write_scene(run_dir, source)

            bundle.write_trace(
                run_dir,
                stage.name,
                bundle.stage_trace(stage, result, model=client.model, reasoning_effort=request.reasoning_effort),
            )
            bundle.write_trace(run_dir, f"{stage.name}.raw", result.raw)
            manifest.stages.append(
                {"stage": stage.name, "artifact": stage.artifact, "tool_calls": len(result.tool_calls)}
            )
            bundle.write_manifest(run_dir, manifest)
            self.progress(f"  [argon-adk] {stage.name:16} -> {stage.artifact}")

        manifest.attempts.append({"attempt": 0, "mode": "google-adk", "status": "completed"})

    def _repair_scene(self, run_dir: Path, request: RunRequest, failures: list[str]) -> None:
        from argon.client import ArgonClientError

        stage: Stage = COMPOSER
        result = self.client.complete(
            stage,
            text=(
                "Repair this Manim scene. Keep the class name, ThreeDScene contract, "
                "and camera rule. Return JSON with a source field containing the "
                "complete file.\n\nFAILURES:\n"
                + "\n".join(f"- {item}" for item in failures)
                + "\n\nCURRENT FILE:\n"
                + bundle.read_scene(run_dir)
            ),
            reasoning_effort=request.reasoning_effort,
        )
        try:
            repaired = extract_scene_source(result.payload, result.text, result.tool_calls)
        except ValueError as exc:
            raise ArgonClientError(f"{stage.name} repair did not return {SCENE_FILE} source") from exc
        bundle.write_scene(run_dir, repaired)
        bundle.write_trace(run_dir, "repair", {"tool_calls": result.tool_calls, "thinking": result.thinking})
