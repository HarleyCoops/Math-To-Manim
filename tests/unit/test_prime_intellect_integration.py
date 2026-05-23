from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

from math_to_manim.cli import main
from math_to_manim.integrations import export_repair_tasks, score_generated_code_completion


VALID_CODE = """from manim import *

class DerivativeSlopeScene(Scene):
    def construct(self):
        title = Text("Derivatives are slopes by a limit")
        formula = MathTex(r"\\lim_{h \\to 0} \\frac{f(x+h)-f(x)}{h}")
        self.play(Write(title))
        self.play(Write(formula))
"""

CROWDED_CODE = """from manim import *

class DerivativeSlopeScene(Scene):
    def construct(self):
        title = Text("Derivatives are slopes by a limit, but the complete explanatory caption is too large for the frame", font_size=46).to_edge(UP).fix_in_frame()
        formula = MathTex(r"f'(a)=\\lim_{h\\to0}\\frac{f(a+h)-f(a)}{h}=\\text{the slope of the tangent line after a long secant collapse}", font_size=42).to_edge(DOWN).fix_in_frame()
        note = Text("This sentence competes with the formula instead of being staged as a separate beat", font_size=40).to_edge(DOWN).fix_in_frame()
        group = VGroup(title, formula, note).arrange(DOWN, buff=0.05)
        self.play(FadeIn(title), Write(formula), FadeIn(note))
        self.wait()
"""

READABLE_CODE = """from manim import *

class DerivativeSlopeScene(Scene):
    def construct(self):
        title = Text("Derivatives are slopes", font_size=34).to_edge(UP)
        formula = MathTex(r"f'(a)=\\lim_{h\\to0}\\frac{f(a+h)-f(a)}{h}", font_size=34)
        formula.scale_to_fit_width(6.5).to_edge(DOWN)
        note = Text("Secants collapse into one tangent direction.", font_size=26).scale_to_fit_width(6.8).next_to(formula, UP, buff=0.25)
        self.play(FadeIn(title))
        self.play(Write(formula))
        self.play(FadeOut(formula), FadeIn(note))
        self.wait()
"""


def test_score_generated_code_completion_accepts_valid_scene() -> None:
    task = {"scene_name": "DerivativeSlopeScene", "acceptance_terms": ["Derivatives", "slopes", "limit"]}
    completion = _completion("DerivativeSlopeScene", VALID_CODE)

    score = score_generated_code_completion(task, completion)

    assert score.score == 1.0
    assert score.components["static_validation"] == 1.0
    assert score.scene_classes == ["DerivativeSlopeScene"]


def test_score_generated_code_completion_penalizes_missing_tag() -> None:
    task = {"scene_name": "DerivativeSlopeScene", "acceptance_terms": ["Derivatives"]}
    raw_json = json.dumps({"scene_name": "DerivativeSlopeScene", "language": "python", "code": VALID_CODE})

    score = score_generated_code_completion(task, raw_json)

    assert score.components["format"] == 0.0
    assert score.score < 1.0


def test_score_generated_code_completion_rejects_unsafe_code() -> None:
    task = {"scene_name": "DerivativeSlopeScene", "acceptance_terms": []}
    unsafe = "import subprocess\nfrom manim import *\n\nclass DerivativeSlopeScene(Scene):\n    def construct(self):\n        subprocess.run(['echo', 'bad'])\n"

    score = score_generated_code_completion(task, _completion("DerivativeSlopeScene", unsafe))

    assert score.components["safety"] == 0.0
    assert any("subprocess" in error for error in score.errors)


def test_score_generated_code_completion_penalizes_crowded_text_layout() -> None:
    task = {"scene_name": "DerivativeSlopeScene", "acceptance_terms": ["Derivatives", "slopes", "limit"]}

    crowded = score_generated_code_completion(task, _completion("DerivativeSlopeScene", CROWDED_CODE))
    readable = score_generated_code_completion(task, _completion("DerivativeSlopeScene", READABLE_CODE))

    assert crowded.components["layout_static"] < readable.components["layout_static"]
    assert readable.components["layout_static"] == 1.0
    assert any("layout risk" in error for error in crowded.errors)


