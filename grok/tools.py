"""Local function tools Grok may call during composer."""

from __future__ import annotations

import base64
import binascii
import json
from pathlib import Path

from grok.validation import verify_scene_report


def verify_scene(*, source: str = "", **_unused) -> dict:
    if not source or not str(source).strip():
        return {"passed": False, "scene_name": None, "errors": ["source was empty"]}
    return verify_scene_report(str(source))


def write_stills(run_dir: Path, images: list[dict]) -> list[str]:
    if not images:
        return []
    stills_dir = run_dir / "stills"
    stills_dir.mkdir(exist_ok=True)
    written: list[str] = []
    for index, image in enumerate(images, start=1):
        raw = image.get("result")
        if not raw or not isinstance(raw, str):
            continue
        if raw.startswith("data:") and "," in raw:
            raw = raw.split(",", 1)[1]
        path = stills_dir / f"{index:02d}.jpg"
        try:
            path.write_bytes(base64.b64decode(raw, validate=False))
        except (ValueError, binascii.Error):
            continue
        meta = {
            "filename": path.name,
            "prompt": image.get("prompt"),
            "id": image.get("id"),
        }
        (stills_dir / f"{index:02d}.json").write_text(
            json.dumps(meta, indent=2),
            encoding="utf-8",
        )
        written.append(str(path.relative_to(run_dir)).replace("\\", "/"))
    return written
