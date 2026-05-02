"""Optional rendering wrappers that degrade gracefully when binaries are absent."""

from .commands import ToolResult, resolve_binary
from .ffmpeg import VideoProbe, extract_frame, probe_video
from .manim import QUALITY_FLAGS, render_manim_scene

__all__ = [
    "QUALITY_FLAGS",
    "ToolResult",
    "VideoProbe",
    "extract_frame",
    "probe_video",
    "render_manim_scene",
    "resolve_binary",
]
