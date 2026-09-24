"""Offline behavioral checks for the independent evaluator and acceptance gate."""
import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from sol.client import CodexCli
from sol.harness import SolHarness
from sol.jev import Criterion, JevAssessment, JevEvaluator
from sol.models import RunRequest
from sol.offline import write_offline_bundle


def assessment(score=0.9, verified=True, defects=None):
    def criterion(evidence):
        return Criterion(score=score, verified=verified, rationale="Checked supplied evidence",
                         evidence=[evidence])
    return JevAssessment(mathematics=criterion("04_math_dossier.json"),
                         presentation=criterion("frame.png"), defects=defects or [],
                         observations=[], limitations=["Stills do not verify motion"])


class Reviewer(CodexCli):
    def __init__(self, result=None, mutation=None):
        super().__init__(sandbox="read-only", model="gpt-6-astra")
        self.result = result or assessment()
        self.mutation = mutation
        self.calls = []

    def run(self, prompt, **kwargs):
        self.calls.append(kwargs)
        if self.mutation:
            self.mutation(kwargs["cwd"])
        return self.result


@pytest.fixture
def bundle(tmp_path):
    write_offline_bundle(tmp_path, RunRequest(prompt="Explain a theorem"))
    (tmp_path / "frame.png").write_bytes(b"test frame")
    return tmp_path


def review(bundle, client):
    return JevEvaluator(client).review_render(bundle, RunRequest(prompt="Explain a theorem"),
                                             evidence_paths=[bundle / "frame.png"])


def test_astra_independent_read_only_configuration(monkeypatch, tmp_path):
    monkeypatch.setattr("sol.client.shutil.which", lambda _: "codex")
    evaluator = JevEvaluator.from_client(CodexCli(model="writer", reasoning_effort="low"))
    assert evaluator.client.model == "gpt-6-astra"
    assert evaluator.client.reasoning_effort == "high"
    command = evaluator.client.build_command(cwd=tmp_path, schema_path=tmp_path / "schema",
                                             output_path=tmp_path / "output",
                                             image_paths=[tmp_path / "frame.png"])
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert "resume" not in command
    assert "--image" in command
    with pytest.raises(ValueError, match="read-only"):
        JevEvaluator(CodexCli())


def test_gate_and_attempt_snapshots(bundle):
    client = Reviewer()
    assert review(bundle, client)["status"] == "approved"
    (bundle / "frame.png").write_bytes(b"new frame")
    assert review(bundle, client)["status"] == "approved"
    assert (bundle / "jev/001/inputs/frame.png").read_bytes() == b"test frame"
    assert (bundle / "jev/002/inputs/frame.png").read_bytes() == b"new frame"
    assert all("session_id" not in call for call in client.calls)
    assert client.calls[0]["image_paths"] == [bundle / "frame.png"]
    record = json.loads((bundle / "jev/001/record.json").read_text())
    assert record["status"] == "completed"
    assert record["score_kind"] == "uncalibrated_model_judgment"


@pytest.mark.parametrize("score,verified,defects", [(0.79, True, []), (0.99, False, []),
                                                   (1, True, ["Incorrect equality at source line 4"])])
def test_rejection_produces_revision_feedback(bundle, score, verified, defects):
    result = review(bundle, Reviewer(assessment(score, verified, defects)))
    assert result["status"] == "needs_repair"
    assert result["defects"]
    assert result["repair_stage"] == "math-director"


def test_presentation_only_repair(bundle):
    result = assessment()
    result.presentation.score = 0.5
    assert review(bundle, Reviewer(result))["repair_stage"] == "scene-composer"


@pytest.mark.parametrize("value", [-1, 1.01, float("nan"), float("inf")])
def test_invalid_scores_fail(value):
    with pytest.raises(ValidationError):
        assessment(value)


def test_mutation_fails_closed_and_records_error(bundle):
    client = Reviewer(mutation=lambda root: (root / "sol_scene.py").write_text("changed"))
    with pytest.raises(ValueError, match="changed during"):
        review(bundle, client)
    record = json.loads((bundle / "jev/001/record.json").read_text())
    assert record["status"] == "failed"
    assert not (bundle / "review.json").exists()


@pytest.mark.parametrize("kind", ["unknown", "no_frame", "no_source"])
def test_invalid_citations_fail_closed(bundle, kind):
    result = assessment()
    if kind == "unknown":
        result.mathematics.evidence = ["invented.json"]
    elif kind == "no_frame":
        result.presentation.evidence = ["sol_scene.py"]
    else:
        result.mathematics.evidence = ["frame.png"]
    with pytest.raises(ValueError):
        review(bundle, Reviewer(result))


