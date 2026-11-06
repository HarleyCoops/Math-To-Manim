"""Final application-side validation for MiMo-produced run bundles."""

from __future__ import annotations

import ast
import json
import py_compile
from pathlib import Path

from mimo.models import ARTIFACT_NAMES
from mimo.tools import _BLOCKED_CALLS, _BLOCKED_IMPORTS


def validation_template() -> dict:
    return {
        "status": "pending",
        "scene_name": None,
        "errors": [],
        "checks": [],
    }


def validation_from_scene(source: str) -> dict:
    errors: list[str] = []
    checks: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"status": "failed", "scene_name": None, "errors": [str(exc)], "checks": []}

    scene_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _BLOCKED_IMPORTS:
                    errors.append(f"blocked import {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in _BLOCKED_IMPORTS:
                errors.append(f"blocked import {node.module!r}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in _BLOCKED_CALLS:
                errors.append(f"blocked call {node.func.id}()")
        elif isinstance(node, ast.Attribute) and node.attr == "animate":
            value = node.value
            if isinstance(value, ast.Attribute) and value.attr == "camera":
                errors.append("forbidden self.camera.animate")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                name = base.id if isinstance(base, ast.Name) else getattr(base, "attr", "")
                if name in {"Scene", "ThreeDScene", "MovingCameraScene"}:
                    scene_names.append(node.name)
    if len(scene_names) != 1:
        errors.append(f"expected one Scene subclass, found {scene_names}")
    else:
        checks.append(f"scene_class:{scene_names[0]}")

    if "set_camera_orientation" in source or "move_camera" in source:
        checks.append("camera_helpers_used")
    if ".animate" in source and "camera" in source:
        # soft signal already covered by AST rule
        checks.append("camera_rule_checked")

    return {
        "status": "failed" if errors else "passed",
        "scene_name": scene_names[0] if len(scene_names) == 1 else None,
        "errors": errors,
        "checks": checks,
    }


def validate_run(run_dir: Path, *, require_video: bool) -> tuple[list[str], str | None, str | None]:
    failures: list[str] = []
    scene_path = run_dir / "mimo_scene.py"
    validation_path = run_dir / "validation.json"
    if scene_path.is_file():
        report = validation_from_scene(scene_path.read_text(encoding="utf-8"))
        validation_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        failures.extend(f"mimo_scene.py: {error}" for error in report["errors"])
        scene_name = report["scene_name"]
        try:
            py_compile.compile(str(scene_path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"mimo_scene.py: compilation failed ({exc})")
            scene_name = None
    elif not validation_path.is_file():
        validation_path.write_text(json.dumps(validation_template(), indent=2), encoding="utf-8")
        failures.append("missing required artifact: mimo_scene.py")
        scene_name = None
    else:
        scene_name = None

    for name in ARTIFACT_NAMES:
        path = run_dir / name
        if not path.is_file():
            if name == "review.json":
                path.write_text(json.dumps({"status": "skipped"}, indent=2), encoding="utf-8")
                continue
            failures.append(f"missing required artifact: {name}")
            continue
        if name.endswith(".json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"{name}: invalid JSON ({exc})")
                continue
            if name != "review.json" and (not isinstance(payload, dict) or not payload):
                failures.append(f"{name}: expected a non-empty JSON object")

    video_path = None
    if require_video:
        media = run_dir / "media"
        videos = list(media.rglob("*.mp4")) if media.is_dir() else []
        if not videos:
            failures.append("render required but no mp4 found under media/")
        else:
            video_path = str(videos[0])
    return failures, scene_name, video_path
