"""Companion deliverables: the LaTeX paper and the Lean file of a Mythos run."""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from mythos import companions
from mythos.charter import CINEMATIC_CHARTER
from mythos.companions import (
    BUILD_SKIPPED,
    COMPANIONS_BY_SLUG,
    OFFLINE_LEAN,
    OFFLINE_PAPER,
    build_lean,
    check_lean_source,
    check_paper_source,
    companion_prompt,
    extract_fenced_block,
    parse_companions,
    strip_lean_comments,
)
from mythos.harness import MythosHarness

ROOT = Path(__file__).resolve().parents[1]
FILM = ROOT / "docs" / "showcase" / "every-orbit-great-circle"
SCENE = ROOT / "examples" / "mythos" / "every_orbit_great_circle.py"


@pytest.fixture
def no_toolchain(monkeypatch):
    """Builds are skipped: the tests must not depend on TeX or Lean."""
    monkeypatch.setattr(companions.shutil, "which", lambda name: None)
    monkeypatch.delenv("M2M_LEAN_PROJECT", raising=False)


def test_parse_companions_orders_and_rejects():
    assert [c.slug for c in parse_companions("lean, paper")] == ["paper", "lean"]
    assert parse_companions("") == ()
    assert parse_companions(None) == ()
    with pytest.raises(ValueError, match="unknown companion 'slides'"):
        parse_companions("paper,slides")


def test_offline_stand_ins_pass_their_own_checks():
    assert check_paper_source(OFFLINE_PAPER) == []
    assert check_lean_source(OFFLINE_LEAN) == []


def test_lean_check_ignores_comments_and_strings():
    source = (
        "/- no sorry here /- nested: axiom foo -/ still a comment -/\n"
        "import Mathlib\n"
        "-- sorry, this line is a comment\n"
        'def note : String := "-- not a comment, and no sorry"\n'
        "theorem t : (1 : ℕ) = 1 := rfl\n"
        "#print axioms t\n"
    )
    assert "sorry" not in strip_lean_comments(source).replace('"-- not a comment, and no sorry"', "")
    assert check_lean_source(source) == ["contains `sorry`"]  # the string literal is code
    assert check_lean_source(source.replace("and no sorry", "and no gap")) == []


@pytest.mark.parametrize("line, problem", [
    ("theorem bad : False := by sorry", "contains `sorry`"),
    ("axiom cheat : False", "declares an `axiom`"),
    ("theorem fast : 2 + 2 = 4 := by native_decide", "contains `native_decide`"),
    ("import Development.Upstream", "imports 'Development.Upstream': only Mathlib is allowed"),
])
def test_lean_check_rejects_gaps(line, problem):
    assert problem in check_lean_source(OFFLINE_LEAN + line + "\n")


def test_lean_check_requires_theorem_and_audit():
    errors = check_lean_source("import Mathlib\ndef x : ℕ := 1\n")
    assert "no theorem" in errors and "no `#print axioms` audit" in errors


def test_paper_check_rejects_unproved_and_external():
    no_proof = OFFLINE_PAPER.replace("\\begin{proof}", "").replace("\\end{proof}", "")
    assert "no proof environment" in check_paper_source(no_proof)
    unbalanced = OFFLINE_PAPER.replace("\\end{theorem}", "")
    assert any("theorem" in e and "\\begin" in e for e in check_paper_source(unbalanced))
    external = OFFLINE_PAPER.replace("\\maketitle", "\\maketitle\n\\input{secret}")
    assert "not self-contained: \\input" in check_paper_source(external)
    todo = OFFLINE_PAPER.replace("By Euler", "TODO. By Euler")
    assert any("placeholder" in e for e in check_paper_source(todo))
    # a commented-out \input is not a problem
    assert check_paper_source(OFFLINE_PAPER + "% \\input{old}\n") == []


def test_prompt_carries_charter_dossier_and_user_prompt():
    paper = COMPANIONS_BY_SLUG["paper"]
    text = companion_prompt(paper, {"04_math_dossier.json": {"formulas": ["m(s)"]}},
                            prompt="why does the pole survive?")
    assert "Paper Author of the Mythos chain" in text
    assert '"m(s)"' in text and "why does the pole survive?" in text
    assert "name: mythos-paper-author" not in text  # front matter is stripped
    lean = companion_prompt(COMPANIONS_BY_SLUG["lean"], {})
    assert "No `sorry`" in lean and "#print axioms" in lean


def test_extract_fenced_block():
    assert extract_fenced_block("x\n```lean\nimport Mathlib\n```\ny", ("lean",)) == "import Mathlib\n"
    assert extract_fenced_block("\\documentclass{article}", ("latex",)).startswith("\\documentclass")
    with pytest.raises(RuntimeError):
        extract_fenced_block("I could not write the file.", ("lean",))


def test_lean_build_is_skipped_without_a_project(tmp_path):
    (tmp_path / "Companion.lean").write_text(OFFLINE_LEAN, encoding="utf-8")
    result = build_lean(tmp_path, project_dir=None)
    assert result["status"] == BUILD_SKIPPED and "M2M_LEAN_PROJECT" in result["reason"]
    assert build_lean(tmp_path, project_dir=tmp_path)["status"] == BUILD_SKIPPED


