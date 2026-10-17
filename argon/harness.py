"""Argon Google ADK (`google-adk` + `google-genai`) 6-stage reasoning chain harness."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from argon.charters import STAGES, load_charter
from argon.client import ArgonClient, ArgonClientError
from argon.jsonutil import extract_json_object, extract_scene_source
from argon.models import ARTIFACT_NAMES, RunManifest, RunRequest
from argon.offline import write_offline_bundle
from argon.tools import execute_math_check, verify_scene
from argon.validation import normalize_reverse_tree, validate_run, verify_scene_report

REPO_ROOT = Path(__file__).resolve().parents[1]


def default_runs_dir() -> Path:
    return REPO_ROOT / "runs" / "argon"


def _resolve_manim_cmd() -> list[str]:
    override = os.getenv("M2M_MANIM")
    if override:
        return [override]
    manim_bin = shutil.which("manim")
    if manim_bin:
        return [manim_bin]
    return [sys.executable, "-m", "manim"]


class ArgonHarness:
    """Runs the 6-stage Argon Google ADK chain: intent -> cartographer -> curriculum -> math-director -> cinematographer -> composer, then static verify & Manim render."""

    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: ArgonClient | None = None,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.client = client or ArgonClient()

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
            model="offline" if request.offline else self.client.model,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            image=request.image,
            created_utc=now,
            artifacts={"validation": "validation.json", "scene": "argon_scene.py"},
            status_detail={"validation": "pending"},
        )
        manifest_path = run_dir / "manifest.json"
        self._write_manifest(manifest_path, manifest)
        (run_dir / "request.json").write_text(request.model_dump_json(indent=2), encoding="utf-8")
        traces_dir = run_dir / "traces"
        traces_dir.mkdir(exist_ok=True)

        try:
            if request.offline:
                write_offline_bundle(run_dir, request)
                manifest.attempts.append({"attempt": 0, "mode": "offline", "status": "completed"})
            else:
                self._run_live(run_dir, request, manifest)

            failures, scene_name, video_path = validate_run(run_dir, require_video=False)
            repair = 0
            while failures and not request.offline and repair < request.max_repairs:
                repair += 1
                self._repair_scene(run_dir, request, failures)
                manifest.attempts.append(
                    {
                        "attempt": repair,
                        "mode": "composer-repair",
                        "input_failures": failures,
                    }
                )
                failures, scene_name, video_path = validate_run(run_dir, require_video=False)

            if failures:
                raise RuntimeError("run bundle validation failed: " + "; ".join(failures))

            if request.render and not request.offline:
                video_path = self._render(run_dir, scene_name or "ArgonOfflineJourney", request.quality)

            report = verify_scene_report((run_dir / "argon_scene.py").read_text(encoding="utf-8"))
            (run_dir / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            manifest.scene_file = "argon_scene.py"
            manifest.scene_name = scene_name
            manifest.video_path = video_path
            manifest.status = "completed"
            manifest.completed_utc = datetime.now(timezone.utc).isoformat()
            manifest.status_detail["validation"] = "complete"
            manifest.artifacts = {name: name for name in ARTIFACT_NAMES}
            self._write_manifest(manifest_path, manifest)
            return json.loads(manifest.model_dump_json())
        except Exception as exc:
            manifest.status = "failed"
            manifest.error = str(exc)
            manifest.completed_utc = datetime.now(timezone.utc).isoformat()
            self._write_manifest(manifest_path, manifest)
            raise

    def _run_live(self, run_dir: Path, request: RunRequest, manifest: RunManifest) -> None:
        if not self.client.api_key:
            raise ArgonClientError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set")
        prior: dict[str, dict] = {}
        image_path = Path(request.image) if request.image else None
        if image_path is not None and not image_path.is_file():
            raise ArgonClientError(f"image file not found: {request.image}")

        tool_registry = {
            "execute_math_check": execute_math_check,
            "verify_scene": verify_scene,
        }

        for stage in STAGES:
            charter = load_charter(stage.charter_file)
            user_text = _stage_prompt(stage.name, request.prompt, prior)
            stage_tools = [tool_registry[name] for name in stage.tools if name in tool_registry]
            result = self.client.complete(
                stage_name=stage.name,
                instructions=charter,
                text=user_text,
                tools=stage_tools,
                image_path=image_path if stage.name == "intent" else None,
            )
            payload = result.payload if result.payload and "raw_text" not in result.payload else None
            if payload is None and result.text.strip():
                try:
                    payload = extract_json_object(result.text)
                except (ValueError, json.JSONDecodeError) as exc:
                    raise ArgonClientError(f"stage {stage.name} did not return JSON") from exc
            if not isinstance(payload, dict) or not payload:
                raise ArgonClientError(f"stage {stage.name} did not return JSON")
            if stage.name == "cartographer":
                payload = normalize_reverse_tree(payload)
            artifact_path = run_dir / stage.artifact
            artifact_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            prior[stage.artifact] = payload

            if stage.name == "composer":
                try:
                    source = extract_scene_source(payload, result.text, result.tool_calls)
                except ValueError as exc:
                    raise ArgonClientError("composer did not return argon_scene.py source") from exc
                (run_dir / "argon_scene.py").write_text(source, encoding="utf-8")

            trace = {
                "stage": stage.name,
                "sdk": "google-adk",
                "model": self.client.model,
                "reasoning_effort": self.client.reasoning_effort,
                "tools_requested": list(stage.tools),
                "tool_calls": result.tool_calls,
                "thinking": result.thinking,
            }
            (run_dir / "traces" / f"{stage.name}.json").write_text(
                json.dumps(trace, indent=2),
                encoding="utf-8",
            )
            (run_dir / "traces" / f"{stage.name}.raw.json").write_text(
                json.dumps(result.raw, indent=2),
                encoding="utf-8",
            )
            manifest.stages.append(
                {
                    "stage": stage.name,
                    "artifact": stage.artifact,
                    "tool_calls": len(result.tool_calls),
                }
            )
            self._write_manifest(run_dir / "manifest.json", manifest)
            print(f"  [argon-adk] {stage.name:16} -> {stage.artifact}")

        scene_source = (run_dir / "argon_scene.py").read_text(encoding="utf-8")
        (run_dir / "validation.json").write_text(
            json.dumps(verify_scene_report(scene_source), indent=2),
            encoding="utf-8",
        )
        review = {
            "offline": False,
            "sdk": "google-adk + google-genai",
            "model": self.client.model,
            "checks": ["artifact contract", "reverse tree", "python compilation"],
            "rendered": False,
        }
        (run_dir / "review.json").write_text(json.dumps(review, indent=2), encoding="utf-8")
        manifest.attempts.append({"attempt": 0, "mode": "google-adk", "status": "completed"})

    def _repair_scene(self, run_dir: Path, request: RunRequest, failures: list[str]) -> None:
        source = (run_dir / "argon_scene.py").read_text(encoding="utf-8")
        result = self.client.complete(
            stage_name="composer-repair",
            instructions=load_charter("argon-composer.md"),
            text=(
                "Repair this Manim scene. Keep the class name, ThreeDScene contract, "
                "and camera rule. Return JSON with a source field containing the "
                "complete file.\n\nFAILURES:\n"
                + "\n".join(f"- {item}" for item in failures)
                + "\n\nCURRENT FILE:\n"
                + source
            ),
            tools=(verify_scene,),
        )
        try:
            repaired = extract_scene_source(result.payload, result.text, result.tool_calls)
        except ValueError as exc:
            raise ArgonClientError("composer repair did not return argon_scene.py source") from exc
        (run_dir / "argon_scene.py").write_text(repaired, encoding="utf-8")
        (run_dir / "traces" / "repair.json").write_text(
            json.dumps({"tool_calls": result.tool_calls, "thinking": result.thinking}, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _render(run_dir: Path, scene_name: str, quality: str) -> str:
        cmd_prefix = _resolve_manim_cmd()
        media = run_dir / "media"
        command = [
            *cmd_prefix,
            f"-q{quality}",
            "--media_dir",
            str(media),
            str(run_dir / "argon_scene.py"),
            scene_name,
        ]
        env = dict(os.environ)
        miktex_bin = r"C:\Program Files\MiKTeX\miktex\bin\x64"
        if os.path.isdir(miktex_bin) and miktex_bin.lower() not in env.get("PATH", "").lower():
            env["PATH"] = env.get("PATH", "") + os.pathsep + miktex_bin
        for secret_var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ARGON_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
            env.pop(secret_var, None)
        completed = subprocess.run(command, cwd=run_dir, env=env, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise RuntimeError((completed.stderr or completed.stdout)[-4000:])
        videos = [
            p for p in sorted(media.rglob("*.mp4"))
            if "partial_movie_files" not in p.parts
        ]
        if not videos:
            raise RuntimeError("manim exited 0 but wrote no final mp4")
        return str(videos[-1])


def _stage_prompt(stage: str, prompt: str, prior: dict[str, dict]) -> str:
    dossier = json.dumps(prior, indent=2) if prior else "{}"
    return (
        f"User request:\n{prompt}\n\n"
        f"You are the {stage} stage in the Argon Google ADK chain. Read the charter. "
        "Return one JSON object with exactly the keys the charter names.\n"
        "If you write the scene, also include a source field with the complete "
        "Python file, or a fenced python block.\n\n"
        f"Upstream artifacts:\n{dossier}\n"
    )
