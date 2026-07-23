"""Command line for the independent Codex CLI-native Sol silo."""

from __future__ import annotations

import argparse
import os
import subprocess

from sol import __version__
from sol.client import CodexCli, CodexCliError, FAST_SERVICE_TIER
from sol.models import RunRequest
from sol.service import SolService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim-sol",
        description="Produce complete Math-To-Manim films through the logged-in Codex CLI.",
    )
    parser.add_argument("--version", action="version", version=f"math-to-manim-sol {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Create one complete film-production run bundle")
    run.add_argument("prompt")
    run.add_argument("--render", action="store_true")
    run.add_argument("-q", "--quality", default="l", choices=["l", "m", "h", "p", "k"])
    run.add_argument(
        "--reasoning-effort",
        default="high",
        choices=["low", "medium", "high", "xhigh", "max"],
    )
    run.add_argument("--max-repairs", default=2, type=int, choices=range(0, 6))
    run.add_argument("--offline", action="store_true")

    runs = sub.add_parser("runs", help="List recent Sol run manifests")
    runs.add_argument("--limit", type=int, default=20)

    sub.add_parser("doctor", help="Check the Codex executable and cached ChatGPT login")
    return parser


def _doctor() -> int:
    client = CodexCli()
    try:
        executable = client.resolve()
    except CodexCliError as exc:
        print(f"not ready: {exc}")
        return 1
    env = {key: value for key, value in os.environ.items() if key != "OPENAI_API_KEY"}
    version = subprocess.run(
        [executable, "--version"], capture_output=True, text=True, env=env, check=False
    )
    login = subprocess.run(
        [executable, "-c", FAST_SERVICE_TIER, "login", "status"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    print((version.stdout or version.stderr).strip())
    print((login.stdout or login.stderr).strip())
    if version.returncode or login.returncode:
        print("not ready: run `codex login` with your ChatGPT account")
        return 1
    print(f"ready: Codex CLI + cached ChatGPT login; model={client.model}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = SolService()
    if args.command == "run":
        response = service.run(RunRequest(
            prompt=args.prompt,
            reasoning_effort=args.reasoning_effort,
            offline=args.offline,
            render=args.render,
            quality=args.quality,
            max_repairs=args.max_repairs,
        ))
        import json

        print(json.dumps(response, indent=2))
        return 0
    if args.command == "runs":
        for manifest in service.list_runs(limit=max(1, args.limit)):
            print(f"{manifest.run_id}\t{manifest.status}\t{manifest.prompt}")
        return 0
    return _doctor()


if __name__ == "__main__":
    raise SystemExit(main())
