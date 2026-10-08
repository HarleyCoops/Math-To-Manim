"""Grok-native chain: typed stages, independent audits, and render evidence."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from grok.backends.grok_build import GrokBuildBackend, auth_source_for
from grok.charters import STAGES, VERIFY_SCENE_TOOL, load_charter
from grok.client import XAIClient, XAIClientError, resolve_model
from grok.jsonutil import extract_scene_source
from grok.ledger import file_hashes, hashes_match, load_ledger, save_ledger
from grok.models import ARTIFACT_NAMES, RunManifest, RunRequest
from grok.offline import write_offline_bundle
from grok.rendering import probe as probe_scene
from grok.rendering import render as render_scene
from grok.review import AUDITOR_CHARTER, audit_prompt, parse_assessment
from grok.schemas import STAGE_MODELS, Assessment, validate_stage_output
from grok.tools import verify_scene, write_stills
from grok.validation import validate_run, verify_scene_report

STAGE_ORDER = [stage.name for stage in STAGES]


class RenderNeedsRepair(RuntimeError):
    def __init__(self, repair_stage: str, feedback: str):
        super().__init__(feedback)
        self.repair_stage = repair_stage
        self.feedback = feedback


def default_runs_dir() -> Path:
    override = os.getenv("M2M_RUNS_DIR", "").strip()
    if override:
        return Path(override) / "grok"
    return Path.cwd() / "runs" / "grok"


class GrokHarness:
    def __init__(
        self,
        *,
        runs_dir: Path | None = None,
        client: XAIClient | GrokBuildBackend | None = None,
        renderer=None,
        prober=None,
    ):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.client = client if client is not None else XAIClient()
        self._injected = client is not None
        self.renderer = renderer or render_scene
        self.prober = prober or probe_scene

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

    def _resolve_run_dir(self, run_id: str) -> Path:
        if Path(run_id).name != run_id:
            raise ValueError("run_id must be a single directory name")
        run_dir = (self.runs_dir / run_id).resolve()
        runs_root = self.runs_dir.resolve()
        if runs_root not in run_dir.parents:
            raise ValueError(f"Invalid run_id: {run_id!r}")
        if not run_dir.is_dir():
            raise FileNotFoundError(f"unknown Grok run: {run_id}")
        return run_dir

    @staticmethod
    def _write_manifest(path: Path, manifest: RunManifest) -> None:
        temporary = path.with_suffix(".tmp")
        temporary.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(path)

    def _prepare_client(self, request: RunRequest) -> None:
        if request.offline:
            return
        if not self._injected and request.backend == "grok-build":
            self.client = GrokBuildBackend(
                model=request.model or resolve_model(),
                reasoning_effort=request.reasoning_effort,
            )
        if request.model:
            self.client.model = request.model
        if hasattr(self.client, "reasoning_effort"):
            self.client.reasoning_effort = request.reasoning_effort

    def _require_auth(self, request: RunRequest) -> None:
        if self._injected or request.offline:
            return
        if request.backend == "grok-build":
            self.client.require_auth()
            return
        if not getattr(self.client, "api_key", ""):
            raise XAIClientError("XAI_API_KEY is not set")

    def run(self, request: RunRequest, *, resume_dir: Path | None = None) -> dict:
        if request.backend == "offline":
            request = request.model_copy(update={"offline": True})
        self._prepare_client(request)
        if resume_dir is None:
            run_dir = self._create_run_dir(request.prompt)
            (run_dir / "request.json").write_text(request.model_dump_json(indent=2), encoding="utf-8")
            manifest = self._fresh_manifest(run_dir, request)
        else:
            run_dir = Path(resume_dir)
            if not (run_dir / "request.json").is_file():
                (run_dir / "request.json").write_text(request.model_dump_json(indent=2), encoding="utf-8")
            manifest = self._load_or_fresh_manifest(run_dir, request)
        manifest.status = "running"
        manifest.error = None
        manifest_path = run_dir / "manifest.json"
        self._write_manifest(manifest_path, manifest)
        (run_dir / "traces").mkdir(exist_ok=True)
        ledger = load_ledger(run_dir)
        try:
            if request.offline:
                self._run_offline(run_dir, request, manifest, ledger)
            else:
                self._require_auth(request)
                self._run_live(run_dir, request, manifest, ledger)
            failures, scene_name, video_path = validate_run(run_dir, require_video=False)
            repair = 0
            while failures and not request.offline and repair < request.max_repairs:
                repair += 1
                self._repair_scene(run_dir, request, failures)
                manifest.attempts.append(
                    {"attempt": repair, "mode": "composer-repair", "input_failures": failures}
                )
                failures, scene_name, video_path = validate_run(run_dir, require_video=False)
            if failures:
                raise RuntimeError("run bundle validation failed: " + "; ".join(failures))
            manifest.scene_file = "grok_scene.py"
            manifest.scene_name = scene_name
            if manifest.video_path is None and video_path:
                manifest.video_path = video_path
            manifest.status = "completed"
            manifest.completed_utc = datetime.now(timezone.utc).isoformat()
            manifest.status_detail["validation"] = "complete"
            manifest.artifacts = {name: name for name in ARTIFACT_NAMES}
            manifest.ledger = ledger
            manifest.review_status = _review_status(request)
            self._write_manifest(manifest_path, manifest)
            save_ledger(run_dir, ledger)
            return json.loads(manifest.model_dump_json())
        except Exception as exc:
            manifest.status = "failed"
            manifest.error = str(exc)
            manifest.completed_utc = datetime.now(timezone.utc).isoformat()
            manifest.ledger = ledger
            self._write_manifest(manifest_path, manifest)
            save_ledger(run_dir, ledger)
            raise

    def resume(self, run_id: str, **overrides) -> dict:
        run_dir = self._resolve_run_dir(run_id)
        request = RunRequest.model_validate_json((run_dir / "request.json").read_text(encoding="utf-8"))
        if overrides:
            request = request.model_copy(update={key: value for key, value in overrides.items() if value is not None})
        return self.run(request, resume_dir=run_dir)

    def render_existing(
        self,
        run_id: str,
        *,
        quality: str = "l",
        render_timeout: float = 7200,
        min_duration: float = 20,
        max_duration: float = 240,
    ) -> dict:
        """Render a saved scene. This path makes zero model calls."""
        run_dir = self._resolve_run_dir(run_id)
        source_path = run_dir / "grok_scene.py"
        if not source_path.is_file():
            raise FileNotFoundError(f"grok_scene.py is missing from {run_id}")
        source = source_path.read_text(encoding="utf-8")
        manifest_path = run_dir / "manifest.json"
        if manifest_path.is_file():
            manifest = RunManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
        else:
            manifest = self._fresh_manifest(
                run_dir,
                RunRequest(prompt=run_dir.name, offline=True, backend="offline"),
            )
        attempt = _next_attempt(run_dir)
        manifest.status = "rendering"
        manifest.review_status = "not_reviewed"
        manifest.quality = quality
        manifest.error = None
        manifest.status_detail["render"] = "not_reviewed"
        ledger = load_ledger(run_dir)
        ledger.setdefault("events", []).append(
            {
                "stage": "local_render",
                "attempt": attempt,
                "quality": quality,
                "reason": "render-existing makes zero model calls; output is not_reviewed",
            }
        )
        self._write_manifest(run_dir / "manifest.json", manifest)
        try:
            video, _frames, sheet = self.renderer(
                run_dir,
                source,
                quality,
                attempt,
                timeout=render_timeout,
                min_duration=min_duration,
                max_duration=max_duration,
            )
        except Exception as exc:
            manifest.status = "failed"
            manifest.error = f"{type(exc).__name__}: {exc}"
            manifest.review_status = "not_reviewed"
            self._write_manifest(run_dir / "manifest.json", manifest)
            save_ledger(run_dir, ledger)
            raise
        manifest.video_path = Path(video).resolve().relative_to(run_dir.resolve()).as_posix()
        manifest.status = "completed"
        manifest.review_status = "not_reviewed"
        manifest.completed_utc = datetime.now(timezone.utc).isoformat()
        manifest.status_detail["render"] = "not_reviewed"
        manifest.status_detail["contact_sheet"] = Path(sheet).resolve().relative_to(run_dir.resolve()).as_posix()
        manifest.ledger = ledger
        self._note_local_render(run_dir)
        self._write_manifest(run_dir / "manifest.json", manifest)
        save_ledger(run_dir, ledger)
        return json.loads(manifest.model_dump_json())

    def _fresh_manifest(self, run_dir: Path, request: RunRequest) -> RunManifest:
        backend = "offline" if request.offline else request.backend
        if backend == "xai-responses":
            backend = "xai-api"
        return RunManifest(
            run_id=run_dir.name,
            prompt=request.prompt,
            model="offline" if request.offline else self.client.model,
            backend=backend,
            offline=request.offline,
            render_requested=request.render,
            quality=request.quality,
            image=request.image,
            created_utc=datetime.now(timezone.utc).isoformat(),
            artifacts={"validation": "validation.json", "scene": "grok_scene.py"},
            status_detail={"validation": "pending"},
            review=request.review,
            auth_source="none" if request.offline else auth_source_for(backend),
        )

    def _load_or_fresh_manifest(self, run_dir: Path, request: RunRequest) -> RunManifest:
        path = run_dir / "manifest.json"
        if path.is_file():
            try:
                manifest = RunManifest.model_validate_json(path.read_text(encoding="utf-8"))
                manifest.review = request.review
                manifest.render_requested = request.render
                return manifest
            except (OSError, ValueError):
                pass
        return self._fresh_manifest(run_dir, request)

    def _run_offline(self, run_dir: Path, request: RunRequest, manifest: RunManifest, ledger: dict) -> None:
        if not _ledger_covers(run_dir, ledger):
            write_offline_bundle(run_dir, request)
            for index, stage in enumerate(STAGES):
                ledger["stages"][stage.name] = {"hashes": file_hashes(run_dir, _dependency_paths(index))}
            ledger["events"].append({"stage": "offline", "attempt": 0, "status": "completed"})
            save_ledger(run_dir, ledger)
        review_path = run_dir / "review.json"
        if review_path.is_file():
            review = json.loads(review_path.read_text(encoding="utf-8"))
            if isinstance(review, dict):
                review["review_status"] = "not_reviewed"
                review_path.write_text(json.dumps(review, indent=2), encoding="utf-8")
        manifest.attempts.append({"attempt": 0, "mode": "offline", "status": "completed"})
        manifest.review_status = "not_reviewed"
        manifest.ledger = ledger

    def _run_live(self, run_dir: Path, request: RunRequest, manifest: RunManifest, ledger: dict) -> None:
        prior: dict[str, dict] = {}
        for stage in STAGES:
            artifact = run_dir / stage.artifact
            if artifact.is_file():
                try:
                    prior[stage.artifact] = json.loads(artifact.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    pass
        revisions = 0
        index = 0
        feedback = ""
        while True:
            while index < len(STAGES):
                stage = STAGES[index]
                cached = ledger["stages"].get(stage.name) or {}
                if cached.get("hashes") and hashes_match(run_dir, cached["hashes"]):
                    print(f"  [grok] {stage.name:16} cached")
                    artifact = run_dir / stage.artifact
                    if artifact.is_file():
                        prior[stage.artifact] = json.loads(artifact.read_text(encoding="utf-8"))
                    index += 1
                    continue
                for name in STAGE_ORDER[index:]:
                    ledger["stages"].pop(name, None)
                    dropped = next(item for item in STAGES if item.name == name)
                    prior.pop(dropped.artifact, None)
                save_ledger(run_dir, ledger)
                result, source = self._generate(run_dir, request, stage, prior, feedback)
                prior[stage.artifact] = json.loads((run_dir / stage.artifact).read_text(encoding="utf-8"))
                if request.review != "off":
                    paths = [run_dir / "request.json"] + [run_dir / item.artifact for item in STAGES[: index + 1]]
                    if stage.name == "composer":
                        paths.append(run_dir / "grok_scene.py")
                    assessment = self._audit(
                        run_dir,
                        request,
                        stage.name,
                        paths,
                        frame_names=None,
                        images=(),
                        feedback=feedback,
                    )
                    if request.review == "gated" and assessment.verdict != "pass":
                        revisions += 1
                        ledger["events"].append(
                            {
                                "stage": stage.name,
                                "verdict": assessment.verdict,
                                "repair_stage": assessment.repair_stage,
                            }
                        )
                        save_ledger(run_dir, ledger)
                        if revisions > request.max_revisions:
                            raise RuntimeError("revision budget exhausted")
                        index = STAGE_ORDER.index(assessment.repair_stage)
                        feedback = assessment.feedback or assessment.model_dump_json()
                        for name in STAGE_ORDER[index:]:
                            ledger["stages"].pop(name, None)
                        save_ledger(run_dir, ledger)
                        continue
                ledger["stages"][stage.name] = {"hashes": file_hashes(run_dir, _dependency_paths(index))}
                save_ledger(run_dir, ledger)
                manifest.stages.append(
                    {
                        "stage": stage.name,
                        "artifact": stage.artifact,
                        "tool_calls": len(result.tool_calls),
                        "warnings": result.warnings,
                    }
                )
                self._write_manifest(run_dir / "manifest.json", manifest)
                print(f"  [grok] {stage.name:16} -> {stage.artifact}")
                index += 1
                feedback = ""
            if not request.render:
                break
            try:
                video = self._render_evidence(run_dir, request, manifest, feedback)
            except RenderNeedsRepair as exc:
                revisions += 1
                ledger["events"].append(
                    {"stage": "render", "repair_stage": exc.repair_stage, "error": exc.feedback}
                )
                save_ledger(run_dir, ledger)
                if revisions > request.max_revisions:
                    raise RuntimeError("revision budget exhausted") from exc
                index = STAGE_ORDER.index(exc.repair_stage) if exc.repair_stage in STAGE_ORDER else STAGE_ORDER.index("composer")
                feedback = exc.feedback
                for name in STAGE_ORDER[index:]:
                    ledger["stages"].pop(name, None)
                save_ledger(run_dir, ledger)
                continue
            manifest.video_path = video.resolve().relative_to(run_dir.resolve()).as_posix()
            break
        scene_source = (run_dir / "grok_scene.py").read_text(encoding="utf-8")
        (run_dir / "validation.json").write_text(
            json.dumps(verify_scene_report(scene_source), indent=2),
            encoding="utf-8",
        )
        review_path = run_dir / "review.json"
        review = {}
        if review_path.is_file():
            try:
                loaded = json.loads(review_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    review = loaded
            except json.JSONDecodeError:
                review = {}
        review.update(
            {
                "offline": False,
                "model": self.client.model,
                "review": request.review,
                "review_status": _review_status(request),
                "checks": ["schema", "independent audit", "allowlist"],
                "rendered": bool(request.render and manifest.video_path),
            }
        )
        review_path.write_text(json.dumps(review, indent=2), encoding="utf-8")
        manifest.attempts.append(
            {"attempt": 0, "mode": manifest.backend, "status": "completed"}
        )
        manifest.ledger = ledger

    def _generate(self, run_dir, request, stage, prior, feedback):
        charter = load_charter(stage.charter_file)
        base_text = _stage_prompt(stage.name, request.prompt, prior)
        if feedback:
            base_text += "\n\nReviewer feedback to address:\n" + feedback
        schema = STAGE_MODELS[stage.name].model_json_schema()
        image = None
        if stage.name == "intent" and request.image:
            image = Path(request.image)
            if not image.is_file():
                raise XAIClientError(f"image file not found: {request.image}")
        tool_choice = "required" if stage.name == "math-director" else None
        handlers = {"verify_scene": verify_scene} if stage.name == "composer" else None

        def once(user_text: str):
            result = self.client.complete(
                instructions=charter,
                text=user_text,
                tools=stage.tools,
                image_path=image,
                tool_choice=tool_choice,
                function_handlers=handlers,
                schema=schema,
                schema_name=stage.name,
                prompt_cache_key=f"{run_dir.name}:{stage.name}",
                cwd=run_dir,
            )
            payload, errors = validate_stage_output(
                stage.name,
                result.payload if isinstance(result.payload, dict) else {},
            )
            source = None
            if stage.name == "composer" and not errors:
                try:
                    source = extract_scene_source(payload, result.text, result.tool_calls)
                except ValueError:
                    errors = ["composer did not return grok_scene.py source"]
                else:
                    report = verify_scene_report(source)
                    if not report["passed"]:
                        errors = list(report["errors"])
            return result, payload, source, errors

        result, payload, source, errors = once(base_text)
        if errors:
            corrective = (
                base_text
                + "\n\nThe previous reply failed validation:\n"
                + "\n".join(f"- {item}" for item in errors)
                + "\nReturn one corrected JSON object."
            )
            result, payload, source, errors = once(corrective)
        if errors:
            raise XAIClientError(f"stage {stage.name} failed validation: " + "; ".join(errors))
        written = payload
        if stage.name == "composer":
            written = {
                key: payload[key]
                for key in (
                    "scene_name",
                    "scene_class",
                    "palette",
                    "objects",
                    "timeline",
                    "constraints",
                    "acceptance",
                )
            }
            text = source if source.endswith("\n") else source + "\n"
            (run_dir / "grok_scene.py").write_text(text, encoding="utf-8")
        (run_dir / stage.artifact).write_text(json.dumps(written, indent=2), encoding="utf-8")
        stills = write_stills(run_dir, result.images)
        trace = {
            "stage": stage.name,
            "model": self.client.model,
            "reasoning_effort": getattr(self.client, "reasoning_effort", None),
            "tools_requested": [tool.get("type") or tool.get("name") for tool in stage.tools],
            "tool_calls": result.tool_calls,
            "thinking": result.thinking,
            "stills": stills,
            "warnings": result.warnings,
            "prompt_cache_key": f"{run_dir.name}:{stage.name}",
        }
        (run_dir / "traces" / f"{stage.name}.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
        (run_dir / "traces" / f"{stage.name}.raw.json").write_text(
            json.dumps(result.raw, indent=2),
            encoding="utf-8",
        )
        return result, source

    def _audit(self, run_dir, request, stage_name, paths, frame_names, images, feedback):
        allowed: set[str] = set()
        filenames: list[str] = []
        for path in paths:
            if Path(path).is_file():
                filenames.append(Path(path).name)
                allowed.add(Path(path).name)
        if frame_names:
            for name in frame_names:
                allowed.add(name)
                if name not in filenames:
                    filenames.append(name)
        prompt = audit_prompt(
            stage_name,
            request.prompt,
            filenames,
            feedback=feedback,
            frames=sorted(frame_names or []),
        )

        def once(text: str):
            return self.client.complete(
                instructions=AUDITOR_CHARTER,
                text=text,
                schema=Assessment.model_json_schema(),
                schema_name="assessment",
                prompt_cache_key=f"{run_dir.name}:{stage_name}:audit",
                image_paths=list(images or []),
                cwd=run_dir,
            )

        result = once(prompt)
        assessment, issues = parse_assessment(
            result.payload if isinstance(result.payload, dict) else {},
            allowed,
            set(frame_names) if frame_names is not None else None,
        )
        if issues:
            result = once(
                prompt
                + "\n\nYour previous assessment was rejected:\n"
                + "\n".join(f"- {item}" for item in issues)
                + "\nReturn one corrected assessment JSON object."
            )
            assessment, issues = parse_assessment(
                result.payload if isinstance(result.payload, dict) else {},
                allowed,
                set(frame_names) if frame_names is not None else None,
            )
        if issues or assessment is None:
            if request.review == "gated":
                raise XAIClientError("audit failed: " + "; ".join(issues or ["invalid assessment"]))
            repair = stage_name if stage_name in STAGE_ORDER else "composer"
            evidence = filenames[:1] or ["grok_scene.py"]
            assessment = Assessment(
                verdict="fail",
                evidence=evidence,
                repair_stage=repair,
                feedback="; ".join(issues or ["invalid assessment"]),
                defects=list(issues or ["invalid assessment"]),
            )
        audit_dir = run_dir / "audits"
        audit_dir.mkdir(exist_ok=True)
        (audit_dir / f"{stage_name}.json").write_text(assessment.model_dump_json(indent=2), encoding="utf-8")
        (run_dir / "traces" / f"{stage_name}.audit.json").write_text(
            json.dumps({"warnings": result.warnings, "schema_name": "assessment"}, indent=2),
            encoding="utf-8",
        )
        return assessment

    def _render_evidence(self, run_dir, request, manifest, feedback):
        source = (run_dir / "grok_scene.py").read_text(encoding="utf-8")
        attempt = _next_attempt(run_dir)
        try:
            record, still = self.prober(
                run_dir,
                source,
                attempt,
                quality=request.quality,
                timeout=min(600, request.render_timeout),
            )
        except (RuntimeError, OSError, ValueError) as exc:
            raise RenderNeedsRepair("composer", f"Final-frame probe failed: {exc}") from exc
        try:
            video, frames, sheet = self.renderer(
                run_dir,
                source,
                request.quality,
                attempt,
                timeout=request.render_timeout,
                min_duration=request.min_duration,
                max_duration=request.max_duration,
            )
        except (RuntimeError, OSError, ValueError) as exc:
            raise RenderNeedsRepair("composer", f"Render failed: {exc}") from exc
        review_note = {
            "frames": [frame.name for frame in frames],
            "contact_sheet": Path(sheet).name,
            "probe": Path(record).name,
            "still": Path(still).name,
        }
        if request.review == "off":
            review_note["verdict"] = "not_reviewed"
            self._merge_review(run_dir, review_note)
            return video
        paths = [run_dir / stage.artifact for stage in STAGES]
        paths.extend([run_dir / "grok_scene.py", record, still, sheet])
        paths.extend(frames)
        assessment = self._audit(
            run_dir,
            request,
            "render",
            paths,
            frame_names={frame.name for frame in frames},
            images=frames,
            feedback=feedback,
        )
        review_note["verdict"] = assessment.verdict
        review_note["evidence"] = assessment.evidence
        self._merge_review(run_dir, review_note)
        manifest.video_path = video.resolve().relative_to(run_dir.resolve()).as_posix()
        if request.review == "gated" and assessment.verdict != "pass":
            raise RenderNeedsRepair(assessment.repair_stage, assessment.feedback or "render review failed")
        return video

    def _repair_scene(self, run_dir: Path, request: RunRequest, failures: list[str]) -> None:
        source = (run_dir / "grok_scene.py").read_text(encoding="utf-8")
        result = self.client.complete(
            instructions=load_charter("grok-composer.md"),
            text=(
                "Repair this Manim scene. Keep the class name, ThreeDScene contract, "
                "and camera rule. Return JSON with a source field containing the "
                "complete file.\n\nFAILURES:\n"
                + "\n".join(f"- {item}" for item in failures)
                + "\n\nCURRENT FILE:\n"
                + source
            ),
            tools=(VERIFY_SCENE_TOOL,),
            function_handlers={"verify_scene": verify_scene},
            schema=STAGE_MODELS["composer"].model_json_schema(),
            schema_name="composer",
            prompt_cache_key=f"{run_dir.name}:composer:repair",
            cwd=run_dir,
        )
        try:
            repaired = extract_scene_source(result.payload, result.text, result.tool_calls)
        except ValueError as exc:
            raise XAIClientError("composer repair did not return grok_scene.py source") from exc
        (run_dir / "grok_scene.py").write_text(repaired, encoding="utf-8")
        (run_dir / "traces" / "repair.json").write_text(
            json.dumps(
                {"tool_calls": result.tool_calls, "thinking": result.thinking, "warnings": result.warnings},
                indent=2,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _merge_review(run_dir: Path, note: dict) -> None:
        path = run_dir / "review.json"
        review = {}
        if path.is_file():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    review = loaded
            except json.JSONDecodeError:
                review = {}
        review["render_evidence"] = note
        path.write_text(json.dumps(review, indent=2), encoding="utf-8")

    @staticmethod
    def _note_local_render(run_dir: Path) -> None:
        path = run_dir / "review.json"
        review = {}
        if path.is_file():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    review = loaded
            except json.JSONDecodeError:
                review = {}
        review["local_render"] = {
            "review_status": "not_reviewed",
            "model_calls": 0,
        }
        path.write_text(json.dumps(review, indent=2), encoding="utf-8")


def _review_status(request: RunRequest) -> str:
    if request.offline or request.review == "off":
        return "not_reviewed"
    if request.review == "gated":
        return "approved"
    return "advisory"


def _dependency_paths(index: int) -> list[str]:
    rels = ["request.json"]
    for stage in STAGES[: index + 1]:
        rels.append(stage.artifact)
    if STAGES[index].name == "composer":
        rels.append("grok_scene.py")
    return rels


def _ledger_covers(run_dir: Path, ledger: dict) -> bool:
    stages = ledger.get("stages") or {}
    for index, stage in enumerate(STAGES):
        hashes = (stages.get(stage.name) or {}).get("hashes")
        if not hashes or not hashes_match(run_dir, hashes):
            return False
    return True


def _next_attempt(run_dir: Path) -> int:
    numbers: list[int] = []
    for folder_name in ("renders", "probes"):
        folder = run_dir / folder_name
        if not folder.is_dir():
            continue
        numbers.extend(int(path.name) for path in folder.iterdir() if path.name.isdigit())
    return max(numbers or [0]) + 1


def _stage_prompt(stage: str, prompt: str, prior: dict[str, dict]) -> str:
    dossier = json.dumps(prior, indent=2) if prior else "{}"
    return (
        f"User request:\n{prompt}\n\n"
        f"You are the {stage} stage. Read the charter. Return one JSON object "
        "with exactly the keys the charter names.\n"
        "If you write the scene, also include a source field with the complete "
        "Python file, or a fenced python block.\n\n"
        f"Upstream artifacts:\n{dossier}\n"
    )
