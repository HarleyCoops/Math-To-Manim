"""`math-to-manim doctor`: preflight checks before you spend 30 minutes.

Verifies, without touching any model unless asked:

- configuration: which backend/model the chain will use and where it came from
- the backend CLI resolves on PATH
- render toolchain: manim, ffmpeg, latex, dvisvgm
- the runs directory is writable
- (with ``--ping``) one tiny model call to prove the backend is logged in

Exit code 0 when every required check passes.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from mythos.backends import (
    DEFAULT_COMMAND,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    FUGU_API_COMMANDS,
    BackendAuthError,
    fugu_api_key_from_env,
    run_model,
)
from mythos.charter import load_env_file, resolve_command
from mythos.harness import DEFAULT_RENDER_TIMEOUT, default_runs_dir, resolve_manim

_OK = "  [ok]  "
_BAD = "  [FAIL]"
_INFO = "  [--]  "


def _which(name: str) -> str | None:
    return shutil.which(name)


def run_doctor(command: str = DEFAULT_COMMAND, model: str = DEFAULT_MODEL,
               ping: bool = False) -> int:
    load_env_file()
    failures = 0

    print("math-to-manim doctor")
    print("configuration:")
    src = "M2M_MODEL" if os.getenv("M2M_MODEL") else "default"
    print(f"{_INFO}model:          {model}  (from {src})")
    if os.getenv("M2M2_MYTHOS_MODEL"):
        print(f"{_INFO}note: M2M2_MYTHOS_MODEL is set but ignored "
              "(archived-pipeline setting); use M2M_MODEL")
    print(f"{_INFO}command:        {command}  "
          f"(from {'M2M_COMMAND' if os.getenv('M2M_COMMAND') else 'default'})")
    print(f"{_INFO}timeout:        {DEFAULT_TIMEOUT:.0f}s model / "
          f"{DEFAULT_RENDER_TIMEOUT:.0f}s render")
    env_path = Path(".env")
    print(f"{_INFO}.env:           "
          f"{'present (gitignored)' if env_path.exists() else 'none'}")

    print("backend:")
    if command in FUGU_API_COMMANDS:
        key, env_name = fugu_api_key_from_env()
        if key:
            print(f"{_OK}HTTP backend key found in {env_name}")
        else:
            failures += 1
            print(f"{_BAD}no API key: set FUGU_API_KEY (or SAKANA_API_KEY)")
    else:
        resolved = resolve_command(command)
        if _which(resolved) or Path(resolved).exists():
            print(f"{_OK}{command!r} resolves to {resolved}")
        else:
            failures += 1
            print(f"{_BAD}{command!r} not found on PATH")
        if ping:
            try:
                out = run_model("Reply with exactly: OK", command=command,
                                model=model, timeout=120)
                snippet = (out or "").strip().splitlines()[:1]
                print(f"{_OK}auth ping succeeded ({snippet})")
            except BackendAuthError as exc:
                failures += 1
                print(f"{_BAD}auth ping: {str(exc).splitlines()[0]}")
            except Exception as exc:  # noqa: BLE001 — diagnostic surface
                failures += 1
                print(f"{_BAD}auth ping: {type(exc).__name__}: {exc}")
        else:
            print(f"{_INFO}auth not verified (rerun with --ping for a live "
                  "1-line model call)")

    print("render toolchain:")
    manim_cmd = resolve_manim()
    label = " ".join(manim_cmd)
    try:
        completed = subprocess.run(manim_cmd + ["--version"], text=True,
                                   capture_output=True, timeout=60)
        version = (completed.stdout or completed.stderr).strip().splitlines()
        if completed.returncode == 0 and version:
            print(f"{_OK}manim: {version[0]}  ({label})")
        else:
            failures += 1
            print(f"{_BAD}manim --version failed via {label}")
    except (OSError, subprocess.TimeoutExpired) as exc:
        failures += 1
        print(f"{_BAD}manim not runnable via {label}: {exc}")
    for tool, required in (("ffmpeg", True), ("latex", False),
                           ("dvisvgm", False)):
        found = _which(tool)
        if found:
            print(f"{_OK}{tool}: {found}")
        elif required:
            failures += 1
            print(f"{_BAD}{tool} not found (required for rendering)")
        else:
            print(f"{_INFO}{tool} not found (needed for MathTex/LaTeX scenes)")

    print("runs ledger:")
    runs = default_runs_dir()
    try:
        runs.mkdir(parents=True, exist_ok=True)
        probe = runs / ".doctor-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        print(f"{_OK}writable: {runs}")
    except OSError as exc:
        failures += 1
        print(f"{_BAD}runs dir not writable ({runs}): {exc}")

    print("summary:", "all checks passed" if failures == 0
          else f"{failures} check(s) failed")
    return 0 if failures == 0 else 1


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", default=DEFAULT_COMMAND)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--ping", action="store_true",
                        help="make one tiny model call to verify login")
    args = parser.parse_args(argv)
    return run_doctor(command=args.command, model=args.model, ping=args.ping)


if __name__ == "__main__":
    raise SystemExit(main())
