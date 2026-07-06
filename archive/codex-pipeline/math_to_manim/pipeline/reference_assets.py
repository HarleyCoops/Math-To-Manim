"""Reference asset capture for reproducible animation runs."""

from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path
import re
import shutil

from math_to_manim.schemas import ReferenceAsset, ReferenceAssets


def store_reference_images(run_dir: Path, image_paths: list[str | Path] | None) -> ReferenceAssets | None:
    if not image_paths:
        return None

    asset_dir = run_dir / "reference_assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    assets = []
    for index, raw_path in enumerate(image_paths, start=1):
        source = Path(raw_path).expanduser().resolve()
        if not source.exists():
            raise FileNotFoundError(f"Reference image does not exist: {source}")
        if not source.is_file():
            raise ValueError(f"Reference image path is not a file: {source}")

        digest = _sha256(source)
        destination = asset_dir / _asset_filename(source, digest=digest, index=index)
        shutil.copy2(source, destination)
        media_type, _encoding = mimetypes.guess_type(source.name)
        assets.append(
            ReferenceAsset(
                source_path=str(source),
                bundle_path=str(destination),
                media_type=media_type,
                sha256=digest,
                size_bytes=source.stat().st_size,
                metadata={"original_name": source.name},
            )
        )

    return ReferenceAssets(
        assets=assets,
        metadata={
            "count": len(assets),
            "directory": str(asset_dir),
        },
    )


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _asset_filename(source: Path, *, digest: str, index: int) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", source.stem).strip("-") or f"reference-{index}"
    suffix = source.suffix if source.suffix else ".bin"
    return f"{stem}-{digest[:12]}{suffix}"
