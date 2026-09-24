from __future__ import annotations

from pathlib import Path

import pytest

from m2m2_visual_improvement.renderer import ProcessResult
from m2m2_visual_improvement.schemas import (
    FocusBeat,
    OcrBox,
    Resolution,
    TrackedObject,
)
from m2m2_visual_improvement.telemetry import (
    clipping_ratio,
    density_ratio,
    detect_colored_object,
    extract_visual_evidence,
    overlap_ratio,
    sample_video_frames,
)

PIL = pytest.importorskip("PIL")
from PIL import Image, ImageDraw  # noqa: E402


class StaticOcrEngine:
    def extract(self, image_path: Path, *, timestamp: float) -> tuple[OcrBox, ...]:
        return (
            OcrBox(
                text="Visible formula",
                confidence=0.95,
                x=0,
                y=10,
                width=30,
                height=12,
                timestamp=timestamp,
            ),
        )


class FrameWritingRunner:
    def __init__(self):
        self.commands: list[tuple[str, ...]] = []

    def run(
        self,
        args: tuple[str, ...],
        *,
        cwd: Path,
        timeout_seconds: float,
        env: dict[str, str],
    ) -> ProcessResult:
        self.commands.append(args)
        output_path = Path(args[-1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (100, 50), "#f3ecd8").save(output_path)
        return ProcessResult(
            returncode=0,
            stdout="",
            stderr="",
            timed_out=False,
        )


def test_frame_sampling_emits_one_bounded_ffmpeg_command_per_timestamp(
    tmp_path: Path,
) -> None:
    video = tmp_path / "lesson.mp4"
    video.write_bytes(b"video")
    runner = FrameWritingRunner()

    frames = sample_video_frames(
        video,
        timestamps=(0.0, 2.5),
        output_dir=tmp_path / "frames",
        runner=runner,
    )

    assert [path.name for path in frames] == [
        "frame_000.png",
        "frame_001.png",
    ]
    assert len(runner.commands) == 2
    assert runner.commands[1][runner.commands[1].index("-ss") + 1] == "2.500000"
    assert runner.commands[0][-1] == str(frames[0])


def test_clipping_overlap_and_density_have_hand_checked_values() -> None:
    resolution = Resolution(width=100, height=50)
    boxes = (
        TrackedObject(
            object_id="a",
            timestamp=0,
            x=0,
            y=0,
            width=20,
            height=10,
        ),
        TrackedObject(
            object_id="b",
            timestamp=0,
            x=5,
            y=0,
            width=20,
            height=10,
        ),
    )
    assert clipping_ratio(
        boxes[:1],
        resolution=resolution,
        safe_margin_pixels=5,
    ) == pytest.approx(0.625)
    assert overlap_ratio(boxes) == pytest.approx(0.75)

    six = tuple(
        TrackedObject(
            object_id=str(index),
            timestamp=0,
            x=index * 5,
            y=20,
            width=4,
            height=4,
        )
        for index in range(6)
    )
    assert density_ratio(six, max_simultaneous=12) == pytest.approx(0.5)


def test_exact_color_target_is_detected_from_rendered_pixels(
    tmp_path: Path,
) -> None:
    frame = tmp_path / "frame.png"
    image = Image.new("RGB", (100, 50), "#f3ecd8")
    ImageDraw.Draw(image).rectangle((40, 20, 59, 29), fill="#b24c3d")
    image.save(frame)

    detected = detect_colored_object(
        frame,
        object_id="focus_target",
        color_hex="#b24c3d",
        timestamp=5.0,
        tolerance=0,
    )

    assert detected is not None
    assert detected.object_id == "focus_target"
    assert (detected.x, detected.y, detected.width, detected.height) == (
        40,
        20,
        20,
        10,
    )


def test_evidence_extracts_hashed_contact_sheet_ocr_and_focus(
    tmp_path: Path,
) -> None:
    frames: list[Path] = []
    for index in range(2):
        frame = tmp_path / f"input_{index}.png"
        image = Image.new("RGB", (100, 50), "#f3ecd8")
        ImageDraw.Draw(image).rectangle((40, 20, 59, 29), fill="#b24c3d")
        image.save(frame)
        frames.append(frame)
    focus = FocusBeat(
        beat_id="detail",
        timestamp=5.0,
        target_id="focus_target",
        intended_region=(-0.2, -0.2, 0.2, 0.2),
        min_viewport_occupancy=0.02,
        max_viewport_occupancy=0.2,
    )

    evidence = extract_visual_evidence(
        frame_paths=tuple(frames),
        timestamps=(0.0, 5.0),
        duration_seconds=6.0,
        resolution=Resolution(width=100, height=50),
        focus_beats=(focus,),
        output_dir=tmp_path / "evidence",
        ocr_engine=StaticOcrEngine(),
        target_colors={"focus_target": "#b24c3d"},
    )

    contact_sheet = tmp_path / "evidence" / "contact_sheet.png"
    assert contact_sheet.is_file()
    assert Image.open(contact_sheet).size == (200, 50)
    assert len(evidence.frame_sha256) == 2
    assert len(evidence.contact_sheet_sha256) == 64
    assert [box.text for box in evidence.ocr_boxes] == [
        "Visible formula",
        "Visible formula",
    ]
    assert len(evidence.tracked_objects) == 2
    assert evidence.focus_measurements[0].inside_frame
    assert evidence.focus_measurements[0].viewport_occupancy == pytest.approx(
        0.04
    )
    assert evidence.clipping_ratio > 0
