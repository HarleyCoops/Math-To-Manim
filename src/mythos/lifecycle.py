"""Explicit lifecycles for Mythos jobs and runs.

Before this module, three state machines were implied by scattered fields:

- a job's ``status`` was a free string that any code could set to anything
- a run's status was inferred from whether ``completed_utc`` existed, so a
  run that crashed looked the same on disk as a run still in progress
- a run's result had to be assembled from ``static_check.passed``,
  ``status.render``, ``render_error`` and ``render_timed_out``

The values written to the wire and to ``manifest.json`` are unchanged. This
module names them, lists the legal job transitions, and gives one answer to
each of "where is this run?" and "how did it end?".

Manifest fields owned here (all under ``manifest["status"]``, all additive):

- ``run``: ``running`` | ``completed`` | ``failed``
- ``stage``: the step that is executing now (or that failed); absent when
  the run completed
- ``outcome``: see :class:`RunOutcome`; absent while the run is running

Manifests written before these fields existed are read through
:func:`run_status` and :func:`run_outcome`, which derive the answer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any


class IllegalTransition(RuntimeError):
    """A job was asked to move to a status its current status does not allow."""


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


JOB_TRANSITIONS: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.QUEUED: frozenset({JobStatus.RUNNING, JobStatus.FAILED}),
    JobStatus.RUNNING: frozenset({JobStatus.COMPLETED, JobStatus.FAILED}),
    JobStatus.COMPLETED: frozenset(),
    JobStatus.FAILED: frozenset(),
}

TERMINAL_JOB_STATUSES = frozenset(
    status.value for status, targets in JOB_TRANSITIONS.items() if not targets
)


def next_job_status(current: str, target: str) -> str:
    """Return ``target`` if a job in ``current`` may move to it, else raise."""
    try:
        source, destination = JobStatus(current), JobStatus(target)
    except ValueError as exc:
        raise IllegalTransition(f"unknown job status: {exc}") from exc
    if destination not in JOB_TRANSITIONS[source]:
        allowed = sorted(s.value for s in JOB_TRANSITIONS[source]) or ["none"]
        raise IllegalTransition(
            f"job cannot move from {source.value!r} to {destination.value!r} "
            f"(allowed: {', '.join(allowed)})"
        )
    return destination.value


class RunStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    #: A manifest from before ``status.run`` existed, with no
    #: ``completed_utc``. The run is in progress or it crashed; the manifest
    #: cannot tell which.
    UNKNOWN = "unknown"


class RunOutcome(str, Enum):
    """How a finished run ended. One value answers "is there a film?"."""

    FILM_READY = "film_ready"  # rendered; the video exists
    SCENE_READY = "scene_ready"  # scene code passed checks; render not requested
    VALIDATION_FAILED = "validation_failed"  # scene code failed static checks
    RENDER_FAILED = "render_failed"  # manim exited non-zero; repairs exhausted
    RENDER_TIMED_OUT = "render_timed_out"  # render exceeded its time budget
    RENDER_BLOCKED = "render_blocked"  # machine lacks manim/TeX/ffmpeg
    CHAIN_FAILED = "chain_failed"  # an exception stopped the chain


def _status(manifest: dict[str, Any] | None) -> dict[str, Any]:
    status = (manifest or {}).get("status")
    return status if isinstance(status, dict) else {}


def run_status(manifest: dict[str, Any] | None) -> str | None:
    """Status of a run, for manifests of any age. ``None`` if no manifest."""
    if not manifest:
        return None
    explicit = _status(manifest).get("run")
    if explicit in {s.value for s in RunStatus}:
        return explicit
    if manifest.get("completed_utc"):
        return RunStatus.COMPLETED.value
    return RunStatus.UNKNOWN.value


def run_stage(manifest: dict[str, Any] | None) -> str | None:
    """The step executing now, or the step that failed. ``None`` otherwise."""
    stage = _status(manifest).get("stage")
    return stage if isinstance(stage, str) else None


def run_outcome(manifest: dict[str, Any] | None) -> str | None:
    """How the run ended. ``None`` while it is running or status is unknown."""
    status = run_status(manifest)
    if status == RunStatus.FAILED.value:
        return RunOutcome.CHAIN_FAILED.value
    if status != RunStatus.COMPLETED.value:
        return None
    assert manifest is not None
    render = _status(manifest).get("render")
    if render == "complete":
        return RunOutcome.FILM_READY.value
    if manifest.get("render_error"):
        return RunOutcome.RENDER_BLOCKED.value
    if manifest.get("render_timed_out"):
        return RunOutcome.RENDER_TIMED_OUT.value
    if render == "failed":
        return RunOutcome.RENDER_FAILED.value
    static_check = manifest.get("static_check")
    if isinstance(static_check, dict) and static_check.get("passed") is False:
        return RunOutcome.VALIDATION_FAILED.value
    return RunOutcome.SCENE_READY.value


# ---------------------------------------------------------------------- #
# Writers: the only code that sets status.run / status.stage / status.outcome
# ---------------------------------------------------------------------- #

def _writable_status(manifest: dict[str, Any]) -> dict[str, Any]:
    status = manifest.get("status")
    if not isinstance(status, dict):
        status = {}
        manifest["status"] = status
    return status


def enter_stage(manifest: dict[str, Any], stage: str) -> None:
    """Record that the run is running and ``stage`` is the current step."""
    status = _writable_status(manifest)
    status["run"] = RunStatus.RUNNING.value
    status["stage"] = stage
    status.pop("outcome", None)


def mark_run_completed(manifest: dict[str, Any]) -> None:
    status = _writable_status(manifest)
    status["run"] = RunStatus.COMPLETED.value
    status.pop("stage", None)
    status["outcome"] = run_outcome(manifest)


def mark_run_failed(manifest: dict[str, Any], exc: BaseException) -> None:
    """Record a crash. ``status.stage`` is kept: it names the step that failed."""
    status = _writable_status(manifest)
    status["run"] = RunStatus.FAILED.value
    status["outcome"] = RunOutcome.CHAIN_FAILED.value
    manifest["error"] = f"{type(exc).__name__}: {exc}"[:2000]
    manifest["failed_utc"] = datetime.now(timezone.utc).isoformat()


def refresh_outcome(manifest: dict[str, Any]) -> None:
    """Recompute ``status.outcome`` after a later render of a finished run."""
    outcome = run_outcome(manifest)
    if outcome is not None:
        _writable_status(manifest)["outcome"] = outcome
