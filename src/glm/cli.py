"""Command line for the independent GLM-native Math To Manim silo.

stdout carries only the command's output (the run manifest as JSON, the run
list, a manifest); progress lines go to stderr.
"""

from __future__ import annotations

import argparse
import json
import sys

from glm import __version__
from glm.client import GlmClient, GlmSettings, api_key_status, opencode_auth_path
from glm.models import MAX_REPAIRS_LIMIT, QUALITIES, REASONING_EFFORTS, RunRequest
from glm.service import GlmService


def build_parser() -> argparse.ArgumentParser:
    fields = RunRequest.model_fields
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
    run.add_argument("-q", "--quality", default=fields["quality"].default, choices=list(QUALITIES))
    run.add_argument(
        "--reasoning-effort",
        default=None,
        choices=list(REASONING_EFFORTS),
    )
    run.add_argument(
        "--max-repairs",
        default=fields["max_repairs"].default,
        type=int,
        choices=range(0, MAX_REPAIRS_LIMIT + 1),
    )
    run.add_argument("--offline", action="store_true")

    runs = sub.add_parser("runs", help="List recent GLM run manifests")
    runs.add_argument("--limit", type=int, default=20)

    status = sub.add_parser("status", help="Show one GLM run manifest")
    status.add_argument("run_id")

    sub.add_parser("doctor", help="Ping Z.ai when a key is set; never prints the key")
    return parser


def _doctor(settings: GlmSettings) -> int:
    ok, detail = api_key_status()
    print(
        f"endpoint chat/completions under {settings.base_url}; "
        f"model={settings.model}; effort={settings.reasoning_effort}"
    )
    if not ok:
        print(f"not ready: {detail}")
        print(f"opencode auth expected at: {opencode_auth_path()}")
        return 1
    client = GlmClient.from_env()
    ping_ok, ping_detail = client.ping()
    if not ping_ok:
        print(f"not ready: {ping_detail}")
        return 1
    print(f"ready: {ping_detail}; key source: {client.key_source}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "doctor":
        return _doctor(GlmSettings.from_env())
    service = GlmService()
    if args.command == "run":
        response = service.run(
            RunRequest(
                prompt=args.prompt,
                image=args.image,
                reasoning_effort=args.reasoning_effort or GlmSettings.from_env().reasoning_effort,
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
    print(service.get_run(args.run_id).model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
