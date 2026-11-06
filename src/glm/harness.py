"""GLM-native chain: intent through composer, then local verify and render.

One run is one directory under the runs dir. The harness writes the request,
the manifest (kept current after every stage), each stage's artifact and
traces, the scene, and finally validation.json and review.json, exactly once
each, whether the chain ran live or offline.
"""

from __future__ import annotations

import os
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from glm.client import GlmClient, GlmClientError, StageReply
from glm.jsonutil import extract_json_object, extract_scene_source
from glm.models import (
    MANIFEST_FILE,
    REPAIR_TRACE_FILE,
    REQUEST_FILE,
    REVIEW_CHECKS,
    REVIEW_FILE,
    SCENE_FILE,
    TRACES_DIR,
    VALIDATION_FILE,
    RunManifest,
    RunRequest,
)
from glm.offline import OFFLINE_LIMITATION, write_offline_bundle
from glm.stages import BUNDLE_FILES, SCENE_STAGE, STAGES, Stage, stage_prompt
from glm.validation import verify_scene_report

Progress = Callable[[str], None]


def default_runs_dir() -> Path:
    """``$M2M_RUNS_DIR/glm``; else ``runs/glm`` in the source checkout this
    package runs from; else ``./runs/glm`` (installed wheel). Resolved at call time."""
    if os.getenv("M2M_RUNS_DIR"):
        return Path(os.environ["M2M_RUNS_DIR"]) / "glm"
    checkout = Path(__file__).resolve().parents[2]
    base = checkout if (checkout / "pyproject.toml").is_file() else Path.cwd()
    return base / "runs" / "glm"


