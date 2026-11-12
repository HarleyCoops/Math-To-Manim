"""Complete Codex CLI-native Math-To-Manim run harness and run ledger."""

from __future__ import annotations

import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from sol.astra_reviewer import AstraReviewer
from sol.client import CodexCli
from sol.layout import MANIFEST_FILE, REQUEST_FILE, REVIEW_FILE, SCENE_FILE, VALIDATION_FILE
from sol.manifest_schema import migrate_manifest
from sol.models import RunManifest, RunRequest
from sol.offline import write_offline_bundle
from sol.rendering import RenderError, preflight_render, render_scene
from sol.staged import REVIEW_REPAIR_STAGE, StagedPipeline, write_offline_stage_records
from sol.validation import validate_run

Renderer = Callable[..., list[Path]]
Preflight = Callable[[], list[str]]


def default_runs_dir() -> Path:
    """``$M2M_RUNS_DIR/sol``; else ``runs/sol`` in the source checkout this
    package runs from; else ``./runs/sol`` (installed wheel). Resolved at call time."""
    if os.getenv("M2M_RUNS_DIR"):
        return Path(os.environ["M2M_RUNS_DIR"]) / "sol"
    checkout = Path(__file__).resolve().parents[2]
    base = checkout if (checkout / "pyproject.toml").is_file() else Path.cwd()
    return base / "runs" / "sol"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_dir_name(runs_dir: Path, prompt: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:48] or "film"
    candidate = runs_dir / f"{stamp}-{slug}"
    suffix = 1
    while candidate.exists():
        suffix += 1
        candidate = runs_dir / f"{stamp}-{slug}-{suffix}"
    return candidate


def _write_manifest(path: Path, manifest: RunManifest) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    temporary.replace(path)


def _read_manifest(path: Path) -> RunManifest:
    payload = migrate_manifest(json.loads(path.read_text(encoding="utf-8")))
    return RunManifest.model_validate(payload)


def _check_run_id(run_id: str) -> None:
    if Path(run_id).name != run_id:
        raise ValueError("run_id must be a single directory name")


