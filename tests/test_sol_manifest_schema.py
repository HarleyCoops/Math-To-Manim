"""WAR-1531 / WAR-1532: Sol validation.json seed and schema_version migrations."""

from __future__ import annotations

import json

from sol.harness import SolHarness
from sol.manifest_schema import migrate_manifest as migrate_sol
from sol.models import RunRequest


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
