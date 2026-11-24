"""The motion chain runner (see :mod:`mythos.motion`)."""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from mythos import trace as tr
from mythos.charter import JSON_CONTRACT, extract_json_object
from mythos.charters.motion import CHARTER
from mythos.harness import AGENT_DIR, MythosHarness, StageValidationError
from mythos.layout import create_run_dir, write_json
from mythos.lifecycle import enter_stage, mark_run_completed, mark_run_failed
from mythos.manifest_schema import manifest_template
from mythos.motion import qa
from mythos.motion import render as mrender
from mythos.motion.contracts import (
    VISION_QA_SCHEMA,
    BriefSpec,
    QACheck,
    QAReport,
    StyleSheet,
    Timeline,
    brief_spec_problems,
    style_sheet_problems,
    timeline_problems,
)
from mythos.settings import agent_config_dir, trace_scrub_names

PROFILE = "motion"
SCENE_FILE = "scene.py"
SCENE_CLASS = "MotionScene"
BRIEF_FILE = "00_brief.md"
EVENTS_FILE = "events.jsonl"
MAX_REPAIR_LOOPS = 4
QA_FRAME_WIDTH = 960

STAGE_FILES = {
    "brief_parser": ("motion-brief-parser.md", "01_brief_spec.json"),
    "art_director": ("motion-art-director.md", "02_style_sheet.json"),
    "storyboard": ("motion-storyboard.md", "03_timeline.json"),
}


def load_stage_text(file_name: str) -> str:
    text = (AGENT_DIR / file_name).read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return text.strip()


def _schema(model: type[BaseModel]) -> str:
    return json.dumps(model.model_json_schema(), separators=(",", ":"))


def typed_stage_prompt(stage: str, brief: str, inputs: dict[str, Any],
                       model: type[BaseModel]) -> str:
    """The exact prompt a typed stage (1-3) receives; the system text is the charter."""
    parts = [load_stage_text(STAGE_FILES[stage][0]),
             "THE BRIEF (verbatim; it is the specification):\n<<<\n" + brief + "\n>>>"]
    for name, value in inputs.items():
        parts.append(f"{name} JSON:\n{json.dumps(value, indent=2, ensure_ascii=False)}")
    parts.append(f"Your answer must validate against this JSON schema ({model.__name__}):\n"
                 + _schema(model))
    return "\n\n".join(parts) + JSON_CONTRACT


def coder_prompt(brief: str, spec: BriefSpec, sheet: StyleSheet, timeline: Timeline) -> str:
    brands = [e for e in spec.elements if e.brand_mark]
    brand_note = ""
    if brands or spec.brand_names:
        names = ", ".join(spec.brand_names) or "the brand"
        brand_note = (f"\nREAL BRANDS: {names}. Elements "
                      f"{', '.join(e.id for e in brands) or '(none flagged)'} describe a real "
                      "brand mark: set the brand name as plain text in their place. Do not "
                      "draw or imitate the mark.\n")
    return (
        f"TASK: write {SCENE_FILE} in the current folder with exactly one scene class named "
        f"{SCENE_CLASS}. The harness renders the final video at {spec.width}x{spec.height}, "
        f"{spec.fps:g} fps; it must last {spec.duration_s:.3f} s (+/-0.1 s). You render "
        "drafts with render_draft and look at them before you stop.\n"
        f"{brand_note}\n"
        "THE BRIEF (verbatim; it is the specification):\n<<<\n" + brief + "\n>>>\n\n"
        "BriefSpec JSON:\n" + spec.model_dump_json(indent=2) + "\n\n"
        "StyleSheet JSON:\n" + sheet.model_dump_json(indent=2) + "\n\n"
        "Timeline JSON:\n" + timeline.model_dump_json(indent=2) + "\n"
    )


