"""Companion deliverables of a Mythos run: the paper and the Lean file.

A film shows an idea. Two companions make the same mathematics checkable:

* ``paper``: a publication-level LaTeX paper, ``paper.tex``. When a TeX
  compiler is on PATH it is compiled to ``paper.pdf``.
* ``lean``: a Lean 4 file, ``Companion.lean``, that proves the film's claims
  with Mathlib and evaluates its numbers. When ``M2M_LEAN_PROJECT`` names a
  Lake project that requires Mathlib, the file is checked there with
  ``lake env lean``.

Each companion has a charter in ``src/mythos/agents``, a static check that
needs no toolchain, and a build that needs one. A missing toolchain is
recorded as ``skipped``; it never fails the run. The result of both steps is
written to ``manifest["companions"][<slug>]``:

    {"artifact": "paper.tex", "static": {"passed": true, "errors": []},
     "build": {"status": "built" | "skipped" | "failed", ...}}

The pure pieces (prompt, static checks) are module functions, so an operator
can drive them by hand (``scripts/operate_mythos_chain.py --companions``).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

AGENT_DIR = Path(__file__).resolve().parent / "agents"

BUILD_BUILT = "built"
BUILD_SKIPPED = "skipped"
BUILD_FAILED = "failed"


@dataclass(frozen=True)
class Companion:
    slug: str
    charter_file: str
    artifact: str
    #: Fence languages the model may use for the file it returns.
    fences: tuple[str, ...]
    #: Deterministic stand-in for offline runs.
    offline_text: str


OFFLINE_PAPER = r"""\documentclass{article}
\usepackage{amsmath,amsthm}
\newtheorem{theorem}{Theorem}
\title{Mythos harness: offline rehearsal}
\author{Mythos chain}
\begin{document}
\maketitle
\begin{theorem}
$e^{i\pi}+1=0$.
\end{theorem}
\begin{proof}
By Euler's formula, $e^{i\pi}=\cos\pi+i\sin\pi=-1$.
\end{proof}
\end{document}
"""

OFFLINE_LEAN = """/- Mythos harness: offline rehearsal. -/
import Mathlib

theorem offline_rehearsal : (1 : ℕ) + 1 = 2 := rfl

