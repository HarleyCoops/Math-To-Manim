"""Complete MiMo 2.6 tool-calling Math-To-Manim run harness."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from mimo.client import DEFAULT_MODEL, MimoClient
from mimo.models import MimoRunResult, RunManifest, RunRequest
from mimo.offline import write_offline_bundle
from mimo.staged import ToolCallingPipeline
from mimo.validation import validate_run

REPO_ROOT = Path(__file__).resolve().parents[1]


def default_runs_dir() -> Path:
    return REPO_ROOT / "runs" / "mimo"


class MimoHarness:
    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: MimoClient | None = None,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.client = client or MimoClient()

    def _create_run_dir(self, prompt: str) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:48] or "film"
        candidate = self.runs_dir / f"{stamp}-{slug}"
        suffix = 1
        while candidate.exists():
            suffix += 1
            candidate = self.runs_dir / f"{stamp}-{slug}-{suffix}"
        candidate.mkdir(parents=True)
        return candidate

    @staticmethod
    def _write_manifest(path: Path, manifest: RunManifest) -> None:
        temporary = path.with_suffix(".tmp")
        temporary.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(path)

    def run(self, request: RunRequest) -> dict:
        self.client.reasoning_effort = request.reasoning_effort
        run_dir = self._create_run_dir(request.prompt)
        now = datetime.now(timezone.utc).isoformat()
        manifest = RunManifest(
            schema_version=1,
            run_id=run_dir.name,
            prompt=request.prompt,
            model=self.client.model,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            created_utc=now,
            artifacts={"validation": "validation.json", "scene": "mimo_scene.py"},
            status_detail={"validation": "pending"},
        )
        manifest_path = run_dir / "manifest.json"
        self._write_manifest(manifest_path, manifest)
        (run_dir / "request.json").write_text(request.model_dump_json(indent=2), encoding="utf-8")

        try:
            if request.offline:
                result = write_offline_bundle(run_dir, request)
                manifest.attempts.append({"attempt": 0, "mode": "offline", "status": "completed"})
            else:
                pipeline = ToolCallingPipeline(client=self.client)
                result = pipeline.run(run_dir, request)
                manifest.attempts.append(
                    {"attempt": 0, "mode": "mimo-tool-calling", "status": result["status"]}
                )
                manifest.tool_call_count = len(result.get("tool_calls") or [])

            failures, scene_name, video_path = validate_run(run_dir, require_video=False)
            repair = 0
            while failures and not request.offline and repair < request.max_repairs:
                repair += 1
                evidence = "\n".join(f"- {failure}" for failure in failures)
                pipeline = ToolCallingPipeline(client=self.client)
                pipeline.run(
                    run_dir,
                    request,
                    from_stage="scene-composer",
                    feedback={"scene-composer": evidence},
                )
                manifest.attempts.append(
                    {
                        "attempt": repair,
                        "mode": "scene-composer-static-repair",
                        "status": "completed",
                        "input_failures": failures,
                    }
                )
                failures, scene_name, video_path = validate_run(run_dir, require_video=False)

            if failures:
                raise RuntimeError("run bundle validation failed: " + "; ".join(failures))

            if request.render and not request.offline:
                from mimo.validation import validation_from_scene  # local import

                scene_src = (run_dir / "mimo_scene.py").read_text(encoding="utf-8")
                report = validation_from_scene(scene_src)
                scene_name = report["scene_name"] or scene_name
                if not scene_name:
                    raise RuntimeError("render requested but no scene class was found")
                # Wrapper-owned render via the manim CLI entry on PATH.
                import subprocess
                import sys

                manim = Path(sys.executable).with_name("manim")
                cmd = [
                    str(manim) if manim.exists() else "manim",
                    f"-q{request.quality}",
                    str(run_dir / "mimo_scene.py"),
                    scene_name,
                    "--media_dir",
                    str(run_dir / "media"),
                ]
                completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
                (run_dir / "render.log").write_text(
                    (completed.stdout or "") + (completed.stderr or ""), encoding="utf-8"
                )
                if completed.returncode != 0:
                    raise RuntimeError(f"manim render failed ({completed.returncode})")
                failures, scene_name, video_path = validate_run(run_dir, require_video=True)
                if failures:
                    raise RuntimeError("post-render validation failed: " + "; ".join(failures))
                result["rendered"] = True
                result["video_path"] = video_path

            manifest.scene_file = "mimo_scene.py"
            manifest.scene_name = scene_name
            manifest.video_path = video_path
            manifest.status = "completed"
            manifest.completed_utc = datetime.now(timezone.utc).isoformat()
            manifest.status_detail["validation"] = "passed"
            self._write_manifest(manifest_path, manifest)
            return {
                "run_id": manifest.run_id,
                "status": manifest.status,
                "scene_name": manifest.scene_name,
                "scene_file": manifest.scene_file,
                "video_path": manifest.video_path,
                "run_dir": str(run_dir),
                **{key: result[key] for key in ("artifacts", "checks", "notes") if key in result},
            }
        except Exception as exc:  # noqa: BLE001 - persist failure state
            manifest.status = "failed"
            manifest.error = str(exc)
            manifest.completed_utc = datetime.now(timezone.utc).isoformat()
            self._write_manifest(manifest_path, manifest)
            raise

    def list_runs(self, *, limit: int = 20) -> list[RunManifest]:
        manifests: list[RunManifest] = []
        if not self.runs_dir.is_dir():
            return manifests
        for path in sorted(self.runs_dir.glob("*/manifest.json"), reverse=True)[: max(1, limit)]:
            try:
                manifests.append(RunManifest.model_validate_json(path.read_text(encoding="utf-8")))
            except ValueError:
                continue
        return manifests

    def get_run(self, run_id: str) -> RunManifest:
        path = self.runs_dir / run_id / "manifest.json"
        return RunManifest.model_validate_json(path.read_text(encoding="utf-8"))
