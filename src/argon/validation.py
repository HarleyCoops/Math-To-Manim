"""Reverse-tree and static Manim scene checks for Argon Google ADK runs.

Pure functions over payloads and source text; the run-bundle walk that applies
them to files lives in ``argon.bundle``.
"""

from __future__ import annotations

import ast
import re

from argon.models import SCENE_FILE

_BLOCKED_IMPORTS = {"os", "subprocess", "socket", "requests", "urllib", "httpx", "shutil"}
_BLOCKED_CALLS = {"eval", "exec", "compile", "open", "__import__"}


def _as_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    return value


def _as_int(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    return value


def normalize_reverse_tree(payload: dict) -> dict:
    """Coerce common model shapes into the reverse-tree contract."""
    if not isinstance(payload, dict):
        return {}
    data = dict(payload)
    nodes = data.get("nodes")
    if isinstance(nodes, dict):
        nodes = list(nodes.values())
    normalized_nodes: list[dict] = []
    for node in nodes or []:
        if not isinstance(node, dict):
            continue
        item = dict(node)
        item["depth"] = _as_int(item.get("depth"))
        if "assumed" in item:
            item["assumed"] = _as_bool(item.get("assumed"))
        normalized_nodes.append(item)
    data["nodes"] = normalized_nodes

    edges = data.get("edges") or []
    normalized_edges: list[list] = []
    for edge in edges:
        if isinstance(edge, (list, tuple)) and len(edge) == 2:
            normalized_edges.append([edge[0], edge[1]])
        elif isinstance(edge, dict):
            src = edge.get("from") or edge.get("from_id") or edge.get("src")
            dst = edge.get("to") or edge.get("to_id") or edge.get("dst")
            if src and dst:
                normalized_edges.append([src, dst])
    data["edges"] = normalized_edges

    spine = data.get("spine")
    if isinstance(spine, str):
        data["spine"] = [part.strip() for part in re.split(r"[\s,]+", spine) if part.strip()]

    if not (isinstance(data.get("target"), str) and data["target"].strip()):
        zero = next((node for node in normalized_nodes if node.get("depth") == 0), None)
        if zero:
            data["target"] = str(zero.get("name") or zero.get("id") or "").strip()
    return data


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


def _scene_classes(tree: ast.Module) -> list[str]:
    found: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for base in node.bases:
            name = base.id if isinstance(base, ast.Name) else ""
            if name.endswith("Scene"):
                found.append(node.name)
                break
    return found


def _animates_camera(source: str) -> bool:
    return "self.camera.animate" in source.replace(" ", "")


def verify_scene_report(source: str) -> dict:
    """The one static check of a scene file: compiles, no blocked imports/calls,
    no camera animation, exactly one Scene subclass.

    Returns ``{"passed": bool, "scene_name": str | None, "errors": [...]}``.
    """
    failures: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"passed": False, "scene_name": None, "errors": [f"{SCENE_FILE}: syntax error ({exc})"]}
    try:
        compile(tree, f"<{SCENE_FILE}>", "exec")
    except (SyntaxError, ValueError) as exc:
        failures.append(f"{SCENE_FILE}: Python compilation failed ({exc})")

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

    if _animates_camera(source):
        failures.append(
            f"{SCENE_FILE}: never animate self.camera; use move_camera or set_camera_orientation"
        )

    scene_classes = _scene_classes(tree)
    if len(scene_classes) != 1:
        failures.append(
            f"{SCENE_FILE}: expected exactly one Scene subclass, found {len(scene_classes)}"
        )
    return {
        "passed": not failures,
        "scene_name": scene_classes[0] if len(scene_classes) == 1 else None,
        "errors": failures,
    }
