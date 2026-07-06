from __future__ import annotations

import json
from pathlib import Path

from math_to_manim.cli import main
from math_to_manim.config import RuntimeConfig
from math_to_manim.eval_runner import load_prompt_suite, run_prompt_suite


def test_prompt_suite_runner_executes_deterministic_structural_checks(tmp_path) -> None:
    suite_path = _write_suite(tmp_path, acceptance_terms=["derivatives", "slopes"])

    result = run_prompt_suite(
        suite_path,
        config=RuntimeConfig(deterministic=True, trace_enabled=False),
        runs_dir=tmp_path / "runs",
        render=False,
    )

    assert result.passed
    assert result.passed_count == 1
    case = result.cases[0]
    assert case.run_dir is not None
    assert {check.name for check in case.checks} >= {
        "required_artifacts",
        "scene_name",
        "generated_scene_parses",
        "static_validation",
        "render_status",
        "expected_terms",
    }


def test_prompt_suite_runner_reports_missing_acceptance_terms(tmp_path) -> None:
    suite_path = _write_suite(tmp_path, acceptance_terms=["not in this run"])

    result = run_prompt_suite(
        suite_path,
        config=RuntimeConfig(deterministic=True, trace_enabled=False),
        runs_dir=tmp_path / "runs",
        render=False,
    )

    assert not result.passed
    failed = [check for check in result.cases[0].checks if not check.passed]
    assert failed[0].name == "expected_terms"
    assert "not in this run" in failed[0].message


def test_eval_suite_cli_outputs_json(tmp_path, capsys) -> None:
    suite_path = _write_suite(tmp_path, acceptance_terms=["derivatives"])

    exit_code = main(["eval-suite", str(suite_path), "--runs-dir", str(tmp_path / "runs"), "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["passed"] is True
    assert payload["case_count"] == 1


def test_load_prompt_suite_rejects_empty_cases(tmp_path) -> None:
    suite_path = tmp_path / "empty.yaml"
    suite_path.write_text("suite_id: empty\ncases: []\n", encoding="utf-8")

    try:
        load_prompt_suite(suite_path)
    except ValueError as exc:
        assert "at least one case" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def _write_suite(tmp_path: Path, *, acceptance_terms: list[str]) -> Path:
    terms = "\n".join(f"        - {json.dumps(term)}" for term in acceptance_terms)
    suite_path = tmp_path / "suite.yaml"
    suite_path.write_text(
        f"""schema_version: "m2m2.prompt_eval.v1"
suite_id: "unit_suite"
cases:
  - id: "derivative_case"
    input:
      prompt: "Explain why derivatives are slopes."
      audience: "high_school"
      duration_seconds: 30
      style: "clear"
    expected:
      acceptance_terms:
{terms}
      required_artifacts:
        - "request_spec"
        - "concept_plan"
        - "knowledge_tree"
        - "math_enrichment"
        - "visual_spec"
        - "scene_spec"
""",
        encoding="utf-8",
    )
    return suite_path
