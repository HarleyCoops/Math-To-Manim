"""GLM-native chain: intent through composer, then local verify and render."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from glm.charters import VERIFY_SCENE_TOOL, load_charter
from glm.client import GlmClient, GlmClientError
from glm.jsonutil import extract_json_object, extract_scene_source
from glm.models import ARTIFACT_NAMES, RunManifest, RunRequest
from glm.offline import write_offline_bundle
from glm.tools import verify_scene
from glm.validation import normalize_reverse_tree, validate_run, verify_scene_report

REPO_ROOT = Path(__file__).resolve().parents[1]


def default_runs_dir() -> Path:
    return REPO_ROOT / "runs" / "glm"


class GlmHarness:
    """Runs the six-stage chain against Z.ai chat/completions, or offline."""

    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: GlmClient | None = None,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.client = client or GlmClient()

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
            key_source=None if request.offline else self.client.key_source,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            image=request.image,
            created_utc=now,
            artifacts={"validation": "validation.json", "scene": "glm_scene.py"},
            status_detail={"validation": "pending"},
        )
        manifest_path = run_dir / "manifest.json"
        self._write_manifest(manifest_path, manifest)
        (run_dir / "request.json").write_text(
            request.model_dump_json(indent=2), encoding="utf-8"
        )
        traces_dir = run_dir / "traces"
        traces_dir.mkdir(exist_ok=True)

        try:
            if request.offline:
                write_offline_bundle(run_dir, request)
                manifest.attempts.append(
                    {"attempt": 0, "mode": "offline", "status": "completed"}
                )
            else:
                self._run_live(run_dir, request, manifest)

            failures, scene_name, video_path = validate_run(run_dir, require_video=False)
            repair = 0
            while failures and not request.offline and repair < request.max_repairs:
                repair += 1
                self._repair_scene(run_dir, failures)
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

            video_path = video_path or (
                self._render(run_dir, scene_name or "GlmOfflineStory", request.quality)
                if request.render
                else None
            )

            report = verify_scene_report(
                (run_dir / "glm_scene.py").read_text(encoding="utf-8")
            )
            (run_dir / "validation.json").write_text(
                json.dumps(report, indent=2), encoding="utf-8"
            )
            manifest.scene_file = "glm_scene.py"
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
            raise GlmClientError("no GLM key found; set ZHIPU_API_KEY or ZAI_API_KEY")
        prior: dict[str, dict] = {}
        image_path = Path(request.image) if request.image else None
        if image_path is not None and not image_path.is_file():
            raise GlmClientError(f"image file not found: {request.image}")

        for stage in load_stages():
            charter = load_charter(stage.charter_file)
            user_text = _stage_prompt(stage.name, request.prompt, prior, stage.tools)
            # Only real local functions reach the wire; server-side abilities
            # (web research, sandbox) stay advisory notes inside the prompt.
            api_tools = tuple(tool for tool in stage.tools if tool.get("type") == "function")
            handlers = {"verify_scene": verify_scene} if stage.name == "composer" else None
            result = self.client.complete(
                instructions=charter,
                text=user_text,
                tools=api_tools,
                image_path=image_path if stage.name == "intent" else None,
                function_handlers=handlers,
            )
            payload = result.payload or None
            if payload is None and result.text.strip():
                try:
                    payload = extract_json_object(result.text)
                except (ValueError, json.JSONDecodeError) as exc:
                    raise GlmClientError(
                        f"stage {stage.name} did not return JSON"
                    ) from exc
            if not isinstance(payload, dict) or not payload:
                raise GlmClientError(f"stage {stage.name} did not return JSON")
            if stage.name == "cartographer":
                payload = normalize_reverse_tree(payload)
            artifact_path = run_dir / stage.artifact
            artifact_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            prior[stage.artifact] = payload

            if stage.name == "composer":
                try:
                    source = extract_scene_source(payload, result.text, result.tool_calls)
                except ValueError as exc:
                    raise GlmClientError(
                        "composer did not return glm_scene.py source"
                    ) from exc
                (run_dir / "glm_scene.py").write_text(source, encoding="utf-8")

            trace = {
                "stage": stage.name,
                "model": self.client.model,
                "reasoning_effort": self.client.reasoning_effort,
                "thinking_enabled": True,
                "tools_requested": [
                    tool.get("function", {}).get("name") or tool.get("type")
                    for tool in stage.tools
                ],
                "tool_calls": result.tool_calls,
                "thinking": result.thinking,
            }
            (run_dir / "traces" / f"{stage.name}.json").write_text(
                json.dumps(trace, indent=2), encoding="utf-8"
            )
            (run_dir / "traces" / f"{stage.name}.raw.json").write_text(
                json.dumps(result.raw, indent=2), encoding="utf-8"
            )
            manifest.stages.append(
                {
                    "stage": stage.name,
                    "artifact": stage.artifact,
                    "tool_calls": len(result.tool_calls),
                }
            )
            self._write_manifest(run_dir / "manifest.json", manifest)
            print(f"  [glm] {stage.name:16} -> {stage.artifact}")

        scene_source = (run_dir / "glm_scene.py").read_text(encoding="utf-8")
        (run_dir / "validation.json").write_text(
            json.dumps(verify_scene_report(scene_source), indent=2),
            encoding="utf-8",
        )
        review = {
            "offline": False,
            "model": self.client.model,
            "thinking_enabled": True,
            "checks": ["artifact contract", "reverse tree", "python compilation"],
            "rendered": False,
        }
        (run_dir / "review.json").write_text(json.dumps(review, indent=2), encoding="utf-8")
        manifest.attempts.append(
            {"attempt": 0, "mode": "zai-chat-completions", "status": "completed"}
        )

    def _repair_scene(self, run_dir: Path, failures: list[str]) -> None:
        source = (run_dir / "glm_scene.py").read_text(encoding="utf-8")
        result = self.client.complete(
            instructions=load_charter("glm-composer.md"),
            text=(
                "Repair this Manim scene. Keep the class name, ThreeDScene "
                "contract, paper palette, and camera rule. Return JSON with a "
                "source field containing the complete file.\n\nFAILURES:\n"
                + "\n".join(f"- {item}" for item in failures)
                + "\n\nCURRENT FILE:\n"
                + source
            ),
            tools=(VERIFY_SCENE_TOOL,),
            function_handlers={"verify_scene": verify_scene},
        )
        try:
            repaired = extract_scene_source(result.payload, result.text, result.tool_calls)
        except ValueError as exc:
            raise GlmClientError(
                "composer repair did not return glm_scene.py source"
            ) from exc
        (run_dir / "glm_scene.py").write_text(repaired, encoding="utf-8")
        (run_dir / "traces" / "repair.json").write_text(
            json.dumps(
                {"tool_calls": result.tool_calls, "thinking": result.thinking},
                indent=2,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _render(run_dir: Path, scene_name: str, quality: str) -> str:
        manim = shutil.which("manim")
        if not manim:
            raise RuntimeError("manim was not found; pip install -e '.[render]'")
        media = run_dir / "media"
        command = [
            manim,
            f"-q{quality}",
            "--media_dir",
            str(media),
            str(run_dir / "glm_scene.py"),
            scene_name,
        ]
        completed = subprocess.run(
            command, cwd=run_dir, capture_output=True, text=True, check=False
        )
        if completed.returncode != 0:
            raise RuntimeError((completed.stderr or completed.stdout)[-4000:])
        videos = sorted(media.rglob("*.mp4"))
        if not videos:
            raise RuntimeError("manim exited 0 but wrote no mp4")
        return str(videos[-1])


def load_stages():
    from glm.charters import STAGES

    return STAGES


def _stage_prompt(stage: str, prompt: str, prior: dict[str, dict], tools=()) -> str:
    """User turn for one stage; platform-only abilities become advisories."""
    dossier = json.dumps(prior, indent=2) if prior else "{}"
    platform_only = [
        tool.get("type") for tool in tools or [] if tool.get("type") != "function"
    ]
    advisory = ""
    if platform_only:
        advisory = (
            f"Platform abilities this stage may reference conceptually: "
            f"{', '.join(filter(None, platform_only))}. Output stays plain text/JSON.\n"
        )
    return (
        f"User request:\n{prompt}\n\n"
        f"You are the {stage} stage of the GLM chain. Thinking is on.\n"
        "Return one JSON object with exactly the keys the charter names.\n"
        "If you write the scene, also include a source field with the complete "
        "Python file, or a fenced python block.\n"
        f"{advisory}\n"
        f"Upstream artifacts:\n{dossier}\n"
    )
