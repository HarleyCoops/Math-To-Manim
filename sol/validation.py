"""Final application-side validation for Codex-produced run bundles."""

from __future__ import annotations

import ast
import json
import py_compile
import re
from pathlib import Path

from sol.models import ARTIFACT_NAMES

_BLOCKED_IMPORTS = {"os", "subprocess", "socket", "requests", "urllib", "httpx", "shutil"}
_BLOCKED_CALLS = {"eval", "exec", "compile", "open", "__import__"}


def _validate_json(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"{path.name}: invalid JSON ({exc})"
    if not isinstance(payload, dict) or not payload:
        return f"{path.name}: expected a non-empty JSON object"
    return None


def _validate_scene(path: Path) -> tuple[list[str], str | None]:
    failures: list[str] = []
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        return [f"sol_scene.py: Python compilation failed ({exc})"], None
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"sol_scene.py: syntax error ({exc})"], None

    scene_classes: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _BLOCKED_IMPORTS:
                    failures.append(f"sol_scene.py: blocked import {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in _BLOCKED_IMPORTS:
                failures.append(f"sol_scene.py: blocked import {node.module!r}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in _BLOCKED_CALLS:
                failures.append(f"sol_scene.py: blocked call {node.func.id}()")
        elif isinstance(node, ast.ClassDef):
            bases = {base.id for base in node.bases if isinstance(base, ast.Name)}
            if bases & {"Scene", "ThreeDScene", "MovingCameraScene"}:
                scene_classes.append(node.name)
    if len(scene_classes) != 1:
        failures.append(f"sol_scene.py: expected exactly one Scene subclass, found {len(scene_classes)}")
    if re.search(r"self\.camera\.animate", source):
        failures.append("sol_scene.py: animate the frame or use move_camera, never self.camera.animate")
    return failures, scene_classes[0] if len(scene_classes) == 1 else None


def validate_run(run_dir: Path, *, require_video: bool) -> tuple[list[str], str | None, str | None]:
    failures: list[str] = []
    for name in ARTIFACT_NAMES:
        path = run_dir / name
        if not path.is_file():
            failures.append(f"missing required artifact: {name}")
        elif name.endswith(".json"):
            failure = _validate_json(path)
            if failure:
                failures.append(failure)

    scene_name = None
    scene_path = run_dir / "sol_scene.py"
    if scene_path.is_file():
        scene_failures, scene_name = _validate_scene(scene_path)
        failures.extend(scene_failures)

    video_path = None
    videos = sorted(run_dir.glob("**/*.mp4"))
    if videos:
        video_path = str(videos[-1].relative_to(run_dir))
        if videos[-1].stat().st_size < 1024:
            failures.append("rendered video is unexpectedly small")
    elif require_video:
        failures.append("render requested but no MP4 exists inside the run directory")
    return failures, scene_name, video_path

