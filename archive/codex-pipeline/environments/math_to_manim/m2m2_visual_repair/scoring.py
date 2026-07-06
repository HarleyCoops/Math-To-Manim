"""Static reward scoring for Math-To-Manim generated-code repair."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import json
import re
from typing import Any


GENERATED_CODE_TAG_RE = re.compile(r"<generated_code>\s*(.*?)\s*</generated_code>", re.DOTALL | re.IGNORECASE)
SCENE_BASES = {
    "Scene",
    "ThreeDScene",
    "MovingCameraScene",
    "ZoomedScene",
    "GraphScene",
    "VectorScene",
    "LinearTransformationScene",
    "SpecialThreeDScene",
    "SampleSpaceScene",
}
ALLOWED_IMPORT_ROOTS = {"collections", "dataclasses", "functools", "itertools", "manim", "math", "numpy", "typing"}
FORBIDDEN_IMPORT_ROOTS = {"builtins", "importlib", "os", "pathlib", "runpy", "shutil", "socket", "subprocess", "sys"}
FORBIDDEN_CALL_NAMES = {
    "__import__",
    "breakpoint",
    "compile",
    "eval",
    "exec",
    "input",
    "open",
    "os.popen",
    "os.system",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.run",
}
TEXT_CONSTRUCTORS = {"MarkupText", "MathTex", "Paragraph", "SingleStringMathTex", "Tex", "Text"}
WIDTH_GUARD_METHODS = {"scale_to_fit_width", "set_width"}
TEXT_LAYOUT_METHODS = WIDTH_GUARD_METHODS | {"arrange", "next_to", "shift", "to_corner", "to_edge"}
WEIGHTS = {
    "format": 0.08,
    "schema": 0.12,
    "python_parse": 0.12,
    "static_validation": 0.22,
    "safety": 0.13,
    "acceptance_terms": 0.15,
    "layout_static": 0.18,
}


@dataclass(frozen=True)
class ScoreResult:
    score: float
    components: dict[str, float]
    errors: list[str] = field(default_factory=list)
    scene_classes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TextLayoutItem:
    constructor: str
    text: str
    font_size: float | None
    methods: set[str] = field(default_factory=set)
    name: str | None = None


def score_completion(task: dict[str, Any], completion: str) -> ScoreResult:
    """Score one model completion against a repair task."""

    payload, used_tags = extract_generated_code_payload(completion)
    components = {key: 0.0 for key in WEIGHTS}
    components["format"] = 1.0 if used_tags else 0.0
    errors: list[str] = []
    scene_classes: list[str] = []

    if payload is None:
        return _weighted(components, ["missing generated_code block"])
    try:
        generated = json.loads(payload)
    except json.JSONDecodeError as exc:
        return _weighted(components, [f"invalid JSON: {exc.msg}"])
    if not isinstance(generated, dict):
        return _weighted(components, ["generated_code payload must be an object"])

    scene_name = generated.get("scene_name")
    code = generated.get("code")
    language = generated.get("language", "python")
    if isinstance(scene_name, str) and scene_name and isinstance(code, str) and code and language == "python":
        components["schema"] = 1.0
    else:
        return _weighted(components, ["generated_code requires scene_name, code, and python language"])

    expected_scene = str(task.get("scene_name") or "")
    if expected_scene and scene_name != expected_scene:
        errors.append(f"scene_name mismatch: expected {expected_scene}, got {scene_name}")

    ast_result = validate_source(code)
    if ast_result["parsed"]:
        components["python_parse"] = 1.0
        scene_classes = discover_scene_classes(code)
        if scene_name in scene_classes and not errors:
            components["static_validation"] = 1.0
        elif scene_name not in scene_classes:
            errors.append(f"missing construct-bearing scene class {scene_name}")
        layout_score, layout_errors = layout_static_score(code)
        components["layout_static"] = layout_score
        errors.extend(layout_errors)
    errors.extend(ast_result["errors"])
    components["safety"] = 1.0 if not ast_result["unsafe"] else 0.0
    components["acceptance_terms"] = term_score([str(term) for term in task.get("acceptance_terms") or []], code)
    return _weighted(components, errors, scene_classes)


def extract_generated_code_payload(text: str) -> tuple[str | None, bool]:
    match = GENERATED_CODE_TAG_RE.search(text)
    if match:
        return match.group(1).strip(), True
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped, False
    return None, False


def validate_source(source: str) -> dict[str, Any]:
    errors: list[str] = []
    unsafe = False
    if len(source.encode("utf-8")) > 1_000_000:
        return {"parsed": False, "unsafe": True, "errors": ["source too large"]}
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"parsed": False, "unsafe": False, "errors": [f"syntax error: {exc.msg}"]}
    node_count = 0
    for node in ast.walk(tree):
        node_count += 1
        if node_count > 20_000:
            unsafe = True
            errors.append("AST too large")
            break
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for root in import_roots(node):
                if root in FORBIDDEN_IMPORT_ROOTS:
                    unsafe = True
                    errors.append(f"forbidden import: {root}")
                elif root not in ALLOWED_IMPORT_ROOTS:
                    unsafe = True
                    errors.append(f"import not allowed: {root}")
        elif isinstance(node, ast.Call):
            name = call_name(node.func)
            if name in FORBIDDEN_CALL_NAMES:
                unsafe = True
                errors.append(f"forbidden call: {name}")
    return {"parsed": True, "unsafe": unsafe, "errors": errors}


def discover_scene_classes(source: str) -> list[str]:
    tree = ast.parse(source)
    scenes: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases = {base_name(base).rsplit(".", 1)[-1] for base in node.bases if base_name(base)}
        if not (bases & SCENE_BASES or any(base.endswith("Scene") for base in bases)):
            continue
        has_construct = any(isinstance(child, ast.FunctionDef) and child.name == "construct" for child in node.body)
        if has_construct:
            scenes.append(node.name)
    return scenes


def layout_static_score(source: str) -> tuple[float, list[str]]:
    """Estimate text-crowding risk from Manim source without rendering."""

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return 0.0, [f"layout check skipped: syntax error: {exc.msg}"]

    annotate_parents(tree)
    name_methods = methods_by_name(tree)
    items = collect_text_layout_items(tree, name_methods)
    if not items:
        return 1.0, []

    warnings: list[str] = []
    penalty = 0.0
    for item in items:
        visible_chars = len(normalize_text(item.text))
        if visible_chars == 0:
            continue
        font_size = item.font_size or 48.0
        guarded = item.constructor == "Paragraph" or bool(item.methods & WIDTH_GUARD_METHODS)
        has_line_break = "\n" in item.text
        label = item.name or item.constructor

        if visible_chars >= 46 and font_size >= 34 and not guarded:
            penalty += 0.12
            warnings.append(f"layout risk: long high-font text without width guard: {label}")
        if visible_chars >= 80 and not (guarded or has_line_break):
            penalty += 0.10
            warnings.append(f"layout risk: very long single-line text: {label}")
        if item.constructor in {"MathTex", "Tex", "SingleStringMathTex"} and visible_chars >= 55 and font_size >= 30 and not guarded:
            penalty += 0.10
            warnings.append(f"layout risk: wide formula without scale_to_fit_width: {label}")

    fixed_overlay_count = count_call_names(tree, {"fix_in_frame", "add_fixed_in_frame_mobjects"})
    fadeout_count = count_call_names(tree, {"FadeOut", "ReplacementTransform", "Transform"})
    if len(items) >= 20:
        penalty += 0.06
        warnings.append("layout risk: many text/formula objects in one scene")
    if fixed_overlay_count >= 12:
        penalty += 0.08
        warnings.append("layout risk: high number of fixed-frame overlays")
    if len(items) >= 8 and fixed_overlay_count >= 4 and fadeout_count < max(2, fixed_overlay_count // 2):
        penalty += 0.15
        warnings.append("layout risk: many fixed-frame text overlays with limited cleanup")
    if len(items) >= 10 and fadeout_count < max(2, len(items) // 4):
        penalty += 0.12
        warnings.append("layout risk: many text objects with few FadeOut/Transform cleanups")

    dense_groups = count_dense_arranges(tree)
    if dense_groups:
        penalty += min(0.15, dense_groups * 0.06)
        warnings.append("layout risk: tight text/group arrangement buffer")

    return round(max(0.0, 1.0 - min(0.85, penalty)), 6), warnings


def annotate_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "_parent", parent)


def methods_by_name(tree: ast.AST) -> dict[str, set[str]]:
    methods: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if isinstance(node.func.value, ast.Name):
            methods.setdefault(node.func.value.id, set()).add(node.func.attr)
    return methods


def collect_text_layout_items(tree: ast.AST, name_methods: dict[str, set[str]]) -> list[TextLayoutItem]:
    items: list[TextLayoutItem] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        constructor = call_name(node.func)
        if constructor not in TEXT_CONSTRUCTORS:
            continue
        name = assigned_name(node)
        methods = call_chain_methods(node)
        if name:
            methods |= name_methods.get(name, set())
        items.append(
            TextLayoutItem(
                constructor=constructor,
                text=literal_text(node),
                font_size=font_size_arg(node),
                methods=methods,
                name=name,
            )
        )
    return items


def assigned_name(node: ast.AST) -> str | None:
    current = node
    parent = getattr(current, "_parent", None)
    while parent is not None:
        if isinstance(parent, ast.Assign):
            for target in parent.targets:
                if isinstance(target, ast.Name):
                    return target.id
            return None
        current = parent
        parent = getattr(current, "_parent", None)
    return None


def call_chain_methods(node: ast.AST) -> set[str]:
    methods: set[str] = set()
    current = node
    parent = getattr(current, "_parent", None)
    while parent is not None:
        if isinstance(parent, ast.Attribute) and parent.value is current:
            methods.add(parent.attr)
            current = parent
            parent = getattr(current, "_parent", None)
            continue
        if isinstance(parent, ast.Call) and parent.func is current:
            current = parent
            parent = getattr(current, "_parent", None)
            continue
        break
    return methods


def literal_text(node: ast.Call) -> str:
    parts = []
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            parts.append(arg.value)
    return " ".join(parts)


def font_size_arg(node: ast.Call) -> float | None:
    for keyword in node.keywords:
        if keyword.arg == "font_size":
            return numeric_literal(keyword.value)
    return None


def numeric_literal(node: ast.AST) -> float | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        value = numeric_literal(node.operand)
        return -value if value is not None else None
    return None


def count_call_names(tree: ast.AST, names: set[str]) -> int:
    count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node.func)
        if name and name.rsplit(".", 1)[-1] in names:
            count += 1
    return count


def count_dense_arranges(tree: ast.AST) -> int:
    dense = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node.func)
        if not name or name.rsplit(".", 1)[-1] != "arrange":
            continue
        for keyword in node.keywords:
            if keyword.arg == "buff":
                value = numeric_literal(keyword.value)
                if value is not None and value < 0.18:
                    dense += 1
    return dense


def import_roots(node: ast.Import | ast.ImportFrom) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name.split(".", 1)[0] for alias in node.names]
    return ["" if node.module is None else node.module.split(".", 1)[0]]


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def base_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = base_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Subscript):
        return base_name(node.value)
    return None


def term_score(terms: list[str], text: str) -> float:
    terms = [term for term in terms if term.strip()]
    if not terms:
        return 1.0
    normalized = normalize_text(text)
    hits = sum(1 for term in terms if normalize_text(term) in normalized)
    return hits / len(terms)


def normalize_text(text: str) -> str:
    return " ".join(str(text).casefold().split())


def _weighted(components: dict[str, float], errors: list[str], scene_classes: list[str] | None = None) -> ScoreResult:
    score = sum(components[key] * WEIGHTS[key] for key in WEIGHTS)
    return ScoreResult(round(score, 6), dict(components), errors, scene_classes or [])
