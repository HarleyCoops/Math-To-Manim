"""Command line for the independent GLM-native Math To Manim silo."""

from __future__ import annotations

import argparse
import json
import os

from glm import __version__
from glm.client import (
    DEFAULT_MODEL,
    DEFAULT_REASONING_EFFORT,
    GlmClient,
    api_key_status,
    opencode_auth_path,
)
from glm.models import REASONING_EFFORTS, RunRequest
from glm.service import GlmService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim-glm",
        description=(
            "Produce Manim explainers through the Z.ai Coding Plan "
            "(glm-5.3-flash, thinking always on)."
        ),
    )
    parser.add_argument("--version", action="version", version=f"math-to-manim-glm {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Create one complete GLM film-production run")
    run.add_argument("prompt")
    run.add_argument("--image", help="Photographed homework page or diagram")
    run.add_argument("--render", action="store_true")
    run.add_argument("-q", "--quality", default="l", choices=["l", "m", "h", "p", "k"])
    run.add_argument(
        "--reasoning-effort",
        default=DEFAULT_REASONING_EFFORT,
        choices=list(REASONING_EFFORTS),
    )
    run.add_argument("--max-repairs", default=2, type=int, choices=range(0, 6))
    run.add_argument("--offline", action="store_true")

    runs = sub.add_parser("runs", help="List recent GLM run manifests")
    runs.add_argument("--limit", type=int, default=20)

    status = sub.add_parser("status", help="Show one GLM run manifest")
    status.add_argument("run_id")

    sub.add_parser("doctor", help="Ping Z.ai when a key is set; never prints the key")
    return parser


def _doctor() -> int:
    ok, detail = api_key_status()
    model = os.getenv("GLM_MODEL", DEFAULT_MODEL)
    effort = os.getenv("GLM_REASONING_EFFORT", DEFAULT_REASONING_EFFORT)
    print(f"endpoint chat/completions under {GlmClient().base_url}; model={model}; effort={effort}")
    if not ok:
        print(f"not ready: {detail}")
        print(f"opencode auth expected at: {opencode_auth_path()}")
        return 1
    client = GlmClient()
    ping_ok, ping_detail = client.ping()
    if not ping_ok:
        print(f"not ready: {ping_detail}")
        return 1
    print(f"ready: {ping_detail}; key source: {client.key_source}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = GlmService()
    if args.command == "run":
        response = service.run(
            RunRequest(
                prompt=args.prompt,
                image=args.image,
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
        for manifest in service.list_runs(limit=max(1, args.limit)):
            print(f"{manifest.run_id}\t{manifest.status}\t{manifest.prompt}")
        return 0
    if args.command == "status":
        print(service.get_run(args.run_id).model_dump_json(indent=2))
        return 0
    return _doctor()


if __name__ == "__main__":
    raise SystemExit(main())
