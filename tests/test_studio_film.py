"""Studio film path with fake tools: expressions, shot kinds, assembly, agents, the run."""

import json
import sys
from pathlib import Path

import pytest
from PIL import Image

from studio import authoring, film, machine
from studio.runtime import AgentResult
from studio.spec.compile import camera_path, compile_shot
from studio.spec.expr import ExpressionError, compile_expression
from studio.spec.models import SceneSpec, load_spec

OFFLINE = machine.OFFLINE_SPEC


def offline_dict() -> dict:
    return json.loads(OFFLINE.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- expressions

def test_expressions_evaluate_arithmetic_and_named_functions():
    assert compile_expression("0.5 * x * y", ("x", "y"))(x=2.0, y=3.0) == 3.0
    assert compile_expression("2 * cos(t) + pi", ("t",))(t=0.0) == pytest.approx(5.14159, abs=1e-4)
    assert compile_expression("x^2", ("x",))(x=3.0) == 9.0


@pytest.mark.parametrize("source", [
    "__import__('os').system('echo hi')", "x.real", "open('f')", "lambda: 1", "y + 1",
    "[1, 2]", "x if x else 1", "'text'"])
def test_expressions_reject_everything_else(source):
    with pytest.raises(ExpressionError):
        compile_expression(source, ("x",))


def test_expression_that_is_not_finite_is_an_error():
    with pytest.raises(ExpressionError, match="failed at|not finite"):
        compile_expression("1 / x", ("x",))(x=0.0)


# ---------------------------------------------------------------------- spec

def test_shot_kinds_need_their_fields():
    data = offline_dict()
    data["shots"][0]["headline"] = ""
    with pytest.raises(ValueError, match="needs a headline"):
        SceneSpec.model_validate(data)
    data = offline_dict()
    data["shots"][1]["camera"] = None
    with pytest.raises(ValueError, match="needs a camera"):
        SceneSpec.model_validate(data)


def test_unsafe_surface_expression_is_rejected_with_the_object_id():
    data = offline_dict()
    data["objects"][1]["z"] = "__import__('os')"
    with pytest.raises(ValueError, match="band_up"):
        SceneSpec.model_validate(data)


def test_compile_card_surface_curve_and_camera_path():
    spec = load_spec(OFFLINE)
    card = compile_shot(spec, "s1_title")
    assert card["kind"] == "card" and card["frames"] == 60
    assert card["headline"] == "Studio offline rehearsal" and len(card["equations"]) == 1

    bands = compile_shot(spec, "s3_bands")
    assert bands["frames"] == 48 and len(bands["camera_path"]) == 48
    mesh = bands["meshes"][0]
    assert len(mesh["vertices"]) == 37 * 37 and len(mesh["faces"]) == 36 * 36
    corner = mesh["vertices"][0]
    assert corner[2] == pytest.approx(0.35 * corner[0] * corner[1])
    assert len(bands["tubes"][0]["points"]) == 97
    assert bands["caption"] and bands["equations"]

    path = camera_path((10.0, 0.0, 5.0), (0.0, 0.0, 0.0), 90.0, 3)
    assert path[0] == pytest.approx([10.0, 0.0, 5.0])
    assert path[-1] == pytest.approx([0.0, 10.0, 5.0])
    assert spec.duration_s() == pytest.approx(8.5)


# ------------------------------------------------------------------ fake tools

class FakeTools:
    """Stands in for blender, manim, ffmpeg and ffprobe; records every command."""

    def __init__(self, *, fail_blender_for: str | None = None, latex_fails: bool = False):
        self.commands: list[list[str]] = []
        self.fail_blender_for = fail_blender_for
        self.latex_fails = latex_fails

    def __call__(self, command, timeout):
        self.commands.append(command)
        if "--gpu-backend" in command:
            return self._blender(command)
        if command[:3] == [sys.executable, "-m", "manim"]:
            return self._manim(command)
        if command[0] == "ffprobe":
            folder = Path(command[-1]).parent
            compiled = folder / "compiled.json"
            if compiled.is_file():
                return 0, str(json.loads(compiled.read_text(encoding="utf-8"))["duration_s"])
            return 0, "8.5"
        if command[0] == "ffmpeg":
            output = Path(command[-1])
            if output.suffix == ".png":
                Image.new("RGB", (64, 36), "#333333").save(output)
            else:
                output.write_bytes(b"mp4")
            return 0, ""
        raise AssertionError(f"unexpected command: {command[:3]}")

    def _blender(self, command):
        index = command.index("--")
        compiled = json.loads(Path(command[index + 1]).read_text(encoding="utf-8"))
        if compiled["shot"] == self.fail_blender_for:
            return 1, "EEVEE crashed"
        frames_dir = Path(command[index + 2])
        frames_dir.mkdir(parents=True, exist_ok=True)
        picture = Image.linear_gradient("L").resize((64, 36)).convert("RGB")
        for number in range(1, compiled["frames"] + 1):
            picture.save(frames_dir / f"frame_{number:04d}.png")
        return 0, "STUDIO_SHOT_OK"

    def _manim(self, command):
        class_name = command[-1]
        media = Path(command[command.index("--media_dir") + 1])
        scene_text = Path(command[-2]).read_text(encoding="utf-8")
        compiled_path = Path(scene_text.split("(r'")[-1].split("')")[0]
                             if "(r'" in scene_text else
                             scene_text.split("('")[-1].split("')")[0].replace("\\\\", "\\"))
        compiled = json.loads(compiled_path.read_text(encoding="utf-8"))
        if self.latex_fails and compiled["equations"]:
            return 1, "LaTeX compilation error"
        if class_name == "StudioCard":
            target = media / "videos" / "x" / "StudioCard.mp4"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"mp4")
        else:
            target = media / "images" / "x" / "StudioOverlay_v.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (64, 36), (0, 0, 0, 0)).save(target)
        return 0, ""