def test_export_repair_tasks_writes_jsonl(tmp_path: Path) -> None:
    run_dir = _write_run_bundle(tmp_path / "runs" / "run-1")
    output = tmp_path / "tasks.jsonl"

    result = export_repair_tasks(run_dir.parent, output)

    assert result.written == 1
    payload = json.loads(output.read_text(encoding="utf-8").strip())
    assert payload["schema_version"] == "m2m2.pi_repair_task.v1"
    assert payload["task_id"] == run_dir.name
    assert payload["scene_name"] == "DerivativeSlopeScene"
    assert "generated_code" in payload
    assert "render" in payload["evidence"]


def test_pi_export_runs_cli_outputs_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    runs_dir = tmp_path / "runs"
    _write_run_bundle(runs_dir / "run-1")
    output = tmp_path / "tasks.jsonl"

    exit_code = main(["pi-export-runs", "--runs-dir", str(runs_dir), "--output", str(output), "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["written"] == 1
    assert output.exists()


def test_standalone_environment_scoring_module_matches_contract() -> None:
    env_path = Path(__file__).resolve().parents[2] / "environments" / "math_to_manim"
    sys.path.insert(0, str(env_path))
    try:
        from m2m2_visual_repair.scoring import score_completion

        task = {"scene_name": "DerivativeSlopeScene", "acceptance_terms": ["Derivatives", "slopes"]}
        score = score_completion(task, _completion("DerivativeSlopeScene", VALID_CODE))
        crowded = score_completion(task, _completion("DerivativeSlopeScene", CROWDED_CODE))
    finally:
        sys.path.remove(str(env_path))

    assert score.score == 1.0
    assert crowded.components["layout_static"] < 1.0


def test_verifiers_environment_loads_sample_when_dependency_available() -> None:
    verifiers = pytest.importorskip("verifiers")
    env_path = Path(__file__).resolve().parents[2] / "environments" / "math_to_manim"
    sys.path.insert(0, str(env_path))
    try:
        env = verifiers.load_environment("math-to-manim", max_examples=1, eval_fraction=0)
    finally:
        sys.path.remove(str(env_path))

    assert len(env.dataset) == 1


def _completion(scene_name: str, code: str) -> str:
    return "<generated_code>" + json.dumps({"scene_name": scene_name, "language": "python", "code": code}) + "</generated_code>"


def _write_run_bundle(run_dir: Path) -> Path:
    run_dir.mkdir(parents=True)
    request = {
        "prompt": "Explain why derivatives are slopes.",
        "target_audience": "high_school",
        "style": "clear",
        "duration_seconds": 60,
        "metadata": {},
    }
    scene_spec = {
        "scene_name": "DerivativeSlopeScene",
        "objects": [],
        "animations": [],
        "metadata": {"original_prompt": request["prompt"]},
    }
    generated = {
        "scene_name": "DerivativeSlopeScene",
        "language": "python",
        "code": VALID_CODE,
        "dependencies": ["manim"],
        "metadata": {"file_path": "generated_scene.py"},
    }
    validation = {"status": "passed", "issues": [], "summary": "Static validation passed.", "metadata": {}}
    render = {"status": "skipped", "scene_name": "DerivativeSlopeScene", "stderr": "render skipped", "stdout": "", "metadata": {"skipped": True}}
    review = {"approved": False, "score": 0.0, "observations": [], "issues": [], "recommendations": [], "metadata": {}}

    for name, payload in {
        "request": request,
        "scene_spec": scene_spec,
        "generated_code": generated,
        "validation_report": validation,
        "render_result": render,
        "review_report": review,
    }.items():
        (run_dir / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")
    (run_dir / "generated_scene.py").write_text(VALID_CODE, encoding="utf-8")
    return run_dir
