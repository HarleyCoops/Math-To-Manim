"""Every silo except Astra resolves its run ledger the same way, at call time."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

CHECKOUT = Path(__file__).resolve().parents[1]
LOCATIONS = {
    "argon": "argon.bundle",
    "glm": "glm.harness",
    "grok": "grok.harness",
    "mimo": "mimo.harness",
    "mythos": "mythos.settings",
    "sol": "sol.harness",
    "studio": "studio.settings",
}


@pytest.mark.parametrize("silo", sorted(LOCATIONS))
def test_env_var_names_the_parent_of_every_ledger(silo, tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path))
    module = importlib.import_module(LOCATIONS[silo])
    assert module.default_runs_dir() == tmp_path / silo


@pytest.mark.parametrize("silo", sorted(LOCATIONS))
def test_source_checkout_keeps_runs_in_the_checkout(silo, tmp_path, monkeypatch):
    monkeypatch.delenv("M2M_RUNS_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    module = importlib.import_module(LOCATIONS[silo])
    assert module.default_runs_dir() == CHECKOUT / "runs" / silo
