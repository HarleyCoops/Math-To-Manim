"""Command-line entrypoint for Math-To-Manim."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Sequence

from math_to_manim.config import RuntimeConfig, parse_command
from math_to_manim.agents import RenderAgent, StaticReviewAgent, VideoReviewAgent
from math_to_manim.eval_runner import EvalSuiteResult, run_prompt_suite
from math_to_manim.pipeline.run_bundle import RunBundle
from math_to_manim.pipeline.runner import AnimationPipeline
from math_to_manim.schemas import AnimationPackage, RenderResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="math-to-manim")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate a typed animation run")
    generate.add_argument("prompt", help="Short educational animation prompt")
    generate.add_argument("--audience-level", default="high_school")
    generate.add_argument("--duration", type=int, default=60)
    generate.add_argument("--style", default="cinematic")
    generate.add_argument("--quality", default=None, help="Manim quality flag: l, m, h, p, or k")
    generate.add_argument("--manim-command", default=None, help='Manim command override, e.g. "python -m manim"')
    generate.add_argument("--model", default=None)
    generate.add_argument("--runs-dir", type=Path, default=None)
    generate.add_argument(
        "--reference-image",
        action="append",
        type=Path,
        default=None,
        help="Reference image to copy into the run bundle; may be repeated",
    )
    generate.add_argument("--no-render", action="store_true", help="Skip Manim execution")
    generate.add_argument("--deterministic", action="store_true", help="Do not call model adapters")
    generate.add_argument(
        "--codegen-provider",
        choices=["openai-agents", "codex-cli"],
        default=None,
        help="Provider for Manim codegen/repair stages; codex-cli uses local Codex subscription login",
    )
    generate.add_argument("--codex-full-auto", action="store_true", help="Pass --full-auto to codex exec")
    generate.add_argument("--json", action="store_true", help="Print the full AnimationPackage JSON")

    inspect_run = subparsers.add_parser("inspect-run", help="Print a run manifest")
    inspect_run.add_argument("run_dir", type=Path)

    render_run = subparsers.add_parser("render-run", help="Render an existing run bundle")
    render_run.add_argument("run_dir", type=Path)
    render_run.add_argument("--quality", default=None, help="Manim quality flag: l, m, h, p, or k")
    render_run.add_argument("--manim-command", default=None, help='Manim command override, e.g. "python -m manim"')

    review_run = subparsers.add_parser("review-run", help="Review an existing rendered run bundle")
    review_run.add_argument("run_dir", type=Path)

    recover_render = subparsers.add_parser("recover-render", help="Validate, render, review, and record recovery artifacts")
    recover_render.add_argument("run_dir", type=Path)
    recover_render.add_argument("--quality", default=None, help="Manim quality flag: l, m, h, p, or k")
    recover_render.add_argument("--manim-command", default=None, help='Manim command override, e.g. "python -m manim"')

    eval_suite = subparsers.add_parser("eval-suite", help="Run a YAML prompt eval suite")
    eval_suite.add_argument("suite_path", type=Path)
    eval_suite.add_argument("--runs-dir", type=Path, default=None)
    eval_suite.add_argument("--render", action="store_true", help="Require a successful low-quality render")
    eval_suite.add_argument("--quality", default=None, help="Manim quality flag when --render is set")
    eval_suite.add_argument("--manim-command", default=None, help='Manim command override, e.g. "python -m manim"')
    eval_suite.add_argument("--model-backed", action="store_true", help="Use configured model stages instead of deterministic mode")
    eval_suite.add_argument("--json", action="store_true", help="Print the full eval result JSON")

    return parser


def run_generate(args: argparse.Namespace) -> int:
    config = _config_from_args(args)

    pipeline = AnimationPipeline(config=config)
    package = pipeline.generate(
        prompt=args.prompt,
        audience_level=args.audience_level,
        desired_duration=args.duration,
        style=args.style,
        render=not args.no_render,
        reference_images=args.reference_image,
    )
    if args.json:
        print(json.dumps(package.to_public_dict(), indent=2))
    else:
        print(_format_generate_summary(package))
    return 0


def run_inspect(args: argparse.Namespace) -> int:
    manifest = args.run_dir / "manifest.json"
    if not manifest.exists():
        raise SystemExit(f"No manifest found at {manifest}")
    print(manifest.read_text(encoding="utf-8"))
    return 0


def run_render_run(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    bundle = RunBundle(args.run_dir)
    generated = bundle.load_current_generated_code()
    scene_path = bundle.generated_scene_path

    validation = StaticReviewAgent(config).run((generated, scene_path))
    bundle.save_artifact("validation_report", validation)
    if validation.is_successful:
        render = RenderAgent(config).run((generated, scene_path, config.default_quality))
    else:
        render = RenderResult(
            status="skipped",
            scene_name=generated.scene_name,
            output_path=None,
            command=[],
            stdout="",
            stderr="static validation did not pass",
            metadata={"skipped": True, "reason": "static_validation_failed"},
        )
    bundle.save_artifact("render_result", render)
    print(_format_render_run_summary(bundle, validation, render))
    return 0 if render.status == "succeeded" else 1


def run_review_run(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    bundle = RunBundle(args.run_dir)
    render = bundle.load_artifact("render_result", RenderResult)
    review = VideoReviewAgent(config).run(render)
    bundle.save_artifact("review_report", review)
    print(_format_review_run_summary(bundle, review))
    return 0


def run_recover_render(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    bundle = RunBundle(args.run_dir)
    generated = bundle.load_current_generated_code()
    scene_path = bundle.generated_scene_path

    validation = StaticReviewAgent(config).run((generated, scene_path))
    bundle.save_artifact("validation_report", validation)
    if validation.is_successful:
        render = RenderAgent(config).run((generated, scene_path, config.default_quality))
    else:
        render = RenderResult(
            status="skipped",
            scene_name=generated.scene_name,
            output_path=None,
            command=[],
            stdout="",
            stderr="static validation did not pass",
            metadata={"skipped": True, "reason": "static_validation_failed"},
        )
    bundle.save_artifact("render_result", render)

    review = VideoReviewAgent(config).run(render)
    bundle.save_artifact("review_report", review)
    recovery_manifest = _write_recovery_manifest(bundle, validation, render, review)

    print(_format_recover_render_summary(bundle, validation, render, review, recovery_manifest))
    return 0 if render.status == "succeeded" else 1


def run_eval_suite(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    config = RuntimeConfig(**{**config.__dict__, "deterministic": bool(not args.model_backed)})
    result = run_prompt_suite(args.suite_path, config=config, runs_dir=args.runs_dir, render=args.render)
    if args.json:
        print(json.dumps(result.to_public_dict(), indent=2))
    else:
        print(_format_eval_suite_summary(result))
    return 0 if result.passed else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "generate":
        return run_generate(args)
    if args.command == "inspect-run":
        return run_inspect(args)
    if args.command == "render-run":
        return run_render_run(args)
    if args.command == "review-run":
        return run_review_run(args)
    if args.command == "recover-render":
        return run_recover_render(args)
    if args.command == "eval-suite":
        return run_eval_suite(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


def _config_from_args(args: argparse.Namespace) -> RuntimeConfig:
    config = RuntimeConfig.from_env()
    if getattr(args, "model", None):
        config = RuntimeConfig(**{**config.__dict__, "model": args.model})
    if getattr(args, "runs_dir", None):
        config = RuntimeConfig(**{**config.__dict__, "runs_dir": args.runs_dir})
    if getattr(args, "quality", None):
        config = RuntimeConfig(**{**config.__dict__, "default_quality": args.quality})
    if getattr(args, "manim_command", None):
        config = RuntimeConfig(**{**config.__dict__, "manim_command": parse_command(args.manim_command)})
    if getattr(args, "deterministic", False):
        config = RuntimeConfig(**{**config.__dict__, "deterministic": True})
    if getattr(args, "codegen_provider", None):
        config = RuntimeConfig(**{**config.__dict__, "codegen_provider": args.codegen_provider})
    if getattr(args, "codex_full_auto", False):
        config = RuntimeConfig(**{**config.__dict__, "codex_full_auto": True})
    return config


def _format_generate_summary(package: AnimationPackage) -> str:
    render = package.render_result
    review = package.video_review_report
    metadata = package.metadata
    manifest_path = metadata.get("reproducibility_manifest")
    run_dir = str(Path(manifest_path).parent) if manifest_path else None

    lines = [
        "Math-To-Manim run complete",
        f"Run dir: {run_dir or 'unknown'}",
    ]
    if render is not None:
        lines.extend(
            [
                f"Scene: {render.scene_name or 'unknown'}",
                f"Render: {render.status}",
                f"Video: {render.output_path or 'not produced'}",
            ]
        )
    if package.validation_report is not None:
        lines.append(f"Static validation: {package.validation_report.status}")
    if review is not None:
        render_integrity = review.metadata.get("render_integrity_passed")
        draft = review.metadata.get("draft_review")
        draft_status = "needs editor review" if review.metadata.get("requires_editor_review") else "not created"
        if isinstance(draft, dict) and not review.metadata.get("requires_editor_review"):
            draft_status = "complete"
        lines.extend(
            [
                f"Draft review: {draft_status}",
                f"Render integrity: {render_integrity if render_integrity is not None else 'not checked'}",
                f"Review score: {review.score}",
            ]
        )
        if isinstance(draft, dict):
            lines.extend(
                [
                    f"Draft notes: {draft.get('notes_path') or 'not produced'}",
                    f"Contact sheet: {draft.get('contact_sheet') or 'not produced'}",
                ]
            )
        if review.recommendations:
            lines.append("Recommendations:")
            lines.extend(f"- {recommendation}" for recommendation in review.recommendations[:6])

    lines.extend(
        [
            f"Manifest: {manifest_path or 'not produced'}",
            "Use --json to print the complete typed package.",
        ]
    )
    return "\n".join(lines)


def _format_render_run_summary(bundle: RunBundle, validation: object, render: RenderResult) -> str:
    return "\n".join(
        [
            "Math-To-Manim render-run complete",
            f"Run dir: {bundle.run_dir}",
            f"Static validation: {getattr(validation, 'status', 'unknown')}",
            f"Scene: {render.scene_name or 'unknown'}",
            f"Render: {render.status}",
            f"Video: {render.output_path or 'not produced'}",
            f"Manifest: {bundle.manifest_path}",
        ]
    )


def _format_review_run_summary(bundle: RunBundle, review: object) -> str:
    metadata = getattr(review, "metadata", {}) or {}
    draft = metadata.get("draft_review") if isinstance(metadata, dict) else None
    return "\n".join(
        [
            "Math-To-Manim review-run complete",
            f"Run dir: {bundle.run_dir}",
            f"Review score: {getattr(review, 'score', None)}",
            f"Approved: {getattr(review, 'approved', False)}",
            f"Draft notes: {(draft or {}).get('notes_path') if isinstance(draft, dict) else 'not produced'}",
            f"Contact sheet: {(draft or {}).get('contact_sheet') if isinstance(draft, dict) else 'not produced'}",
            f"Manifest: {bundle.manifest_path}",
        ]
    )


def _write_recovery_manifest(bundle: RunBundle, validation: object, render: RenderResult, review: object) -> Path:
    metadata = getattr(review, "metadata", {}) or {}
    draft = metadata.get("draft_review") if isinstance(metadata, dict) else None
    path = bundle.run_dir / "recovery_manifest.json"
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(bundle.run_dir),
        "static_validation": getattr(validation, "status", "unknown"),
        "render_status": render.status,
        "review_score": getattr(review, "score", None),
        "approved": getattr(review, "approved", False),
        "artifacts": {
            "validation_report": str(bundle.run_dir / "validation_report.json"),
            "render_result": str(bundle.run_dir / "render_result.json"),
            "review_report": str(bundle.run_dir / "review_report.json"),
            "draft_notes": (draft or {}).get("notes_path") if isinstance(draft, dict) else None,
            "contact_sheet": (draft or {}).get("contact_sheet") if isinstance(draft, dict) else None,
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    bundle.update_manifest("recovery_manifest")
    return path


def _format_recover_render_summary(
    bundle: RunBundle,
    validation: object,
    render: RenderResult,
    review: object,
    recovery_manifest: Path,
) -> str:
    metadata = getattr(review, "metadata", {}) or {}
    draft = metadata.get("draft_review") if isinstance(metadata, dict) else None
    return "\n".join(
        [
            "Math-To-Manim recover-render complete",
            f"Run dir: {bundle.run_dir}",
            f"Static validation: {getattr(validation, 'status', 'unknown')}",
            f"Scene: {render.scene_name or 'unknown'}",
            f"Render: {render.status}",
            f"Video: {render.output_path or 'not produced'}",
            f"Review score: {getattr(review, 'score', None)}",
            f"Draft notes: {(draft or {}).get('notes_path') if isinstance(draft, dict) else 'not produced'}",
            f"Contact sheet: {(draft or {}).get('contact_sheet') if isinstance(draft, dict) else 'not produced'}",
            f"Recovery manifest: {recovery_manifest}",
            f"Manifest: {bundle.manifest_path}",
        ]
    )


def _format_eval_suite_summary(result: EvalSuiteResult) -> str:
    lines = [
        "Math-To-Manim eval-suite complete",
        f"Suite: {result.suite_id}",
        f"Cases: {result.passed_count}/{len(result.cases)} passed",
        f"Runs dir: {result.runs_dir}",
    ]
    for case in result.cases:
        status = "PASS" if case.passed else "FAIL"
        lines.append(f"- {status} {case.case_id}: {case.run_dir or 'no run'}")
        for check in case.checks:
            if not check.passed:
                lines.append(f"  - {check.name}: {check.message}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
