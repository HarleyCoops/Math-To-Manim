"""Grok-native chain: intent through composer, then local verify and render.

The harness walks ``grok.stages.STAGES`` and owns the run bundle: it is the
only writer of manifest.json, validation.json and review.json.
"""

from __future__ import annotations

import os
import base64
import binascii
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from grok.client import XAIClient, XAIClientError
from grok.jsonutil import extract_scene_source
from grok.models import (
    MANIFEST_FILE,
    MEDIA_DIR,
    REQUEST_FILE,
    REVIEW_FILE,
    SCENE_FILE,
    STILLS_DIR,
    TRACES_DIR,
    VALIDATION_FILE,
    RunManifest,
    RunRequest,
)
from grok.offline import OFFLINE_MODEL, write_offline_bundle
from grok.stages import (
    ARTIFACT_NAMES,
    COMPOSER,
    STAGES,
    Stage,
    load_charter,
    tool_labels,
    validate_run,
)

REVIEW_CHECKS = ("artifact contract", "reverse tree", "python compilation")


def default_runs_dir() -> Path:
    """``$M2M_RUNS_DIR/grok``; else ``runs/grok`` in the source checkout this
    package runs from; else ``./runs/grok`` (installed wheel). Resolved at call time."""
    if os.getenv("M2M_RUNS_DIR"):
        return Path(os.environ["M2M_RUNS_DIR"]) / "grok"
    checkout = Path(__file__).resolve().parents[2]
    base = checkout if (checkout / "pyproject.toml").is_file() else Path.cwd()
    return base / "runs" / "grok"


def log_to_stderr(line: str) -> None:
    print(line, file=sys.stderr, flush=True)