def qa_prompt(brief: str, spec: BriefSpec, timeline: Timeline,
              frames: list[tuple[float, Path]]) -> str:
    beats = sorted(timeline.beats, key=lambda b: b.start_s)

    def beat_of(t: float) -> str:
        for beat in beats:
            if beat.start_s - 1e-6 <= t < beat.end_s + 1e-6:
                return beat.id
        return beats[-1].id

    listing = "\n".join(f"- {p.name}: t = {t:.3f} s (beat {beat_of(t)})" for t, p in frames)
    return (
        "Check this rendered video against its brief. The frames are in the current "
        "folder; open every one with Read before you answer.\n\n"
        f"FRAMES ({len(frames)}, {QA_FRAME_WIDTH}px wide copies of the "
        f"{spec.width}x{spec.height} render):\n{listing}\n\n"
        "THE BRIEF (verbatim):\n<<<\n" + brief + "\n>>>\n\n"
        "BriefSpec JSON:\n" + spec.model_dump_json(indent=2) + "\n\n"
        "Timeline JSON:\n" + timeline.model_dump_json(indent=2) + "\n\n"
        "Format, duration and palette presence are measured separately; do not "
        "repeat them. Return one check per text, element, motion and rule in the "
        "BriefSpec, plus layout checks."
    )


def repair_message(loop: int, report: QAReport | None, render_error: str | None) -> str:
    if render_error:
        failures = "The full-quality render FAILED:\n" + render_error[-6000:]
    else:
        assert report is not None
        failures = "QA failures:\n" + qa.failure_text(report)
    return load_stage_text("motion-repair.md").format(
        loop=loop, max_loops=MAX_REPAIR_LOOPS, failures=failures)


# ---------------------------------------------------------------------- #
# Offline stand-ins (no model, no SDK)                                   #
# ---------------------------------------------------------------------- #

