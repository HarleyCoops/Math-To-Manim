"""``math-to-manim-studio doctor``: prove the environment before a run.

The doctor checks each tool and its version, renders one test shot per
engine, measures the seconds per frame, and writes ``env.lock.json`` in the
Studio runs directory. Later stages read that file to plan shot lengths that
this machine can render.

Every external command goes through one ``Runner`` so tests can replace it.
No secret is read or written: the Managed Agents check records only whether
the ``ant`` CLI is signed in.
"""

from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from studio import __version__
from studio.settings import (
    BLENDER_GPU_BACKEND,
    checkout_root,
    default_runs_dir,
    find_ant,
    find_blender,
)

#: ``runner(command, timeout_seconds) -> (exit_code, combined_output)``
Runner = Callable[[list[str], float], tuple[int, str]]
Logger = Callable[[str], None]

SMOKE_DIR = Path(__file__).resolve().parent / "smoke"
LOCK_FILE = "env.lock.json"
#: Tools a Studio run cannot work without on this machine.
REQUIRED = ("manim", "ffmpeg", "latex", "dvisvgm", "blender")


def run_command(command: list[str], timeout: float) -> tuple[int, str]:
    """Run one command. 127 = not found, 124 = timed out."""
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                              encoding="utf-8", errors="replace", check=False)
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout:.0f} s"
    return done.returncode, (done.stdout or "") + (done.stderr or "")


@dataclass
class ToolCheck:
    name: str
    ok: bool
    version: str | None
    path: str | None
    required: bool


def _first_line(text: str) -> str | None:
    for line in text.splitlines():
        if line.strip():
            return line.strip()[:200]
    return None


def check_tool(name: str, command: list[str], runner: Runner) -> ToolCheck:
    """Ask a tool for its version. ``command[0]`` may be a name or a path."""
    code, output = runner(command, 60.0)
    path = command[0] if Path(command[0]).is_file() else shutil.which(command[0])
    return ToolCheck(name=name, ok=code == 0, version=_first_line(output) if code == 0 else None,
                     path=str(path) if path else None, required=name in REQUIRED)


def check_tools(runner: Runner) -> list[ToolCheck]:
    blender = find_blender()
    ant = find_ant()
    checks = [
        check_tool("manim", [sys.executable, "-m", "manim", "--version"], runner),
        check_tool("ffmpeg", ["ffmpeg", "-version"], runner),
        check_tool("latex", ["latex", "--version"], runner),
        check_tool("dvisvgm", ["dvisvgm", "--version"], runner),
        check_tool("blender", [str(blender) if blender else "blender", "--version"], runner),
        check_tool("node", ["node", "--version"], runner),
        check_tool("typst", ["typst", "--version"], runner),
        check_tool("ant", [str(ant) if ant else "ant", "--version"], runner),
    ]
    return checks


def blender_smoke(blender: Path, out_dir: Path, runner: Runner, *, frames: int = 4,
                  width: int = 1920, height: int = 1080, samples: int = 64) -> dict[str, Any]:
    """Render the Blender test scene with EEVEE and return its measured timings."""
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(blender), "--background", "--factory-startup",
        "--gpu-backend", BLENDER_GPU_BACKEND,
        "--python", str(SMOKE_DIR / "blender_smoke.py"),
        "--", str(out_dir), str(frames), str(width), str(height), str(samples),
    ]
    code, output = runner(command, 900.0)
    result_path = out_dir / "result.json"
    if code != 0 or not result_path.is_file():
        return {"ok": False, "exit_code": code, "detail": output[-2000:]}
    result = json.loads(result_path.read_text(encoding="utf-8"))
    seconds = result.get("seconds_per_frame") or []
    steady = seconds[1:] or seconds  # the first frame also compiles shaders
    return {
        "ok": True,
        "version": result.get("blender"),
        "engine": result.get("engine"),
        "gpu": result.get("gpu"),
        "width": result.get("width"),
        "height": result.get("height"),
        "samples": result.get("samples"),
        "first_frame_seconds": seconds[0] if seconds else None,
        "seconds_per_frame": round(sum(steady) / len(steady), 3) if steady else None,
        "frames": sorted(p.name for p in out_dir.glob("frame_*.png")),
    }


