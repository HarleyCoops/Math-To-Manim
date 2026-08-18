"""Static scene, LaTeX, and MathTex checks for generated Mythos films.

These replace the retired Hermes substring heuristics. Scene discovery and
MathTex raw-string policy are AST-based. LaTeX is tokenized and parsed as a
document of commands, groups, and environments — not counted braces. ``chktex``
is used when present and treated as an optional second opinion.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from mythos.settings import PipelineSettings

# Manim Community scene bases all end in ``Scene``. Matching that suffix via
# AST (not the substring ``"Scene)"``) is what keeps ThreeDScene, ZoomedScene,
# LinearTransformationScene, and similar subclasses from false-failing.
_SCENE_SUFFIX = "Scene"
_TEX_CTORS = frozenset({"MathTex", "Tex"})
_COMMAND_ARITY = {
    "frac": 2,
    "dfrac": 2,
    "tfrac": 2,
    "binom": 2,
    "dbinom": 2,
    "tbinom": 2,
    "overset": 2,
    "underset": 2,
    "sqrt": 1,
    "overline": 1,
    "underline": 1,
    "widehat": 1,
    "widetilde": 1,
    "hat": 1,
    "tilde": 1,
    "bar": 1,
    "vec": 1,
    "dot": 1,
    "ddot": 1,
    "mathbf": 1,
    "mathrm": 1,
    "mathit": 1,
    "mathsf": 1,
    "mathtt": 1,
    "mathbb": 1,
    "mathcal": 1,
    "mathscr": 1,
    "mathfrak": 1,
    "text": 1,
    "textrm": 1,
    "textbf": 1,
    "textit": 1,
    "emph": 1,
    "operatorname": 1,
    "mbox": 1,
}


@dataclass(frozen=True)
class LatexIssue:
    line: int
    severity: str
    message: str

    def as_text(self) -> str:
        return f"L{self.line}: {self.message}"


@dataclass
class LatexReport:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    issues: list[LatexIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "issues": [
                {
                    "line": issue.line,
                    "severity": issue.severity,
                    "message": issue.message,
                }
                for issue in self.issues
            ],
        }


@dataclass
class SceneCheckReport:
    valid: bool
    scene_names: list[str]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    latex: LatexReport | None = None
    complexity: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "scene_names": list(self.scene_names),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "suggestions": list(self.suggestions),
            "latex": None if self.latex is None else self.latex.to_dict(),
            "complexity": dict(self.complexity),
        }


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _base_name(node: ast.AST) -> str | None:
    return _call_name(node)


def discover_scene_classes(tree: ast.AST) -> list[str]:
    """Return class names whose bases look like a Manim Scene subclass."""
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for base in node.bases:
            name = _base_name(base)
            if name and name.endswith(_SCENE_SUFFIX):
                names.append(node.name)
                break
    return names


def find_scene_class(code: str) -> str:
    """Return the first Scene subclass name, or raise if none exist."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise RuntimeError(f"Generated code is not valid Python: {exc}") from exc
    names = discover_scene_classes(tree)
    if not names:
        raise RuntimeError("Generated code defines no Scene subclass")
    return names[0]


def _is_raw_string_literal(source: str, node: ast.Constant) -> bool:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return True
    return segment.lstrip().startswith(("r", "R"))


def non_raw_tex_calls(source: str, tree: ast.AST) -> list[tuple[int, str]]:
    """Locate MathTex/Tex calls whose first positional arg is a non-raw string.

    f-strings (JoinedStr) are left alone — they cannot be raw in the usual
    sense and are often used to splice already-validated fragments.
    """
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name not in _TEX_CTORS or not node.args:
            continue
        arg = node.args[0]
        if isinstance(arg, ast.JoinedStr):
            continue
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            if not _is_raw_string_literal(source, arg):
                hits.append((arg.lineno, name))
    return hits


def extract_tex_fragments(source: str, tree: ast.AST) -> list[tuple[int, str]]:
    fragments: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _call_name(node.func) not in _TEX_CTORS:
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                fragments.append((arg.lineno, arg.value))
    return fragments


def scene_complexity(tree: ast.AST) -> dict[str, int]:
    tex_calls = 0
    waits = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name in _TEX_CTORS:
            tex_calls += 1
        elif name == "wait":
            waits += 1
    return {
        "scene_classes": len(discover_scene_classes(tree)),
        "tex_calls": tex_calls,
        "wait_calls": waits,
    }


