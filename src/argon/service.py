"""Run-ledger and job facade for the Argon Google ADK pipeline."""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from argon.harness import ArgonHarness, default_runs_dir
from argon.models import RunManifest, RunRequest

SCENE_CANDIDATES = ("argon_scene.py", "mythos_scene.py")


@dataclass
class Job:
    """One Argon animation request moving through the Google ADK chain."""

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


class ArgonService:
    def __init__(self, *, runs_dir: Path | None = None, harness: ArgonHarness | None = None):
        resolved = Path(runs_dir) if runs_dir else default_runs_dir()
        self.harness = harness or ArgonHarness(runs_dir=resolved)
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
        except Exception as exc:  # noqa: BLE001
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
            name=f"argon-job-{job.id}",
            daemon=True,
        )
        thread.start()
        return job

    def get_run(self, run_id: str) -> RunManifest:
        manifest_path = self._resolve_run_dir(run_id) / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(f"unknown Argon run: {run_id}")
        return RunManifest.model_validate(json.loads(manifest_path.read_text(encoding="utf-8")))

    def list_runs(self, *, limit: int = 20) -> list[RunManifest]:
        if not self.runs_dir.exists():
            return []
        manifests: list[RunManifest] = []
        for path in sorted(self.runs_dir.glob("*/manifest.json"), reverse=True):
            try:
                manifests.append(RunManifest.model_validate(json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if len(manifests) >= limit:
                break
        return manifests

    def _resolve_run_dir(self, run_id: str) -> Path:
        if Path(run_id).name != run_id:
            raise ValueError("run_id must be a single directory name")
        run_dir = (self.runs_dir / run_id).resolve()
        runs_root = self.runs_dir.resolve()
        if runs_root not in run_dir.parents:
            raise ValueError(f"Invalid run_id: {run_id!r}")
        if not run_dir.is_dir():
            raise FileNotFoundError(f"unknown Argon run: {run_id}")
        return run_dir
