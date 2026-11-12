"""The one scene checker and run-bundle validator for the MiMo silo.

``validation_from_scene`` is used both by the model-facing ``verify_scene`` tool
and by the application-side gate, so the two can never disagree. ``validate_run``
is read-only: it reports, the harness writes ``validation.json``.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from mimo.models import SCENE_FILE

BLOCKED_IMPORTS = frozenset({"os", "subprocess", "socket", "requests", "urllib", "httpx", "shutil"})
BLOCKED_CALLS = frozenset({"eval", "exec", "compile", "open", "__import__"})
SCENE_BASES = frozenset({"Scene", "ThreeDScene", "MovingCameraScene"})


def validation_from_scene(source: str) -> dict[str, Any]:
    """Statically check one complete Manim CE scene source.

    Returns ``{"status", "scene_name", "errors", "checks"}``. Rules: no blocked
    imports or calls, exactly one Scene subclass, camera moves only through
    ``move_camera``/``set_camera_orientation`` (never ``self.camera.animate``),
    and the module must compile.
    """
    errors: list[str] = []
    checks: list[str] = []
    if not source or not source.strip():
        return _report(["empty source"], None, checks)
    try:
        tree = ast.parse(source, filename=SCENE_FILE)
    except SyntaxError as exc:
        return _report([f"syntax error: {exc}"], None, checks)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in BLOCKED_IMPORTS:
                    errors.append(f"blocked import {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in BLOCKED_IMPORTS:
                errors.append(f"blocked import {node.module!r}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in BLOCKED_CALLS:
                errors.append(f"blocked call {node.func.id}()")
        elif isinstance(node, ast.Attribute) and node.attr == "animate":
            if isinstance(node.value, ast.Attribute) and node.value.attr == "camera":
                errors.append("forbidden camera animation via self.camera.animate")

    scene_names = [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and any(_base_name(base) in SCENE_BASES for base in node.bases)
    ]
    scene_name = scene_names[0] if len(scene_names) == 1 else None
    if scene_name is None:
        errors.append(f"expected exactly one Scene subclass, found {scene_names}")
    else:
        checks.append(f"scene_class:{scene_name}")

    try:
        compile(tree, SCENE_FILE, "exec")
    except (SyntaxError, ValueError, TypeError) as exc:
        errors.append(f"compilation failed: {exc}")
    else:
        checks.append("compiles")

    if "set_camera_orientation" in source or "move_camera" in source:
        checks.append("camera_helpers_used")
    return _report(errors, scene_name, checks)


def _base_name(base: ast.expr) -> str:
    if isinstance(base, ast.Name):
        return base.id
    return getattr(base, "attr", "")


def _report(errors: list[str], scene_name: str | None, checks: list[str]) -> dict[str, Any]:
    return {
        "status": "failed" if errors else "passed",
        "scene_name": scene_name,
        "errors": errors,
        "checks": checks,
    }


@dataclass
class RunValidation:
    """Outcome of checking a run directory. ``report`` is the validation.json payload."""

    failures: list[str] = field(default_factory=list)
    scene_name: str | None = None
    checks: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

    @property
    def report(self) -> dict[str, Any]:
        return _report(list(self.failures), self.scene_name, list(self.checks))


def artifact_failures(run_dir: Path, names: Iterable[str]) -> list[str]:
    """Presence and shape of artifacts: each file exists and is non-empty; JSON ones hold an object."""
    failures: list[str] = []
    for name in dict.fromkeys(names):
        path = Path(run_dir) / name
        if not path.is_file():
            failures.append(f"missing required artifact: {name}")
        elif path.stat().st_size == 0:
            failures.append(f"{name}: empty artifact")
        elif name.endswith(".json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"{name}: invalid JSON ({exc})")
                continue
            if not isinstance(payload, dict) or not payload:
                failures.append(f"{name}: expected a non-empty JSON object")
    return failures


def validate_run(run_dir: Path, required_artifacts: Iterable[str]) -> RunValidation:
    """Check the stage artifacts of a run bundle without writing anything.

    Every required artifact must exist and be well-formed (``artifact_failures``);
    the scene file must pass ``validation_from_scene``.
    """
    run_dir = Path(run_dir)
    required = tuple(dict.fromkeys(required_artifacts))
    result = RunValidation(failures=artifact_failures(run_dir, required))
    scene_path = run_dir / SCENE_FILE
    if SCENE_FILE in required and scene_path.is_file():
        report = validation_from_scene(scene_path.read_text(encoding="utf-8"))
        result.failures.extend(f"{SCENE_FILE}: {error}" for error in report["errors"])
        result.checks.extend(report["checks"])
        result.scene_name = report["scene_name"]
    return result
