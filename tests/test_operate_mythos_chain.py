"""scripts/operate_mythos_chain.py drives the Mythos chain with an operator."""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILM = ROOT / "docs" / "showcase" / "every-orbit-great-circle"
SCENE = ROOT / "examples" / "mythos" / "every_orbit_great_circle.py"


def _load():
    spec = importlib.util.spec_from_file_location("operate_mythos_chain",
                                                  ROOT / "scripts" / "operate_mythos_chain.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _stages(tmp_path: Path, upto: int = 6, scene: bool = True) -> Path:
    stages = tmp_path / "stages"
    stages.mkdir()
    shutil.copy(FILM / "prompt.txt", stages / "prompt.txt")
    for path in sorted(FILM.glob("0[1-6]_*.json"))[:upto]:
        shutil.copy(path, stages / path.name)
    if scene:
        shutil.copy(SCENE, stages / "mythos_scene.py")
    return stages


def test_replays_the_committed_film(tmp_path):
    op = _load()
    rc, run_dir = op.operate(_stages(tmp_path), runs_dir=tmp_path / "runs")
    assert rc == 0
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert [s["stage"] for s in manifest["stages"]] == [
        "intent", "cartographer", "curriculum", "math-director",
        "cinematographer", "scene-composer", "codegen"]
    assert manifest["command"] == "operator"
    assert manifest["static_check"]["passed"] is True
    assert manifest["schema_version"] == 2
    cartographer_prompt = (run_dir / "02_knowledge_map.prompt.txt").read_text(encoding="utf-8")
    assert "Cartographer of the Mythos chain" in cartographer_prompt
    assert "the_big_zoom" in cartographer_prompt  # the intent reply is its input
    # The recorded replies are the committed stage artifacts, unchanged.
    for path in FILM.glob("0[1-6]_*.json"):
        assert json.loads((run_dir / path.name).read_text(encoding="utf-8")) == \
            json.loads(path.read_text(encoding="utf-8"))


def test_stops_at_the_first_missing_reply(tmp_path):
    op = _load()
    stages = _stages(tmp_path, upto=2, scene=False)
    rc, run_dir = op.operate(stages, runs_dir=tmp_path / "runs")
    assert rc == op.NEEDS_REPLY and run_dir is None
    ask = (stages / "NEXT_PROMPT.txt").read_text(encoding="utf-8")
    assert "Curriculum agent of the Mythos chain" in ask
    assert "MYTHOS CINEMATIC CHARTER" in ask
    assert not (tmp_path / "runs").exists()


def test_asks_for_codegen_after_the_six_stages(tmp_path):
    op = _load()
    stages = _stages(tmp_path, scene=False)
    rc, _ = op.operate(stages, runs_dir=tmp_path / "runs")
    assert rc == op.NEEDS_REPLY
    assert "write the film" in (stages / "NEXT_PROMPT.txt").read_text(encoding="utf-8")
