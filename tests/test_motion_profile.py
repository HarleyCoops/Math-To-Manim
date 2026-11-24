"""The motion prompt profile: contracts, profile plumbing and an offline run."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from mythos.charters import DEFAULT_PROFILE, PROFILE_NAMES, get_profile
from mythos.charter import CINEMATIC_CHARTER
from mythos.cli import build_parser
from mythos.motion import MotionHarness
from mythos.motion import pipeline
from mythos.motion.contracts import (
    BriefSpec,
    QACheck,
    QAReport,
    StyleSheet,
    Timeline,
    brief_spec_problems,
    source_found,
    style_sheet_problems,
    timeline_problems,
)
from mythos.motion.qa import frame_times
from mythos.service import MythosService
from mythos.trace import EVENT_FIELDS

BRIEF = ('Demo BENEFITS - feature list, 16:9, ~4.0s. Brand purple #6A4DFF; text dark '
         '~#2C2359. Camera fully static. Labels in order: "Fast" / "Simple". '
         'The circle never fills solid purple.')


def _spec(**overrides) -> BriefSpec:
    data = {
        "aspect_ratio": "16:9", "width": 1920, "height": 1080, "duration_s": 4.0,
        "fps": 30, "format_source": "16:9, ~4.0s", "background": "white",
        "camera": "Camera fully static.",
        "palette": [{"role": "brand", "hex": "#6a4dff", "source": "Brand purple #6A4DFF"}],
        "texts": [{"id": "l1", "text": "Fast", "source": '"Fast"'}],
        "rules": [{"id": "r1", "rule": "no solid fill",
                   "source": "The circle never fills solid purple."}],
    }
    data.update(overrides)
    return BriefSpec.model_validate(data)


def test_profiles_registry_keeps_math_unchanged():
    assert DEFAULT_PROFILE == "math"
    assert set(PROFILE_NAMES) == {"math", "motion"}
    assert get_profile(None).charter == CINEMATIC_CHARTER
    assert get_profile("math").charter == CINEMATIC_CHARTER
    motion = get_profile("motion").charter
    assert "ADHERENCE BEFORE INVENTION" in motion and "plain text only" in motion
    with pytest.raises(ValueError):
        get_profile("cartoon")


def test_brief_spec_normalises_hex_and_rejects_bad_colours():
    assert _spec().palette[0].hex == "#6A4DFF"
    with pytest.raises(ValidationError):
        _spec(palette=[{"role": "x", "hex": "purple", "source": "Brand purple #6A4DFF"}])


def test_brief_spec_sources_must_quote_the_brief():
    assert brief_spec_problems(_spec(), BRIEF) == []
    bad = _spec(texts=[{"id": "l1", "text": "Fast", "source": "an invented line"}])
    assert any("does not quote" in p for p in brief_spec_problems(bad, BRIEF))
    assert source_found("default: charter", BRIEF)
    assert source_found("Brand purple ... text dark", BRIEF)
    assert any("aspect" in p for p in brief_spec_problems(_spec(width=1000), BRIEF))


def test_style_sheet_colours_come_from_the_palette():
    spec = _spec()
    sheet = StyleSheet.model_validate({
        "type_scale": [{"role": "label", "font": "Inter", "size_px": 44, "colour": "#6A4DFF"}],
        "safe_margin_px": 60,
        "easings": [{"name": "pop", "use": "entrances", "manim_rate_func": "ease_out_back"}],
        "colour_roles": [{"role": "accent", "hex": "#6A4DFF"},
                         {"role": "glow", "hex": "#123456"}],
    })
    problems = style_sheet_problems(sheet, spec)
    assert len(problems) == 1 and "#123456" in problems[0]


def test_timeline_must_cover_the_duration_without_gaps():
    spec = _spec()
    good = Timeline.model_validate({"duration_s": 4.0, "beats": [
        {"id": "a", "start_s": 0, "end_s": 2.0, "focal_point": "list"},
        {"id": "b", "start_s": 2.0, "end_s": 4.0, "focal_point": "list"}]})
    assert timeline_problems(good, spec) == []
    gap = Timeline.model_validate({"duration_s": 4.0, "beats": [
        {"id": "a", "start_s": 0, "end_s": 1.5, "focal_point": "list"},
        {"id": "b", "start_s": 2.0, "end_s": 3.5, "focal_point": "list"}]})
    problems = timeline_problems(gap, spec)
    assert any("gap" in p for p in problems) and any("sum" in p for p in problems)
    assert frame_times(good, 4.0, 30) == [0.0, 1.0, 1.967, 3.0, 3.967]


def test_qa_report_pass_rate_by_field_type():
    report = QAReport(checks=[
        QACheck(field="a", field_type="text", expected="x", passed=True, method="vision"),
        QACheck(field="b", field_type="text", expected="y", passed=False, method="vision"),
        QACheck(field="c", field_type="format", expected="z", passed=True, method="probe"),
    ])
    assert not report.passed and [c.field for c in report.failures] == ["b"]
    assert report.pass_rate_by_type()["text"] == {"passed": 1, "total": 2, "rate": 0.5}


def test_typed_stage_prompt_carries_the_brief_verbatim():
    prompt = pipeline.typed_stage_prompt("brief_parser", BRIEF, {}, BriefSpec)
    assert BRIEF in prompt and "BriefSpec" in prompt
    repair = pipeline.repair_message(2, QAReport(checks=[QACheck(
        field="l1", field_type="text", expected="Fast", observed="Fsat", passed=False,
        method="vision", frame="t001.000s.png")]), None)
    assert "REPAIR LOOP 2 of 4" in repair and "Fsat" in repair


def test_cli_profile_flag_defaults_to_math():
    parser = build_parser()
    assert parser.parse_args(["run", "x"]).profile == "math"
    args = parser.parse_args(["run", "--profile", "motion", "--brief-file", "b.md"])
    assert args.profile == "motion" and args.prompt is None and args.max_repairs is None
    with pytest.raises(SystemExit):
        parser.parse_args(["run", "x", "--profile", "cartoon"])


def test_offline_motion_run_writes_contracts_code_and_trace(tmp_path):
    harness = MotionHarness(offline=True, runs_dir=tmp_path / "runs", log=lambda m: None)
    manifest = harness.run(BRIEF, task_id="Demo_01", run_dir=tmp_path / "runs" / "Demo_01")
    run = tmp_path / "runs" / "Demo_01"
    assert manifest["profile"] == "motion" and manifest["task_id"] == "Demo_01"
    assert manifest["motion_status"] == "scene_ready"
    assert (run / "00_brief.md").read_text(encoding="utf-8") == BRIEF
    spec = BriefSpec.model_validate_json((run / "01_brief_spec.json").read_text())
    assert spec.duration_s == 4.0 and [t.text for t in spec.texts] == ["Fast", "Simple"]
    StyleSheet.model_validate_json((run / "02_style_sheet.json").read_text())
    Timeline.model_validate_json((run / "03_timeline.json").read_text())
    assert (run / "code" / "v001.py").is_file() and (run / "work" / "scene.py").is_file()
    events = [json.loads(line) for line in (run / "events.jsonl").read_text().splitlines()]
    assert [e["seq"] for e in events] == list(range(1, len(events) + 1))
    assert {e["event_type"] for e in events} == {"code_version", "final"}
    assert all(tuple(e) == EVENT_FIELDS for e in events)
    final = events[-1]["output"]
    assert final["status"] == "scene_ready" and final["loops_used"] == 0
    assert json.loads((run / "run_summary.json").read_text())["status"] == "scene_ready"


def test_service_runs_the_motion_profile_offline(tmp_path):
    service = MythosService(runs_dir=tmp_path / "runs")
    job = service.run_sync(BRIEF, offline=True, profile="motion")
    assert job.status == "completed", job.error
    assert job.options["profile"] == "motion"
    assert job.manifest["profile"] == "motion"
    math_job = service.run_sync("the heat equation", offline=True)
    assert math_job.options["profile"] == "math" and "profile" not in math_job.manifest
    with pytest.raises(ValueError):
        service.run_sync(BRIEF, offline=True, profile="cartoon")


def test_api_and_mcp_accept_the_profile():
    from mythos.api import RunRequest
    from mythos.mcp_server import CreateAnimationInput

    assert RunRequest(prompt="abc").profile == "math"
    assert RunRequest(prompt="abc", profile="motion").profile == "motion"
    assert CreateAnimationInput(prompt="abc", profile="motion").profile == "motion"
    with pytest.raises(ValidationError):
        RunRequest(prompt="abc", profile="cartoon")
