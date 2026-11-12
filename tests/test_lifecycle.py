"""Explicit job and run lifecycles (mythos.lifecycle)."""

import json

import pytest

from mythos.harness import STAGES, MythosHarness
from mythos.lifecycle import (
    IllegalTransition,
    JobStatus,
    TERMINAL_JOB_STATUSES,
    next_job_status,
    run_outcome,
    run_stage,
    run_status,
)
from mythos.service import MythosService


def test_job_transitions_allow_only_the_documented_moves():
    assert next_job_status("queued", "running") == "running"
    assert next_job_status("running", "completed") == "completed"
    assert next_job_status("running", "failed") == "failed"
    assert TERMINAL_JOB_STATUSES == {"completed", "failed"}
    for current, target in [("completed", "running"), ("failed", "completed"),
                            ("queued", "completed"), ("running", "queued")]:
        with pytest.raises(IllegalTransition):
            next_job_status(current, target)
    with pytest.raises(IllegalTransition):
        next_job_status("running", "paused")


def test_completed_run_records_status_and_outcome(tmp_path):
    manifest = MythosHarness(offline=True, runs_dir=tmp_path).run("lifecycle")
    on_disk = json.loads(
        (tmp_path / manifest["run_id"] / "manifest.json").read_text(encoding="utf-8"))
    assert on_disk["status"]["run"] == "completed"
    assert on_disk["status"]["outcome"] == "scene_ready"
    assert "stage" not in on_disk["status"]
    assert run_status(on_disk) == "completed"
    assert run_stage(on_disk) is None


def test_crashed_run_is_recorded_as_failed_with_the_failing_stage(tmp_path, monkeypatch):
    harness = MythosHarness(offline=True, runs_dir=tmp_path)

    def boom(*args, **kwargs):
        raise RuntimeError("codegen exploded")

    monkeypatch.setattr(harness, "_codegen", boom)
    with pytest.raises(RuntimeError, match="codegen exploded"):
        harness.run("crash me")

    (run_dir,) = [p for p in tmp_path.iterdir() if p.is_dir()]
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"]["run"] == "failed"
    assert manifest["status"]["stage"] == "codegen"
    assert manifest["status"]["outcome"] == "chain_failed"
    assert "codegen exploded" in manifest["error"]
    assert "completed_utc" not in manifest
    assert len(manifest["stages"]) == len(STAGES)


def test_failed_job_reports_stage_and_outcome(tmp_path, monkeypatch):
    harness = MythosHarness(offline=True, runs_dir=tmp_path / "runs")
    monkeypatch.setattr(
        harness, "_codegen",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no scene")))
    service = MythosService(runs_dir=harness.runs_dir,
                            harness_factory=lambda **kwargs: harness)
    job = service.run_sync("job crash").to_dict()
    assert job["status"] == JobStatus.FAILED.value
    assert job["stage"] == "codegen"
    assert job["outcome"] == "chain_failed"
    assert service.list_runs()[0]["status"] == "failed"


def test_completed_job_and_run_summary_carry_outcome(tmp_path):
    service = MythosService(runs_dir=tmp_path / "runs")
    job = service.run_sync("outcome", offline=True).to_dict()
    assert job["status"] == "completed"
    assert job["stage"] is None
    assert job["outcome"] == "scene_ready"
    summary = service.list_runs()[0]
    assert summary["completed"] is True
    assert summary["status"] == "completed"
    assert summary["outcome"] == "scene_ready"


def test_old_manifests_are_read_without_the_new_fields():
    finished = {"run_id": "a", "completed_utc": "2026-01-01T00:00:00+00:00",
                "static_check": {"passed": True}}
    assert run_status(finished) == "completed"
    assert run_outcome(finished) == "scene_ready"
    unfinished = {"run_id": "b", "stages": []}
    assert run_status(unfinished) == "unknown"
    assert run_outcome(unfinished) is None
    assert run_status(None) is None


@pytest.mark.parametrize("extra, expected", [
    ({"status": {"render": "complete"}, "render_timed_out": True}, "film_ready"),
    ({"status": {"render": "failed"},
      "render_error": {"type": "environment", "detail": "no ffmpeg"}}, "render_blocked"),
    ({"status": {"render": "failed"}, "render_timed_out": True}, "render_timed_out"),
    ({"status": {"render": "failed"}}, "render_failed"),
    ({"static_check": {"passed": False}}, "validation_failed"),
])
def test_run_outcome_names_each_ending(extra, expected):
    manifest = {"run_id": "x", "completed_utc": "2026-01-01T00:00:00+00:00", **extra}
    assert run_outcome(manifest) == expected
