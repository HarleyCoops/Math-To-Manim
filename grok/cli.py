"""Command line for the independent Grok-native Math To Manim silo."""

from __future__ import annotations

import argparse
import json
import os
import subprocess

from grok import __version__
from grok.backends.grok_build import describe_auth, login_command
from grok.client import (
    XAIClient,
    XAIClientError,
    api_key_status,
    resolve_model,
    resolve_reasoning_effort,
)
from grok.envfile import load_local_env
from grok.models import REASONING_EFFORTS, RunRequest
from grok.service import GrokService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim-grok",
        description="Produce Manim explainers through Grok on the xAI Responses API or a cached grok login.",
    )
    parser.add_argument("--version", action="version", version=f"math-to-manim-grok {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Create one complete Grok film-production run")
    run.add_argument("prompt")
    run.add_argument("--image", help="Photographed homework page or diagram")
    run.add_argument("--render", action="store_true")
    run.add_argument("-q", "--quality", default="l", choices=["l", "m", "h", "p", "k"])
    run.add_argument("--reasoning-effort", default=None, choices=list(REASONING_EFFORTS))
    run.add_argument("--max-repairs", default=2, type=int, choices=range(0, 6))
    run.add_argument("--max-revisions", default=2, type=int, choices=range(0, 6))
    run.add_argument("--offline", action="store_true")
    run.add_argument("--backend", choices=["xai-api", "grok-build", "offline"], default=None)
    run.add_argument("--model", default=None, help="Responses model id (default: XAI_MODEL or grok-4.7)")
    run.add_argument("--review", choices=["advisory", "gated", "off"], default="advisory")
    run.add_argument("--render-timeout", type=float, default=7200)
    run.add_argument("--min-duration", type=float, default=20)
    run.add_argument("--max-duration", type=float, default=240)

    runs = sub.add_parser("runs", help="List recent Grok run manifests")
    runs.add_argument("--limit", type=int, default=20)

    status = sub.add_parser("status", help="Show one Grok run manifest")
    status.add_argument("run_id")

    resume = sub.add_parser("resume", help="Continue a hash-bound run from the first stale stage")
    resume.add_argument("run_id")
    resume.add_argument("--render", action="store_true")
    resume.add_argument("--review", choices=["advisory", "gated", "off"], default=None)
    resume.add_argument("-q", "--quality", default=None, choices=["l", "m", "h", "p", "k"])

    local = sub.add_parser(
        "render-existing",
        help="Render a saved scene with zero model calls",
    )
    local.add_argument("run_id")
    local.add_argument("-q", "--quality", default="l", choices=["l", "m", "h", "p", "k"])
    local.add_argument("--render-timeout", type=float, default=7200)

    login = sub.add_parser("login", help="Cache a Grok Build login by running grok login")
    login.add_argument("--device-auth", action="store_true")

    doctor = sub.add_parser("doctor", help="Report auth source and ping xAI without printing secrets")
    doctor.add_argument("--backend", choices=["xai-api", "grok-build"], default="xai-api")

    server = sub.add_parser("serve-mcp", help="Serve the Grok MCP tools over stdio or HTTP")
    server.add_argument("--transport", choices=["stdio", "http", "streamable-http"], default="stdio")
    server.add_argument("--port", type=int, default=8643)
    return parser


def _doctor(backend: str) -> int:
    described = describe_auth(backend)
    model = resolve_model()
    effort = resolve_reasoning_effort()
    key = os.getenv("XAI_API_KEY", "")
    lines = [
        f"backend={described['backend']}",
        f"auth_source={described['auth_source']}",
        f"grok_login={described['grok_login']}",
        f"model={model}",
        f"reasoning_effort={effort}",
    ]
    if backend == "grok-build" and described["auth_source"] == "grok-login":
        detail = "cached grok login; live token was not printed"
        print("ready: " + detail + "; " + "; ".join(lines))
        return 0
    if described["auth_source"] == "none":
        print("not ready: " + described["key_detail"] + "; " + "; ".join(lines))
        return 1
    if backend == "xai-api":
        ok, key_detail = api_key_status()
        if not ok:
            print(f"not ready: {key_detail}; " + "; ".join(lines))
            return 1
        client = XAIClient()
        ok, detail = client.ping()
        if key and key in detail:
            print("not ready: doctor refused to describe the key")
            return 1
        if not ok:
            print(f"not ready: {detail}; " + "; ".join(lines))
            print(f"endpoint: {client.base_url}/responses")
            return 1
        print(f"ready: {detail}; " + "; ".join(lines))
        print(f"endpoint: {client.base_url}/responses")
        return 0
    ok, detail = XAIClient().ping()
    if key and key in detail:
        print("not ready: doctor refused to describe the key")
        return 1
    if not ok:
        print(f"not ready: {detail}; " + "; ".join(lines))
        return 1
    print(f"ready: {detail}; " + "; ".join(lines))
    return 0


def _request_from_run_args(args) -> RunRequest:
    offline = bool(args.offline or args.backend == "offline")
    backend = "offline" if offline else (args.backend or "xai-api")
    return RunRequest(
        prompt=args.prompt,
        image=args.image,
        reasoning_effort=args.reasoning_effort or resolve_reasoning_effort(),
        offline=offline,
        backend=backend,
        render=args.render,
        quality=args.quality,
        max_repairs=args.max_repairs,
        max_revisions=args.max_revisions,
        review=args.review,
        render_timeout=args.render_timeout,
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        model=args.model or None,
    )


def main(argv: list[str] | None = None) -> int:
    load_local_env()
    args = build_parser().parse_args(argv)
    service = GrokService()
    if args.command == "run":
        response = service.run(_request_from_run_args(args))
        print(json.dumps(response, indent=2))
        return 0
    if args.command == "runs":
        for manifest in service.list_runs(limit=max(1, args.limit)):
            print(f"{manifest.run_id}\t{manifest.status}\t{manifest.prompt}")
        return 0
    if args.command == "status":
        print(service.get_run(args.run_id).model_dump_json(indent=2))
        return 0
    if args.command == "resume":
        overrides = {}
        if args.render:
            overrides["render"] = True
        if args.review:
            overrides["review"] = args.review
        if args.quality:
            overrides["quality"] = args.quality
        print(json.dumps(service.resume(args.run_id, **overrides), indent=2))
        return 0
    if args.command == "render-existing":
        print(
            json.dumps(
                service.render_existing(
                    args.run_id,
                    quality=args.quality,
                    render_timeout=args.render_timeout,
                ),
                indent=2,
            )
        )
        return 0
    if args.command == "login":
        try:
            command = login_command(device_auth=args.device_auth)
        except XAIClientError as exc:
            print(f"not ready: {exc}")
            return 1
        return subprocess.call(command)
    if args.command == "serve-mcp":
        from grok.mcp_server import main as serve

        transport = "streamable-http" if args.transport in {"http", "streamable-http"} else "stdio"
        serve(transport, args.port)
        return 0
    return _doctor(args.backend)


if __name__ == "__main__":
    raise SystemExit(main())
