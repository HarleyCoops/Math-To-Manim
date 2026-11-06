"""Final application-side validation for Codex-produced run bundles.

``validate_run`` is the only writer of ``validation.json``: every pass records
what it found about the scene source, or an empty template when none exists.
"""

from __future__ import annotations

import ast
import hashlib
import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sol.agents import ARTIFACT_NAMES
from sol.layout import SCENE_FILE, VALIDATION_FILE
from sol.rendering import MIN_VIDEO_BYTES, find_final_video
from sol.scene_checks import SceneCheckReport, validate_manim_code_report

_BLOCKED_IMPORTS = {"os", "subprocess", "socket", "requests", "urllib", "httpx", "shutil"}
_BLOCKED_CALLS = {"eval", "exec", "compile", "open", "__import__"}


def json_object_failure(path: Path) -> str | None:
    """Why ``path`` is not a non-empty JSON object, or None when it is one."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"{path.name}: invalid JSON ({exc})"
    if not isinstance(payload, dict) or not payload:
        return f"{path.name}: expected a non-empty JSON object"
    return None


def validation_payload(source: str | None, report: SceneCheckReport | None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "latex": None,
        "manim_code": None,
        "complexity": None,
        "ran_at": datetime.now(timezone.utc).isoformat(),
    }
    if source is None or report is None:
        return payload
    payload.update({
        "latex": report.latex.to_dict() if report.latex is not None else None,
        "manim_code": {
            "valid": report.valid,
            "scene_names": report.scene_names,
            "errors": report.errors,
            "warnings": report.warnings,
            "suggestions": report.suggestions,
        },
        "complexity": report.complexity,
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
    })
    return payload


def _validate_scene(
    path: Path, source: str
) -> tuple[list[str], str | None, SceneCheckReport | None]:
    failures: list[str] = []
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        return [f"{SCENE_FILE}: Python compilation failed ({exc})"], None, None
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _BLOCKED_IMPORTS:
                    failures.append(f"{SCENE_FILE}: blocked import {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in _BLOCKED_IMPORTS:
                failures.append(f"{SCENE_FILE}: blocked import {node.module!r}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in _BLOCKED_CALLS:
                failures.append(f"{SCENE_FILE}: blocked call {node.func.id}()")

    report = validate_manim_code_report(source, tree)
    if len(report.scene_names) != 1:
        failures.append(
            f"{SCENE_FILE}: expected exactly one Scene subclass, found {len(report.scene_names)}"
        )
    failures.extend(f"{SCENE_FILE}: {error}" for error in report.errors)
    scene_name = report.scene_names[0] if len(report.scene_names) == 1 else None
    return failures, scene_name, report


def validate_run(run_dir: Path, *, require_video: bool) -> tuple[list[str], str | None, str | None]:
    """Check the artifact contract, scene safety, and render evidence.

    Returns ``(failures, scene_name, video_path)`` and rewrites validation.json.
    """
    failures: list[str] = []
    scene_name = None
    scene_path = run_dir / SCENE_FILE
    source = report = None
    if scene_path.is_file():
        source = scene_path.read_text(encoding="utf-8")
        scene_failures, scene_name, report = _validate_scene(scene_path, source)
        failures.extend(scene_failures)
    (run_dir / VALIDATION_FILE).write_text(
        json.dumps(validation_payload(source, report), indent=2), encoding="utf-8"
    )

    for name in ARTIFACT_NAMES:
        path = run_dir / name
        if not path.is_file():
            failures.append(f"missing required artifact: {name}")
        elif name.endswith(".json"):
            failure = json_object_failure(path)
            if failure:
                failures.append(failure)

    video_path = None
    video = find_final_video(run_dir)
    if video:
        video_path = video.relative_to(run_dir).as_posix()
        if video.stat().st_size < MIN_VIDEO_BYTES:
            failures.append("rendered video is unexpectedly small")
    elif require_video:
        failures.append("render requested but no MP4 exists inside the run directory")
    return failures, scene_name, video_path
