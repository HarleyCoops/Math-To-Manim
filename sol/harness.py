"""Complete Codex CLI-native Math-To-Manim run harness."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from sol.client import DEFAULT_MODEL, CodexCli
from sol.contract import SOL_FILM_CONTRACT, build_prompt, build_repair_prompt
from sol.models import CodexRunResult, RunManifest, RunRequest
from sol.offline import write_offline_bundle
from sol.validation import validate_run

REPO_ROOT = Path(__file__).resolve().parents[1]


def default_runs_dir() -> Path:
    return REPO_ROOT / "runs" / "sol"


class SolHarness:
    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: CodexCli | None = None,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.client = client or CodexCli()

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
            run_id=run_dir.name,
            prompt=request.prompt,
            model=self.client.model,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            created_utc=now,
        )
        manifest_path = run_dir / "manifest.json"
        self._write_manifest(manifest_path, manifest)
        (run_dir / "request.json").write_text(request.model_dump_json(indent=2), encoding="utf-8")
        (run_dir / "CONTRACT.md").write_text(SOL_FILM_CONTRACT + "\n", encoding="utf-8")
        schema_path = run_dir / "final-result.schema.json"
        schema_path.write_text(json.dumps(CodexRunResult.model_json_schema(), indent=2), encoding="utf-8")

        try:
            if request.offline:
                result = write_offline_bundle(run_dir, request)
                manifest.attempts.append({"attempt": 0, "mode": "offline", "status": "completed"})
            else:
                prompt = build_prompt(request, repo_root=REPO_ROOT, run_dir=run_dir)
                result = self.client.run(
                    prompt,
                    cwd=run_dir,
                    schema_path=schema_path,
                    output_path=run_dir / "final-result-0.json",
                    trace_path=run_dir / "codex-trace-0.jsonl",
                )
                manifest.attempts.append({"attempt": 0, "mode": "codex-cli", "status": result.status})

            failures, scene_name, video_path = validate_run(run_dir, require_video=request.render)
            repair = 0
            while failures and not request.offline and repair < request.max_repairs:
                repair += 1
                repair_prompt = build_repair_prompt(
                    request,
                    repo_root=REPO_ROOT,
                    run_dir=run_dir,
                    failures=failures,
                    attempt=repair,
                )
                result = self.client.run(
                    repair_prompt,
                    cwd=run_dir,
                    schema_path=schema_path,
                    output_path=run_dir / f"final-result-{repair}.json",
                    trace_path=run_dir / f"codex-trace-{repair}.jsonl",
                )
                manifest.attempts.append({
                    "attempt": repair,
                    "mode": "codex-cli-repair",
                    "status": result.status,
                    "input_failures": failures,
                })
                failures, scene_name, video_path = validate_run(run_dir, require_video=request.render)

            if failures:
                raise RuntimeError("run bundle validation failed: " + "; ".join(failures))
            manifest.status = "completed"
            manifest.scene_file = "sol_scene.py"
            manifest.scene_name = scene_name or result.scene_name
            manifest.video_path = video_path or result.video_path
            manifest.completed_utc = datetime.now(timezone.utc).isoformat()
        except Exception as exc:
            manifest.status = "failed"
            manifest.error = f"{type(exc).__name__}: {exc}"
            manifest.completed_utc = datetime.now(timezone.utc).isoformat()
            self._write_manifest(manifest_path, manifest)
            raise

        self._write_manifest(manifest_path, manifest)
        return manifest.model_dump()
