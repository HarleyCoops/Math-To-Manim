"""Artifact and reverse-tree checks for Grok runs."""

from __future__ import annotations

import ast
import json
import py_compile
from pathlib import Path

from grok.models import ARTIFACT_NAMES

_BLOCKED_IMPORTS = {"os", "subprocess", "socket", "requests", "urllib", "httpx", "shutil"}
_BLOCKED_CALLS = {"eval", "exec", "compile", "open", "__import__"}


def validate_reverse_tree(payload: dict) -> list[str]:
    """Depth 0 is the target. Edges are prerequisites. Spine starts assumed."""
    failures: list[str] = []
    if not isinstance(payload, dict) or not payload:
        return ["knowledge map is not a non-empty JSON object"]

    target = payload.get("target")
    if not isinstance(target, str) or not target.strip():
        failures.append("knowledge map is missing a target claim")

    nodes = payload.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return failures + ["knowledge map needs a non-empty nodes list"]

    by_id: dict[str, dict] = {}
    depth_zero: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            failures.append("knowledge map node is not an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            failures.append("knowledge map node is missing id")
            continue
        if node_id in by_id:
            failures.append(f"duplicate knowledge map node id {node_id!r}")
        by_id[node_id] = node
        depth = node.get("depth")
        if not isinstance(depth, int) or depth < 0:
            failures.append(f"node {node_id!r} needs a non-negative integer depth")
        elif depth == 0:
            depth_zero.append(node_id)
        if "assumed" not in node:
            failures.append(f"node {node_id!r} needs an assumed flag")

    if len(depth_zero) != 1:
        failures.append("exactly one node must have depth 0 (the target)")
    elif by_id.get(depth_zero[0], {}).get("assumed") is True:
        failures.append("the depth 0 target must not be assumed")

    edges = payload.get("edges")
    if not isinstance(edges, list) or not edges:
        failures.append("knowledge map needs prerequisite edges")
    else:
        for edge in edges:
            if not (isinstance(edge, (list, tuple)) and len(edge) == 2):
                failures.append("each edge must be a [from_id, to_id] pair")
                continue
            src, dst = edge
            if src not in by_id or dst not in by_id:
                failures.append(f"edge {edge!r} refers to an unknown node")
                continue
            src_depth = by_id[src].get("depth")
            dst_depth = by_id[dst].get("depth")
            if (
                isinstance(src_depth, int)
                and isinstance(dst_depth, int)
                and src_depth <= dst_depth
            ):
                failures.append(
                    f"edge {src!r}->{dst!r} is not a prerequisite: "
                    "from_id must be deeper than to_id"
                )

    spine = payload.get("spine")
    if not isinstance(spine, list) or not spine:
        failures.append("knowledge map needs a spine from foundations to target")
        return failures
    if any(node_id not in by_id for node_id in spine):
        failures.append("spine refers to an unknown node")
        return failures
    start = by_id[spine[0]]
    if start.get("assumed") is not True:
        failures.append("spine must start at an assumed foundation")
    if depth_zero and spine[-1] != depth_zero[0]:
        failures.append("spine must end at the depth 0 target")
    depths = [by_id[node_id].get("depth") for node_id in spine]
    if all(isinstance(depth, int) for depth in depths) and depths != sorted(depths, reverse=True):
        failures.append("spine must walk from deeper foundations toward depth 0")
    return failures


def discover_scene_classes(tree: ast.AST) -> list[str]:
    found: list[str] = []
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if not isinstance(node, ast.ClassDef):
            continue
        for base in node.bases:
            name = base.id if isinstance(base, ast.Name) else ""
            if name.endswith("Scene"):
                found.append(node.name)
                break
    return found


def validate_scene_source(source: str) -> tuple[list[str], str | None]:
    failures: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"grok_scene.py: syntax error ({exc})"], None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _BLOCKED_IMPORTS:
                    failures.append(f"grok_scene.py: blocked import {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in _BLOCKED_IMPORTS:
                failures.append(f"grok_scene.py: blocked import {node.module!r}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in _BLOCKED_CALLS:
                failures.append(f"grok_scene.py: blocked call {node.func.id}()")

    if re_search_camera_animate(source):
        failures.append(
            "grok_scene.py: never animate self.camera; "
            "use move_camera or set_camera_orientation"
        )

    scene_classes = discover_scene_classes(tree)
    if len(scene_classes) != 1:
        failures.append(
            f"grok_scene.py: expected exactly one Scene subclass, found {len(scene_classes)}"
        )
    return failures, scene_classes[0] if len(scene_classes) == 1 else None


def re_search_camera_animate(source: str) -> bool:
    return "self.camera.animate" in source or "self.camera.animate" in source.replace(" ", "")


def verify_scene_report(source: str) -> dict:
    compile_error = None
    try:
        compile(source, "<grok_scene>", "exec")
    except SyntaxError as exc:
        compile_error = str(exc)
    failures, scene_name = validate_scene_source(source)
    if compile_error:
        failures = [f"grok_scene.py: Python compilation failed ({compile_error})"] + failures
    return {
        "passed": not failures,
        "scene_name": scene_name,
        "errors": failures,
    }


def validate_run(run_dir: Path, *, require_video: bool = False) -> tuple[list[str], str | None, str | None]:
    failures: list[str] = []
    for name in ARTIFACT_NAMES:
        path = run_dir / name
        if not path.is_file():
            failures.append(f"missing required artifact: {name}")
            continue
        if name.endswith(".json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                failures.append(f"{name}: invalid JSON ({exc})")
                continue
            if not isinstance(payload, dict) or not payload:
                failures.append(f"{name}: expected a non-empty JSON object")
            if name == "02_knowledge_map.json":
                failures.extend(validate_reverse_tree(payload))

    scene_path = run_dir / "grok_scene.py"
    scene_name = None
    if scene_path.is_file():
        try:
            py_compile.compile(str(scene_path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"grok_scene.py: Python compilation failed ({exc})")
        source = scene_path.read_text(encoding="utf-8")
        scene_failures, scene_name = validate_scene_source(source)
        failures.extend(scene_failures)

    video_path = None
    media = run_dir / "media"
    if media.is_dir():
        videos = sorted(media.rglob("*.mp4"))
        if videos:
            video_path = str(videos[-1])
    if require_video and not video_path:
        failures.append("render requested but no mp4 was found")
    return failures, scene_name, video_path
