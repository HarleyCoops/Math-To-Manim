"""Sandboxed Manim render for a Mythos run directory.

The previous harness invoked Manim with ``cwd`` at the repository root and no
``--media_dir``, so generated media leaked into ``media/`` at the checkout
root. Render outputs now stay inside the run directory.

Threat model (see ``docs/security.md``): ``mythos_scene.py`` is
trusted-with-caveats agent output. This wrapper pins paths, cwd, argument
vector, and a wall-clock timeout. It does not give Manim a full OS sandbox.
"""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None  # type: ignore[assignment]

DEFAULT_RENDER_TIMEOUT = float(os.getenv("M2M_RENDER_TIMEOUT", "1800"))

_SCENE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_QUALITY = re.compile(r"^[lmhpk]$")
_TEX_BINARIES = frozenset({"latex", "pdflatex", "xelatex", "lualatex", "tectonic", "dvisvgm"})
_RENDER_BINARIES = _TEX_BINARIES | {"ffmpeg"}


def resolve_manim() -> list[str]:
    """Find the manim entry point, preferring the active interpreter's env."""
    override = os.getenv("M2M_MANIM")
    if override:
        return [override]
    if importlib.util.find_spec("manim") is not None:
        return [sys.executable, "-m", "manim"]
    return [shutil.which("manim") or "manim"]


class RenderError(RuntimeError):
    pass


def render_dependency_guidance(dependencies: tuple[str, ...]) -> str:
    """Installation hints only; never install or alter the caller's PATH."""
    hints = [
        "Ensure the tools are on PATH in the same terminal that starts Manim; "
        "restart the terminal after installation. See README: Render system setup."
    ]
    if "manim" in dependencies:
        hints.append('Install Manim in the active Python environment with '
                     'python -m pip install -e ".[render]", or fix M2M_MANIM.')
    if "ffmpeg" in dependencies:
        hints.append("Install FFmpeg with your platform's package manager.")
    if _TEX_BINARIES.intersection(dependencies) or "tex-toolchain" in dependencies:
        hints.append("Install a TeX distribution and dvisvgm: BasicTeX/MacTeX "
                     "or TinyTeX on macOS, MiKTeX/TeX Live on Windows, "
                     "TeX Live on Linux. Verify latex --version and dvisvgm --version.")
    return "\n".join(hints)


class RenderEnvironmentError(RenderError):
    """A missing render dependency that scene-code repair cannot fix."""

    def __init__(self, dependencies: tuple[str, ...], *, output: str = "",
                 exit_code: int = 127):
        self.dependencies = dependencies
        self.output = output
        self.exit_code = exit_code
        tex_error = bool(_TEX_BINARIES.intersection(dependencies) or "tex-toolchain" in dependencies)
        capability = ("MathTex/Tex cannot render. "
                      if tex_error
                      else "Rendering cannot continue. ")
        names = ["a TeX toolchain command (compiler or dvisvgm)" if tool == "tex-toolchain"
                 else tool for tool in dependencies]
        super().__init__(
            f"Render environment error: missing {', '.join(names)}. "
            f"{capability}Skipping model scene repair.\n"
            + render_dependency_guidance(dependencies)
        )

    def to_dict(self) -> dict:
        return {"type": "environment", "missing_dependencies": list(self.dependencies),
                "detail": str(self)}


