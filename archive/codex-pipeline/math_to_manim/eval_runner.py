"""Executable prompt-suite checks for local M2M2 regression evals."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import json
from pathlib import Path
import tempfile
from typing import Any

import yaml

from math_to_manim.config import RuntimeConfig
from math_to_manim.pipeline.runner import AnimationPipeline


DEFAULT_REQUIRED_ARTIFACTS = (
    "request",
    "intent",
    "knowledge_graph",
    "curriculum",
    "math_packet",
    "storyboard",
    "scene_spec",
    "generated_code",
    "generated_scene",
    "validation_report",
    "render_result",
    "review_report",
    "animation_package",
    "manifest",
)

ARTIFACT_ALIASES = {
    "request_spec": "request",
    "concept_plan": "intent",
    "knowledge_tree": "knowledge_graph",
    "math_enrichment": "math_packet",
    "visual_spec": "storyboard",
    "narrative_spec": "storyboard",
}


@dataclass(frozen=True)
class EvalCheck:
    name: str
    passed: bool
    message: str

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
        }


@dataclass(frozen=True)
class EvalCaseResult:
    case_id: str
    prompt: str
    run_dir: str | None
    checks: list[EvalCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return bool(self.checks) and all(check.passed for check in self.checks)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "prompt": self.prompt,
            "run_dir": self.run_dir,
            "passed": self.passed,
            "checks": [check.to_public_dict() for check in self.checks],
        }


@dataclass(frozen=True)
class EvalSuiteResult:
    suite_id: str
    suite_path: str
    runs_dir: str
    render_requested: bool
    cases: list[EvalCaseResult]

    @property
    def passed(self) -> bool:
        return bool(self.cases) and all(case.passed for case in self.cases)

    @property
    def passed_count(self) -> int:
        return sum(1 for case in self.cases if case.passed)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "suite_id": self.suite_id,
            "suite_path": self.suite_path,
            "runs_dir": self.runs_dir,
            "render_requested": self.render_requested,
            "passed": self.passed,
            "passed_count": self.passed_count,
            "case_count": len(self.cases),
            "cases": [case.to_public_dict() for case in self.cases],
        }


def load_prompt_suite(path: str | Path) -> dict[str, Any]:
    """Load and minimally validate a prompt eval suite YAML file."""

    suite_path = Path(path)
    payload = yaml.safe_load(suite_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Prompt suite must be a mapping: {suite_path}")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"Prompt suite must contain at least one case: {suite_path}")
    return payload


def run_prompt_suite(
    suite_path: str | Path,
    *,
    config: RuntimeConfig | None = None,
    runs_dir: str | Path | None = None,
    render: bool = False,
) -> EvalSuiteResult:
    """Run each YAML prompt case through the local pipeline and score hard gates."""

    suite_file = Path(suite_path)
    suite = load_prompt_suite(suite_file)
    suite_runs_dir = Path(runs_dir) if runs_dir is not None else Path(tempfile.mkdtemp(prefix="m2m2-evals-"))
    suite_runs_dir.mkdir(parents=True, exist_ok=True)

    base_config = config or RuntimeConfig.from_env()
    eval_config = RuntimeConfig(**{**base_config.__dict__, "runs_dir": suite_runs_dir})

    case_results = [
        _run_case(case, config=eval_config, render=render)
        for case in suite["cases"]
    ]
    return EvalSuiteResult(
        suite_id=str(suite.get("suite_id") or suite_file.stem),
        suite_path=str(suite_file),
        runs_dir=str(suite_runs_dir),
        render_requested=render,
        cases=case_results,
    )


def _run_case(case: dict[str, Any], *, config: RuntimeConfig, render: bool) -> EvalCaseResult:
    case_id = str(case.get("id") or "unnamed_case")
    input_payload = case.get("input") or {}
    if not isinstance(input_payload, dict):
        return EvalCaseResult(
            case_id=case_id,
            prompt="",
            run_dir=None,
            checks=[EvalCheck("case_input", False, "case.input must be a mapping")],
        )

    prompt = str(input_payload.get("prompt") or "").strip()
    if not prompt:
        return EvalCaseResult(
            case_id=case_id,
            prompt=prompt,
            run_dir=None,
            checks=[EvalCheck("case_prompt", False, "case.input.prompt is required")],
        )

    try:
        package = AnimationPipeline(config=config).generate(
            prompt=prompt,
            audience_level=str(input_payload.get("audience") or "high_school"),
            desired_duration=int(input_payload.get("duration_seconds") or 60),
            style=str(input_payload.get("style") or "cinematic"),
            render=render,
        )
    except Exception as exc:  # pragma: no cover - exercised as a defensive CLI path
        return EvalCaseResult(
            case_id=case_id,
            prompt=prompt,
            run_dir=None,
            checks=[EvalCheck("pipeline_run", False, f"{type(exc).__name__}: {exc}")],
        )

    run_dir = _run_dir_from_package(package)
    checks = [EvalCheck("pipeline_run", True, "pipeline completed")]
    checks.extend(_evaluate_run(case, Path(run_dir), render=render))
    return EvalCaseResult(case_id=case_id, prompt=prompt, run_dir=run_dir, checks=checks)


def _evaluate_run(case: dict[str, Any], run_dir: Path, *, render: bool) -> list[EvalCheck]:
    return [
        _check_required_artifacts(case, run_dir),
        _check_scene_name(run_dir),
        _check_generated_scene_parses(run_dir),
        _check_static_validation(run_dir),
        _check_render_status(run_dir, render=render),
        _check_expected_terms(case, run_dir),
    ]


def _check_required_artifacts(case: dict[str, Any], run_dir: Path) -> EvalCheck:
    required = set(DEFAULT_REQUIRED_ARTIFACTS)
    expected = case.get("expected") or {}
    if isinstance(expected, dict):
        required.update(_normalize_artifact_name(name) for name in expected.get("required_artifacts") or [])

    missing = sorted(name for name in required if not _artifact_path(run_dir, name).exists())
    if missing:
        return EvalCheck("required_artifacts", False, f"missing artifacts: {', '.join(missing)}")
    return EvalCheck("required_artifacts", True, f"{len(required)} artifacts present")


def _check_scene_name(run_dir: Path) -> EvalCheck:
    scene_spec = _read_json(run_dir / "scene_spec.json")
    generated_code = _read_json(run_dir / "generated_code.json")
    request = _read_json(run_dir / "request.json")

    scene_name = str(scene_spec.get("scene_name") or "")
    prompt = str(request.get("prompt") or "")
    failures = []
    if not scene_name:
        failures.append("scene_name is empty")
    if not scene_name.endswith("Scene"):
        failures.append("scene_name must end with Scene")
    if len(scene_name) > 80:
        failures.append("scene_name exceeds 80 characters")
    if scene_name and not scene_name.isidentifier():
        failures.append("scene_name is not a valid Python identifier")
    if prompt and scene_name.lower() == prompt.lower():
        failures.append("scene_name is the raw prompt")
    if generated_code.get("scene_name") != scene_name:
        failures.append("generated_code.scene_name does not match scene_spec.scene_name")

    if failures:
        return EvalCheck("scene_name", False, "; ".join(failures))
    return EvalCheck("scene_name", True, scene_name)


def _check_generated_scene_parses(run_dir: Path) -> EvalCheck:
    path = run_dir / "generated_scene.py"
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return EvalCheck("generated_scene_parses", False, f"{exc.msg} at line {exc.lineno}")
    return EvalCheck("generated_scene_parses", True, "generated_scene.py parses")


def _check_static_validation(run_dir: Path) -> EvalCheck:
    report = _read_json(run_dir / "validation_report.json")
    status = report.get("status")
    error_count = sum(1 for issue in report.get("issues") or [] if issue.get("severity") == "error")
    if status not in {"passed", "warning"} or error_count:
        return EvalCheck("static_validation", False, f"status={status}, error_count={error_count}")
    return EvalCheck("static_validation", True, f"status={status}")


def _check_render_status(run_dir: Path, *, render: bool) -> EvalCheck:
    result = _read_json(run_dir / "render_result.json")
    status = result.get("status")
    if render:
        if status == "succeeded" and result.get("output_path"):
            return EvalCheck("render_status", True, "render succeeded")
        return EvalCheck("render_status", False, f"expected succeeded render, got {status}")
    if status == "skipped":
        return EvalCheck("render_status", True, "render skipped as requested")
    return EvalCheck("render_status", False, f"expected skipped render, got {status}")


def _check_expected_terms(case: dict[str, Any], run_dir: Path) -> EvalCheck:
    expected = case.get("expected") or {}
    terms = expected.get("acceptance_terms") if isinstance(expected, dict) else None
    if not terms:
        return EvalCheck("expected_terms", True, "no acceptance_terms configured")

    text = _combined_run_text(run_dir)
    missing = [str(term) for term in terms if not _contains_term(text, str(term))]
    if missing:
        return EvalCheck("expected_terms", False, f"missing terms: {', '.join(missing)}")
    return EvalCheck("expected_terms", True, f"{len(terms)} terms found")


def _run_dir_from_package(package: Any) -> str:
    manifest_path = package.metadata.get("reproducibility_manifest") if package.metadata else None
    if not manifest_path:
        raise ValueError("AnimationPackage metadata did not include reproducibility_manifest")
    return str(Path(manifest_path).parent)


def _artifact_path(run_dir: Path, name: str) -> Path:
    if name == "generated_scene":
        return run_dir / "generated_scene.py"
    if name == "manifest":
        return run_dir / "manifest.json"
    return run_dir / f"{name}.json"


def _normalize_artifact_name(name: Any) -> str:
    key = str(name).strip()
    return ARTIFACT_ALIASES.get(key, key)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _combined_run_text(run_dir: Path) -> str:
    chunks = []
    for path in sorted(run_dir.glob("*.json")) + sorted(run_dir.glob("*.py")):
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _contains_term(text: str, term: str) -> bool:
    return _normalize_text(term) in _normalize_text(text)


def _normalize_text(text: str) -> str:
    return " ".join(text.casefold().split())