def test_offline_run_writes_and_records_companions(tmp_path, no_toolchain):
    harness = MythosHarness(offline=True, runs_dir=tmp_path)
    manifest = harness.run("the pythagorean theorem", companions=parse_companions("paper,lean"))
    run_dir = tmp_path / manifest["run_id"]
    assert (run_dir / "paper.tex").read_text(encoding="utf-8") == OFFLINE_PAPER
    assert (run_dir / "Companion.lean").read_text(encoding="utf-8") == OFFLINE_LEAN
    for slug in ("paper", "lean"):
        record = manifest["companions"][slug]
        assert record["static"] == {"passed": True, "errors": []}
        assert record["build"]["status"] == BUILD_SKIPPED
    assert manifest["artifacts"]["paper"] == "paper.tex"
    assert manifest["artifacts"]["lean"] == "Companion.lean"
    assert [s["stage"] for s in manifest["stages"]][-2:] == ["paper", "lean"]
    assert manifest["status"]["run"] == "completed"
    on_disk = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert on_disk["companions"] == manifest["companions"]


def test_run_without_companions_is_unchanged(tmp_path):
    manifest = MythosHarness(offline=True, runs_dir=tmp_path).run("no companions")
    assert "companions" not in manifest
    assert not (tmp_path / manifest["run_id"] / "paper.tex").exists()


def test_rejected_companion_gets_one_repair(tmp_path, no_toolchain):
    replies: list[str] = []

    def run_model(prompt, *, system_extra, command, model, timeout):
        if "Lean Author of the Mythos chain" in prompt:
            first = "The file below was rejected" not in prompt
            replies.append("first" if first else "repair")
            body = OFFLINE_LEAN + ("theorem gap : False := by sorry\n" if first else "")
            return f"```lean\n{body}```"
        if "write the film" in prompt:
            return ("```python\nfrom manim import *\n\n\nclass StubJourney(ThreeDScene):\n"
                    "    def construct(self):\n        self.wait(0.1)\n```")
        return json.dumps({"formulas": ["a", "b"], "shots": [{"beat": i} for i in range(9)],
                           "padding": "x" * 600})

    harness = MythosHarness(runs_dir=tmp_path, run_model=run_model, command="stub",
                            log=lambda message: None)
    manifest = harness.run("repair path", companions=parse_companions("lean"))
    assert replies == ["first", "repair"]
    record = manifest["companions"]["lean"]
    assert record["static"]["passed"] is True
    assert manifest["stages"][-1] == {**manifest["stages"][-1], "stage": "lean", "repaired": True}
    run_dir = tmp_path / manifest["run_id"]
    assert "sorry" not in (run_dir / "Companion.lean").read_text(encoding="utf-8")
    assert (run_dir / "lean.repair.raw.txt").exists()


def _load_operator():
    spec = importlib.util.spec_from_file_location(
        "operate_mythos_chain", ROOT / "scripts" / "operate_mythos_chain.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _stages(tmp_path: Path) -> Path:
    stages = tmp_path / "stages"
    stages.mkdir()
    shutil.copy(FILM / "prompt.txt", stages / "prompt.txt")
    for path in sorted(FILM.glob("0[1-6]_*.json")):
        shutil.copy(path, stages / path.name)
    shutil.copy(SCENE, stages / "mythos_scene.py")
    return stages


def test_operator_asks_for_each_companion_then_records(tmp_path, no_toolchain):
    op = _load_operator()
    stages = _stages(tmp_path)
    both = parse_companions("paper,lean")
    rc, run_dir = op.operate(stages, runs_dir=tmp_path / "runs", companions=both)
    assert rc == op.NEEDS_REPLY and run_dir is None
    assert "Paper Author of the Mythos chain" in (stages / "NEXT_PROMPT.txt").read_text(encoding="utf-8")
    (stages / "paper.tex").write_text(OFFLINE_PAPER, encoding="utf-8")
    rc, _ = op.operate(stages, runs_dir=tmp_path / "runs", companions=both)
    assert rc == op.NEEDS_REPLY
    assert "Lean Author of the Mythos chain" in (stages / "NEXT_PROMPT.txt").read_text(encoding="utf-8")
    assert not (tmp_path / "runs").exists()
    (stages / "Companion.lean").write_text(OFFLINE_LEAN, encoding="utf-8")
    rc, run_dir = op.operate(stages, runs_dir=tmp_path / "runs", companions=both)
    assert rc == 0
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["companions"]["paper"]["static"]["passed"] is True
    assert manifest["companions"]["lean"]["build"]["status"] == BUILD_SKIPPED
    # a finished operator run is closed: status.run and status.outcome are set
    assert manifest["status"]["run"] == "completed"
    assert manifest["status"]["outcome"] == "scene_ready"
    assert manifest["scene_name"] == "HiddenSphereJourney" and manifest["completed_utc"]
    assert (run_dir / "paper.prompt.txt").exists() and (run_dir / "Companion.lean").exists()


def test_operator_reports_a_companion_that_fails_its_check(tmp_path, no_toolchain):
    op = _load_operator()
    stages = _stages(tmp_path)
    (stages / "Companion.lean").write_text(OFFLINE_LEAN + "axiom cheat : False\n", encoding="utf-8")
    rc, run_dir = op.operate(stages, runs_dir=tmp_path / "runs", companions=parse_companions("lean"))
    assert rc == 1
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["companions"]["lean"]["static"]["errors"] == ["declares an `axiom`"]


def test_charter_has_the_space_rules():
    for phrase in ("8. SPACE.", "9. GEOMETRY IS COMPUTED.", "10. FORMULA ON A CARD.",
                   "11. HONEST PICTURES.", "at most 14 words"):
        assert phrase in CINEMATIC_CHARTER


def test_render_cpu_cap_follows_the_wall_clock_budget():
    from mythos.render import MIN_CPU_SECONDS, cpu_limit_for

    assert cpu_limit_for(120) == MIN_CPU_SECONDS == 600
    assert cpu_limit_for(1800) == 1800
    assert cpu_limit_for(7200.5) == 7200