def offline_brief_spec(brief: str) -> BriefSpec:
    duration = 6.0
    match = re.search(r"~?\s*(\d+(?:\.\d+)?)\s*s\b", brief)
    if match:
        duration = float(match.group(1))
    hexes = list(dict.fromkeys(h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}\b", brief)))
    quoted = re.findall(r"\"([^\"]{2,80})\"", brief)
    return BriefSpec.model_validate({
        "aspect_ratio": "16:9", "width": 1920, "height": 1080, "duration_s": duration,
        "fps": 30, "format_source": "default: charter", "background": "offline",
        "camera": "static",
        "palette": [{"role": f"colour_{i}", "hex": h, "source": h}
                    for i, h in enumerate(hexes, 1)],
        "texts": [{"id": f"text_{i}", "text": t, "order": i, "source": t}
                  for i, t in enumerate(quoted, 1)],
    })


def offline_style_sheet(spec: BriefSpec) -> StyleSheet:
    hex_value = spec.palette[0].hex if spec.palette else "#FFFFFF"
    return StyleSheet.model_validate({
        "type_scale": [{"role": "label", "font": "default", "size_px": 40,
                        "colour": hex_value}],
        "safe_margin_px": int(0.05 * min(spec.width, spec.height)) + 1,
        "easings": [{"name": "enter", "use": "entrances", "manim_rate_func": "smooth"}],
        "colour_roles": [{"role": "accent", "hex": hex_value}],
    })


def offline_timeline(spec: BriefSpec) -> Timeline:
    half = round(spec.duration_s / 2, 3)
    return Timeline.model_validate({"duration_s": spec.duration_s, "beats": [
        {"id": "build", "start_s": 0, "end_s": half, "focal_point": "text"},
        {"id": "hold", "start_s": half, "end_s": spec.duration_s, "focal_point": "text"},
    ]})


def offline_scene(spec: BriefSpec) -> str:
    texts = [t.text for t in spec.texts][:4] or ["Motion profile: offline rehearsal"]
    colour = spec.palette[0].hex if spec.palette else "#FFFFFF"
    return (
        "from manim import *\n\n\n"
        f"class {SCENE_CLASS}(Scene):\n"
        "    def construct(self):\n"
        f"        lines = VGroup(*[Text(t, font_size=36, color={colour!r}) for t in {texts!r}])\n"
        "        lines.arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT)\n"
        "        self.play(LaggedStart(*[FadeIn(m, shift=0.2 * RIGHT) for m in lines],\n"
        "                              lag_ratio=0.3), run_time=1.0, rate_func=smooth)\n"
        f"        self.wait({max(spec.duration_s - 1.0, 0.1):.3f})\n"
    )


# ---------------------------------------------------------------------- #
# The harness                                                             #
# ---------------------------------------------------------------------- #

class MotionHarness(MythosHarness):
    """Runs the motion chain. Shares the fallback ladder and bookkeeping of
    :class:`mythos.harness.MythosHarness`; the stages are its own."""

    profile = PROFILE

    def __init__(self, *, agent_config_dir_override: str | None = None,
                 agents_factory: Callable[..., Any] | None = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.agent_config_dir = agent_config_dir_override or agent_config_dir()
        self.agents_factory = agents_factory

    # ------------------------------------------------------------------ #

    def run(self, prompt: str, *, render: bool = False, quality: str = "l",
            max_repairs: int = MAX_REPAIR_LOOPS,
            run_dir_callback: Callable[[str], None] | None = None,
            task_id: str | None = None, run_dir: Path | None = None) -> dict:
        brief = prompt.replace(chr(0xFEFF), "")
        if not brief.strip():
            raise ValueError("the brief is empty")
        max_repairs = max(0, min(int(max_repairs), MAX_REPAIR_LOOPS))
        if run_dir is None:
            run_dir = create_run_dir(self.runs_dir, brief)
        else:
            run_dir = Path(run_dir)
            run_dir.mkdir(parents=True, exist_ok=True)
        if run_dir_callback is not None:
            run_dir_callback(run_dir.name)
        (run_dir / BRIEF_FILE).write_text(brief, encoding="utf-8")
        manifest = manifest_template(
            run_id=run_dir.name, prompt=brief, model=self.model, command=self.command,
            offline=self.offline, created_utc=datetime.now(timezone.utc).isoformat())
        manifest.update({"profile": PROFILE, "task_id": task_id, "brief_file": BRIEF_FILE,
                         "events": EVENTS_FILE, "warnings": []})
        writer = tr.TraceWriter(
            run_dir / EVENTS_FILE, run_id=run_dir.name, task_id=task_id, profile=PROFILE,
            runtime="offline" if self.offline else "local", model=self.model,
            scrubber=tr.Scrubber.from_environment(extra_names=trace_scrub_names()))
        enter_stage(manifest, "brief_parser")
        self._save(run_dir, manifest)
        started = time.perf_counter()
        try:
            self._run_motion(brief, run_dir, manifest, writer, render=render,
                             max_repairs=max_repairs)
        except BaseException as exc:
            mark_run_failed(manifest, exc)
            self._final_event(writer, manifest, started, status="error",
                              error=f"{type(exc).__name__}: {exc}")
            try:
                self._save(run_dir, manifest)
            except Exception:  # noqa: BLE001 - never mask the original error
                pass
            raise
        manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
        mark_run_completed(manifest)
        self._final_event(writer, manifest, started, status=manifest.get("motion_status", ""))
        self._save(run_dir, manifest)
        self.log(f"motion run {manifest.get('motion_status')} -> {run_dir}")
        return manifest

    # ------------------------------------------------------------------ #
    # Stages 1-3                                                          #
    # ------------------------------------------------------------------ #

    def _typed(self, stage: str, brief: str, inputs: dict[str, Any], model: type[BaseModel],
               check: Callable[[Any], list[str]], run_dir: Path, writer: tr.TraceWriter,
               manifest: dict) -> Any:
        prompt = typed_stage_prompt(stage, brief, inputs, model)
        artifact_name = STAGE_FILES[stage][1]
        problems: list[str] = []
        value = None
        best: tuple[Any, list[str]] | None = None
        for attempt in (1, 2):
            text = prompt if attempt == 1 else (
                prompt + "\n\nPREVIOUS ATTEMPT REJECTED. Fix these problems and answer "
                "again with the complete object:\n- " + "\n- ".join(problems))
            with tr.bind(writer, stage):
                raw = self._model(text, system_extra=CHARTER)
            suffix = "" if attempt == 1 else ".retry"
            (run_dir / f"{Path(artifact_name).stem}{suffix}.raw.txt").write_text(
                raw, encoding="utf-8")
            try:
                value = model.model_validate(extract_json_object(raw))
            except (ValidationError, RuntimeError, ValueError) as exc:
                value, problems = None, [f"invalid {model.__name__}: {str(exc)[:3000]}"]
                continue
            problems = check(value)
            if best is None or len(problems) <= len(best[1]):
                best = (value, problems)
            if not problems:
                break
        if best is not None:
            value, problems = best
        if value is None:
            raise StageValidationError(f"stage {stage!r} gave no valid {model.__name__} "
                                       f"after a retry: {problems}")
        if problems:
            manifest["warnings"].extend(f"{stage}: {p}" for p in problems)
        return value

    def _run_motion(self, brief: str, run_dir: Path, manifest: dict,
                    writer: tr.TraceWriter, *, render: bool, max_repairs: int) -> None:
        def record(stage: str, value: BaseModel, seconds: float) -> None:
            name = STAGE_FILES[stage][1]
            write_json(run_dir / name, value.model_dump(mode="json"))
            manifest["artifacts"][stage] = name
            manifest["stages"].append({"stage": stage, "artifact": name,
                                       "seconds": round(seconds, 2)})
            self._save(run_dir, manifest)
            self.log(f"{stage:<16} -> {name}")

        t0 = time.perf_counter()
        if self.offline:
            spec = offline_brief_spec(brief)
        else:
            spec = self._typed("brief_parser", brief, {}, BriefSpec,
                               lambda s: brief_spec_problems(s, brief), run_dir, writer,
                               manifest)
        record("brief_parser", spec, time.perf_counter() - t0)

        enter_stage(manifest, "art_director")
        t0 = time.perf_counter()
        sheet = (offline_style_sheet(spec) if self.offline else self._typed(
            "art_director", brief, {"BriefSpec": spec.model_dump(mode="json")}, StyleSheet,
            lambda s: style_sheet_problems(s, spec), run_dir, writer, manifest))
        record("art_director", sheet, time.perf_counter() - t0)

        enter_stage(manifest, "storyboard")
        t0 = time.perf_counter()
        timeline = (offline_timeline(spec) if self.offline else self._typed(
            "storyboard", brief, {"BriefSpec": spec.model_dump(mode="json"),
                                  "StyleSheet": sheet.model_dump(mode="json")}, Timeline,
            lambda t: timeline_problems(t, spec), run_dir, writer, manifest))
        record("storyboard", timeline, time.perf_counter() - t0)

        work = run_dir / "work"
        work.mkdir(exist_ok=True)
        from mythos.motion.agent import CodeVersions

        versions = CodeVersions(writer, run_dir / "code", work / SCENE_FILE)
        enter_stage(manifest, "scene_coder")
        self._save(run_dir, manifest)
        if self.offline:
            (work / SCENE_FILE).write_text(offline_scene(spec), encoding="utf-8")
            versions.snapshot("scene_coder", "offline stand-in")
            manifest["scene_file"] = f"work/{SCENE_FILE}"
            manifest["scene_name"] = SCENE_CLASS
            if render:
                report, _ = self._render_and_check(run_dir, work, spec, timeline, writer,
                                                    manifest, loop=0, vision=None)
                manifest["motion_status"] = "passed" if report and report.passed else "qa_failed"
            else:
                manifest["motion_status"] = "scene_ready"
            manifest["code_versions"] = len(versions.paths)
            return
        asyncio.run(self._agent_stages(brief, run_dir, work, spec, sheet, timeline, writer,
                                       manifest, versions, render=render,
                                       max_repairs=max_repairs))

    # ------------------------------------------------------------------ #
    # Stages 4-6                                                          #
    # ------------------------------------------------------------------ #

    def _agents(self, writer: tr.TraceWriter, work: Path, spec: BriefSpec, versions: Any):
        from mythos.motion.agent import MotionAgents

        factory = self.agents_factory or MotionAgents
        agents = factory(
            writer=writer, work_dir=work, scene_file=SCENE_FILE, width=spec.width,
            height=spec.height, fps=spec.fps, model=self.model,
            coder_system=CHARTER + "\n\n" + load_stage_text("motion-scene-coder.md"),
            qa_system=CHARTER + "\n\n" + load_stage_text("motion-visual-qa.md"),
            versions=versions, render_timeout=self.render_timeout,
            config_dir=self.agent_config_dir, log=self.log)
        agents.target_duration = spec.duration_s
        return agents

    async def _agent_stages(self, brief: str, run_dir: Path, work: Path, spec: BriefSpec,
                            sheet: StyleSheet, timeline: Timeline, writer: tr.TraceWriter,
                            manifest: dict, versions: Any, *, render: bool,
                            max_repairs: int) -> None:
        from mythos.motion.agent import client_class

        agents = self._agents(writer, work, spec, versions)
        manifest["agent_runtime"] = {"runtime": "claude-agent-sdk", "model": self.model,
                                     "login": "cli" if not self.agent_config_dir
                                     else "CLAUDE_CONFIG_DIR"}
        loops: list[dict] = []
        manifest["repair_loops"] = loops
        async with client_class()(options=agents.coder_options()) as client:
            turn = await agents.ask(client, coder_prompt(brief, spec, sheet, timeline),
                                    "scene_coder")
            versions.snapshot("scene_coder", "end of coder turn", turn.seq)
            if turn.error:
                manifest["warnings"].append(f"scene_coder: {turn.error}")
            manifest["scene_file"] = f"work/{SCENE_FILE}"
            if not (work / SCENE_FILE).is_file():
                raise RuntimeError("the scene coder did not write the scene file")
            if not render:
                manifest["motion_status"] = "scene_ready"
                manifest["code_versions"] = len(versions.paths)
                return
            loop = 0
            while True:
                enter_stage(manifest, "render_qa")
                self._save(run_dir, manifest)
                report, render_error = await self._render_and_check_async(
                    run_dir, work, spec, timeline, writer, manifest, loop, agents, brief)
                if report is not None and report.passed:
                    manifest["motion_status"] = "passed"
                    break
                if report is not None and report.model_extra.get("vision_error"):
                    manifest["motion_status"] = "qa_incomplete"
                    break
                if loop >= max_repairs:
                    manifest["motion_status"] = ("render_failed" if render_error
                                                 else "qa_failed")
                    break
                loop += 1
                cause = "render_error" if render_error else "qa_failure"
                fields = [] if render_error else [c.field for c in report.failures]
                writer.emit("repair_loop", stage="repair",
                            input={"loop": loop, "cause": cause, "fields": fields},
                            output={"failures": len(fields)})
                loops.append({"loop": loop, "cause": cause, "fields": fields})
                enter_stage(manifest, "repair")
                self._save(run_dir, manifest)
                self.log(f"repair loop {loop}: {cause} ({len(fields)} fields)")
                turn = await agents.ask(client, repair_message(loop, report, render_error),
                                        "repair")
                versions.snapshot("repair", f"end of repair loop {loop}", turn.seq)
        manifest["code_versions"] = len(versions.paths)
        manifest["draft_renders"] = agents.draft_count

    async def _render_and_check_async(self, run_dir: Path, work: Path, spec: BriefSpec,
                                      timeline: Timeline, writer: tr.TraceWriter,
                                      manifest: dict, loop: int, agents: Any, brief: str):
        report, render_error = await asyncio.to_thread(
            self._render_and_check, run_dir, work, spec, timeline, writer, manifest, loop,
            None)
        if render_error is not None:
            return report, render_error
        qa_dir = run_dir / "frames" / f"loop{loop}" / "qa"
        frames = sorted((float(p.stem[1:-1]), p) for p in qa_dir.glob("t*.png"))
        vision = None
        for attempt in (1, 2):
            turn = await agents.visual_qa(qa_prompt(brief, spec, timeline, frames), qa_dir,
                                          VISION_QA_SCHEMA)
            structured = turn.structured if isinstance(turn.structured, dict) else None
            if structured is None and turn.text:
                try:
                    structured = extract_json_object(turn.text)
                except RuntimeError:
                    structured = None
            if structured and isinstance(structured.get("checks"), list):
                try:
                    vision = [QACheck.model_validate({**c, "method": "vision"})
                              for c in structured["checks"]]
                    break
                except ValidationError as exc:
                    manifest["warnings"].append(f"visual_qa attempt {attempt}: {exc}"[:500])
        merged = QAReport(loop=loop, checks=list(report.checks) + (vision or []))
        if vision is None:
            merged = QAReport(loop=loop, checks=merged.checks,
                              vision_error="visual QA agent gave no valid checks")
        else:
            for check in vision:
                writer.emit("qa_check", stage="visual_qa",
                            input={"loop": loop, "field": check.field,
                                   "field_type": check.field_type, "method": "vision",
                                   "frame": check.frame},
                            output=check.model_dump(mode="json"))
        self._write_report(run_dir, manifest, merged)
        return merged, None

    def _write_report(self, run_dir: Path, manifest: dict, report: QAReport) -> None:
        payload = report.model_dump(mode="json")
        payload["passed"] = report.passed
        payload["pass_rate_by_type"] = report.pass_rate_by_type()
        name = f"05_qa_report_loop{report.loop}.json"
        write_json(run_dir / name, payload)
        write_json(run_dir / "05_qa_report.json", payload)
        manifest.setdefault("qa_reports", []).append(name)
        manifest["qa"] = {"loop": report.loop, "passed": report.passed,
                          "failures": len(report.failures),
                          "pass_rate_by_type": report.pass_rate_by_type()}

    def _render_and_check(self, run_dir: Path, work: Path, spec: BriefSpec,
                          timeline: Timeline, writer: tr.TraceWriter, manifest: dict,
                          loop: int, vision: Any) -> tuple[QAReport | None, str | None]:
        """Full-quality render plus probe and pixel checks. Vision is added by the caller."""
        from mythos.scene_checks import find_scene_class

        scene_name = find_scene_class((work / SCENE_FILE).read_text(encoding="utf-8"))
        manifest["scene_name"] = scene_name
        run = mrender.render(work, scene_file=SCENE_FILE, scene_name=scene_name,
                             width=spec.width, height=spec.height, fps=spec.fps,
                             media_subdir="final_media", timeout=self.render_timeout)
        video_copy = None
        if run.video:
            video_copy = run_dir / "renders" / f"loop{loop}.mp4"
            video_copy.parent.mkdir(exist_ok=True)
            shutil.copyfile(run.video, video_copy)
            shutil.copyfile(run.video, run_dir / "final.mp4")
        writer.emit("render_attempt", stage="render_qa",
                    input={"kind": "final", "loop": loop, "command": run.command,
                           "scene": scene_name},
                    output={"exit_code": run.exit_code, "seconds": round(run.seconds, 2),
                            "timed_out": run.timed_out, "stderr_tail": run.tail(3000),
                            "video_sha256": tr.sha256_file(video_copy) if video_copy else None},
                    latency_ms=run.seconds * 1000)
        manifest.setdefault("renders", []).append(
            {"attempt": loop, "exit_code": run.exit_code, "seconds": round(run.seconds, 2)})
        manifest.setdefault("status", {})["render"] = "complete" if run.video else "failed"
        if not run.video:
            if run.timed_out:
                manifest["render_timed_out"] = True
            return None, run.tail(8000)
        info = mrender.probe(run_dir / "final.mp4")
        times = qa.frame_times(timeline, info.duration_s, info.fps or spec.fps)
        frames_dir = run_dir / "frames" / f"loop{loop}"
        frames = mrender.extract_frames(run_dir / "final.mp4", times, frames_dir)
        mrender.extract_frames(run_dir / "final.mp4", times, frames_dir / "qa",
                               width=QA_FRAME_WIDTH)
        checks = qa.format_checks(spec, info) + qa.colour_checks(spec, frames)
        for check in checks:
            writer.emit("qa_check", stage="render_qa",
                        input={"loop": loop, "field": check.field,
                               "field_type": check.field_type, "method": check.method,
                               "frame": check.frame},
                        output=check.model_dump(mode="json"))
        manifest["final_video"] = "final.mp4"
        manifest["duration_error_s"] = round(info.duration_s - spec.duration_s, 3)
        report = QAReport(loop=loop, checks=checks)
        if vision is None and self.offline:
            self._write_report(run_dir, manifest, report)
        return report, None

    # ------------------------------------------------------------------ #

    def _final_event(self, writer: tr.TraceWriter, manifest: dict, started: float, *,
                     status: str, error: str | None = None) -> None:
        video = None
        run_dir = writer.path.parent
        if (run_dir / "final.mp4").is_file():
            video = tr.sha256_file(run_dir / "final.mp4")
        summary = {
            "status": status,
            "loops_used": len(manifest.get("repair_loops") or []),
            "repair_causes": [l["cause"] for l in manifest.get("repair_loops") or []],
            "tokens_in": writer.tokens_in,
            "tokens_out": writer.tokens_out,
            "wall_time_s": round(time.perf_counter() - started, 1),
            "video_sha256": video,
            "duration_error_s": manifest.get("duration_error_s"),
            "qa": manifest.get("qa"),
            "code_versions": manifest.get("code_versions"),
            "draft_renders": manifest.get("draft_renders"),
            "event_counts": dict(writer.counts),
            "warnings": manifest.get("warnings"),
        }
        if error:
            summary["error"] = error[:2000]
        manifest["summary"] = summary
        writer.emit("final", stage="final", output=summary)
        write_json(run_dir / "run_summary.json", summary)