def missing_render_dependencies(output: str) -> tuple[str, ...]:
    """Recognize named missing executables, not arbitrary scene/asset errors.

    Do not infer a missing binary from a failed TeX compile, a mention of
    MathTex, or the exit code alone. Custom compilers and non-LaTeX scenes
    need no default-latex preflight. A nameless Windows error requires both
    Manim's TeX subprocess frame and a subprocess traceback; do not guess a
    specific compiler from an arbitrary FileNotFoundError.
    """
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    # Rich can split a filename itself (tex_file_w / riting.py) across boxed
    # lines. Reassemble those lines before recognizing the subprocess frame.
    plain = re.sub(r"(?m)^[ \t]*[|│][ \t]*[|│][ \t]*$", "", plain)
    plain = re.sub(r"[ \t]*[|│][ \t]*\r?\n[ \t]*[|│][ \t]*", "", plain)
    # If a full traceback is supplied, require subprocess evidence. A scene
    # can fail while opening an asset literally named "latex" or "ffmpeg".
    launch_failure = "Traceback (most recent call last)" not in plain or "subprocess.py" in plain
    missing = []
    for match in re.finditer(
        r"FileNotFoundError:\s*\[(?:Errno|WinError)\s*2\][^\n]*?:\s*['\"]([^'\"\n]+)['\"]",
        plain,
    ):
        name = re.split(r"[\\/]", match.group(1))[-1].lower().removesuffix(".exe")
        if launch_failure and name in _RENDER_BINARIES and name not in missing:
            missing.append(name)
    if re.search(r"(?m)^.*: No module named manim\s*$", plain):
        missing.append("manim")
    if not missing and re.search(r"FileNotFoundError:\s*\[WinError 2\]", plain):
        tex_subprocess = re.search(
            r"manim[\\/]utils[\\/]tex_file_writing\.py[^\n]*\bin (?:compile_tex|convert_to_svg)\b",
            plain,
        )
        if tex_subprocess and "subprocess.py" in plain:
            missing.append("tex-toolchain")
    return tuple(missing)


def resolve_inside(run_dir: Path, path: Path | str) -> Path:
    """Resolve ``path`` and reject anything that escapes ``run_dir``."""
    root = Path(run_dir).resolve()
    candidate = Path(path)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise RenderError(f"path escapes run directory: {path}")
    return resolved


def validate_scene_name(scene_name: str) -> str:
    if not _SCENE_NAME.fullmatch(scene_name):
        raise RenderError(f"invalid scene class name: {scene_name!r}")
    return scene_name


def apply_resource_limits() -> None:
    """Best-effort CPU and address-space caps for the Manim child.

    Residual risk: ``resource`` is unavailable on Windows; even on Linux these
    limits do not stop a scene from opening sockets or writing through Manim
    itself. Follow-up: a user-namespace / bubblewrap jail.
    """
    if resource is None:
        return
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (600, 600))
    except (ValueError, OSError):
        pass
    try:
        resource.setrlimit(resource.RLIMIT_AS, (4 * 1024 ** 3, 4 * 1024 ** 3))
    except (ValueError, OSError):
        pass


def build_manim_command(
    run_dir: Path,
    *,
    scene_file: Path,
    scene_name: str,
    quality: str,
) -> list[str]:
    if not _QUALITY.fullmatch(quality):
        raise RenderError(f"invalid Manim quality flag: {quality!r}")
    root = Path(run_dir).resolve()
    scene_path = resolve_inside(root, scene_file)
    media_dir = resolve_inside(root, root / "media")
    return resolve_manim() + [
        f"-q{quality}",
        "--media_dir",
        str(media_dir),
        "--progress_bar",
        "none",
        str(scene_path.name),
        validate_scene_name(scene_name),
    ]


def find_final_video(run_dir: Path) -> Path | None:
    candidates = [
        path
        for path in Path(run_dir).glob("**/*.mp4")
        if "partial_movie_files" not in {part.lower() for part in path.parts}
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime_ns)


def render_scene_file(
    run_dir: Path,
    *,
    scene_file: Path,
    scene_name: str,
    quality: str,
    timeout: float = DEFAULT_RENDER_TIMEOUT,
) -> tuple[int, str]:
    """Run Manim with cwd and media pinned to ``run_dir``. Never uses shell=True."""
    root = Path(run_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "media").mkdir(exist_ok=True)
    command = build_manim_command(
        root,
        scene_file=scene_file,
        scene_name=scene_name,
        quality=quality,
    )
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            preexec_fn=apply_resource_limits if resource is not None else None,
        )
    except FileNotFoundError as exc:
        # This exception is from launching our command, before scene code runs.
        raise RenderEnvironmentError(("manim",), output=str(exc)) from exc
    except subprocess.TimeoutExpired as exc:
        partial = exc.stderr or exc.stdout or b""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", errors="replace")
        return 124, (
            f"render timed out after {timeout:.0f}s "
            "(raise M2M_RENDER_TIMEOUT or lower the quality)\n" + partial
        )
    output = (completed.stderr or "") + (completed.stdout or "")
    if completed.returncode != 0:
        missing = missing_render_dependencies(output)
        if missing:
            raise RenderEnvironmentError(missing, output=output, exit_code=completed.returncode)
    return completed.returncode, output
