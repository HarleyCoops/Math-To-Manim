"""Complete MiMo 2.6 tool-calling Math-To-Manim run harness.

``run`` creates a run bundle and ``resume`` picks an existing one up; both go
through the same completion path: produce stage artifacts (live chain or
offline bundle), validate, repair the scene stage a bounded number of times,
optionally render, and finish the manifest. The harness is the only writer
of ``validation.json``, ``review.json`` and ``manifest.json``.
"""

from __future__ import annotations

import os
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from mimo.agents import SCENE_STAGE, STAGE_ARTIFACTS
from mimo.client import MimoClient
from mimo.models import (
    MANIFEST_FILE,
    MEDIA_DIR,
    RENDER_LOG_FILE,
    REQUEST_FILE,
    REVIEW_FILE,
    SCENE_FILE,
    VALIDATION_FILE,
    PipelineResult,
    RunManifest,
    RunRequest,
)
from mimo.offline import write_offline_bundle
from mimo.staged import StageClient, ToolCallingPipeline
from mimo.validation import RunValidation, validate_run


def default_runs_dir() -> Path:
    """``$M2M_RUNS_DIR/mimo``; else ``runs/mimo`` in the source checkout this
    package runs from; else ``./runs/mimo`` (installed wheel). Resolved at call time."""
    if os.getenv("M2M_RUNS_DIR"):
        return Path(os.environ["M2M_RUNS_DIR"]) / "mimo"
    checkout = Path(__file__).resolve().parents[2]
    base = checkout if (checkout / "pyproject.toml").is_file() else Path.cwd()
    return base / "runs" / "mimo"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_video(media_dir: Path) -> Path | None:
    """The rendered mp4 under ``media/``, ignoring manim's partial movie files."""
    if not media_dir.is_dir():
        return None
    videos = sorted(
        path for path in media_dir.rglob("*.mp4") if "partial_movie_files" not in path.parts
    )
    return videos[0] if videos else None