def stderr_progress(line: str) -> None:
    print(line, file=sys.stderr)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GlmHarness:
    """Runs the six-stage chain against Z.ai chat/completions, or offline."""

    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: GlmClient | None = None,
        progress: Progress | None = None,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.client = client or GlmClient.from_env()
        self.progress = progress or stderr_progress

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

    def run(self, request: RunRequest) -> dict:
        run_dir = self._create_run_dir(request.prompt)
        manifest = RunManifest(
            run_id=run_dir.name,
            prompt=request.prompt,
            model="offline" if request.offline else self.client.model,
            key_source=None if request.offline else self.client.key_source,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            image=request.image,
            created_utc=_utc_now(),
            status_detail={"validation": "pending"},
        )
        self._write_manifest(run_dir, manifest)
        (run_dir / REQUEST_FILE).write_text(request.model_dump_json(indent=2), encoding="utf-8")
        (run_dir / TRACES_DIR).mkdir(exist_ok=True)
        report: dict | None = None

        try:
            if request.offline:
                write_offline_bundle(run_dir, request)
                manifest.attempts.append({"attempt": 0, "mode": "offline", "status": "completed"})
            else:
                self._run_live(run_dir, request, manifest)
                manifest.attempts.append(
                    {"attempt": 0, "mode": "zai-chat-completions", "status": "completed"}
                )

            report = verify_scene_report((run_dir / SCENE_FILE).read_text(encoding="utf-8"))
            repair = 0
            while not report["passed"] and repair < request.max_repairs:
                repair += 1
                self._repair_scene(run_dir, request, report["errors"])
                manifest.attempts.append(
                    {"attempt": repair, "mode": "composer-repair", "input_failures": report["errors"]}
                )
                report = verify_scene_report((run_dir / SCENE_FILE).read_text(encoding="utf-8"))
            if not report["passed"]:
                raise RuntimeError("run bundle validation failed: " + "; ".join(report["errors"]))

            video_path = (
                self._render(run_dir, report["scene_name"], request.quality)
                if request.render
                else None
            )
            self._write_review(run_dir, request, rendered=video_path is not None)
            self._write_validation(run_dir, report)

            manifest.scene_file = SCENE_FILE
            manifest.scene_name = report["scene_name"]
            manifest.video_path = video_path
            manifest.status = "completed"
            manifest.completed_utc = _utc_now()
            manifest.status_detail["validation"] = "complete"
            manifest.artifacts = {name: name for name in BUNDLE_FILES}
            self._write_manifest(run_dir, manifest)
            return json.loads(manifest.model_dump_json())
        except Exception as exc:
            if report is not None:
                self._write_validation(run_dir, report)
            manifest.status = "failed"
            manifest.error = str(exc)
            manifest.completed_utc = _utc_now()
            self._write_manifest(run_dir, manifest)
            raise

    @staticmethod
    def _write_validation(run_dir: Path, report: dict) -> None:
        (run_dir / VALIDATION_FILE).write_text(json.dumps(report, indent=2), encoding="utf-8")

    def _write_review(self, run_dir: Path, request: RunRequest, *, rendered: bool) -> None:
        review = {
            "offline": request.offline,
            "model": "offline" if request.offline else self.client.model,
            "thinking_enabled": not request.offline,
            "checks": list(REVIEW_CHECKS),
            "rendered": rendered,
            "limitations": [OFFLINE_LIMITATION] if request.offline else [],
        }
        (run_dir / REVIEW_FILE).write_text(json.dumps(review, indent=2), encoding="utf-8")

    def _run_live(self, run_dir: Path, request: RunRequest, manifest: RunManifest) -> None:
        image_path = Path(request.image) if request.image else None
        if image_path is not None and not image_path.is_file():
            raise GlmClientError(f"image file not found: {request.image}")

        prior: dict[str, dict] = {}
        for stage in STAGES:
            reply = self.client.complete(
                instructions=stage.charter(),
                text=stage_prompt(stage, request.prompt, prior),
                reasoning_effort=request.reasoning_effort,
                image_path=image_path if stage.takes_image else None,
                tools=stage.tools,
            )
            payload = self._stage_payload(stage, reply)
            (run_dir / stage.artifact).write_text(json.dumps(payload, indent=2), encoding="utf-8")
            prior[stage.artifact] = payload
            if stage.writes_scene:
                try:
                    source = extract_scene_source(reply.text, reply.tool_calls)
                except ValueError as exc:
                    raise GlmClientError(f"composer did not return {SCENE_FILE} source") from exc
                (run_dir / SCENE_FILE).write_text(source, encoding="utf-8")

            self._write_trace(run_dir, stage, request, reply)
            manifest.stages.append(
                {"stage": stage.name, "artifact": stage.artifact, "tool_calls": len(reply.tool_calls)}
            )
            self._write_manifest(run_dir, manifest)
            self.progress(f"  [glm] {stage.name:16} -> {stage.artifact}")

    @staticmethod
    def _stage_payload(stage: Stage, reply: StageReply) -> dict:
        """The stage's JSON object, normalized and checked against its contract."""
        try:
            payload = extract_json_object(reply.text)
        except ValueError as exc:
            raise GlmClientError(f"stage {stage.name} did not return JSON") from exc
        if not isinstance(payload, dict) or not payload:
            raise GlmClientError(f"stage {stage.name} did not return JSON")
        if stage.normalize is not None:
            payload = stage.normalize(payload)
        failures = stage.check(payload) if stage.check is not None else []
        if failures:
            raise GlmClientError(
                f"stage {stage.name} returned an invalid {stage.artifact}: " + "; ".join(failures)
            )
        return payload

    def _write_trace(self, run_dir: Path, stage: Stage, request: RunRequest, reply: StageReply) -> None:
        trace = {
            "stage": stage.name,
            "model": self.client.model,
            "reasoning_effort": request.reasoning_effort,
            "thinking_enabled": True,
            "tools_requested": stage.tools_requested,
            "tool_calls": reply.tool_calls,
            "thinking": reply.thinking,
        }
        traces = run_dir / TRACES_DIR
        (traces / f"{stage.name}.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
        (traces / f"{stage.name}.raw.json").write_text(json.dumps(reply.raw, indent=2), encoding="utf-8")

    def _repair_scene(self, run_dir: Path, request: RunRequest, failures: list[str]) -> None:
        source = (run_dir / SCENE_FILE).read_text(encoding="utf-8")
        reply = self.client.complete(
            instructions=SCENE_STAGE.charter(),
            text=(
                "Repair this Manim scene. Keep the class name, ThreeDScene "
                "contract, paper palette, and camera rule. Return JSON with a "
                "source field containing the complete file.\n\nFAILURES:\n"
                + "\n".join(f"- {item}" for item in failures)
                + "\n\nCURRENT FILE:\n"
                + source
            ),
            reasoning_effort=request.reasoning_effort,
            tools=SCENE_STAGE.tools,
        )
        try:
            repaired = extract_scene_source(reply.text, reply.tool_calls)
        except ValueError as exc:
            raise GlmClientError(f"composer repair did not return {SCENE_FILE} source") from exc
        (run_dir / SCENE_FILE).write_text(repaired, encoding="utf-8")
        (run_dir / TRACES_DIR / REPAIR_TRACE_FILE).write_text(
            json.dumps({"tool_calls": reply.tool_calls, "thinking": reply.thinking}, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _render(run_dir: Path, scene_name: str, quality: str) -> str:
        manim = shutil.which("manim")
        if not manim:
            raise RuntimeError("manim was not found; pip install -e '.[render]'")
        media = run_dir / "media"
        command = [manim, f"-q{quality}", "--media_dir", str(media), str(run_dir / SCENE_FILE), scene_name]
        completed = subprocess.run(command, cwd=run_dir, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError((completed.stderr or completed.stdout)[-4000:])
        videos = sorted(media.rglob("*.mp4"))
        if not videos:
            raise RuntimeError("manim exited 0 but wrote no mp4")
        return str(videos[-1])
