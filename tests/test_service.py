"""MythosService: jobs, run ledger, artifact access."""

import time

import pytest

from mythos.service import MythosService


@pytest.fixture()
def service(tmp_path):
    return MythosService(runs_dir=tmp_path / "runs")


def test_run_sync_offline_completes(service):
    job = service.run_sync("the heat equation", offline=True)
    assert job.status == "completed"
    assert job.run_id
    assert job.manifest["scene_name"] == "MythosOfflineScene"


def test_submit_background_job_completes(service):
    job = service.submit("fourier series", offline=True)
    for _ in range(100):
        if service.get_job(job.id).status in {"completed", "failed"}:
            break
        time.sleep(0.1)
    assert service.get_job(job.id).status == "completed"


def test_empty_prompt_rejected(service):
    with pytest.raises(ValueError):
        service.run_sync("   ", offline=True)


def test_list_runs_and_get_run(service):
    job = service.run_sync("l'hopital's rule", offline=True)
    runs = service.list_runs()
    assert runs and runs[0]["run_id"] == job.run_id
    detail = service.get_run(job.run_id)
    assert "mythos_scene.py" in detail["artifacts"]
    assert detail["manifest"]["prompt"] == "l'hopital's rule"


def test_read_artifact(service):
    job = service.run_sync("euler's identity", offline=True)
    code = service.read_artifact(job.run_id, "mythos_scene.py")
    assert "class MythosOfflineScene" in code


def test_read_artifact_traversal_blocked(service):
    job = service.run_sync("security", offline=True)
    with pytest.raises((ValueError, FileNotFoundError)):
        service.read_artifact(job.run_id, "../../pyproject.toml")
    with pytest.raises((ValueError, FileNotFoundError)):
        service.read_artifact("..", "manifest.json")


def test_missing_run_raises(service):
    with pytest.raises(FileNotFoundError):
        service.get_run("does-not-exist")