# ------------------------------------------------------------------- assembly

def test_build_film_renders_checks_and_joins_every_shot(tmp_path):
    tools = FakeTools()
    seen: list[tuple[str, str]] = []
    result = film.build_film(load_spec(OFFLINE), tmp_path, runner=tools,
                             on_shot=lambda shot, state: seen.append((shot, state["state"])),
                             log=lambda line: None)
    assert result["outcome"] == "film_ready"
    assert [s["state"] for s in result["shots"].values()] == ["accepted"] * 4
    assert (tmp_path / "film.mp4").is_file() and (tmp_path / "contact_sheet.png").is_file()
    listed = (tmp_path / "segments.txt").read_text(encoding="utf-8").splitlines()
    assert [Path(line.split("'")[1]).parent.name for line in listed] == [
        "s1_title", "s2_crystal", "s3_bands", "s4_end"]
    assert ("s2_crystal", "rendering") in seen and ("s2_crystal", "measuring") in seen
    overlays = [c for c in tools.commands if c[0] == "ffmpeg" and "-filter_complex" in c]
    assert len(overlays) == 2  # both 3D shots have a caption
    blender = next(c for c in tools.commands if "--gpu-backend" in c)
    assert blender[blender.index("--gpu-backend") + 1] == "opengl"


def test_a_failed_shot_is_left_out_and_recorded(tmp_path):
    result = film.build_film(load_spec(OFFLINE), tmp_path,
                             runner=FakeTools(fail_blender_for="s2_crystal"),
                             log=lambda line: None)
    assert result["outcome"] == "film_partial"
    assert result["shots"]["s2_crystal"]["state"] == "failed"
    assert "EEVEE crashed" in result["shots"]["s2_crystal"]["error"]
    assert len((tmp_path / "segments.txt").read_text(encoding="utf-8").splitlines()) == 3


def test_a_card_whose_latex_fails_is_rendered_without_equations(tmp_path):
    result = film.build_film(load_spec(OFFLINE), tmp_path, runner=FakeTools(latex_fails=True),
                             log=lambda line: None)
    title = result["shots"]["s1_title"]
    assert title["state"] == "accepted" and "equations_dropped" in title
    assert "overlay_dropped" in result["shots"]["s3_bands"]
    assert result["outcome"] == "film_ready"


def test_check_frames_reports_missing_and_empty_frames(tmp_path):
    Image.new("RGB", (32, 18), "#0c0c0b").save(tmp_path / "frame_0001.png")
    problems = film.check_frames(tmp_path, 2)
    assert any("expected 2 frames" in p for p in problems)
    assert any("empty" in p for p in problems)


# --------------------------------------------------------------------- agents

class FakeRuntime:
    name = "fake"

    def __init__(self, replies):
        self.replies = list(replies)
        self.prompts: list[str] = []

    def run(self, spec, prompt, *, cwd):
        self.prompts.append(prompt)
        return AgentResult(ok=True, text=self.replies.pop(0), session_id="s", turns=1,
                           runtime=self.name, model="test-model")