#print axioms offline_rehearsal
"""

COMPANIONS: tuple[Companion, ...] = (
    Companion("paper", "mythos-paper-author.md", "paper.tex", ("latex", "tex"), OFFLINE_PAPER),
    Companion("lean", "mythos-lean-author.md", "Companion.lean", ("lean", "lean4"), OFFLINE_LEAN),
)

COMPANIONS_BY_SLUG: dict[str, Companion] = {c.slug: c for c in COMPANIONS}


def parse_companions(spec: str | None) -> tuple[Companion, ...]:
    """``"paper,lean"`` -> the companions, in the order of :data:`COMPANIONS`."""
    names = [name.strip().lower() for name in (spec or "").split(",") if name.strip()]
    unknown = [name for name in names if name not in COMPANIONS_BY_SLUG]
    if unknown:
        raise ValueError(
            f"unknown companion {unknown[0]!r}; choose from: {', '.join(COMPANIONS_BY_SLUG)}")
    return tuple(c for c in COMPANIONS if c.slug in names)


# ---------------------------------------------------------------------- #
# Prompts                                                                 #
# ---------------------------------------------------------------------- #

def load_companion_charter(companion: Companion) -> str:
    """The charter text, without its YAML front matter."""
    text = (AGENT_DIR / companion.charter_file).read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return text.strip()


def companion_prompt(companion: Companion, dossier: dict[str, Any], *, prompt: str = "") -> str:
    """The exact prompt a companion stage receives."""
    return (
        f"{load_companion_charter(companion)}\n\n"
        f"USER PROMPT:\n{prompt}\n\n"
        f"DOSSIER JSON:\n{json.dumps(dossier, indent=2)}"
    )


def companion_repair_prompt(companion: Companion, source: str, problems: str) -> str:
    return (
        f"{load_companion_charter(companion)}\n\n"
        "The file below was rejected. Repair it: keep every statement that is "
        "correct, fix only what is broken, and return the COMPLETE file.\n\n"
        f"CURRENT FILE:\n{source}\n\nPROBLEMS:\n{problems[-8000:]}"
    )


def extract_fenced_block(text: str, fences: tuple[str, ...]) -> str:
    """Pull the companion file out of model output (one fenced block)."""
    names = "|".join(re.escape(name) for name in fences)
    match = re.search(rf"```(?:{names})?[ \t]*\n(.*?)```", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip() + "\n"
    stripped = text.strip()
    if stripped.startswith(("\\documentclass", "/-", "import ", "%")):
        return stripped + "\n"
    raise RuntimeError(f"No fenced block found in model output:\n{text[:800]}")


# ---------------------------------------------------------------------- #
# Static checks (no toolchain needed)                                     #
# ---------------------------------------------------------------------- #

_PLACEHOLDERS = re.compile(r"\b(TODO|TBD|FIXME|lorem ipsum)\b", flags=re.IGNORECASE)
_TEX_EXTERNAL = re.compile(
    r"\\(input|include|includegraphics|bibliography|write18|immediate\\write18)\b")
_THEOREM_ENVS = ("theorem", "proposition", "lemma", "corollary")


def _strip_tex_comments(tex: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", tex)


def check_paper_source(tex: str) -> list[str]:
    """Problems that make a LaTeX paper unfit before any compiler runs."""
    body = _strip_tex_comments(tex)
    errors: list[str] = []
    if "\\documentclass" not in body:
        errors.append("no \\documentclass")
    for marker in ("\\begin{document}", "\\end{document}"):
        if body.count(marker) != 1:
            errors.append(f"expected exactly one {marker}")
    environments = set(re.findall(r"\\begin\{([A-Za-z*]+)\}", body))
    for env in sorted(environments | set(re.findall(r"\\end\{([A-Za-z*]+)\}", body))):
        opened = body.count(f"\\begin{{{env}}}")
        closed = body.count(f"\\end{{{env}}}")
        if opened != closed:
            errors.append(f"environment {env!r}: {opened} \\begin, {closed} \\end")
    statements = sum(body.count(f"\\begin{{{env}}}") for env in _THEOREM_ENVS)
    if statements == 0:
        errors.append("no theorem, proposition, lemma or corollary")
    if body.count("\\begin{proof}") == 0:
        errors.append("no proof environment")
    for match in _TEX_EXTERNAL.finditer(body):
        errors.append(f"not self-contained: \\{match.group(1)}")
    placeholder = _PLACEHOLDERS.search(body)
    if placeholder:
        errors.append(f"placeholder text: {placeholder.group(0)!r}")
    return errors


def strip_lean_comments(source: str) -> str:
    """Lean source without ``--`` line comments and nested ``/- -/`` blocks.

    String literals are kept, so a ``"--"`` inside a string is not a comment.
    """
    out: list[str] = []
    i, depth, n = 0, 0, len(source)
    while i < n:
        two = source[i:i + 2]
        if depth:
            if two == "/-":
                depth += 1
                i += 2
            elif two == "-/":
                depth -= 1
                i += 2
            else:
                if source[i] == "\n":
                    out.append("\n")
                i += 1
            continue
        if two == "/-":
            depth = 1
            i += 2
        elif two == "--":
            end = source.find("\n", i)
            i = n if end == -1 else end
        elif source[i] == '"':
            end = i + 1
            while end < n and source[end] != '"':
                end += 2 if source[end] == "\\" else 1
            out.append(source[i:end + 1])
            i = end + 1
        else:
            out.append(source[i])
            i += 1
    return "".join(out)


_LEAN_FORBIDDEN = (
    (re.compile(r"\bsorry\b"), "contains `sorry`"),
    (re.compile(r"\badmit\b"), "contains `admit`"),
    (re.compile(r"\bnative_decide\b"), "contains `native_decide`"),
    (re.compile(r"^\s*(?:private\s+|protected\s+)?axiom\b", flags=re.MULTILINE),
     "declares an `axiom`"),
)


def check_lean_source(source: str) -> list[str]:
    """Problems that make a Lean file unfit before Lean runs."""
    code = strip_lean_comments(source)
    errors: list[str] = []
    imports = re.findall(r"^\s*import\s+(\S+)", code, flags=re.MULTILINE)
    if not imports:
        errors.append("no `import Mathlib`")
    for name in imports:
        if name != "Mathlib" and not name.startswith("Mathlib."):
            errors.append(f"imports {name!r}: only Mathlib is allowed")
    for pattern, problem in _LEAN_FORBIDDEN:
        if pattern.search(code):
            errors.append(problem)
    if not re.search(r"^\s*(?:private\s+|protected\s+)?(?:theorem|lemma)\b", code,
                     flags=re.MULTILINE):
        errors.append("no theorem")
    if "#print axioms" not in code:
        errors.append("no `#print axioms` audit")
    return errors


STATIC_CHECKS = {"paper": check_paper_source, "lean": check_lean_source}


# ---------------------------------------------------------------------- #
# Builds (toolchain needed; a missing toolchain is "skipped")             #
# ---------------------------------------------------------------------- #

def _run(cmd: list[str], *, cwd: Path, timeout: float) -> tuple[int, str]:
    try:
        done = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired as exc:
        return 124, f"timed out after {timeout:.0f}s\n{exc.stdout or ''}"
    return done.returncode, (done.stdout or "") + (done.stderr or "")


def build_paper(run_dir: Path, artifact: str = "paper.tex", *, timeout: float = 600.0) -> dict[str, Any]:
    """Compile ``paper.tex`` to ``paper.pdf`` with pdflatex (two passes)."""
    run_dir = Path(run_dir)
    compiler = shutil.which("pdflatex")
    if compiler is None:
        return {"status": BUILD_SKIPPED, "reason": "pdflatex is not on PATH"}
    out_dir = run_dir / "paper_build"
    out_dir.mkdir(exist_ok=True)
    cmd = [compiler, "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape",
           f"-output-directory={out_dir.name}", artifact]
    code, output = 0, ""
    for _ in range(2):
        code, output = _run(cmd, cwd=run_dir, timeout=timeout)
        if code != 0:
            break
    (run_dir / "paper_build.log").write_text(output, encoding="utf-8")
    result: dict[str, Any] = {"tool": "pdflatex", "log": "paper_build.log"}
    built = out_dir / (Path(artifact).stem + ".pdf")
    if code != 0 or not built.is_file():
        errors = [line for line in output.splitlines() if line.startswith("!")]
        return {**result, "status": BUILD_FAILED, "exit_code": code,
                "detail": "\n".join(errors[:12]) or output[-1500:]}
    pdf_name = Path(artifact).stem + ".pdf"
    shutil.copyfile(built, run_dir / pdf_name)
    pages = re.search(r"Output written on .*?\((\d+) pages?", output, flags=re.DOTALL)
    return {**result, "status": BUILD_BUILT, "pdf": pdf_name,
            "pages": int(pages.group(1)) if pages else None,
            "undefined_references": "undefined references" in output}


def build_lean(run_dir: Path, artifact: str = "Companion.lean", *,
               project_dir: str | Path | None = None, timeout: float = 900.0) -> dict[str, Any]:
    """Check the Lean file with ``lake env lean`` inside a Mathlib project."""
    run_dir = Path(run_dir)
    if not project_dir:
        return {"status": BUILD_SKIPPED,
                "reason": "M2M_LEAN_PROJECT is not set (a Lake project that requires Mathlib)"}
    project = Path(project_dir)
    if not (project / "lean-toolchain").is_file():
        return {"status": BUILD_SKIPPED, "reason": f"no lean-toolchain in {project}"}
    lake = shutil.which("lake")
    if lake is None:
        return {"status": BUILD_SKIPPED, "reason": "lake is not on PATH"}
    code, output = _run([lake, "env", "lean", str((run_dir / artifact).resolve())],
                        cwd=project, timeout=timeout)
    (run_dir / "lean_build.log").write_text(output, encoding="utf-8")
    toolchain = (project / "lean-toolchain").read_text(encoding="utf-8").strip()
    result: dict[str, Any] = {"tool": "lake env lean", "toolchain": toolchain,
                              "log": "lean_build.log"}
    problems = [line for line in output.splitlines() if ": error" in line]
    if code != 0 or problems:
        return {**result, "status": BUILD_FAILED, "exit_code": code,
                "detail": "\n".join(problems[:12]) or output[-1500:]}
    axioms = sorted(set(re.findall(r"depends on axioms: \[(.*?)\]", output)))
    return {**result, "status": BUILD_BUILT,
            "warnings": sum(": warning" in line for line in output.splitlines()),
            "axioms": axioms}


def build_companion(companion: Companion, run_dir: Path, *,
                    lean_project: str | Path | None = None,
                    timeout: float = 900.0) -> dict[str, Any]:
    if companion.slug == "paper":
        return build_paper(run_dir, companion.artifact, timeout=timeout)
    return build_lean(run_dir, companion.artifact, project_dir=lean_project, timeout=timeout)


def record_companion(manifest: dict[str, Any], companion: Companion,
                     static_errors: list[str], build: dict[str, Any] | None) -> dict[str, Any]:
    """Write one companion's result into the manifest and return the record."""
    record = {
        "artifact": companion.artifact,
        "static": {"passed": not static_errors, "errors": static_errors},
        "build": build or {"status": BUILD_SKIPPED, "reason": "static check failed"},
    }
    manifest.setdefault("companions", {})[companion.slug] = record
    manifest.setdefault("artifacts", {})[companion.slug] = companion.artifact
    return record


def companion_ok(record: dict[str, Any]) -> bool:
    """True when the static check passed and the build did not fail."""
    return bool(record["static"]["passed"]) and record["build"]["status"] != BUILD_FAILED


def check_and_record(companion: Companion, run_dir: Path, manifest: dict[str, Any], *,
                     lean_project: str | Path | None = None,
                     timeout: float = 900.0) -> dict[str, Any]:
    """Static check, then build, then the manifest record, for a file on disk."""
    source = (Path(run_dir) / companion.artifact).read_text(encoding="utf-8")
    errors = STATIC_CHECKS[companion.slug](source)
    build = None if errors else build_companion(
        companion, Path(run_dir), lean_project=lean_project, timeout=timeout)
    return record_companion(manifest, companion, errors, build)
