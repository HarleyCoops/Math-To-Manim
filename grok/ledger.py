"""Hash-bound record of accepted Grok stages."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def empty_ledger() -> dict:
    return {"version": 1, "stages": {}, "events": []}


def load_ledger(run_dir: Path) -> dict:
    path = Path(run_dir) / "ledger.json"
    if not path.is_file():
        return empty_ledger()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty_ledger()
    if not isinstance(data, dict):
        return empty_ledger()
    data.setdefault("version", 1)
    data.setdefault("stages", {})
    data.setdefault("events", [])
    return data


def save_ledger(run_dir: Path, ledger: dict) -> None:
    path = Path(run_dir) / "ledger.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    temporary.replace(path)


def file_hashes(run_dir: Path, relative_paths: list[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    root = Path(run_dir)
    for relative in relative_paths:
        hashes[relative] = digest(root / relative)
    return hashes


def hashes_match(run_dir: Path, hashes: dict[str, str]) -> bool:
    root = Path(run_dir)
    for relative, expected in hashes.items():
        path = root / relative
        if not path.is_file():
            return False
        if digest(path) != expected:
            return False
    return True