def _line_at(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _skip_comment(text: str, index: int) -> int:
    newline = text.find("\n", index)
    return len(text) if newline == -1 else newline


def tokenize_latex(text: str) -> list[tuple[str, str, int]]:
    """Return ``(kind, value, line)`` tokens for a MathTex/Tex fragment."""
    tokens: list[tuple[str, str, int]] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        line = _line_at(text, index)
        if char == "%":
            index = _skip_comment(text, index)
            continue
        if char == "{":
            tokens.append(("LBRACE", char, line))
            index += 1
            continue
        if char == "}":
            tokens.append(("RBRACE", char, line))
            index += 1
            continue
        if char == "[":
            tokens.append(("LBRACK", char, line))
            index += 1
            continue
        if char == "]":
            tokens.append(("RBRACK", char, line))
            index += 1
            continue
        if text.startswith("$$", index):
            tokens.append(("MATH_DISPLAY", "$$", line))
            index += 2
            continue
        if char == "$":
            tokens.append(("MATH_INLINE", "$", line))
            index += 1
            continue
        if char != "\\":
            start = index
            index += 1
            while index < length and text[index] not in "{}[]$\\%":
                index += 1
            tokens.append(("TEXT", text[start:index], line))
            continue
        if index + 1 >= length:
            tokens.append(("COMMAND", "\\", line))
            break
        nxt = text[index + 1]
        if text.startswith(r"\begin", index) and (
            index + 6 == length or not text[index + 6].isalpha()
        ):
            tokens.append(("BEGIN", r"\begin", line))
            index += 6
            continue
        if text.startswith(r"\end", index) and (
            index + 4 == length or not text[index + 4].isalpha()
        ):
            tokens.append(("END", r"\end", line))
            index += 4
            continue
        if nxt in "()[]":
            tokens.append(("MATH_PAIR", "\\" + nxt, line))
            index += 2
            continue
        if nxt.isalpha():
            end = index + 1
            while end < length and text[end].isalpha():
                end += 1
            tokens.append(("COMMAND", text[index + 1 : end], line))
            index = end
            continue
        tokens.append(("COMMAND", nxt, line))
        index += 2
    return tokens


def _read_group_name(tokens: list[tuple[str, str, int]], start: int) -> tuple[str | None, int]:
    if start >= len(tokens) or tokens[start][0] != "LBRACE":
        return None, start
    depth = 0
    name_parts: list[str] = []
    index = start
    while index < len(tokens):
        kind, value, _ = tokens[index]
        if kind == "LBRACE":
            depth += 1
        elif kind == "RBRACE":
            depth -= 1
            if depth == 0:
                name = "".join(name_parts).strip()
                return (name or None), index + 1
        elif depth == 1 and kind in {"TEXT", "COMMAND"}:
            name_parts.append(value)
        index += 1
    return None, start


def parse_latex(text: str, *, math_fragment: bool = True) -> list[LatexIssue]:
    """Parse a LaTeX fragment and return structural issues with line numbers."""
    tokens = tokenize_latex(text)
    issues: list[LatexIssue] = []
    braces: list[int] = []
    brackets: list[int] = []
    environments: list[tuple[str, int]] = []
    math_inline = 0
    math_display = 0
    math_pairs: list[tuple[str, int]] = []
    index = 0

    def peek_kind() -> str | None:
        if index >= len(tokens):
            return None
        return tokens[index][0]

    def consume_required_group(command: str, line: int) -> None:
        nonlocal index
        if peek_kind() is None:
            issues.append(LatexIssue(line, "error", f"\\{command} is missing a required {{...}} argument"))
            return
        if peek_kind() == "LBRACK":
            # optional argument; consume until matching RBRACK
            depth = 0
            start_line = tokens[index][2]
            while index < len(tokens):
                kind, _, tok_line = tokens[index]
                index += 1
                if kind == "LBRACK":
                    depth += 1
                elif kind == "RBRACK":
                    depth -= 1
                    if depth == 0:
                        break
            else:
                issues.append(LatexIssue(start_line, "error", f"\\{command} has an unclosed optional argument"))
        if peek_kind() == "TEXT" and not tokens[index][1].strip():
            index += 1
        if peek_kind() == "COMMAND":
            index += 1
            return
        if peek_kind() == "TEXT" and tokens[index][1].strip():
            index += 1
            return
        if peek_kind() != "LBRACE":
            issues.append(LatexIssue(line, "error", f"\\{command} is missing a required {{...}} argument"))
            return
        start_line = tokens[index][2]
        depth = 0
        empty = True
        index += 1
        depth = 1
        while index < len(tokens) and depth:
            kind, value, _ = tokens[index]
            if kind == "LBRACE":
                depth += 1
                empty = False
            elif kind == "RBRACE":
                depth -= 1
            elif kind == "TEXT":
                if value.strip():
                    empty = False
            else:
                empty = False
            index += 1
        if depth:
            issues.append(LatexIssue(start_line, "error", f"\\{command} has an unclosed required argument"))
        elif empty:
            issues.append(LatexIssue(start_line, "error", f"\\{command} has an empty required argument"))

    while index < len(tokens):
        kind, value, line = tokens[index]
        if kind == "LBRACE":
            braces.append(line)
            index += 1
            continue
        if kind == "RBRACE":
            if braces:
                braces.pop()
            else:
                issues.append(LatexIssue(line, "error", "unmatched closing brace"))
            index += 1
            continue
        if kind == "LBRACK":
            brackets.append(line)
            index += 1
            continue
        if kind == "RBRACK":
            if brackets:
                brackets.pop()
            else:
                issues.append(LatexIssue(line, "warning", "unmatched closing bracket"))
            index += 1
            continue
        if kind == "MATH_INLINE":
            math_inline += 1
            index += 1
            continue
        if kind == "MATH_DISPLAY":
            math_display += 1
            index += 1
            continue
        if kind == "MATH_PAIR":
            closer = {r"\(": r"\)", r"\[": r"\]"}.get(value)
            if closer:
                math_pairs.append((closer, line))
            else:
                if math_pairs and math_pairs[-1][0] == value:
                    math_pairs.pop()
                else:
                    issues.append(LatexIssue(line, "error", f"unmatched math delimiter {value}"))
            index += 1
            continue
        if kind == "BEGIN":
            index += 1
            env, index = _read_group_name(tokens, index)
            if env is None:
                issues.append(LatexIssue(line, "error", r"\begin is missing an environment name"))
            else:
                environments.append((env, line))
            continue
        if kind == "END":
            index += 1
            env, index = _read_group_name(tokens, index)
            if env is None:
                issues.append(LatexIssue(line, "error", r"\end is missing an environment name"))
            elif not environments:
                issues.append(LatexIssue(line, "error", f"orphan \\end{{{env}}}"))
            else:
                opened, open_line = environments.pop()
                if opened != env:
                    issues.append(
                        LatexIssue(
                            line,
                            "error",
                            f"\\end{{{env}}} does not match \\begin{{{opened}}} on line {open_line}",
                        )
                    )
            continue
        if kind == "COMMAND":
            index += 1
            arity = _COMMAND_ARITY.get(value)
            if arity:
                for _ in range(arity):
                    consume_required_group(value, line)
            continue
        index += 1

    for open_line in braces:
        issues.append(LatexIssue(open_line, "error", "unclosed brace"))
    for open_line in brackets:
        issues.append(LatexIssue(open_line, "warning", "unclosed bracket"))
    for env, open_line in environments:
        issues.append(LatexIssue(open_line, "error", f"unclosed \\begin{{{env}}}"))
    for closer, open_line in math_pairs:
        issues.append(LatexIssue(open_line, "error", f"unclosed math delimiter (expected {closer})"))
    if not math_fragment:
        if math_inline % 2:
            issues.append(LatexIssue(1, "error", "unmatched $ math delimiter"))
        if math_display % 2:
            issues.append(LatexIssue(1, "error", "unmatched $$ math delimiter"))
    elif math_inline % 2:
        issues.append(LatexIssue(1, "warning", "unmatched $ inside a MathTex fragment"))
    return issues


def _run_chktex(text: str) -> list[LatexIssue]:
    binary = shutil.which("chktex")
    if binary is None:
        return []
    try:
        completed = subprocess.run(
            [binary, "-q", "-v0", "-"],
            input=text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    issues: list[LatexIssue] = []
    for raw in (completed.stdout or "").splitlines():
        match = re.match(r"^[^:]+:(\d+):(\d+):(\d+):(.*)$", raw)
        if not match:
            continue
        line = int(match.group(1))
        code = int(match.group(3))
        message = match.group(4).strip()
        severity = "warning" if code >= 10 else "error"
        issues.append(LatexIssue(line, severity, f"chktex {code}: {message}"))
    return issues


def _run_lualatex(text: str) -> list[LatexIssue]:
    """Optional deeper compile when ``M2M_LATEX_DEEP_CHECK`` is on.

    MathTex fragments are wrapped in a tiny math document. Failures become
    warnings on fragments so a missing TeX tree cannot fail offline pytest.
    """
    if not PipelineSettings.from_env().latex_deep_check:
        return []
    binary = shutil.which("lualatex")
    if binary is None:
        return []
    wrapper = (
        "\\documentclass{article}\n"
        "\\usepackage{amsmath,amssymb}\n"
        "\\begin{document}\n"
        f"${text}$\n"
        "\\end{document}\n"
    )
    try:
        with tempfile.TemporaryDirectory(prefix="m2m-latex-") as tmp:
            tex = Path(tmp) / "fragment.tex"
            tex.write_text(wrapper, encoding="utf-8")
            completed = subprocess.run(
                [
                    binary,
                    "--halt-on-error",
                    "--interaction=nonstopmode",
                    tex.name,
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
            )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if completed.returncode == 0:
        return []
    log = (completed.stdout or "") + (completed.stderr or "")
    issues: list[LatexIssue] = []
    for raw in log.splitlines():
        if raw.startswith("!"):
            issues.append(LatexIssue(1, "warning", f"lualatex: {raw[1:].strip()}"))
    if not issues:
        issues.append(LatexIssue(1, "warning", "lualatex: compile failed"))
    return issues


def validate_latex_report(latex: str, *, math_fragment: bool = True) -> LatexReport:
    """Return the historical ``{valid, errors, warnings}`` MCP-compatible report."""
    issues = parse_latex(latex, math_fragment=math_fragment)
    # chktex is a full-document linter. On MathTex fragments it is useful as
    # a second opinion but too noisy to fail a run. Keep those hits as warnings.
    for issue in _run_chktex(latex):
        if math_fragment:
            issues.append(LatexIssue(issue.line, "warning", issue.message))
        else:
            issues.append(issue)
    issues.extend(_run_lualatex(latex))
    errors = [issue.as_text() for issue in issues if issue.severity == "error"]
    warnings = [issue.as_text() for issue in issues if issue.severity != "error"]
    return LatexReport(
        valid=not errors,
        errors=errors,
        warnings=warnings,
        issues=issues,
    )


def validate_manim_code_report(source: str) -> SceneCheckReport:
    """AST-based Manim scene report used by verify and validation.json."""
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return SceneCheckReport(
            valid=False,
            scene_names=[],
            errors=[f"syntax error: {exc}"],
        )

    scene_names = discover_scene_classes(tree)
    if not scene_names:
        errors.append(
            "No Scene subclass found. A class must inherit from Scene, "
            "ThreeDScene, MovingCameraScene, ZoomedScene, or another Manim "
            "Community type whose name ends in Scene."
        )

    if re.search(r"self\.camera\.animate", source):
        errors.append(
            "never animate self.camera in a ThreeDScene; use move_camera "
            "or set_camera_orientation"
        )

    for line, ctor in non_raw_tex_calls(source, tree):
        suggestions.append(f"L{line}: Prefer raw strings for {ctor} content.")

    latex_errors: list[str] = []
    latex_warnings: list[str] = []
    latex_issues: list[LatexIssue] = []
    for line, fragment in extract_tex_fragments(source, tree):
        report = validate_latex_report(fragment, math_fragment=True)
        for issue in report.issues:
            relocated = LatexIssue(line, issue.severity, issue.message)
            latex_issues.append(relocated)
            target = latex_errors if issue.severity == "error" else latex_warnings
            target.append(relocated.as_text())
    latex = LatexReport(
        valid=not latex_errors,
        errors=latex_errors,
        warnings=latex_warnings,
        issues=latex_issues,
    )
    if latex_errors:
        errors.extend(f"LaTeX {item}" for item in latex_errors)
    warnings.extend(latex_warnings)

    return SceneCheckReport(
        valid=not errors,
        scene_names=scene_names,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
        latex=latex,
        complexity=scene_complexity(tree),
    )


def validation_template() -> dict[str, Any]:
    return {
        "latex": None,
        "manim_code": None,
        "complexity": None,
        "ran_at": None,
    }


def validation_from_scene(source: str) -> dict[str, Any]:
    report = validate_manim_code_report(source)
    latex = report.latex.to_dict() if report.latex is not None else None
    return {
        "latex": latex,
        "manim_code": {
            "valid": report.valid,
            "scene_names": report.scene_names,
            "errors": report.errors,
            "warnings": report.warnings,
            "suggestions": report.suggestions,
        },
        "complexity": report.complexity,
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def iter_known_scene_bases() -> Iterable[str]:
    return (
        "Scene",
        "ThreeDScene",
        "MovingCameraScene",
        "ZoomedScene",
        "LinearTransformationScene",
        "VectorScene",
        "GraphScene",
    )
