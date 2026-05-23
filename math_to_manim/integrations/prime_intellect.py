"""Prime Intellect Verifiers export and scoring helpers."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Iterable

from math_to_manim.schemas import GeneratedCode
from math_to_manim.tools import discover_scene_classes, validate_python_source


REPAIR_TASK_SCHEMA_VERSION = "m2m2.pi_repair_task.v1"
GENERATED_CODE_TAG_RE = re.compile(r"<generated_code>\s*(.*?)\s*</generated_code>", re.DOTALL | re.IGNORECASE)
TEXT_CONSTRUCTORS = {"MarkupText", "MathTex", "Paragraph", "SingleStringMathTex", "Tex", "Text"}
WIDTH_GUARD_METHODS = {"scale_to_fit_width", "set_width"}
DEFAULT_REPAIR_INSTRUCTIONS = (
    "Repair the generated Manim scene while preserving the requested educational intent. "
    "Return exactly one <generated_code> block containing JSON with scene_name, language, code, "
    "dependencies, manim_version, source_spec_id, checksum, and metadata fields. Do not shell out, "
    "read local files, access the network, or use external assets."
)


@dataclass(frozen=True)
class RepairTaskExportResult:
    output_path: str
    written: int
    skipped: int
    skipped_reasons: dict[str, int] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "output_path": self.output_path,
            "written": self.written,
            "skipped": self.skipped,
            "skipped_reasons": dict(sorted(self.skipped_reasons.items())),
        }


@dataclass(frozen=True)
class RepairScore:
    score: float
    components: dict[str, float]
    errors: list[str] = field(default_factory=list)
    scene_classes: list[str] = field(default_factory=list)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "components": self.components,
            "errors": self.errors,
            "scene_classes": self.scene_classes,
        }


@dataclass(frozen=True)
class TextLayoutItem:
    constructor: str
    text: str
    font_size: float | None
    methods: set[str] = field(default_factory=set)
    name: str | None = None


def iter_repair_tasks(runs_dir: str | Path, *, limit: int | None = None) -> Iterable[dict[str, Any]]:
    """Yield Prime-compatible repair tasks from complete M2M2 run bundles."""

    count = 0
    for run_dir in sorted(Path(runs_dir).iterdir()):
        if not run_dir.is_dir():
            continue
        try:
            task = build_repair_task(run_dir)
        except ValueError:
            continue
        yield task
        count += 1
        if limit is not None and count >= limit:
            break


def export_repair_tasks(runs_dir: str | Path, output: str | Path, *, limit: int | None = None) -> RepairTaskExportResult:
    """Write M2M2 repair tasks as JSONL for a Prime Intellect environment."""

    runs_root = Path(runs_dir)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    skipped_reasons: dict[str, int] = {}
    with output_path.open("w", encoding="utf-8") as handle:
        for run_dir in sorted(runs_root.iterdir()):
            if not run_dir.is_dir():
                continue
            if limit is not None and written >= limit:
                break
            try:
                task = build_repair_task(run_dir)
            except ValueError as exc:
                skipped += 1
                reason = str(exc)
                skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1
                continue
            handle.write(json.dumps(task, sort_keys=True, default=str) + "\n")
            written += 1
    return RepairTaskExportResult(str(output_path), written, skipped, skipped_reasons)


def build_repair_task(run_dir: str | Path) -> dict[str, Any]:
    """Build one repair-task record from a run bundle."""

    root = Path(run_dir)
    required = ["request.json", "scene_spec.json", "generated_code.json", "generated_scene.py", "validation_report.json"]
    missing = [name for name in required if not (root / name).exists()]
    if missing:
        raise ValueError(f"missing required artifacts: {', '.join(missing)}")

    request = _read_json(root / "request.json")
    scene_spec = _read_json(root / "scene_spec.json")
    generated_code = _read_json(root / "generated_code.json")
    generated_code["code"] = (root / "generated_scene.py").read_text(encoding="utf-8")
    validation = _read_json(root / "validation_report.json")
    render = _read_json(root / "render_result.json") if (root / "render_result.json").exists() else {}
    review = _read_json(root / "review_report.json") if (root / "review_report.json").exists() else {}

    prompt = str(request.get("prompt") or "")
    scene_name = str(scene_spec.get("scene_name") or generated_code.get("scene_name") or "")
    if not prompt or not scene_name:
        raise ValueError("missing prompt or scene_name")

    return {
        "schema_version": REPAIR_TASK_SCHEMA_VERSION,
        "task_id": root.name,
        "source_run_dir": str(root),
        "prompt": prompt,
        "audience": request.get("target_audience"),
        "style": request.get("style"),
        "duration_seconds": request.get("duration_seconds"),
        "scene_name": scene_name,
        "acceptance_terms": _acceptance_terms(request, scene_spec),
        "scene_spec": scene_spec,
        "generated_code": generated_code,
        "evidence": {
            "validation": _validation_evidence(validation),
            "render": _render_evidence(render),
            "review": _review_evidence(review),
        },
        "instructions": DEFAULT_REPAIR_INSTRUCTIONS,
        "metadata": {
            "source": "math_to_manim",
            "reward_mode": "static_no_render",
        },
    }


def extract_generated_code_payload(text: str) -> tuple[str | None, bool]:
    """Return JSON payload text and whether it came from the required tags."""

    match = GENERATED_CODE_TAG_RE.search(text)
    if match:
        return match.group(1).strip(), True
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped, False
    return None, False


def score_generated_code_completion(task: dict[str, Any], completion: str) -> RepairScore:
    """Score a repair completion using fast static checks."""

    payload, used_tags = extract_generated_code_payload(completion)
    components = {
        "format": 1.0 if used_tags else 0.0,
        "schema": 0.0,
        "python_parse": 0.0,
        "static_validation": 0.0,
        "safety": 0.0,
        "acceptance_terms": 0.0,
        "layout_static": 0.0,
    }
    errors: list[str] = []
    scene_classes: list[str] = []
    if payload is None:
        return _weighted_score(components, ["missing generated_code block"])

    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        return _weighted_score(components, [f"invalid generated_code JSON: {exc.msg}"])
    if not isinstance(raw, dict):
        return _weighted_score(components, ["generated_code payload must be a JSON object"])

    try:
        generated = GeneratedCode.model_validate(raw)
    except Exception as exc:
        return _weighted_score(components, [f"generated_code schema error: {exc}"])

    components["schema"] = 1.0
    expected_scene = str(task.get("scene_name") or "")
    if expected_scene and generated.scene_name != expected_scene:
        errors.append(f"scene_name mismatch: expected {expected_scene}, got {generated.scene_name}")

    ast_report = validate_python_source(generated.code)
    if ast_report.ok:
        components["python_parse"] = 1.0
        scene_classes = [scene.name for scene in discover_scene_classes(generated.code, require_construct=True)]
        if generated.scene_name in scene_classes and not errors:
            components["static_validation"] = 1.0
        elif generated.scene_name not in scene_classes:
            errors.append(f"missing construct-bearing scene class {generated.scene_name}")
        layout_score, layout_errors = _layout_static_score(generated.code)
        components["layout_static"] = layout_score
        errors.extend(layout_errors)
    else:
        errors.extend(f"{issue.code}: {issue.message}" for issue in ast_report.issues)

    components["safety"] = 1.0 if not _has_unsafe_code_errors(ast_report) else 0.0
    terms = [str(term) for term in task.get("acceptance_terms") or [] if str(term).strip()]
    components["acceptance_terms"] = _term_score(terms, generated.code)
    return _weighted_score(components, errors, scene_classes)


def _weighted_score(components: dict[str, float], errors: list[str], scene_classes: list[str] | None = None) -> RepairScore:
    weights = {
        "format": 0.08,
        "schema": 0.12,
        "python_parse": 0.12,
        "static_validation": 0.22,
        "safety": 0.13,
        "acceptance_terms": 0.15,
        "layout_static": 0.18,
    }
    score = sum(components[key] * weights[key] for key in weights)
    return RepairScore(round(score, 6), components, errors, scene_classes or [])


def _layout_static_score(source: str) -> tuple[float, list[str]]:
    """Estimate text-crowding risk from Manim source without rendering."""

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return 0.0, [f"layout check skipped: syntax error: {exc.msg}"]

    _annotate_parents(tree)
    name_methods = _methods_by_name(tree)
    items = _collect_text_layout_items(tree, name_methods)
    if not items:
        return 1.0, []

    warnings: list[str] = []
    penalty = 0.0
    for item in items:
        visible_chars = len(_normalize_text(item.text))
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

    fixed_overlay_count = _count_call_names(tree, {"fix_in_frame", "add_fixed_in_frame_mobjects"})
    fadeout_count = _count_call_names(tree, {"FadeOut", "ReplacementTransform", "Transform"})
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

    dense_groups = _count_dense_arranges(tree)
    if dense_groups:
        penalty += min(0.15, dense_groups * 0.06)
        warnings.append("layout risk: tight text/group arrangement buffer")

    return round(max(0.0, 1.0 - min(0.85, penalty)), 6), warnings


def _annotate_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "_parent", parent)


def _methods_by_name(tree: ast.AST) -> dict[str, set[str]]:
    methods: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if isinstance(node.func.value, ast.Name):
            methods.setdefault(node.func.value.id, set()).add(node.func.attr)
    return methods


def _collect_text_layout_items(tree: ast.AST, name_methods: dict[str, set[str]]) -> list[TextLayoutItem]:
    items: list[TextLayoutItem] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        constructor = _call_name(node.func)
        if constructor not in TEXT_CONSTRUCTORS:
            continue
        name = _assigned_name(node)
        methods = _call_chain_methods(node)
        if name:
            methods |= name_methods.get(name, set())
        items.append(
            TextLayoutItem(
                constructor=constructor,
                text=_literal_text(node),
                font_size=_font_size_arg(node),
                methods=methods,
                name=name,
            )
        )
    return items


def _assigned_name(node: ast.AST) -> str | None:
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


def _call_chain_methods(node: ast.AST) -> set[str]:
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


def _literal_text(node: ast.Call) -> str:
    parts = []
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            parts.append(arg.value)
    return " ".join(parts)


def _font_size_arg(node: ast.Call) -> float | None:
    for keyword in node.keywords:
        if keyword.arg == "font_size":
            return _numeric_literal(keyword.value)
    return None


def _numeric_literal(node: ast.AST) -> float | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        value = _numeric_literal(node.operand)
        return -value if value is not None else None
    return None


def _count_call_names(tree: ast.AST, names: set[str]) -> int:
    count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name and name.rsplit(".", 1)[-1] in names:
            count += 1
    return count


def _count_dense_arranges(tree: ast.AST) -> int:
    dense = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if not name or name.rsplit(".", 1)[-1] != "arrange":
            continue
        for keyword in node.keywords:
            if keyword.arg == "buff":
                value = _numeric_literal(keyword.value)
                if value is not None and value < 0.18:
                    dense += 1
    return dense


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _has_unsafe_code_errors(ast_report: Any) -> bool:
    unsafe_codes = {"forbidden-import", "import-not-allowed", "forbidden-call", "source-too-large", "ast-too-large"}
    return any(issue.code in unsafe_codes for issue in ast_report.issues)


def _term_score(terms: list[str], text: str) -> float:
    if not terms:
        return 1.0
    normalized = _normalize_text(text)
    hits = sum(1 for term in terms if _normalize_text(term) in normalized)
    return hits / len(terms)


def _acceptance_terms(request: dict[str, Any], scene_spec: dict[str, Any]) -> list[str]:
    metadata = request.get("metadata") if isinstance(request.get("metadata"), dict) else {}
    configured = metadata.get("acceptance_terms") if isinstance(metadata, dict) else None
    if isinstance(configured, list) and configured:
        return [str(term) for term in configured if str(term).strip()]
    prompt = str(request.get("prompt") or scene_spec.get("metadata", {}).get("original_prompt") or "")
    terms = []
    stop_words = {
        "about",
        "animation",
        "create",
        "explain",
        "make",
        "show",
        "the",
        "this",
        "using",
        "what",
        "when",
        "where",
        "why",
        "with",
    }
    for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", prompt):
        key = token.casefold()
        if key in stop_words or key in {term.casefold() for term in terms}:
            continue
        terms.append(token)
        if len(terms) >= 8:
            break
    return terms


def _validation_evidence(report: dict[str, Any]) -> dict[str, Any]:
    issues = report.get("issues") if isinstance(report.get("issues"), list) else []
    return {
        "status": report.get("status"),
        "summary": report.get("summary"),
        "issues": issues[:8],
        "metadata": report.get("metadata") or {},
    }


def _render_evidence(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result.get("status"),
        "scene_name": result.get("scene_name"),
        "stderr_tail": str(result.get("stderr") or "")[-2000:],
        "stdout_tail": str(result.get("stdout") or "")[-1000:],
        "metadata": result.get("metadata") or {},
    }


def _review_evidence(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "approved": report.get("approved"),
        "score": report.get("score"),
        "observations": (report.get("observations") or [])[:12],
        "issues": (report.get("issues") or [])[:8],
        "recommendations": (report.get("recommendations") or [])[:8],
        "metadata": {
            "render_integrity_passed": (report.get("metadata") or {}).get("render_integrity_passed")
            if isinstance(report.get("metadata"), dict)
            else None
        },
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_text(text: str) -> str:
    return " ".join(str(text).casefold().split())
