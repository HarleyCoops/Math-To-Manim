"""Run-ledger and job facade for the GLM-native pipeline.

Owns background jobs for future front doors and inspects ``runs/glm/``.
This module never imports Mythos, Sol, or Grok.
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from glm.harness import GlmHarness, default_runs_dir
from glm.models import RunManifest, RunRequest

SCENE_CANDIDATES = ("glm_scene.py",)


@dataclass
class Job:
    """One GLM animation request moving through the chain."""

    id: str
    prompt: str
    status: str = "queued"
    created_utc: str = ""
    options: dict[str, Any] = field(default_factory=dict)
    run_id: str | None = None
    manifest: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "status": self.status,
            "created_utc": self.created_utc,
            "options": self.options,
            "run_id": self.run_id,
            "manifest": self.manifest,
            "error": self.error,
        }


class GlmService:
    def __init__(self, *, runs_dir: Path | None = None, harness: GlmHarness | None = None):
        resolved = Path(runs_dir) if runs_dir else default_runs_dir()
        self.harness = harness or GlmHarness(runs_dir=resolved)
        self.runs_dir = self.harness.runs_dir
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def run(self, request: RunRequest) -> dict:
        return self.harness.run(request)

    def _new_job(self, request: RunRequest) -> Job:
        if not request.prompt or not request.prompt.strip():
            raise ValueError("prompt must be a non-empty string")
        job = Job(
            id=uuid.uuid4().hex[:12],
            prompt=request.prompt.strip(),
            created_utc=datetime.now(timezone.utc).isoformat(),
            options=request.model_dump(),
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    def _execute(self, job: Job, request: RunRequest) -> None:
        try:
            manifest = self.harness.run(request)
            with self._lock:
                job.manifest = manifest
                job.run_id = manifest.get("run_id")
                job.status = "completed"
        except Exception as exc:  # noqa: BLE001 - job boundary
            with self._lock:
                job.error = f"{type(exc).__name__}: {exc}"
                job.status = "failed"

    def run_sync(self, request: RunRequest) -> Job:
        job = self._new_job(request)
        job.status = "running"
        self._execute(job, request)
        return job

    def submit(self, request: RunRequest) -> Job:
        job = self._new_job(request)
        job.status = "running"
        thread = threading.Thread(
            target=self._execute,
            args=(job, request),
            name=f"glm-job-{job.id}",
            daemon=True,
        )
        thread.start()
        return job

    def get_job(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                return Job(**job.to_dict()) if False else job
        return None

    def get_run(self, run_id: str) -> RunManifest:
        manifest_path = self._resolve_run_dir(run_id) / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(f"unknown GLM run: {run_id}")
        return RunManifest.model_validate(
            json.loads(manifest_path.read_text(encoding="utf-8"))
        )

    def list_runs(self, *, limit: int = 20) -> list[RunManifest]:
        if not self.runs_dir.exists():
            return []
        manifests: list[RunManifest] = []
        for path in sorted(self.runs_dir.glob("*/manifest.json"), reverse=True):
            try:
                manifests.append(
                    RunManifest.model_validate(
                        json.loads(path.read_text(encoding="utf-8"))
                    )
                )
            except (OSError, ValueError):
                continue
            if len(manifests) >= limit:
                break
        return manifests

    def list_run_summaries(self, *, limit: int = 20) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        for manifest in self.list_runs(limit=limit):
            summaries.append(
                {
                    "run_id": manifest.run_id,
                    "prompt": manifest.prompt,
                    "model": manifest.model,
                    "offline": manifest.offline,
                    "key_source": manifest.key_source,
                    "created_utc": manifest.created_utc,
                    "completed": manifest.status == "completed",
                    "scene_name": manifest.scene_name,
                }
            )
        return summaries

    def inspect_run(self, run_id: str) -> dict[str, Any]:
        run_dir = self._resolve_run_dir(run_id)
        manifest_path = run_dir / "manifest.json"
        manifest = (
            json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest_path.is_file()
            else {}
        )
        artifacts = sorted(path.name for path in run_dir.iterdir() if path.is_file())
        return {"run_id": run_id, "manifest": manifest, "artifacts": artifacts}

    def read_artifact(self, run_id: str, artifact_name: str) -> str:
        run_dir = self._resolve_run_dir(run_id)
        if Path(artifact_name).name != artifact_name:
            raise ValueError(f"Invalid artifact name: {artifact_name!r}")
        artifact_path = (run_dir / artifact_name).resolve()
        if run_dir not in artifact_path.parents:
            raise ValueError(f"Invalid artifact name: {artifact_name!r}")
        if not artifact_path.is_file():
            available = sorted(path.name for path in run_dir.iterdir() if path.is_file())
            raise FileNotFoundError(
                f"No artifact {artifact_name!r} in run {run_id!r}. "
                f"Available: {', '.join(available)}"
            )
        return artifact_path.read_text(encoding="utf-8")

    def read_scene_code(self, run_id: str) -> str:
        last_error: Exception | None = None
        for name in SCENE_CANDIDATES:
            try:
                return self.read_artifact(run_id, name)
            except FileNotFoundError as exc:
                last_error = exc
        assert last_error is not None
        raise last_error

    def _resolve_run_dir(self, run_id: str) -> Path:
        if Path(run_id).name != run_id:
            raise ValueError("run_id must be a single directory name")
        run_dir = (self.runs_dir / run_id).resolve()
        runs_root = self.runs_dir.resolve()
        if runs_root not in run_dir.parents:
            raise ValueError(f"Invalid run_id: {run_id!r}")
        if not run_dir.is_dir():
            raise FileNotFoundError(f"unknown GLM run: {run_id}")
        return run_dir
