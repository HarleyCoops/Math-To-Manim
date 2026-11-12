"""Command line for the independent Codex CLI-native Sol silo."""

from __future__ import annotations

import argparse
import json

from sol import __version__
from sol.agents import STAGE_NAMES
from sol.client import CodexCli, CodexCliError
from sol.harness import SolHarness
from sol.models import (
    EVALUATOR_CHOICES,
    MAX_REPAIRS_LIMIT,
    QUALITY_CHOICES,
    REASONING_EFFORT_CHOICES,
    RunRequest,
)


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
    run.add_argument("-q", "--quality", default="l", choices=QUALITY_CHOICES)
    run.add_argument(
        "--reasoning-effort",
        default=None,
        choices=REASONING_EFFORT_CHOICES,
        help="Override every stage's reasoning effort (default: each stage's own)",
    )
    run.add_argument("--max-repairs", default=2, type=int, choices=range(0, MAX_REPAIRS_LIMIT + 1))
    run.add_argument("--offline", action="store_true")
    run.add_argument("--evaluator", choices=EVALUATOR_CHOICES,
                     default="cinematographer", help="Reviewer for rendered runs")

    runs = sub.add_parser("runs", help="List recent Sol run manifests")
    runs.add_argument("--limit", type=int, default=20)

    resume = sub.add_parser("resume", help="Resume a staged Sol run")
    resume.add_argument("run_id")
    resume.add_argument("--from", dest="from_stage", choices=STAGE_NAMES)

    status = sub.add_parser("status", help="Show one Sol run manifest")
    status.add_argument("run_id")

    sub.add_parser("doctor", help="Check the Codex executable and cached ChatGPT login")
    return parser


def _doctor() -> int:
    client = CodexCli()
    try:
        ready, lines = client.check_login()
    except CodexCliError as exc:
        print(f"not ready: {exc}")
        return 1
    print("\n".join(lines))
    if not ready:
        print("not ready: run `codex login` with your ChatGPT account")
        return 1
    print(f"ready: Codex CLI + cached ChatGPT login; model={client.model}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "doctor":
        return _doctor()
    harness = SolHarness()
    if args.command == "run":
        response = harness.run(RunRequest(
            prompt=args.prompt,
            reasoning_effort=args.reasoning_effort,
            offline=args.offline,
            render=args.render,
            quality=args.quality,
            max_repairs=args.max_repairs,
            evaluator=args.evaluator,
        ))
        print(json.dumps(response, indent=2))
        return 0
    if args.command == "runs":
        for manifest in harness.list_runs(limit=max(1, args.limit)):
            print(f"{manifest.run_id}\t{manifest.status}\t{manifest.prompt}")
        return 0
    if args.command == "resume":
        print(json.dumps(harness.resume(args.run_id, from_stage=args.from_stage), indent=2))
        return 0
    print(harness.get_run(args.run_id).model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
