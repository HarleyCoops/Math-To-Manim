"""Command line for the independent MiMo 2.6 tool-calling silo."""

from __future__ import annotations

import argparse
import json
from typing import get_args

from mimo import __version__
from mimo.agents import STAGE_NAMES
from mimo.client import MimoClient, MimoClientError, api_key_status
from mimo.harness import MimoHarness
from mimo.models import ReasoningEffort, RenderQuality, RunRequest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim-mimo",
        description="Produce complete Math-To-Manim films through the MiMo 2.6 tool-calling chain.",
    )
    parser.add_argument("--version", action="version", version=f"math-to-manim-mimo {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Create one complete film-production run bundle")
    run.add_argument("prompt")
    run.add_argument("--render", action="store_true")
    run.add_argument("-q", "--quality", default="l", choices=get_args(RenderQuality))
    run.add_argument("--reasoning-effort", default="high", choices=get_args(ReasoningEffort))
    run.add_argument("--max-repairs", default=2, type=int, choices=range(0, 6))
    run.add_argument("--offline", action="store_true")

    runs = sub.add_parser("runs", help="List recent MiMo run manifests")
    runs.add_argument("--limit", type=int, default=20)

    resume = sub.add_parser("resume", help="Resume a MiMo run (cached stages are kept)")
    resume.add_argument("run_id")
    resume.add_argument("--from", dest="from_stage", choices=STAGE_NAMES)

    status = sub.add_parser("status", help="Show one MiMo run manifest")
    status.add_argument("run_id")

    sub.add_parser("doctor", help="Check MiMo endpoint reachability and key status")
    return parser


def _doctor(client: MimoClient) -> int:
    ready, message = api_key_status()
    print(message)
    try:
        reply = client.ping()
        print(f"endpoint: {client.endpoint}")
        print(f"model: {client.model}")
        print(f"ping: {reply.strip()[:80]}")
    except MimoClientError as exc:
        print(f"not ready: {exc}")
        print("offline mode remains available: math-to-manim-mimo run \"...\" --offline")
        return 0 if ready else 1
    print("ready: MiMo tool-calling chain")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    harness = MimoHarness()
    if args.command == "run":
        response = harness.run(
            RunRequest(
                prompt=args.prompt,
                reasoning_effort=args.reasoning_effort,
                offline=args.offline,
                render=args.render,
                quality=args.quality,
                max_repairs=args.max_repairs,
            )
        )
        print(json.dumps(response, indent=2))
        return 0
    if args.command == "runs":
        for manifest in harness.list_runs(limit=max(1, args.limit)):
            print(f"{manifest.run_id}\t{manifest.status}\t{manifest.prompt}")
        return 0
    if args.command == "resume":
        print(json.dumps(harness.resume(args.run_id, from_stage=args.from_stage), indent=2))
        return 0
    if args.command == "status":
        print(harness.get_run(args.run_id).model_dump_json(indent=2))
        return 0
    return _doctor(harness.client)


if __name__ == "__main__":
    raise SystemExit(main())
