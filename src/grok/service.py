"""Run-ledger and job facade for the Grok-native pipeline.

Owns background jobs for the MCP server and inspects the Grok runs dir.
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from grok.harness import GrokHarness
from grok.models import MANIFEST_FILE, SCENE_FILE, RunManifest, RunRequest


@dataclass
class Job:
    """One Grok animation request moving through the chain."""

    id: str
    prompt: str
    status: str = "running"
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
        self.harness = harness or GrokHarness(runs_dir=runs_dir)
        self.runs_dir = self.harness.runs_dir
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def run(self, request: RunRequest) -> dict:
        return self.harness.run(request)

    def submit(self, request: RunRequest) -> Job:
        """Start one run on a background thread and return its job record."""
        job = Job(
            id=uuid.uuid4().hex[:12],
            prompt=request.prompt.strip(),
            created_utc=datetime.now(timezone.utc).isoformat(),
            options=request.model_dump(),
        )
        with self._lock:
            self._jobs[job.id] = job
        thread = threading.Thread(
            target=self._execute,
            args=(job, request),
            name=f"grok-job-{job.id}",
            daemon=True,
        )
        thread.start()
        return job

    def _execute(self, job: Job, request: RunRequest) -> None:
        def started(run_id: str) -> None:
            with self._lock:
                job.run_id = run_id

        try:
            manifest = self.harness.run(request, on_start=started)
            with self._lock:
                job.manifest = manifest
                job.status = "completed"
        except Exception as exc:  # noqa: BLE001 — job boundary
            with self._lock:
                job.error = f"{type(exc).__name__}: {exc}"
                job.status = "failed"

    def get_job(self, job_id: str) -> Job | None:
        """The job record; until it completes, its manifest is the one on disk."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            if job.status != "completed" and job.run_id:
                manifest_path = self.runs_dir / job.run_id / MANIFEST_FILE
                try:
                    job.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    pass
            return job

    def get_run(self, run_id: str) -> RunManifest:
        manifest_path = self._resolve_run_dir(run_id) / MANIFEST_FILE
        if not manifest_path.is_file():
            raise FileNotFoundError(f"unknown Grok run: {run_id}")
        return RunManifest.model_validate(json.loads(manifest_path.read_text(encoding="utf-8")))

    def list_runs(self, *, limit: int = 20) -> list[RunManifest]:
        if not self.runs_dir.exists():
            return []
        manifests: list[RunManifest] = []
        for path in sorted(self.runs_dir.glob(f"*/{MANIFEST_FILE}"), reverse=True):
            try:
                manifests.append(RunManifest.model_validate(json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if len(manifests) >= limit:
                break
        return manifests

    def list_run_summaries(self, *, limit: int = 20) -> list[dict[str, Any]]:
        return [
            {
                "run_id": manifest.run_id,
                "prompt": manifest.prompt,
                "model": manifest.model,
                "offline": manifest.offline,
                "created_utc": manifest.created_utc,
                "completed": manifest.status == "completed",
                "scene_name": manifest.scene_name,
            }
            for manifest in self.list_runs(limit=limit)
        ]

    def inspect_run(self, run_id: str) -> dict[str, Any]:
        run_dir = self._resolve_run_dir(run_id)
        manifest_path = run_dir / MANIFEST_FILE
        manifest = (
            json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest_path.is_file()
            else {}
        )
        return {"run_id": run_id, "manifest": manifest, "artifacts": _files_in(run_dir)}

    def read_artifact(self, run_id: str, artifact_name: str) -> str:
        run_dir = self._resolve_run_dir(run_id)
        if Path(artifact_name).name != artifact_name:
            raise ValueError(f"Invalid artifact name: {artifact_name!r}")
        artifact_path = (run_dir / artifact_name).resolve()
        if run_dir not in artifact_path.parents:
            raise ValueError(f"Invalid artifact name: {artifact_name!r}")
        if not artifact_path.is_file():
            raise FileNotFoundError(
                f"No artifact {artifact_name!r} in run {run_id!r}. "
                f"Available: {', '.join(_files_in(run_dir))}"
            )
        return artifact_path.read_text(encoding="utf-8")

    def read_scene_code(self, run_id: str) -> str:
        return self.read_artifact(run_id, SCENE_FILE)

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


def _files_in(run_dir: Path) -> list[str]:
    return sorted(path.name for path in run_dir.iterdir() if path.is_file())
