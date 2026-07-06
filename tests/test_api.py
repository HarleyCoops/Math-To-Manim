"""REST API surface, exercised offline through the FastAPI test client."""

import time

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from mythos.api import create_app  # noqa: E402
from mythos.service import MythosService  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    service = MythosService(runs_dir=tmp_path / "runs")
    app = create_app(service)
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"].startswith("1.1")


def _wait_for_job(client, job_id, timeout=15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"completed", "failed"}:
            return job
        time.sleep(0.1)
    raise AssertionError("job did not finish in time")


def test_create_run_offline_end_to_end(client):
    response = client.post("/v1/runs", json={
        "prompt": "explain the pythagorean theorem", "offline": True})
    assert response.status_code == 202
    job = _wait_for_job(client, response.json()["id"])
    assert job["status"] == "completed"

    run_id = job["run_id"]
    detail = client.get(f"/v1/runs/{run_id}").json()
    assert "mythos_scene.py" in detail["artifacts"]

    code = client.get(f"/v1/runs/{run_id}/artifacts/mythos_scene.py")
    assert code.status_code == 200
    assert "ThreeDScene" in code.text

    listing = client.get("/v1/runs").json()
    assert listing[0]["run_id"] == run_id


def test_validation_rejects_short_prompt(client):
    response = client.post("/v1/runs", json={"prompt": "x"})
    assert response.status_code == 422


def test_unknown_job_and_run_404(client):
    assert client.get("/v1/jobs/nope").status_code == 404
    assert client.get("/v1/runs/nope").status_code == 404
    assert client.get("/v1/runs/nope/artifacts/manifest.json").status_code == 404
