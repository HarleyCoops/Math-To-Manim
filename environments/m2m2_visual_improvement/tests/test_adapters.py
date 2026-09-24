from __future__ import annotations

import builtins
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from m2m2_visual_improvement.adapters import (
    AdapterError,
    detect_provider,
    export_mythos_run,
    export_run,
    export_sol_run,
)
from m2m2_visual_improvement.adapters.common import normalize_relative_path


FIXTURES = (
    Path(__file__).parents[1]
    / "m2m2_visual_improvement"
    / "fixtures"
    / "provider_holdout"
)
COMMON = {
    "01_intent.json",
    "02_knowledge_map.json",
    "03_curriculum.json",
    "04_math_dossier.json",
    "05_shot_list.json",
    "06_scene_spec.json",
    "manifest.json",
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_detects_provider_from_required_scene_filename() -> None:
    assert detect_provider(FIXTURES / "mythos") == "mythos"
    assert detect_provider(FIXTURES / "sol") == "sol"


def test_mythos_adapter_normalizes_a_complete_bundle() -> None:
    run_dir = FIXTURES / "mythos"
    bundle = export_mythos_run(run_dir)

    assert bundle.provider == "mythos"
    assert bundle.contract.provider == "mythos"
    assert bundle.contract.audience == "grade 6 visual learner"
    assert bundle.scene_spec["scene_name"] == "StructureFirstJourney"
    assert "class StructureFirstJourney" in bundle.code
    assert set(bundle.source_artifact_hashes) == COMMON | {"mythos_scene.py"}
    assert bundle.source_artifact_hashes["06_scene_spec.json"] == file_sha256(
        run_dir / "06_scene_spec.json"
    )


def test_sol_adapter_normalizes_a_complete_bundle() -> None:
    run_dir = FIXTURES / "sol"
    bundle = export_sol_run(run_dir)

    assert bundle.provider == "sol"
    assert bundle.contract.provider == "sol"
    assert bundle.scene_spec["scene_name"] == "Erdos1038PotentialLandscape"
    assert bundle.review is not None
    assert bundle.review["status"] == "approved"
    assert set(bundle.source_artifact_hashes) == COMMON | {
        "sol_scene.py",
        "review.json",
    }


def test_dispatch_and_path_normalization_are_platform_independent() -> None:
    assert export_run(FIXTURES / "mythos").provider == "mythos"
    assert export_run(FIXTURES / "sol").provider == "sol"
    assert normalize_relative_path(r"nested\scene.py") == "nested/scene.py"


def test_missing_reasoning_stage_is_rejected(tmp_path: Path) -> None:
    run_dir = tmp_path / "missing-stage"
    shutil.copytree(FIXTURES / "mythos", run_dir)
    (run_dir / "03_curriculum.json").unlink()

    with pytest.raises(AdapterError, match="03_curriculum.json"):
        export_mythos_run(run_dir)


@pytest.mark.parametrize("provider", ["mythos", "sol"])
def test_failed_or_incomplete_manifest_is_rejected(
    tmp_path: Path,
    provider: str,
) -> None:
    run_dir = tmp_path / provider
    shutil.copytree(FIXTURES / provider, run_dir)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if provider == "mythos":
        manifest.pop("completed_utc")
    else:
        manifest["status"] = "failed"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(AdapterError, match="completed"):
        export_run(run_dir)


def test_manifest_cannot_escape_the_run_directory(tmp_path: Path) -> None:
    run_dir = tmp_path / "escape"
    shutil.copytree(FIXTURES / "mythos", run_dir)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["scene_file"] = "../outside.py"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "outside.py").write_text("pass\n", encoding="utf-8")

    with pytest.raises(AdapterError, match="inside the run directory"):
        export_mythos_run(run_dir)


def test_adapters_do_not_import_provider_orchestration() -> None:
    script = f"""
import builtins
from pathlib import Path

real_import = builtins.__import__
def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if level == 0 and name.split('.')[0] in {{'mythos', 'sol'}}:
        raise AssertionError('provider orchestration import: ' + name)
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = guarded_import
from m2m2_visual_improvement.adapters import export_run
assert export_run(Path({str(FIXTURES / "mythos")!r})).provider == 'mythos'
assert export_run(Path({str(FIXTURES / "sol")!r})).provider == 'sol'
"""
    outcome = subprocess.run(
        [sys.executable, "-c", script],
        text=True,
        capture_output=True,
        check=False,
    )
    assert outcome.returncode == 0, outcome.stderr


def test_import_guard_is_effective() -> None:
    real_import = builtins.__import__

    def guard(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: object = (),
        level: int = 0,
    ) -> object:
        if level == 0 and name == "mythos":
            raise AssertionError("blocked")
        return real_import(name, globals, locals, fromlist, level)

    with pytest.raises(AssertionError, match="blocked"):
        guard("mythos")