def manim_smoke(out_dir: Path, runner: Runner) -> dict[str, Any]:
    """Render one still of the Manim test scene and time it."""
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "manim", "-s", "-ql", "--media_dir", str(out_dir),
               str(SMOKE_DIR / "manim_smoke.py"), "StudioSmoke"]
    started = time.perf_counter()
    code, output = runner(command, 600.0)
    elapsed = round(time.perf_counter() - started, 3)
    stills = sorted(out_dir.rglob("StudioSmoke*.png"))
    if code != 0 or not stills:
        return {"ok": False, "exit_code": code, "detail": output[-2000:]}
    return {"ok": True, "still_seconds": elapsed, "still": str(stills[-1])}


def managed_agents_status(runner: Runner) -> dict[str, Any]:
    """Is ``ant`` signed in, and which resources has ``ant apply`` created."""
    status: dict[str, Any] = {"ant": None, "signed_in": False, "resources": {}}
    ant = find_ant()
    if ant is not None:
        status["ant"] = str(ant)
        code, output = runner([str(ant), "auth", "status"], 60.0)
        status["signed_in"] = code == 0 and bool(re.search(r"Logged in to", output))
    lock = checkout_root() / "environments" / "studio" / "claude-lock.json"
    if lock.is_file():
        try:
            resources = json.loads(lock.read_text(encoding="utf-8")).get("resources", {})
            status["resources"] = {name: {"kind": item.get("kind"), "id": item.get("id")}
                                   for name, item in resources.items()}
        except (ValueError, AttributeError):
            status["resources"] = {}
    return status


def run_doctor(*, render: bool = True, runner: Runner = run_command,
               log: Logger = print) -> int:
    """Check, measure, write ``env.lock.json``. Returns 0 when every required part works."""
    runs_dir = default_runs_dir()
    work = runs_dir / "doctor"
    tools = check_tools(runner)
    log("tools:")
    for tool in tools:
        mark = "ok" if tool.ok else ("MISSING" if tool.required else "not found")
        log(f"  [{mark}] {tool.name}: {tool.version or '-'}")

    engines: dict[str, Any] = {}
    if render:
        by_name = {tool.name: tool for tool in tools}
        if by_name["blender"].ok:
            log("blender: rendering the test scene with EEVEE ...")
            engines["blender"] = blender_smoke(find_blender(), work / "blender", runner)
        else:
            engines["blender"] = {"ok": False, "detail": "blender not found"}
        if by_name["manim"].ok:
            log("manim: rendering the test still ...")
            engines["manim"] = manim_smoke(work / "manim", runner)
        else:
            engines["manim"] = {"ok": False, "detail": "manim not found"}
        for name, result in engines.items():
            if result.get("ok"):
                timing = result.get("seconds_per_frame") or result.get("still_seconds")
                log(f"  [ok] {name}: {timing} s")
            else:
                log(f"  [FAILED] {name}: {str(result.get('detail', ''))[-300:]}")

    agents = managed_agents_status(runner)
    log(f"managed agents: ant signed in = {agents['signed_in']}; "
        f"resources = {len(agents['resources'])}")

    lock = {
        "studio": __version__,
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "platform": {"system": platform.system(), "machine": platform.machine(),
                     "python": platform.python_version()},
        "tools": {tool.name: asdict(tool) for tool in tools},
        "engines": engines,
        "managed_agents": agents,
    }
    runs_dir.mkdir(parents=True, exist_ok=True)
    lock_path = runs_dir / LOCK_FILE
    lock_path.write_text(json.dumps(lock, indent=2), encoding="utf-8")
    log(f"wrote {lock_path}")

    missing = [tool.name for tool in tools if tool.required and not tool.ok]
    failed = [name for name, result in engines.items() if not result.get("ok")]
    if missing or failed:
        log("summary: NOT ready; missing tools: "
            f"{', '.join(missing) or 'none'}; failed renders: {', '.join(failed) or 'none'}")
        return 1
    log("summary: ready")
    return 0
