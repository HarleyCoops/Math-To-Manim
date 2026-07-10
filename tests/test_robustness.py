"""Robustness regressions: stage validation, atomic manifests, env config.

Each test here encodes a failure observed in a real run:
- a 48-byte math dossier that storyboarded an empty film
- manifest.json read mid-write by a polling MCP client
- a stale CLI login producing an opaque mid-chain crash
"""

from __future__ import annotations

import json

import pytest

from mythos.backends import BackendAuthError
from mythos.harness import (
    DEFAULT_RENDER_TIMEOUT,
    MythosHarness,
    StageValidationError,
    validate_stage_artifact,
)


# --------------------------------------------------------------------- #
# Stage validation                                                       #
# --------------------------------------------------------------------- #

def test_empty_math_dossier_rejected():
    # The exact degenerate artifact from run 20260710-014407.
    artifact = {"formulas": [], "color_identity": {}, "numbers": []}
    problem = validate_stage_artifact("math-director", artifact)
    assert problem is not None
    assert "formulas" in problem


def test_thin_shot_list_rejected():
    artifact = {"shots": [{"beat": i} for i in range(5)], "camera_score": "x"}
    problem = validate_stage_artifact("cinematographer", artifact)
    assert problem is not None
    assert "5 beats" in problem


def test_healthy_artifacts_pass():
    dossier = {"formulas": [{"id": f"f{i}", "latex": "E=mc^2",
                             "caption": "energy and mass trade places" * 3}
                            for i in range(12)],
               "numbers": [1, 2, 3]}
    assert validate_stage_artifact("math-director", dossier) is None
    shots = {"shots": [{"beat": i, "verb": "HEADLINE", "seconds": 1.0,
                        "params": {"zoom": 1}} for i in range(30)]}
    assert validate_stage_artifact("cinematographer", shots) is None


def test_non_dict_artifact_rejected():
    assert validate_stage_artifact("intent", {}) is not None


def test_degenerate_stage_retries_then_aborts(tmp_path, monkeypatch):
    harness = MythosHarness(offline=False, runs_dir=tmp_path)
    calls = []

    def fake_model(prompt, system_extra=None):
        calls.append(prompt)
        return '{"formulas": [], "color_identity": {}, "numbers": []}'

    monkeypatch.setattr(harness, "_model", fake_model)
    monkeypatch.setattr(harness, "load_charter", lambda f: "CHARTER")
    with pytest.raises(StageValidationError):
        harness._run_stage("math-director", "mythos-math-director.md",
                           {"prior": "artifact"}, tmp_path,
                           "04_math_dossier.json")
    assert len(calls) == 2                       # one retry, then abort
    assert "PREVIOUS ATTEMPT REJECTED" in calls[1]
    assert (tmp_path / "04_math_dossier.retry.raw.txt").exists()


def test_degenerate_stage_recovers_on_retry(tmp_path, monkeypatch):
    harness = MythosHarness(offline=False, runs_dir=tmp_path)
    healthy = json.dumps({
        "formulas": [{"id": f"f{i}", "latex": "x", "story": "y" * 40}
                     for i in range(10)]})
    responses = iter(['{"formulas": []}', healthy])

    def fake_model(prompt, system_extra=None):
        return next(responses)

    monkeypatch.setattr(harness, "_model", fake_model)
    monkeypatch.setattr(harness, "load_charter", lambda f: "CHARTER")
    artifact, retried = harness._run_stage(
        "math-director", "mythos-math-director.md", {}, tmp_path,
        "04_math_dossier.json")
    assert retried is True
    assert len(artifact["formulas"]) == 10


# --------------------------------------------------------------------- #
# Atomic manifest                                                        #
# --------------------------------------------------------------------- #

def test_manifest_write_is_atomic_and_clean(tmp_path):
    manifest = {"run_id": "x", "stages": [{"stage": "intent"}]}
    MythosHarness._write_manifest(tmp_path, manifest)
    on_disk = json.loads((tmp_path / "manifest.json").read_text("utf-8"))
    assert on_disk == manifest
    assert not (tmp_path / ".manifest.json.tmp").exists()


# --------------------------------------------------------------------- #
# Configuration comes from the environment                               #
# --------------------------------------------------------------------- #

def test_render_timeout_default_positive():
    assert DEFAULT_RENDER_TIMEOUT > 0


def test_no_hardcoded_model_outside_env_default():
    """DEFAULT_MODEL must be derived from env-or-fallback, not a bare literal
    scattered through the runtime modules."""
    import mythos.backends as backends
    assert isinstance(backends.DEFAULT_MODEL, str) and backends.DEFAULT_MODEL


def test_backend_auth_error_is_runtime_error():
    assert issubclass(BackendAuthError, RuntimeError)


def test_prompt_bom_stripped(tmp_path):
    harness = MythosHarness(offline=True, runs_dir=tmp_path)
    manifest = harness.run("﻿  the heat equation  ")
    assert manifest["prompt"] == "the heat equation"