def test_missing_and_outside_frames_rejected(bundle):
    (bundle / "frame.png").unlink()
    with pytest.raises(ValueError, match="missing or empty"):
        review(bundle, Reviewer())
    with pytest.raises(ValueError):
        JevEvaluator(Reviewer()).review_render(bundle, RunRequest(prompt="explain"),
                                              evidence_paths=[bundle.parent / "outside.png"])


@pytest.mark.parametrize("reject_forever", [False, True])
def test_repair_and_resume_always_render_and_review(monkeypatch, tmp_path, reject_forever):
    calls = []
    class Pipeline:
        def __init__(self, **kwargs):
            pass
        def run(self, root, request, **kwargs):
            calls.append(("pipeline", kwargs))
            return write_offline_bundle(root, request)
    def render(root, **kwargs):
        calls.append(("render", kwargs))
        (root / "frame.png").write_bytes(b"test frame")
        video = root / "film.mp4"
        video.write_bytes(b"v" * 4096)
        return SimpleNamespace(frame_paths=[root / "frame.png"], contact_sheet_path=None)
    class SequenceReviewer(Reviewer):
        def run(self, prompt, **kwargs):
            calls.append(("review", {}))
            if reject_forever or sum(c[0] == "review" for c in calls) == 1:
                return assessment(0.2)
            return assessment()
    monkeypatch.setattr("sol.harness.StagedPipeline", Pipeline)
    monkeypatch.setattr("sol.harness.render_scene", render)
    monkeypatch.setattr("sol.harness.preflight_render", lambda: [])
    monkeypatch.setattr(JevEvaluator, "from_client", lambda client: JevEvaluator(SequenceReviewer()))
    harness = SolHarness(runs_dir=tmp_path)
    request = RunRequest(prompt="Explain a theorem", render=True, evaluator="jev", max_repairs=1)
    if reject_forever:
        with pytest.raises(RuntimeError, match="requires repair"):
            harness.run(request)
        manifest = json.loads(next(tmp_path.glob("*/manifest.json")).read_text())
        assert manifest["status"] == "failed"
        assert sum(c[0] == "review" for c in calls) == 2
    else:
        manifest = harness.run(request)
        repair = [kwargs for name, kwargs in calls if name == "pipeline" and kwargs]
        assert repair[0]["from_stage"] == "math-director"
        assert "mathematics" in repair[0]["feedback"]["math-director"]
        assert manifest["status"] == "completed"
        calls.clear()
        harness.resume(manifest["run_id"])
        assert sum(c[0] == "render" for c in calls) == 2
        assert sum(c[0] == "review" for c in calls) == 2


def test_no_render_and_offline_do_not_claim_jev_review(monkeypatch, tmp_path):
    monkeypatch.setattr(JevEvaluator, "from_client", lambda _: pytest.fail("unexpected review"))
    harness = SolHarness(runs_dir=tmp_path)
    result = harness.run(RunRequest(prompt="Explain a theorem", evaluator="jev", offline=True, render=True))
    harness.resume(result["run_id"])
    assert not list(tmp_path.glob("*/jev"))


def test_stale_video_rejected(monkeypatch, tmp_path):
    from sol.rendering import RenderError, render_scene
    (tmp_path / "old.mp4").write_bytes(b"v" * 4096)
    monkeypatch.setattr("sol.rendering.subprocess.run", lambda *a, **k:
                        SimpleNamespace(returncode=0, stdout="", stderr=""))
    with pytest.raises(RenderError, match="fresh video"):
        render_scene(tmp_path, scene_name="ExampleScene", quality="l")


def test_stale_frames_not_reused(monkeypatch, tmp_path):
    from sol.rendering import extract_review_frames
    frames = tmp_path / "review_frames"
    frames.mkdir()
    for i in range(1, 7):
        (frames / f"frame_{i:02d}.png").write_bytes(b"stale")
    (frames / "contact_sheet.png").write_bytes(b"stale")
    def process(command, **kwargs):
        # FFmpeg can exit zero without writing a frame past the end of a video.
        return SimpleNamespace(returncode=0, stdout="10" if command[0] == "ffprobe" else "")
    monkeypatch.setattr("sol.rendering.subprocess.run", process)
    paths, sheet = extract_review_frames(tmp_path, tmp_path / "film.mp4")
    assert paths == []
    assert sheet is None
    assert not list(frames.glob("*.png"))


def test_failed_reviewer_does_not_reuse_approval(bundle):
    assert review(bundle, Reviewer())["status"] == "approved"
    def fail(root):
        raise RuntimeError("reviewer unavailable")
    with pytest.raises(RuntimeError, match="unavailable"):
        review(bundle, Reviewer(mutation=fail))
    assert not (bundle / "review.json").exists()
    assert json.loads((bundle / "jev/002/record.json").read_text())["status"] == "failed"
    assert (bundle / "jev/001/review.json").exists()