class MimoHarness:
    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: StageClient | None = None,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.client = client or MimoClient()

    # -- run bundles ---------------------------------------------------------

    def run_dir(self, run_id: str) -> Path:
        """The directory of an existing run; ``run_id`` must be a plain directory name."""
        if not run_id or run_id in {".", ".."} or Path(run_id).name != run_id:
            raise ValueError(f"invalid MiMo run id: {run_id!r}")
        path = self.runs_dir / run_id
        if not (path / MANIFEST_FILE).is_file():
            raise FileNotFoundError(f"no MiMo run {run_id!r} under {self.runs_dir}")
        return path

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

    def list_runs(self, *, limit: int = 20) -> list[RunManifest]:
        manifests: list[RunManifest] = []
        if not self.runs_dir.is_dir():
            return manifests
        for path in sorted(self.runs_dir.glob(f"*/{MANIFEST_FILE}"), reverse=True)[: max(1, limit)]:
            try:
                manifests.append(RunManifest.model_validate_json(path.read_text(encoding="utf-8")))
            except ValueError:
                continue
        return manifests

    def get_run(self, run_id: str) -> RunManifest:
        path = self.run_dir(run_id) / MANIFEST_FILE
        return RunManifest.model_validate_json(path.read_text(encoding="utf-8"))

    # -- producing and completing a run --------------------------------------

    def run(self, request: RunRequest) -> dict:
        run_dir = self._create_run_dir(request.prompt)
        manifest = RunManifest(
            run_id=run_dir.name,
            prompt=request.prompt,
            model=self.client.model,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            created_utc=_now(),
            artifacts={"validation": VALIDATION_FILE, "scene": SCENE_FILE},
            status_detail={"validation": "pending"},
        )
        self._write_manifest(run_dir, manifest)
        (run_dir / REQUEST_FILE).write_text(request.model_dump_json(indent=2), encoding="utf-8")
        return self._complete(run_dir, manifest, request, from_stage=None)

    def resume(self, run_id: str, *, from_stage: str | None = None) -> dict:
        """Finish an existing run: cached stages are kept, ``from_stage`` and its dependants re-run."""
        run_dir = self.run_dir(run_id)
        manifest = self.get_run(run_id)
        request_path = run_dir / REQUEST_FILE
        if not request_path.is_file():
            raise FileNotFoundError(f"run {run_id!r} has no {REQUEST_FILE}; it cannot be resumed")
        request = RunRequest.model_validate_json(request_path.read_text(encoding="utf-8"))
        manifest.status = "running"
        manifest.error = None
        manifest.completed_utc = None
        manifest.status_detail["validation"] = "pending"
        self._write_manifest(run_dir, manifest)
        return self._complete(run_dir, manifest, request, from_stage=from_stage)

    def _produce(
        self,
        run_dir: Path,
        request: RunRequest,
        *,
        from_stage: str | None,
        feedback: dict[str, str] | None = None,
    ) -> PipelineResult:
        if request.offline:
            return write_offline_bundle(run_dir, request)
        pipeline = ToolCallingPipeline(client=self.client)
        return pipeline.run(run_dir, request, from_stage=from_stage, feedback=feedback)

    def _validate(self, run_dir: Path) -> RunValidation:
        validation = validate_run(run_dir, STAGE_ARTIFACTS)
        (run_dir / VALIDATION_FILE).write_text(json.dumps(validation.report, indent=2), encoding="utf-8")
        return validation

    def _complete(
        self,
        run_dir: Path,
        manifest: RunManifest,
        request: RunRequest,
        *,
        from_stage: str | None,
    ) -> dict:
        mode = "offline" if request.offline else "mimo-tool-calling"
        review_path = run_dir / REVIEW_FILE
        if not review_path.is_file():
            review_path.write_text(json.dumps({"status": "skipped"}, indent=2), encoding="utf-8")
        try:
            result = self._produce(run_dir, request, from_stage=from_stage)
            attempt: dict = {"attempt": len(manifest.attempts), "mode": mode, "status": "completed"}
            if from_stage:
                attempt["from_stage"] = from_stage
            manifest.attempts.append(attempt)
            manifest.tool_call_count = len(result.tool_calls)
            manifest.stage_records = result.stage_records

            validation = self._validate(run_dir)
            repairs = 0
            while not validation.ok and repairs < request.max_repairs:
                repairs += 1
                evidence = "\n".join(f"- {failure}" for failure in validation.failures)
                self._produce(
                    run_dir,
                    request,
                    from_stage=SCENE_STAGE.name,
                    feedback={SCENE_STAGE.name: evidence},
                )
                manifest.attempts.append(
                    {
                        "attempt": len(manifest.attempts),
                        "mode": f"{SCENE_STAGE.name}-static-repair",
                        "status": "completed",
                        "input_failures": validation.failures,
                    }
                )
                validation = self._validate(run_dir)
            if not validation.ok:
                raise RuntimeError("run bundle validation failed: " + "; ".join(validation.failures))

            video_path = None
            if request.render:
                video_path = str(self._render(run_dir, validation.scene_name, request.quality))

            manifest.scene_file = SCENE_FILE
            manifest.scene_name = validation.scene_name
            manifest.video_path = video_path
            manifest.status = "completed"
            manifest.completed_utc = _now()
            manifest.status_detail["validation"] = "passed"
            self._write_manifest(run_dir, manifest)
            return {
                "run_id": manifest.run_id,
                "status": manifest.status,
                "scene_name": manifest.scene_name,
                "scene_file": manifest.scene_file,
                "video_path": manifest.video_path,
                "run_dir": str(run_dir),
                "artifacts": result.artifacts,
                "checks": result.checks,
                "notes": result.notes,
            }
        except Exception as exc:  # noqa: BLE001 - persist failure state
            manifest.status = "failed"
            manifest.error = str(exc)
            manifest.completed_utc = _now()
            self._write_manifest(run_dir, manifest)
            raise

    @staticmethod
    def _render(run_dir: Path, scene_name: str | None, quality: str) -> Path:
        """Wrapper-owned render via the manim CLI next to this interpreter (or on PATH)."""
        if not scene_name:
            raise RuntimeError("render requested but no scene class was found")
        manim = Path(sys.executable).with_name("manim")
        cmd = [
            str(manim) if manim.exists() else "manim",
            f"-q{quality}",
            str(run_dir / SCENE_FILE),
            scene_name,
            "--media_dir",
            str(run_dir / MEDIA_DIR),
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        (run_dir / RENDER_LOG_FILE).write_text(
            (completed.stdout or "") + (completed.stderr or ""), encoding="utf-8"
        )
        if completed.returncode != 0:
            raise RuntimeError(f"manim render failed ({completed.returncode}); see {RENDER_LOG_FILE}")
        video = find_video(run_dir / MEDIA_DIR)
        if video is None:
            raise RuntimeError(f"render finished but no mp4 found under {MEDIA_DIR}/")
        return video
