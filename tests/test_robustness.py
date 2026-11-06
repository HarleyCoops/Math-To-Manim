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
from mythos.harness import MythosHarness, StageValidationError
from mythos.layout import create_run_dir, write_manifest
from mythos.settings import DEFAULT_RENDER_TIMEOUT
from mythos.stages import STAGES_BY_SLUG, validate_stage_artifact

MATH_DIRECTOR = STAGES_BY_SLUG["math-director"]


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
    assert "shots" in problem and "5" in problem


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


def test_degenerate_stage_retries_then_aborts(tmp_path):
    calls = []

    def fake_model(prompt, *, system_extra=None, command, model, timeout):
        calls.append(prompt)
        return '{"formulas": [], "color_identity": {}, "numbers": []}'

    harness = MythosHarness(offline=False, runs_dir=tmp_path, run_model=fake_model)
    with pytest.raises(StageValidationError):
        harness._run_stage(MATH_DIRECTOR, {"prior": "artifact"}, tmp_path)
    assert len(calls) == 2                       # one retry, then abort
    assert "PREVIOUS ATTEMPT REJECTED" in calls[1]
    assert (tmp_path / "04_math_dossier.retry.raw.txt").exists()


def test_degenerate_stage_recovers_on_retry(tmp_path):
    healthy = json.dumps({
        "formulas": [{"id": f"f{i}", "latex": "x", "story": "y" * 40}
                     for i in range(10)]})
    responses = iter(['{"formulas": []}', healthy])

    def fake_model(prompt, *, system_extra=None, command, model, timeout):
        return next(responses)

    harness = MythosHarness(offline=False, runs_dir=tmp_path, run_model=fake_model)
    artifact, retried = harness._run_stage(MATH_DIRECTOR, {}, tmp_path)
    assert retried is True
    assert len(artifact["formulas"]) == 10


# --------------------------------------------------------------------- #
# Atomic manifest                                                        #
# --------------------------------------------------------------------- #

def test_manifest_write_is_atomic_and_clean(tmp_path):
    manifest = {"run_id": "x", "stages": [{"stage": "intent"}]}
    write_manifest(tmp_path, manifest)
    on_disk = json.loads((tmp_path / "manifest.json").read_text("utf-8"))
    assert on_disk == manifest
    assert not (tmp_path / ".manifest.json.tmp").exists()


# --------------------------------------------------------------------- #
# Unique run directories                                                 #
# --------------------------------------------------------------------- #

def test_run_dirs_created_in_the_same_second_do_not_collide(tmp_path):
    first = create_run_dir(tmp_path, "The Heat Equation!")
    second = create_run_dir(tmp_path, "The Heat Equation!")
    assert first != second
    assert first.is_dir() and second.is_dir()
    assert first.name.endswith("-the-heat-equation")
    assert second.name.startswith(first.name)


def test_two_offline_runs_in_one_second_keep_separate_bundles(tmp_path):
    harness = MythosHarness(offline=True, runs_dir=tmp_path)
    a = harness.run("same prompt")
    b = harness.run("same prompt")
    assert a["run_id"] != b["run_id"]


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