class GrokHarness:
    """Runs one request end to end. ``log`` receives progress lines (stderr by
    default; stdout is reserved for CLI JSON and the MCP stdio stream)."""

    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: XAIClient | None = None,
        log: Callable[[str], None] = log_to_stderr,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.client = client or XAIClient()
        self.log = log

    def _create_run_dir(self, prompt: str) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:48] or "film"
        candidate = self.runs_dir / f"{stamp}-{slug}"
        suffix = 1
        while candidate.exists():
            suffix += 1
            candidate = self.runs_dir / f"{stamp}-{slug}-{suffix}"
        candidate.mkdir(parents=True)
        return candidate

    @staticmethod
    def _write_manifest(run_dir: Path, manifest: RunManifest) -> None:
        path = run_dir / MANIFEST_FILE
        temporary = path.with_suffix(".tmp")
        temporary.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(path)

    def run(
        self,
        request: RunRequest,
        *,
        on_start: Callable[[str], None] | None = None,
    ) -> dict:
        """Produce one run bundle and return its final manifest as a dict.

        ``on_start`` is called with the run id as soon as the run directory
        exists, so callers can watch manifest.json while the chain runs.
        """
        model = OFFLINE_MODEL if request.offline else (request.model or self.client.model)
        effort = request.reasoning_effort or self.client.reasoning_effort
        run_dir = self._create_run_dir(request.prompt)
        manifest = RunManifest(
            run_id=run_dir.name,
            prompt=request.prompt,
            model=model,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            image=request.image,
            created_utc=_now(),
            artifacts={"validation": VALIDATION_FILE, "scene": SCENE_FILE},
            status_detail={"validation": "pending"},
        )
        self._write_manifest(run_dir, manifest)
        (run_dir / REQUEST_FILE).write_text(request.model_dump_json(indent=2), encoding="utf-8")
        (run_dir / TRACES_DIR).mkdir(exist_ok=True)
        if on_start is not None:
            on_start(run_dir.name)

        try:
            if request.offline:
                write_offline_bundle(run_dir, request)
                manifest.attempts.append({"attempt": 0, "mode": "offline", "status": "completed"})
            else:
                self._run_live(run_dir, request, manifest, model, effort)
                manifest.attempts.append(
                    {"attempt": 0, "mode": "xai-responses", "status": "completed"}
                )

            failures, scene_name = validate_run(run_dir)
            repair = 0
            while failures and not request.offline and repair < request.max_repairs:
                repair += 1
                self.log(f"  [grok] repair {repair}/{request.max_repairs}: {len(failures)} failure(s)")
                self._repair_scene(run_dir, failures, repair, model, effort)
                manifest.attempts.append(
                    {"attempt": repair, "mode": "composer-repair", "input_failures": failures}
                )
                failures, scene_name = validate_run(run_dir)

            _write_json(
                run_dir / VALIDATION_FILE,
                {"passed": not failures, "scene_name": scene_name, "errors": failures},
            )
            if failures:
                raise RuntimeError("run bundle validation failed: " + "; ".join(failures))

            video_path = None
            if request.render and not request.offline:
                video_path = self._render(run_dir, scene_name, request.quality)

            _write_json(
                run_dir / REVIEW_FILE,
                {
                    "offline": request.offline,
                    "model": model,
                    "checks": list(REVIEW_CHECKS),
                    "rendered": video_path is not None,
                    "limitations": (
                        ["deterministic rehearsal; no xAI call"] if request.offline else []
                    ),
                },
            )
            manifest.scene_file = SCENE_FILE
            manifest.scene_name = scene_name
            manifest.video_path = video_path
            manifest.status = "completed"
            manifest.completed_utc = _now()
            manifest.status_detail["validation"] = "complete"
            manifest.artifacts = {name: name for name in ARTIFACT_NAMES}
            self._write_manifest(run_dir, manifest)
            return json.loads(manifest.model_dump_json())
        except Exception as exc:
            manifest.status = "failed"
            manifest.error = str(exc)
            manifest.completed_utc = _now()
            self._write_manifest(run_dir, manifest)
            raise

    def _run_live(
        self,
        run_dir: Path,
        request: RunRequest,
        manifest: RunManifest,
        model: str,
        effort: str,
    ) -> None:
        if not self.client.api_key:
            raise XAIClientError("XAI_API_KEY is not set")
        image_path = Path(request.image) if request.image else None
        if image_path is not None and not image_path.is_file():
            raise XAIClientError(f"image file not found: {request.image}")

        prior: dict[str, dict] = {}
        for stage in STAGES:
            result = self.client.complete(
                instructions=load_charter(stage.charter_file),
                text=_stage_prompt(stage, request.prompt, prior),
                tools=stage.tools,
                image_path=image_path if stage.takes_image else None,
                tool_choice=stage.tool_choice,
                function_handlers=stage.function_handlers,
                model=model,
                reasoning_effort=effort,
            )
            payload = result.payload
            if not payload:
                raise XAIClientError(f"stage {stage.name} did not return JSON")
            if stage.normalize is not None:
                payload = stage.normalize(payload)
            _write_json(run_dir / stage.artifact, payload)
            prior[stage.artifact] = payload

            if stage.writes_scene:
                try:
                    source = extract_scene_source(payload, result.text, result.tool_calls)
                except ValueError as exc:
                    raise XAIClientError(f"{stage.name} did not return {SCENE_FILE} source") from exc
                (run_dir / SCENE_FILE).write_text(source, encoding="utf-8")

            _write_json(
                run_dir / TRACES_DIR / f"{stage.name}.json",
                {
                    "stage": stage.name,
                    "model": model,
                    "reasoning_effort": effort,
                    "tools_requested": tool_labels(stage),
                    "tool_calls": result.tool_calls,
                    "thinking": result.thinking,
                    "stills": write_stills(run_dir, result.images),
                },
            )
            _write_json(run_dir / TRACES_DIR / f"{stage.name}.raw.json", result.raw)
            manifest.stages.append(
                {"stage": stage.name, "artifact": stage.artifact, "tool_calls": len(result.tool_calls)}
            )
            self._write_manifest(run_dir, manifest)
            self.log(f"  [grok] {stage.name:16} -> {stage.artifact}")

    def _repair_scene(
        self, run_dir: Path, failures: list[str], attempt: int, model: str, effort: str
    ) -> None:
        source = (run_dir / SCENE_FILE).read_text(encoding="utf-8")
        result = self.client.complete(
            instructions=load_charter(COMPOSER.charter_file),
            text=(
                "Repair this Manim scene. Keep the class name, ThreeDScene contract, "
                "and camera rule. Return JSON with a source field containing the "
                "complete file.\n\nFAILURES:\n"
                + "\n".join(f"- {item}" for item in failures)
                + "\n\nCURRENT FILE:\n"
                + source
            ),
            tools=COMPOSER.tools,
            function_handlers=COMPOSER.function_handlers,
            model=model,
            reasoning_effort=effort,
        )
        try:
            repaired = extract_scene_source(result.payload, result.text, result.tool_calls)
        except ValueError as exc:
            raise XAIClientError(f"composer repair did not return {SCENE_FILE} source") from exc
        (run_dir / SCENE_FILE).write_text(repaired, encoding="utf-8")
        _write_json(
            run_dir / TRACES_DIR / f"repair-{attempt}.json",
            {"input_failures": failures, "tool_calls": result.tool_calls, "thinking": result.thinking},
        )

    @staticmethod
    def _render(run_dir: Path, scene_name: str, quality: str) -> str:
        manim = shutil.which("manim")
        if not manim:
            raise RuntimeError("manim was not found; pip install -e '.[render]'")
        media = run_dir / MEDIA_DIR
        command = [manim, f"-q{quality}", "--media_dir", str(media), str(run_dir / SCENE_FILE), scene_name]
        completed = subprocess.run(command, cwd=run_dir, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError((completed.stderr or completed.stdout)[-4000:])
        videos = sorted(media.rglob("*.mp4"))
        if not videos:
            raise RuntimeError("manim exited 0 but wrote no mp4")
        return str(videos[-1])


def write_stills(run_dir: Path, images: list[dict]) -> list[str]:
    """Save image_generation results under stills/ and return their relative paths."""
    if not images:
        return []
    stills_dir = run_dir / STILLS_DIR
    stills_dir.mkdir(exist_ok=True)
    written: list[str] = []
    for index, image in enumerate(images, start=1):
        raw = image.get("result")
        if not raw or not isinstance(raw, str):
            continue
        if raw.startswith("data:") and "," in raw:
            raw = raw.split(",", 1)[1]
        path = stills_dir / f"{index:02d}.jpg"
        try:
            path.write_bytes(base64.b64decode(raw, validate=False))
        except (ValueError, binascii.Error):
            continue
        _write_json(
            stills_dir / f"{index:02d}.json",
            {"filename": path.name, "prompt": image.get("prompt"), "id": image.get("id")},
        )
        written.append(str(path.relative_to(run_dir)).replace("\\", "/"))
    return written


def _stage_prompt(stage: Stage, prompt: str, prior: dict[str, dict]) -> str:
    dossier = json.dumps(prior, indent=2) if prior else "{}"
    note = f"{stage.reply_note}\n" if stage.reply_note else ""
    return (
        f"User request:\n{prompt}\n\n"
        f"You are the {stage.name} stage. Read the charter. Return one JSON object "
        f"with exactly the keys the charter names.\n{note}\n"
        f"Upstream artifacts:\n{dossier}\n"
    )


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
