"""Single-CLI Gemini 4 Neon pipeline harness.

Replaces six sequential stage calls with one cohesive Neon reasoning + tool-use
run: ``plan + verify_math + codegen -> check_scene -> render (+repair) -> publish``.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neon.backends import GenAINeonBackend, NeonBackendError, select_backend
from neon.models import (
    MANIFEST_FILE,
    PLAN_FILE,
    SCENE_FILE,
    TOOL_LOG_FILE,
    VALIDATION_FILE,
    NeonManifest,
    NeonPlan,
    NeonRequest,
    ToolEvent,
    utc_now,
)
from neon.tools import check_scene, publish_film, render_scene


def _stderr_progress(msg: str) -> None:
    print(msg, file=sys.stderr)


def _slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug[:max_len].strip("-")) or "neon-film"


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_runs_dir() -> Path:
    return default_repo_root() / "runs" / "neon"


class NeonHarness:
    """Orchestrates a complete Gemini 4 Neon Math-To-Manim run."""

    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        repo_root: Path | None = None,
        progress: Callable[[str], None] = _stderr_progress,
    ):
        self.repo_root = Path(repo_root) if repo_root else default_repo_root()
        self.runs_dir = Path(runs_dir) if runs_dir else (self.repo_root / "runs" / "neon")
        self.progress = progress

    def _write_manifest(self, run_dir: Path, manifest: NeonManifest) -> None:
        manifest.status.updated_utc = utc_now()
        (run_dir / MANIFEST_FILE).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

    def _append_tool_events(self, run_dir: Path, manifest: NeonManifest, events: list[ToolEvent]) -> None:
        if not events:
            return
        log_path = run_dir / TOOL_LOG_FILE
        with log_path.open("a", encoding="utf-8") as fh:
            for ev in events:
                fh.write(ev.model_dump_json() + "\n")
        manifest.tool_calls_count += len(events)

    def run(self, request: NeonRequest) -> dict[str, Any]:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        slug = _slugify(request.slug or request.prompt)
        run_id = f"{ts}-{slug}"
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "request.json").write_text(request.model_dump_json(indent=2), encoding="utf-8")

        manifest = NeonManifest(
            run_id=run_id,
            model=request.model,
            backend=request.backend,
            prompt=request.prompt,
        )
        self._write_manifest(run_dir, manifest)

        try:
            workspace = Path(request.workspace) if request.workspace else None
            backend = select_backend(
                request.backend,
                model=request.model,
                thinking_budget=request.thinking_budget,
                workspace=workspace,
            )
            manifest.backend = backend.name
            manifest.status.stage = "neon-reason-and-codegen"
            self._write_manifest(run_dir, manifest)
            self.progress(f"  [neon:{backend.name}] reasoning + tool verification ({request.model})...")

            gen = backend.generate(request.prompt, slug=slug)
            plan: NeonPlan = gen.plan
            source: str = gen.source
            self._append_tool_events(run_dir, manifest, gen.tool_events)

            (run_dir / PLAN_FILE).write_text(plan.model_dump_json(indent=2), encoding="utf-8")
            (run_dir / SCENE_FILE).write_text(source, encoding="utf-8")
            manifest.scene_file = str(run_dir / SCENE_FILE)

            # Static validation + optional repair loop
            manifest.status.stage = "validate"
            self._write_manifest(run_dir, manifest)
            validation = check_scene(source)
            repairs = 0
            while not validation["passed"] and repairs < request.max_repairs and isinstance(backend, GenAINeonBackend):
                repairs += 1
                manifest.status.stage = f"repair-{repairs}"
                manifest.repairs = repairs
                self._write_manifest(run_dir, manifest)
                self.progress(f"  [neon] repairing scene (attempt {repairs}/{request.max_repairs})...")
                source, repair_events = backend.repair(source, validation["errors"])
                self._append_tool_events(run_dir, manifest, repair_events)
                (run_dir / SCENE_FILE).write_text(source, encoding="utf-8")
                validation = check_scene(source)

            (run_dir / VALIDATION_FILE).write_text(json.dumps(validation, indent=2), encoding="utf-8")
            if not validation["passed"]:
                manifest.status.run = "failed"
                manifest.status.outcome = "validation_failed"
                manifest.status.error = "; ".join(validation["errors"])
                self._write_manifest(run_dir, manifest)
                return json.loads(manifest.model_dump_json())

            scene_class = validation["scene_class"]
            manifest.scene_class = scene_class
            self.progress(f"  [neon] validated {scene_class} ({validation['line_count']} lines)")

            if not request.render:
                manifest.status.run = "completed"
                manifest.status.stage = "done"
                manifest.status.outcome = "scene_ready"
                self._write_manifest(run_dir, manifest)
                return json.loads(manifest.model_dump_json())

            # Manim render
            manifest.status.stage = "render"
            self._write_manifest(run_dir, manifest)
            self.progress(f"  [neon] rendering {scene_class} with Manim (-q{request.quality})...")
            render_res = render_scene(run_dir, scene_class, quality=request.quality)
            self._append_tool_events(
                run_dir,
                manifest,
                [
                    ToolEvent(
                        tool="render_scene",
                        ok=bool(render_res.get("ok")),
                        input={"scene_class": scene_class, "quality": request.quality},
                        output=render_res,
                    )
                ],
            )
            if not render_res.get("ok"):
                manifest.status.run = "failed"
                manifest.status.outcome = "render_failed"
                manifest.status.error = str(render_res.get("error", "render failed"))
                self._write_manifest(run_dir, manifest)
                return json.loads(manifest.model_dump_json())

            manifest.video_path = render_res.get("video_path")
            manifest.duration_seconds = render_res.get("duration_seconds")
            manifest.resolution = render_res.get("resolution")
            manifest.contact_sheet_path = render_res.get("contact_sheet_path")
            manifest.gif_path = render_res.get("gif_path")
            self.progress(
                f"  [neon] rendered {manifest.video_path} "
                f"({manifest.duration_seconds}s, {manifest.resolution})"
            )

            if request.publish:
                manifest.status.stage = "publish"
                self._write_manifest(run_dir, manifest)
                pub_slug = request.slug or plan.slug or slug
                published = publish_film(run_dir, self.repo_root, pub_slug, plan, manifest)
                manifest.published_assets = published
                self._append_tool_events(
                    run_dir,
                    manifest,
                    [
                        ToolEvent(
                            tool="publish_film",
                            ok=True,
                            input={"slug": pub_slug},
                            output=published,
                        )
                    ],
                )
                manifest.status.run = "completed"
                manifest.status.stage = "done"
                manifest.status.outcome = "film_published"
                self._write_manifest(run_dir, manifest)
                self.progress(f"  [neon] published showcase assets under docs/assets/{pub_slug}/")
                return json.loads(manifest.model_dump_json())

            manifest.status.run = "completed"
            manifest.status.stage = "done"
            manifest.status.outcome = "film_ready"
            self._write_manifest(run_dir, manifest)
            return json.loads(manifest.model_dump_json())

        except NeonBackendError as exc:
            manifest.status.run = "failed"
            manifest.status.outcome = "needs_operator_input" if "operator workspace needs" in str(exc) else "pipeline_failed"
            manifest.status.error = str(exc)
            self._write_manifest(run_dir, manifest)
            return json.loads(manifest.model_dump_json())
        except Exception as exc:  # noqa: BLE001
            manifest.status.run = "failed"
            manifest.status.outcome = "pipeline_failed"
            manifest.status.error = str(exc)
            self._write_manifest(run_dir, manifest)
            raise
