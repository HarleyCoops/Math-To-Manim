"""Video review agent scaffolding.

This agent is designed to be appended to the Claude Agent SDK pipeline after
`CodeGenerator`. It leverages the existing `tools.video_review_toolkit` module
to automate post-render QA tasks such as frame extraction and HTML5 player
generation.

For now the agent exposes a synchronous `review` method returning a structured
result object. The plan is to wrap this inside the Claude agent runtime in a
future iteration so the VideoReview step can participate in the multi-agent
conversation.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional


# Ensure the project root (which contains the `tools` package) is importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from tools.video_review_toolkit import VideoReviewToolkit  # noqa: E402  pylint: disable=wrong-import-position


@dataclass
class VideoReviewResult:
    """Structured output produced by the VideoReview agent."""

    video_path: Path
    frames_dir: Path
    web_player_path: Optional[Path]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation."""

        payload = asdict(self)
        payload.update(
            {
                "video_path": str(self.video_path),
                "frames_dir": str(self.frames_dir),
                "web_player_path": str(self.web_player_path) if self.web_player_path else None,
            }
        )
        return payload

    def to_json(self, **dumps_kwargs: Any) -> str:
        """Serialize the payload to JSON (useful when returning via SDK)."""

        return json.dumps(self.to_dict(), **dumps_kwargs)


@dataclass
class VideoReviewConfig:
    """Optional configuration for the review step."""

    fps: Optional[float] = None
    every_nth_frame: Optional[int] = 10
    quality: int = 4
    generate_web_player: bool = True
    output_frames_dir: Optional[Path] = None
    output_player_name: Optional[str] = None


class VideoReviewAgent:
    """Agent responsible for automating video QA helpers."""

    def __init__(self, toolkit: Optional[VideoReviewToolkit] = None) -> None:
        self.toolkit = toolkit or VideoReviewToolkit()

    def review(self, video_path: Path | str, config: Optional[VideoReviewConfig] = None) -> VideoReviewResult:
        """Run the review workflow for ``video_path``.

        Parameters
        ----------
        video_path:
            Absolute or relative path to the rendered MP4 produced by CodeGenerator.
        config:
            Optional overrides controlling frame sampling and player generation.
        """

        config = config or VideoReviewConfig()
        video_path = Path(video_path).resolve()

        if not video_path.exists():
            raise FileNotFoundError(f"Video not found at {video_path}")

        frames_dir = self.toolkit.extract_frames(
            str(video_path),
            output_dir=str(config.output_frames_dir) if config.output_frames_dir else None,
            fps=config.fps,
            every_nth_frame=config.every_nth_frame,
            quality=config.quality,
        )

        metadata = self.toolkit.get_video_info(str(video_path))

        web_player_path: Optional[Path] = None
        if config.generate_web_player:
            player_name = config.output_player_name or f"{video_path.stem}_review.html"
            web_player_path = self.toolkit.create_web_player(str(video_path), output_html=player_name)

        return VideoReviewResult(
            video_path=video_path,
            frames_dir=frames_dir,
            web_player_path=web_player_path,
            metadata=metadata,
        )


__all__ = ["VideoReviewAgent", "VideoReviewConfig", "VideoReviewResult"]

