import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from sol.api import create_app  # noqa: E402
from sol.service import SolService  # noqa: E402


def test_sol_api_offline(tmp_path):
    client = TestClient(create_app(SolService(runs_dir=tmp_path)))
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["silo"] == "sol"

    response = client.post("/v1/calculate", json={
        "problem": "solve 3x + 11 = 14",
        "offline": True,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["engine"] == "local-symbolic"
    assert body["result"]["answer"] == "x = 1"
    assert "class SolCalculationScene" in body["manim_source"]