BRIEF = {
    "title": "Two sublattices", "audience": "students", "answer": "The bands split by spin.",
    "equations": [{"id": "split", "latex": "E_\\uparrow \\neq E_\\downarrow"}],
    "beats": [{"id": f"b{i}", "idea": "i", "narration": "n", "visual": "v"} for i in range(4)],
}


def test_extract_json_reads_plain_and_fenced_replies():
    assert authoring.extract_json('Here it is:\n```json\n{"a": {"b": 1}}\n```') == {"a": {"b": 1}}
    with pytest.raises(ValueError):
        authoring.extract_json("no object here")


def test_budget_rules_are_reported():
    data = offline_dict()
    data["shots"] = data["shots"][1:]  # starts with a 3D shot
    data["world"]["width"], data["world"]["height"] = 3840, 2160
    problems = authoring.check_budget(SceneSpec.model_validate(data))
    assert any("1280x720" in p for p in problems)
    assert any("must be cards" in p for p in problems)


def test_a_rejected_answer_is_sent_back_with_its_problems(tmp_path):
    bad = offline_dict()
    bad["shots"][1]["camera"] = "nowhere"
    runtime = FakeRuntime([json.dumps(bad), "```json\n" + json.dumps(offline_dict()) + "\n```"])
    spec = authoring.write_spec(runtime, "q", authoring.Brief.model_validate(BRIEF), tmp_path,
                                log=lambda line: None)
    assert spec.title.startswith("Offline rehearsal")
    assert "unknown camera 'nowhere'" in runtime.prompts[1]
    trace = [json.loads(line) for line in
             (tmp_path / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [t["accepted"] for t in trace] == [False, True]
    assert (tmp_path / "agents" / "spec_author_2_reply.txt").is_file()


def test_three_bad_answers_stop_the_step(tmp_path):
    runtime = FakeRuntime(["not json"] * 3)
    with pytest.raises(authoring.AuthoringFailed, match="no valid answer in 3 attempts"):
        authoring.direct(runtime, "q", tmp_path, log=lambda line: None)


# ------------------------------------------------------------------------ run

def test_offline_run_reaches_film_ready_and_records_every_stage(tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path))
    manifest = machine.run_film("offline rehearsal", offline=True, runner=FakeTools(),
                                log=lambda line: None)
    assert manifest["status"] == {"run": "completed", "stage": "done", "outcome": "film_ready"}
    assert [s["stage"] for s in manifest["stages"]] == ["directing", "speccing", "rendering"]
    run_dir = tmp_path / "studio" / manifest["run_id"]
    on_disk = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert on_disk["status"]["outcome"] == "film_ready"
    assert Path(on_disk["film"]).is_file() and (run_dir / "scenespec.json").is_file()
    assert machine.list_runs()[0]["run_id"] == manifest["run_id"]
    assert machine.read_manifest(manifest["run_id"])["mode"] == "offline"


def test_agent_run_writes_brief_spec_and_film(tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path))
    runtime = FakeRuntime([json.dumps(BRIEF), json.dumps(offline_dict())])
    manifest = machine.run_film("What is altermagnetism?", runtime=runtime,
                                runner=FakeTools(), log=lambda line: None)
    run_dir = tmp_path / "studio" / manifest["run_id"]
    assert manifest["status"]["outcome"] == "film_ready" and manifest["runtime"] == "fake"
    assert json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))["title"] == \
        "Two sublattices"
    assert "The Director's brief" in runtime.prompts[1]


def test_a_failed_stage_is_recorded_with_its_name(tmp_path, monkeypatch):
    monkeypatch.setenv("M2M_RUNS_DIR", str(tmp_path))
    manifest = machine.run_film("bad spec", spec_path=tmp_path / "missing.json",
                                runner=FakeTools(), log=lambda line: None)
    assert manifest["status"] == {"run": "failed", "stage": "speccing", "outcome": "failed"}
    assert "FileNotFoundError" in manifest["error"]

    runtime = FakeRuntime(["not json"] * 3)
    manifest = machine.run_film("no brief", runtime=runtime, runner=FakeTools(),
                                log=lambda line: None)
    assert manifest["status"]["stage"] == "directing" and manifest["status"]["run"] == "failed"
