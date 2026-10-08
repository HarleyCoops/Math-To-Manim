"""Run-ledger and job facade for the Grok-native pipeline.

Owns background jobs for the MCP server and inspects ``runs/grok/``.
This module never imports Mythos or Sol.
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from grok.harness import GrokHarness, default_runs_dir
from grok.models import RunManifest, RunRequest

SCENE_CANDIDATES = ("grok_scene.py", "mythos_scene.py")


@dataclass
class Job:
    """One Grok animation request moving through the chain."""

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


class GrokService:
    def __init__(self, *, runs_dir: Path | None = None, harness: GrokHarness | None = None):
        resolved = Path(runs_dir) if runs_dir else default_runs_dir()
        self.harness = harness or GrokHarness(runs_dir=resolved)
        self.runs_dir = self.harness.runs_dir
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def run(self, request: RunRequest) -> dict:
        return self.harness.run(request)

    def resume(self, run_id: str, **overrides) -> dict:
        return self.harness.resume(run_id, **overrides)

    def render_existing(self, run_id: str, **kwargs) -> dict:
        return self.harness.render_existing(run_id, **kwargs)

    def _job_path(self, job_id: str) -> Path:
        return self.runs_dir / "jobs" / f"{job_id}.json"

    def _write_job(self, job: Job) -> None:
        path = self._job_path(job.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(job.to_dict(), indent=2), encoding="utf-8")
        temporary.replace(path)

    def _read_job(self, job_id: str) -> Job | None:
        if not job_id or Path(job_id).name != job_id:
            return None
        path = self._job_path(job_id)
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return Job(
            id=data.get("id", job_id),
            prompt=data.get("prompt", ""),
            status=data.get("status", "queued"),
            created_utc=data.get("created_utc", ""),
            options=data.get("options") or {},
            run_id=data.get("run_id"),
            manifest=data.get("manifest"),
            error=data.get("error"),
        )

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
        self._write_job(job)
        return job

    def _execute(self, job: Job, request: RunRequest) -> None:
        try:
            manifest = self.harness.run(request)
            with self._lock:
                job.manifest = manifest
                job.run_id = manifest.get("run_id")
                job.status = "completed"
        except Exception as exc:  # noqa: BLE001 — job boundary
            with self._lock:
                job.error = f"{type(exc).__name__}: {exc}"
                job.status = "failed"
        self._write_job(job)

    def _execute_saved(self, job: Job, action) -> None:
        try:
            manifest = action()
            with self._lock:
                job.manifest = manifest
                job.run_id = manifest.get("run_id") or job.run_id
                job.status = "completed"
        except Exception as exc:  # noqa: BLE001 — job boundary
            with self._lock:
                job.error = f"{type(exc).__name__}: {exc}"
                job.status = "failed"
        self._write_job(job)

    def run_sync(self, request: RunRequest) -> Job:
        job = self._new_job(request)
        job.status = "running"
        self._write_job(job)
        self._execute(job, request)
        return job

    def submit(self, request: RunRequest) -> Job:
        job = self._new_job(request)
        job.status = "running"
        self._write_job(job)
        thread = threading.Thread(
            target=self._execute,
            args=(job, request),
            name=f"grok-job-{job.id}",
            daemon=True,
        )
        thread.start()
        return job

    def submit_resume(self, run_id: str, **overrides) -> Job:
        request = RunRequest(prompt=f"resume {run_id}", offline=True)
        job = self._new_job(request)
        job.prompt = f"resume {run_id}"
        job.options = {"run_id": run_id, "command": "resume", **overrides}
        job.status = "running"
        job.run_id = run_id
        self._write_job(job)
        thread = threading.Thread(
            target=self._execute_saved,
            args=(job, lambda: self.harness.resume(run_id, **overrides)),
            name=f"grok-resume-{job.id}",
            daemon=True,
        )
        thread.start()
        return job

    def submit_render_existing(self, run_id: str, **kwargs) -> Job:
        request = RunRequest(prompt=f"render {run_id}", offline=True)
        job = self._new_job(request)
        job.prompt = f"render {run_id}"
        job.options = {"run_id": run_id, "command": "render-existing", **kwargs}
        job.status = "running"
        job.run_id = run_id
        self._write_job(job)
        thread = threading.Thread(
            target=self._execute_saved,
            args=(job, lambda: self.harness.render_existing(run_id, **kwargs)),
            name=f"grok-render-{job.id}",
            daemon=True,
        )
        thread.start()
        return job

    def get_job(self, job_id: str) -> Job | None:
        stored = self._read_job(job_id)
        with self._lock:
            job = stored or self._jobs.get(job_id)
            if job is None:
                return None
            self._jobs[job.id] = job
            if job.status == "running" and job.run_id:
                manifest_path = self.runs_dir / job.run_id / "manifest.json"
                try:
                    job.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    pass
            return job

    def get_run(self, run_id: str) -> RunManifest:
        manifest_path = self._resolve_run_dir(run_id) / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(f"unknown Grok run: {run_id}")
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

    def list_run_summaries(self, *, limit: int = 20) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        for manifest in self.list_runs(limit=limit):
            summaries.append(
                {
                    "run_id": manifest.run_id,
                    "prompt": manifest.prompt,
                    "model": manifest.model,
                    "offline": manifest.offline,
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
            raise FileNotFoundError(f"unknown Grok run: {run_id}")
        return run_dir