class SolHarness:
    """Creates, executes, resumes, and lists Sol runs under ``runs_dir``.

    Collaborators are injectable so tests can stand in for Codex, Manim, and
    the independent reviewer without patching module attributes.
    """

    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: CodexCli | None = None,
        pipeline: StagedPipeline | None = None,
        astra_reviewer: AstraReviewer | None = None,
        render: Renderer = render_scene,
        preflight: Preflight = preflight_render,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.client = client or CodexCli()
        self.pipeline = pipeline or StagedPipeline(client=self.client)
        self.astra_reviewer = astra_reviewer or AstraReviewer.from_client(self.client)
        self.render = render
        self.preflight = preflight

    # -- ledger -------------------------------------------------------------

    def get_run(self, run_id: str) -> RunManifest:
        _check_run_id(run_id)
        manifest_path = self.runs_dir / run_id / MANIFEST_FILE
        if not manifest_path.is_file():
            raise FileNotFoundError(f"unknown Sol run: {run_id}")
        return _read_manifest(manifest_path)

    def list_runs(self, *, limit: int = 20) -> list[RunManifest]:
        if not self.runs_dir.exists():
            return []
        manifests: list[RunManifest] = []
        for path in sorted(self.runs_dir.glob(f"*/{MANIFEST_FILE}"), reverse=True):
            try:
                manifests.append(_read_manifest(path))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if len(manifests) >= limit:
                break
        return manifests

    # -- execution ----------------------------------------------------------

    def run(self, request: RunRequest) -> dict:
        run_dir = _run_dir_name(self.runs_dir, request.prompt)
        run_dir.mkdir(parents=True)
        manifest = RunManifest(
            run_id=run_dir.name,
            prompt=request.prompt,
            model=self.client.model,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            created_utc=_now(),
            execution_mode="staged",
            artifacts={"validation": VALIDATION_FILE, "scene": SCENE_FILE},
            status_detail={"validation": "pending"},
        )
        (run_dir / REQUEST_FILE).write_text(request.model_dump_json(indent=2), encoding="utf-8")
        return self._execute(run_dir, manifest, request, from_stage=None)

    def resume(self, run_id: str, *, from_stage: str | None = None) -> dict:
        _check_run_id(run_id)
        run_dir = self.runs_dir / run_id
        request_path = run_dir / REQUEST_FILE
        manifest_path = run_dir / MANIFEST_FILE
        if not request_path.is_file() or not manifest_path.is_file():
            raise FileNotFoundError(f"unknown Sol run: {run_id}")
        request = RunRequest.model_validate_json(request_path.read_text(encoding="utf-8"))
        manifest = _read_manifest(manifest_path)
        manifest.error = None
        manifest.completed_utc = None
        return self._execute(run_dir, manifest, request, from_stage=from_stage)

    def _execute(
        self, run_dir: Path, manifest: RunManifest, request: RunRequest, *, from_stage: str | None
    ) -> dict:
        manifest_path = run_dir / MANIFEST_FILE
        manifest.status = "running"
        manifest.status_detail["validation"] = "pending"
        _write_manifest(manifest_path, manifest)
        live_render = request.render and not request.offline
        try:
            if live_render:
                manifest.attempts.append(
                    {"mode": "render-preflight", "status": "completed", "checks": self.preflight()}
                )
            if request.offline:
                write_offline_bundle(run_dir, request)
                manifest.stage_records = write_offline_stage_records(
                    run_dir, request, self.client.model
                )
                manifest.attempts.append({"attempt": 0, "mode": "offline", "status": "completed"})
            else:
                manifest.stage_records = self.pipeline.run(run_dir, request, from_stage=from_stage)
                manifest.attempts.append(
                    {"attempt": 0, "mode": "codex-cli-staged", "status": "completed"}
                )
            scene_name, video_path = self._validate_and_review(run_dir, request, manifest)
            manifest.status = "completed"
            manifest.scene_file = SCENE_FILE
            manifest.scene_name = scene_name
            manifest.video_path = video_path
            manifest.status_detail["validation"] = "complete"
        except Exception as exc:
            manifest.status = "failed"
            manifest.error = f"{type(exc).__name__}: {exc}"
            manifest.completed_utc = _now()
            _write_manifest(manifest_path, manifest)
            raise
        manifest.completed_utc = _now()
        _write_manifest(manifest_path, manifest)
        return manifest.model_dump()

    def _repair(
        self, run_dir: Path, request: RunRequest, manifest: RunManifest, *,
        stage: str, feedback: str, attempt: dict,
    ) -> str:
        """Re-run ``stage`` and everything downstream, then re-validate statically.

        The repaired stage and the scene composer both receive the evidence;
        the composer always rewrites the source that will be validated next.
        Returns the scene class name.
        """
        self.pipeline.run(
            run_dir, request, from_stage=stage,
            feedback={stage: feedback, REVIEW_REPAIR_STAGE: feedback},
        )
        manifest.attempts.append(attempt)
        failures, scene_name, _ = validate_run(run_dir, require_video=False)
        if failures or not scene_name:
            raise RuntimeError(f"{attempt['mode']} failed: " + "; ".join(failures))
        return scene_name

    def _reviewer(self, request: RunRequest):
        return self.astra_reviewer if request.evaluator == "astra_review" else self.pipeline

    def _validate_and_review(
        self, run_dir: Path, request: RunRequest, manifest: RunManifest
    ) -> tuple[str | None, str | None]:
        live_render = request.render and not request.offline
        # Any earlier verdict belongs to an earlier execution; this one renders
        # and reviews again (or never does, and the placeholder says so).
        (run_dir / REVIEW_FILE).write_text(json.dumps({
            "status": "awaiting_render" if live_render else "not_rendered",
            "evaluator": request.evaluator,
            "defects": [], "observations": [], "evidence": [],
            "rendered": False,
        }, indent=2), encoding="utf-8")

        failures, scene_name, video_path = validate_run(run_dir, require_video=False)
        repair = 0
        while failures and not request.offline and repair < request.max_repairs:
            repair += 1
            self.pipeline.run(
                run_dir, request, from_stage=REVIEW_REPAIR_STAGE,
                feedback={REVIEW_REPAIR_STAGE: "\n".join(f"- {failure}" for failure in failures)},
            )
            manifest.attempts.append({
                "attempt": repair, "mode": f"{REVIEW_REPAIR_STAGE}-static-repair",
                "status": "completed", "input_failures": failures,
            })
            failures, scene_name, video_path = validate_run(run_dir, require_video=False)
        if failures:
            raise RuntimeError("run bundle validation failed: " + "; ".join(failures))
        if not live_render:
            return scene_name, video_path

        if not scene_name:
            raise RuntimeError("render requested but no scene class was found")
        repairs = 0
        while True:
            try:
                evidence_paths = self.render(run_dir, scene_name=scene_name, quality=request.quality)
            except RenderError as exc:
                if repairs >= request.max_repairs:
                    raise
                repairs += 1
                scene_name = self._repair(
                    run_dir, request, manifest, stage=REVIEW_REPAIR_STAGE, feedback=str(exc),
                    attempt={"attempt": repairs, "mode": f"{REVIEW_REPAIR_STAGE}-render-repair",
                             "status": "completed", "input_failure": str(exc)},
                )
                continue
            review = self._reviewer(request).review_render(
                run_dir, request, evidence_paths=evidence_paths
            )
            if review["status"] == "approved":
                manifest.attempts.append({
                    "mode": f"wrapper-render-and-{request.evaluator}-review",
                    "status": "completed",
                    "evidence": [str(path.relative_to(run_dir)) for path in evidence_paths],
                })
                break
            if repairs >= request.max_repairs:
                raise RuntimeError(
                    "visual review still requires repair: " + json.dumps(review["defects"])
                )
            repairs += 1
            stage = review["repair_stage"]
            scene_name = self._repair(
                run_dir, request, manifest, stage=stage,
                feedback=json.dumps(review, ensure_ascii=False),
                attempt={"attempt": repairs, "mode": f"{stage}-review-repair", "review": review},
            )
        failures, scene_name, video_path = validate_run(run_dir, require_video=True)
        if failures:
            raise RuntimeError("rendered run bundle validation failed: " + "; ".join(failures))
        return scene_name, video_path
