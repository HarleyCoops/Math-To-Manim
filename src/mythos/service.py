"""MythosService: one core, three front doors (CLI, REST API, MCP).

The service owns job orchestration around :class:`mythos.harness.MythosHarness`:

- submit a prompt as a background job (thread) or run it synchronously
- inspect job status and the on-disk run ledger (``runs/mythos/``)
- read run artifacts safely (no path traversal)

The API server (:mod:`mythos.api`) is a thin wrapper over this class.
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mythos.harness import MythosHarness
from mythos.layout import MANIFEST_FILE, iter_run_dirs, read_manifest
from mythos.lifecycle import (
    JobStatus,
    next_job_status,
    run_outcome,
    run_stage,
    run_status,
)
from mythos.settings import (
    DEFAULT_COMMAND,
    DEFAULT_MODEL,
    DEFAULT_RENDER_TIMEOUT,
    DEFAULT_TIMEOUT,
    default_runs_dir,
)

HarnessFactory = Callable[..., MythosHarness]


@dataclass
class Job:
    """One animation request moving through the chain.

    ``status`` is a :class:`mythos.lifecycle.JobStatus` value. Change it only
    through :meth:`MythosService._advance`, which enforces the legal
    transitions. ``stage`` and ``outcome`` in :meth:`to_dict` come from the
    run manifest: the step running now, and how a finished run ended.
    """

    id: str
    prompt: str
    status: str = JobStatus.QUEUED.value
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
            "stage": run_stage(self.manifest),
            "outcome": run_outcome(self.manifest),
            "created_utc": self.created_utc,
            "options": self.options,
            "run_id": self.run_id,
            "manifest": self.manifest,
            "error": self.error,
        }


class MythosService:
    """Job orchestration and run inspection around the Mythos harness."""

    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        harness_factory: HarnessFactory | None = None,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self._harness_factory = harness_factory or MythosHarness
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Job lifecycle                                                       #
    # ------------------------------------------------------------------ #

    def _build_harness(self, options: dict[str, Any]) -> MythosHarness:
        return self._harness_factory(
            command=options.get("command", DEFAULT_COMMAND),
            model=options.get("model", DEFAULT_MODEL),
            timeout=float(options.get("timeout", DEFAULT_TIMEOUT)),
            render_timeout=float(options.get("render_timeout", DEFAULT_RENDER_TIMEOUT)),
            offline=bool(options.get("offline", False)),
            runs_dir=self.runs_dir,
        )

    def _advance(self, job: Job, target: JobStatus) -> None:
        """Move ``job`` to ``target``. Caller must hold ``self._lock``."""
        job.status = next_job_status(job.status, target.value)

    def _refresh_manifest(self, job: Job) -> None:
        """Load the on-disk manifest into ``job``. Caller must hold the lock."""
        try:
            job.manifest = read_manifest(self.runs_dir / job.run_id)
        except (OSError, ValueError):
            pass

    def _execute(self, job: Job) -> None:
        def _record_run_dir(run_id: str) -> None:
            with self._lock:
                job.run_id = run_id

        try:
            harness = self._build_harness(job.options)
            manifest = harness.run(
                job.prompt,
                render=bool(job.options.get("render", False)),
                quality=str(job.options.get("quality", "l")),
                max_repairs=int(job.options.get("max_repairs", 3)),
                run_dir_callback=_record_run_dir,
            )
            with self._lock:
                job.manifest = manifest
                job.run_id = manifest.get("run_id")
                render_error = manifest.get("render_error")
                if render_error:
                    job.error = render_error["detail"]
                    self._advance(job, JobStatus.FAILED)
                else:
                    self._advance(job, JobStatus.COMPLETED)
        except Exception as exc:  # noqa: BLE001 — job boundary
            with self._lock:
                job.error = f"{type(exc).__name__}: {exc}"
                if job.run_id:
                    # The harness recorded the crash; keep the step it failed at.
                    self._refresh_manifest(job)
                self._advance(job, JobStatus.FAILED)

    def _new_job(self, prompt: str, **options: Any) -> Job:
        if not prompt or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")
        job = Job(
            id=uuid.uuid4().hex[:12],
            prompt=prompt.strip(),
            created_utc=datetime.now(timezone.utc).isoformat(),
            options=options,
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    def run_sync(self, prompt: str, **options: Any) -> Job:
        """Run the full chain in the calling thread and return the finished job."""
        job = self._new_job(prompt, **options)
        with self._lock:
            self._advance(job, JobStatus.RUNNING)
        self._execute(job)
        return job

    def submit(self, prompt: str, **options: Any) -> Job:
        """Start the chain in a background thread and return immediately."""
        job = self._new_job(prompt, **options)
        with self._lock:
            self._advance(job, JobStatus.RUNNING)
        thread = threading.Thread(
            target=self._execute, args=(job,),
            name=f"mythos-job-{job.id}", daemon=True,
        )
        thread.start()
        return job

    def get_job(self, job_id: str) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            if job.status == JobStatus.RUNNING.value and job.run_id:
                # Live progress: surface the on-disk manifest (written
                # atomically after every stage) instead of waiting for the
                # chain to finish.
                self._refresh_manifest(job)
            return job

    def list_jobs(self) -> list[Job]:
        with self._lock:
            return sorted(self._jobs.values(),
                          key=lambda j: j.created_utc, reverse=True)

    # ------------------------------------------------------------------ #
    # Run ledger (on disk)                                                #
    # ------------------------------------------------------------------ #

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        """Newest-first summaries of on-disk runs under ``runs/mythos``."""
        summaries: list[dict[str, Any]] = []
        for run_dir in iter_run_dirs(self.runs_dir):
            summary: dict[str, Any] = {"run_id": run_dir.name}
            if (run_dir / MANIFEST_FILE).exists():
                try:
                    manifest = read_manifest(run_dir)
                    summary.update({
                        "prompt": manifest.get("prompt"),
                        "model": manifest.get("model"),
                        "offline": manifest.get("offline"),
                        "created_utc": manifest.get("created_utc"),
                        "completed": "completed_utc" in manifest,
                        "status": run_status(manifest),
                        "outcome": run_outcome(manifest),
                        "scene_name": manifest.get("scene_name"),
                    })
                except (json.JSONDecodeError, OSError):
                    summary["prompt"] = None
            summaries.append(summary)
            if len(summaries) >= limit:
                break
        return summaries

    def _resolve_run_dir(self, run_id: str) -> Path:
        run_dir = (self.runs_dir / run_id).resolve()
        runs_root = self.runs_dir.resolve()
        if runs_root not in run_dir.parents:
            raise ValueError(f"Invalid run_id: {run_id!r}")
        if not run_dir.is_dir():
            raise FileNotFoundError(f"No run named {run_id!r} under {runs_root}")
        return run_dir

    def get_run(self, run_id: str) -> dict[str, Any]:
        """Full manifest plus artifact listing for one run."""
        run_dir = self._resolve_run_dir(run_id)
        manifest = read_manifest(run_dir) if (run_dir / MANIFEST_FILE).exists() else {}
        artifacts = sorted(p.name for p in run_dir.iterdir() if p.is_file())
        return {"run_id": run_id, "manifest": manifest, "artifacts": artifacts}

    def read_artifact(self, run_id: str, artifact_name: str) -> str:
        """Return one artifact's text content (path-traversal safe)."""
        run_dir = self._resolve_run_dir(run_id)
        artifact_path = (run_dir / artifact_name).resolve()
        if run_dir not in artifact_path.parents:
            raise ValueError(f"Invalid artifact name: {artifact_name!r}")
        if not artifact_path.is_file():
            available = sorted(p.name for p in run_dir.iterdir() if p.is_file())
            raise FileNotFoundError(
                f"No artifact {artifact_name!r} in run {run_id!r}. "
                f"Available: {', '.join(available)}"
            )
        return artifact_path.read_text(encoding="utf-8")
