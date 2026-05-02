"""Python AST validation for generated scene code."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Literal


Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class ValidationIssue:
    """One AST validation issue."""

    severity: Severity
    code: str
    message: str
    lineno: int = 0
    col_offset: int = 0


@dataclass(frozen=True)
class ValidationResult:
    """Result returned by :func:`validate_python_source`."""

    ok: bool
    issues: tuple[ValidationIssue, ...] = ()
    tree: ast.Module | None = field(default=None, repr=False, compare=False)

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "warning")


@dataclass(frozen=True)
class PythonAstPolicy:
    """Policy knobs for AST validation."""

    allowed_import_roots: tuple[str, ...] | None = (
        "collections",
        "dataclasses",
        "functools",
        "itertools",
        "manim",
        "math",
        "numpy",
        "typing",
    )
    forbidden_import_roots: tuple[str, ...] = (
        "builtins",
        "importlib",
        "os",
        "pathlib",
        "runpy",
        "shutil",
        "socket",
        "subprocess",
        "sys",
    )
    forbidden_call_names: tuple[str, ...] = (
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
    )
    max_source_bytes: int = 1_000_000
    max_ast_nodes: int = 20_000


DEFAULT_SCENE_POLICY = PythonAstPolicy()
RELAXED_PYTHON_POLICY = PythonAstPolicy(allowed_import_roots=None)


def validate_python_source(
    source: str,
    *,
    filename: str = "<generated>",
    policy: PythonAstPolicy = DEFAULT_SCENE_POLICY,
) -> ValidationResult:
    """Parse and validate Python source without executing it."""

    issues: list[ValidationIssue] = []
    if len(source.encode("utf-8")) > policy.max_source_bytes:
        issues.append(
            ValidationIssue(
                "error",
                "source-too-large",
                f"Source exceeds {policy.max_source_bytes} bytes",
            )
        )
        return ValidationResult(False, tuple(issues), None)

    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        issues.append(
            ValidationIssue(
                "error",
                "syntax-error",
                exc.msg,
                lineno=exc.lineno or 0,
                col_offset=exc.offset or 0,
            )
        )
        return ValidationResult(False, tuple(issues), None)

    node_count = 0
    for node in ast.walk(tree):
        node_count += 1
        if node_count > policy.max_ast_nodes:
            issues.append(
                ValidationIssue(
                    "error",
                    "ast-too-large",
                    f"AST exceeds {policy.max_ast_nodes} nodes",
                    lineno=getattr(node, "lineno", 0),
                    col_offset=getattr(node, "col_offset", 0),
                )
            )
            break

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            issues.extend(_validate_import(node, policy))
        elif isinstance(node, ast.Call):
            call_name = _call_name(node.func)
            if call_name in policy.forbidden_call_names:
                issues.append(
                    ValidationIssue(
                        "error",
                        "forbidden-call",
                        f"Call to '{call_name}' is not allowed",
                        lineno=getattr(node, "lineno", 0),
                        col_offset=getattr(node, "col_offset", 0),
                    )
                )

    return ValidationResult(not any(issue.severity == "error" for issue in issues), tuple(issues), tree)


def validate_python_ast(
    tree: ast.Module,
    *,
    policy: PythonAstPolicy = DEFAULT_SCENE_POLICY,
) -> ValidationResult:
    """Validate an existing Python AST module."""

    return validate_python_source(ast.unparse(tree), policy=policy)


def _validate_import(node: ast.Import | ast.ImportFrom, policy: PythonAstPolicy) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    roots = _import_roots(node)
    for root in roots:
        if root in policy.forbidden_import_roots:
            issues.append(
                ValidationIssue(
                    "error",
                    "forbidden-import",
                    f"Import root '{root}' is not allowed",
                    lineno=getattr(node, "lineno", 0),
                    col_offset=getattr(node, "col_offset", 0),
                )
            )
        elif policy.allowed_import_roots is not None and root not in policy.allowed_import_roots:
            issues.append(
                ValidationIssue(
                    "error",
                    "import-not-allowed",
                    f"Import root '{root}' is not in the allowed import list",
                    lineno=getattr(node, "lineno", 0),
                    col_offset=getattr(node, "col_offset", 0),
                )
            )
    return tuple(issues)


def _import_roots(node: ast.Import | ast.ImportFrom) -> tuple[str, ...]:
    if isinstance(node, ast.Import):
        return tuple(alias.name.split(".", 1)[0] for alias in node.names)
    if node.module is None:
        return ("",)
    return (node.module.split(".", 1)[0],)


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent_name = _call_name(node.value)
        if parent_name:
            return f"{parent_name}.{node.attr}"
        return node.attr
    return None
