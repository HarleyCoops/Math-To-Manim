"""Static candidate checks that run before sandbox execution."""

from __future__ import annotations

import ast
import hashlib

from pydantic import Field

from .schemas import NonEmpty, Sha256, StrictFrozenModel

DEFAULT_MAX_BYTES = 256_000
DEFAULT_MAX_AST_NODES = 20_000
ALLOWED_IMPORT_ROOTS = frozenset({"manim", "math", "numpy"})
SCENE_BASES = frozenset(
    {
        "Scene",
        "ThreeDScene",
        "MovingCameraScene",
        "ZoomedScene",
        "LinearTransformationScene",
    }
)
UNSAFE_CALLS = frozenset(
    {
        "__import__",
        "breakpoint",
        "compile",
        "eval",
        "exec",
        "input",
        "open",
    }
)
UNSAFE_ATTRIBUTES = frozenset(
    {
        "chmod",
        "connect",
        "dump",
        "dumps",
        "load",
        "loads",
        "open",
        "popen",
        "read_bytes",
        "read_text",
        "remove",
        "rename",
        "replace",
        "request",
        "rmdir",
        "run",
        "socket",
        "system",
        "unlink",
        "write_bytes",
        "write_text",
    }
)


class SafetyViolation(StrictFrozenModel):
    code: NonEmpty
    message: NonEmpty
    line: int | None = Field(default=None, ge=1)


class SafetyReport(StrictFrozenModel):
    source_sha256: Sha256
    byte_count: int = Field(ge=0)
    ast_node_count: int = Field(ge=0)
    violations: tuple[SafetyViolation, ...]

    @property
    def valid(self) -> bool:
        return not self.violations


class CandidateSafetyError(ValueError):
    def __init__(self, report: SafetyReport):
        self.report = report
        summary = ", ".join(item.code for item in report.violations)
        super().__init__(f"candidate source is unsafe: {summary}")


def _name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return None


def _violation(
    code: str,
    message: str,
    node: ast.AST | None = None,
) -> SafetyViolation:
    return SafetyViolation(
        code=code,
        message=message,
        line=getattr(node, "lineno", None),
    )


def _is_self_camera_animate(node: ast.Attribute) -> bool:
    if node.attr != "animate" or not isinstance(node.value, ast.Attribute):
        return False
    camera = node.value
    return (
        camera.attr == "camera"
        and isinstance(camera.value, ast.Name)
        and camera.value.id == "self"
    )


def validate_candidate_source(
    source: str,
    *,
    expected_scene_name: str,
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_nodes: int = DEFAULT_MAX_AST_NODES,
) -> SafetyReport:
    """Return deterministic violations without executing candidate code."""

    encoded = source.encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    if len(encoded) > max_bytes:
        return SafetyReport(
            source_sha256=digest,
            byte_count=len(encoded),
            ast_node_count=0,
            violations=(
                _violation(
                    "source_too_large",
                    f"source exceeds {max_bytes} bytes",
                ),
            ),
        )

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return SafetyReport(
            source_sha256=digest,
            byte_count=len(encoded),
            ast_node_count=0,
            violations=(
                SafetyViolation(
                    code="syntax_error",
                    message=exc.msg,
                    line=exc.lineno,
                ),
            ),
        )

    nodes = list(ast.walk(tree))
    violations: list[SafetyViolation] = []
    if len(nodes) > max_nodes:
        violations.append(
            _violation(
                "ast_too_large",
                f"AST exceeds {max_nodes} nodes",
            )
        )

    expected_class: ast.ClassDef | None = None
    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root not in ALLOWED_IMPORT_ROOTS:
                    violations.append(
                        _violation(
                            "unsafe_import",
                            f"import root is not allowed: {root}",
                            node,
                        )
                    )
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if node.level or root not in ALLOWED_IMPORT_ROOTS:
                violations.append(
                    _violation(
                        "unsafe_import",
                        f"import root is not allowed: {root or 'relative'}",
                        node,
                    )
                )
        elif isinstance(node, ast.Call):
            function = _name(node.func)
            final_name = function.rsplit(".", 1)[-1] if function else ""
            if final_name in UNSAFE_CALLS or (
                isinstance(node.func, ast.Attribute)
                and final_name in UNSAFE_ATTRIBUTES
            ):
                violations.append(
                    _violation(
                        "unsafe_call",
                        f"call is not allowed: {function or '<dynamic>'}",
                        node,
                    )
                )
        elif isinstance(node, ast.Attribute) and _is_self_camera_animate(node):
            violations.append(
                _violation(
                    "three_d_camera_animate",
                    "use move_camera or set_camera_orientation instead of "
                    "self.camera.animate",
                    node,
                )
            )
        elif isinstance(node, ast.ClassDef) and node.name == expected_scene_name:
            expected_class = node

    if expected_class is None:
        violations.append(
            _violation(
                "missing_scene",
                f"expected scene class is missing: {expected_scene_name}",
            )
        )
    else:
        bases = {_name(base) for base in expected_class.bases}
        if not any(
            base and base.rsplit(".", 1)[-1] in SCENE_BASES for base in bases
        ):
            violations.append(
                _violation(
                    "invalid_scene_base",
                    f"{expected_scene_name} must inherit a supported Manim scene",
                    expected_class,
                )
            )
        construct = next(
            (
                item
                for item in expected_class.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name == "construct"
            ),
            None,
        )
        if construct is None:
            violations.append(
                _violation(
                    "missing_construct",
                    f"{expected_scene_name} has no construct method",
                    expected_class,
                )
            )

    deduplicated = {
        (item.code, item.line, item.message): item for item in violations
    }
    ordered = tuple(
        sorted(
            deduplicated.values(),
            key=lambda item: (item.line or 0, item.code, item.message),
        )
    )
    return SafetyReport(
        source_sha256=digest,
        byte_count=len(encoded),
        ast_node_count=len(nodes),
        violations=ordered,
    )


def assert_safe_candidate(
    source: str,
    *,
    expected_scene_name: str,
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_nodes: int = DEFAULT_MAX_AST_NODES,
) -> str:
    report = validate_candidate_source(
        source,
        expected_scene_name=expected_scene_name,
        max_bytes=max_bytes,
        max_nodes=max_nodes,
    )
    if not report.valid:
        raise CandidateSafetyError(report)
    return source


__all__ = [
    "ALLOWED_IMPORT_ROOTS",
    "CandidateSafetyError",
    "SafetyReport",
    "SafetyViolation",
    "assert_safe_candidate",
    "validate_candidate_source",
]
