"""Keep every test's run ledger inside its own temporary directory."""

import pytest


@pytest.fixture(autouse=True)
def _isolated_runs_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path / "runs"))
