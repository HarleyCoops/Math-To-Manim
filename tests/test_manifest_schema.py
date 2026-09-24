"""WAR-1531 / WAR-1532: validation.json seed and schema_version migrations."""

from __future__ import annotations

import json

from mythos.harness import MythosHarness
from mythos.manifest_schema import (
    CURRENT_SCHEMA_VERSION,
    migrate_manifest,
    validation_template,
)
from sol.harness import SolHarness
from sol.manifest_schema import migrate_manifest as migrate_sol
from sol.models import RunRequest


def test_validation_template_shape():
    payload = validation_template()
    assert payload == {
        "latex": None,
        "manim_code": None,
        "complexity": None,
        "ran_at": None,
    }


def test_unversioned_manifest_migrates_to_current():
    migrated = migrate_manifest(
        {
            "run_id": "demo",
            "prompt": "heat",
            "scene_file": "mythos_scene.py",
        }
    )
    assert migrated["schema_version"] == CURRENT_SCHEMA_VERSION
    assert migrated["artifacts"]["validation"] == "validation.json"
    assert migrated["status"]["validation"] == "pending"


def test_v1_to_v2_round_trip():
    v1 = {
        "schema_version": 1,
        "run_id": "demo",
        "artifacts": {"scene": "mythos_scene.py"},
    }
    v2 = migrate_manifest(v1)
    assert v2["schema_version"] == 2
    assert v2["artifacts"]["validation"] == "validation.json"
    assert v2["artifacts"]["scene"] == "mythos_scene.py"
    again = migrate_manifest(v2)
    assert again["schema_version"] == 2
    assert again["artifacts"]["validation"] == "validation.json"


def test_sol_v1_to_v2_does_not_clobber_lifecycle_status():
    migrated = migrate_sol(
        {
            "schema_version": 1,
            "run_id": "demo",
            "status": "completed",
            "artifacts": {"scene": "sol_scene.py"},
        }
    )
    assert migrated["schema_version"] == 2
    assert migrated["status"] == "completed"
    assert migrated["status_detail"]["validation"] == "pending"


def test_mythos_offline_run_seeds_validation_and_schema(tmp_path):
    harness = MythosHarness(offline=True, runs_dir=tmp_path)
    manifest = harness.run("schema check")
    run_dir = tmp_path / manifest["run_id"]
    assert manifest["schema_version"] == CURRENT_SCHEMA_VERSION
    assert manifest["artifacts"]["validation"] == "validation.json"
    validation = json.loads((run_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["ran_at"]
    assert validation["manim_code"]["valid"] is True
    assert manifest["status"]["validation"] == "complete"


def test_sol_offline_run_seeds_validation_and_schema(tmp_path):
    manifest = SolHarness(runs_dir=tmp_path).run(
        RunRequest(prompt="schema check", offline=True)
    )
    run_dir = tmp_path / manifest["run_id"]
    assert manifest["schema_version"] == 2
    assert (run_dir / "validation.json").is_file()
    validation = json.loads((run_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["manim_code"]["valid"] is True
    assert manifest["status_detail"]["validation"] == "complete"
